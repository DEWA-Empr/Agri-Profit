"""Domain exceptions mapped to HTTP responses by handlers in main.py.

Services raise these instead of importing FastAPI, keeping the business layer
free of web concerns (see STRUCTURE.md §2).
"""


class AppError(Exception):
    """Base class for domain errors that map to an HTTP status."""

    status_code: int = 500
    detail: str = "Internal server error"

    def __init__(self, detail: str | None = None):
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class NotFoundError(AppError):
    status_code = 404
    detail = "Resource not found"


class ConflictError(AppError):
    status_code = 409
    detail = "Conflict"


class ValidationError(AppError):
    """A request that is well-formed but asks for a state the domain forbids.

    422 rather than 400 to sit alongside Pydantic's own schema rejections: from
    the client's point of view "this field is out of range" and "this change
    would leave the farm with no owner" are the same class of problem — the
    request was understood and refused on its content — and answering them with
    two different statuses would make that harder to handle, not easier.
    """
    status_code = 422
    detail = "Request could not be processed"


class ServiceUnavailableError(AppError):
    status_code = 503
    detail = "Service temporarily unavailable"
