import logging
import time
from contextlib import asynccontextmanager

import math

from sqlalchemy import text
from sqlalchemy.orm import Session

from fastapi import Depends, FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.router import api_router
from .core.config import settings
from .core.exceptions import AppError
from .core.logging_safety import safe_request_line
from .models.database import get_db

# Schema is managed by Alembic migrations (applied on container startup).
# Tests create the schema directly via Base.metadata.create_all (see conftest.py).

logger = logging.getLogger("agriprofit")
logger.setLevel(logging.INFO)
# Attach our own stdout handler so logs emit regardless of uvicorn's config.
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(levelname)s:     [agriprofit] %(message)s"))
    logger.addHandler(_handler)
    logger.propagate = False


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Startup work: train the DSS yield model if the image has none baked in."""
    try:
        from .ml import train

        if train.ensure_model():
            logger.info("DSS model trained on startup")
    except Exception:  # never block API startup on an ML failure
        logger.exception("DSS model startup training failed")
    yield


app = FastAPI(title="AgriProfit API", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every request with its status code and duration.

    The request line goes through `safe_request_line`, which replaces a
    credential carried in the path — the investor report's share token is one —
    with a short non-reversible fingerprint. Logging `request.url.path` raw
    wrote working share links into the log on every investor view.
    """
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s -> %s (%.1fms)",
        safe_request_line(request.method, request.url.path, request.url.query),
        response.status_code,
        duration_ms,
    )
    return response

# Set up CORS — origins are configured per environment (see core/config.py).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _json_safe(value):
    """Make a validation-error payload serialisable.

    FastAPI's 422 body echoes the offending input back to the caller. That is
    useful until the input is exactly what the new bounds exist to reject: a
    non-finite float. `json.dumps` refuses to encode inf/NaN, so the default
    handler raised while rendering the error and the caller received a 500 —
    which is how a correctly REJECTED value still produced the wrong answer.

    Non-finite floats become their name as a string; everything else is
    returned unchanged, so ordinary validation errors read exactly as before.
    """
    if isinstance(value, float) and not math.isfinite(value):
        return repr(value)          # 'inf', '-inf', 'nan'
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError):
    """Return a 422 that can always be rendered.

    Also drops the `ctx` field each Pydantic error carries: it can hold the
    originating exception object, whose repr is an implementation detail of the
    validator rather than anything a client can act on.
    """
    errors = [
        _json_safe({k: v for k, v in error.items() if k != "ctx"})
        for error in exc.errors()
    ]
    return JSONResponse(
        # The literal, not status.HTTP_422_*: Starlette renamed that constant
        # (ENTITY -> CONTENT) and importing either name pins this file to a
        # version window for no benefit. The number is stable.
        status_code=422,
        content={"detail": errors},
    )


@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError):
    """Map domain errors (raised by services) to clean JSON responses."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception):
    """Last-resort handler: log the traceback, return a generic 500 (no leak).

    The request line is scrubbed for the same reason as in the middleware: an
    unhandled error on the investor route must not be the one place a share
    token still reaches the log.
    """
    logger.exception(
        "Unhandled error on %s",
        safe_request_line(request.method, request.url.path, request.url.query),
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to the AgriProfit API"}

@app.get("/health")
async def health_check():
    """LIVENESS. Is this process up and serving?

    Deliberately touches nothing else. A liveness probe that checked the
    database would restart a perfectly healthy application every time Postgres
    hiccupped, turning a brief outage into a restart loop that makes recovery
    slower. "Should I be killed and replaced" and "can I serve traffic right
    now" are different questions; the second one is /health/ready.
    """
    return {"status": "healthy"}


@app.get("/health/ready")
async def readiness_check(response: Response, db: Session = Depends(get_db)):
    """READINESS. Can this instance actually serve a request?

    Answers 200 when the database responds and 503 when it does not, so a proxy
    or an operator can tell "the API is down" from "the API is up and its
    database is not" — which are different problems with different fixes.

    The check is `SELECT 1`: enough to prove the connection pool can reach the
    server and get an answer, cheap enough to run on a probe interval. The error
    is logged in full and NOT returned; a connection string in a probe response
    is a credential in a place nobody is watching.
    """
    checks = {"database": "ok"}
    try:
        # Through the SAME dependency every request uses, not a separate engine
        # handle. A probe that reached the database by its own route could report
        # ready while the path requests actually take was broken.
        db.execute(text("SELECT 1"))
    except Exception:
        logger.exception("Readiness check failed: database unreachable")
        checks["database"] = "unreachable"
        response.status_code = 503
        return {"status": "not ready", "checks": checks}

    return {"status": "ready", "checks": checks}
