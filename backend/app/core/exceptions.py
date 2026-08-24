"""
Domain-level exceptions and centralized FastAPI exception handlers.

Services raise these domain exceptions (they know nothing about HTTP);
the handlers registered in main.py translate them into consistent JSON
error responses. This keeps the service layer transport-agnostic.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class AppError(Exception):
    """Base class for all domain errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "An unexpected error occurred."

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Resource not found."


class AlreadyExistsError(AppError):
    status_code = status.HTTP_409_CONFLICT
    default_message = "Resource already exists."


class InvalidCredentialsError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_message = "Invalid credentials."


class TokenError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_message = "Invalid or expired token."


class PermissionDeniedError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    default_message = "You do not have permission to perform this action."


class ValidationAppError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_message = "Validation failed."


class RateLimitExceededError(AppError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_message = "Too many requests. Please slow down."


class ExternalServiceError(AppError):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_message = "An upstream service failed. Please try again shortly."


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        logger.warning("app_error", path=request.url.path, error=exc.message, status=exc.status_code)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "error_type": exc.__class__.__name__},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.error("unhandled_exception", path=request.url.path, error=str(exc), exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error.", "error_type": "InternalServerError"},
        )
