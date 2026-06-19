import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.router import api_router
from .core.config import settings
from .core.exceptions import AppError

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

app = FastAPI(title="AgriProfit API", version="0.1.0")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every request with its status code and duration."""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info("%s %s -> %s (%.1fms)", request.method, request.url.path, response.status_code, duration_ms)
    return response

# Set up CORS — origins are configured per environment (see core/config.py).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError):
    """Map domain errors (raised by services) to clean JSON responses."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception):
    """Last-resort handler: log the traceback, return a generic 500 (no leak)."""
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to the AgriProfit API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
