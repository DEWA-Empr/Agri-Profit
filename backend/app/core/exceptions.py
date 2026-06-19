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
