"""Custom exceptions and error handlers for the StockPilot
API

This module defines:
1. Custom exception classes for different error scenarios
2. Exception handlers that convert exception to clean JSON responses

Every error in the API returns a consistent format:
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable message",
        "status": 400
    }
}
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


# base
class StockPilotError(Exception):
    """Base exception for all StockPilot application erros.
    
    All custom exceptions inherit from this, making it easy to catch any StockPilot-specific error.
    
    Args:
        message: Human-readable error description.
        code: Machine-readable error code (e.g.,"PRODUCT_NOT_FOUND").
        status_code: HTTP status code to return.
    """

    def __init__(
        self,
        message: str = "An unexpected error occured",
        code: str = "Internal_Error",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

# specific
class NotFoundError(StockPilotError):
    """Rased when a request resource doesn't exist."""
    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(
            message=f"{resource} with ID '{identifier}' does not exist.",
            code=f"{resource.upper()}_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )

class DuplicateError(StockPilotError):
    """Raised when attempting to create a resource that already exist"""
    def __init__(self, resource: str, field: str, value: str) -> None:
        super().__init__(
            message=f"{resource} with {field} '{value}' already exist",
            code=f"{resource.upper()}_DUPLICATE",
            status_code=status.HTTP_409_CONFLICT,
        )

class AuthenticationError(StockPilotError):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Invalid Credentials") -> None:
        super().__init__(
            message=message,
            code="AUTHENTICATION_FAILED",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

class AuthorizationError(StockPilotError):
    """Raised when user doesn't have the permission for an action"""
    def __init__(self, message: str = "You do not have permission to perform this action") -> None:
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN,
        )

class ValidationError(StockPilotError):
    """Raised when business logic validation fails"""
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

class InsufficientStockError(StockPilotError):
    """Raised when there isn't enough inventory to fulfill an order"""
    def __init__(self, product_name: str, requested: int, available: int) -> None:
        super().__init__(
            message=f"Insufficient stock for '{product_name}': requested {requested}, available {available}.",
            code="INSUFFICIENT_STOCK",
            status_code=status.HTTP_409_CONFLICT,
        )

# exception handler

def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handler with FastAPI
    
    Called once during app startup in main.py

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(StockPilotError)
    async def stockpilot_error_handler(request: Request, exc: StockPilotError) -> JSONResponse:
        """Handle all SP custom exception"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "status": exc.status_code,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle pydantic validation errors (malformed request bodies).
        FastAPI uses Pydantic to validate incoming data. If someone sends invalid data
        (wrong type, missing field, etc.)
        """
        errors = []
        for error in exc.errors():
            field = "->".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"],
            })

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed. Check the 'details' field.",
                    "status": 422,
                    "details": errors,
                }
            },
        )

    @app.exception_handler(Exception)
    async def general_error_handler(request: Request, exc: Exception) -> JSONResponse:
        """Catch-all handler for unexpected errors"""

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred. Please try again later.",
                    "status": 500,
                }
            },
        )