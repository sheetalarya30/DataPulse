from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional


class DataPulseException(Exception):
    """Base exception for all DataPulse application errors."""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class EntityNotFoundError(DataPulseException):
    def __init__(self, entity_name: str, identifier: Any):
        super().__init__(
            message=f"{entity_name} with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"entity": entity_name, "identifier": str(identifier)},
        )


class PipelineExecutionError(DataPulseException):
    def __init__(self, message: str, run_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"run_id": run_id, **(details or {})},
        )


class ValidationFailedError(DataPulseException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=422,
            details=details or {},
        )



async def datapulse_exception_handler(request: Request, exc: DataPulseException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
                "details": exc.details,
            },
        },
    )


async def generic_exception_handler(request: Request, exc: Exception):
    # Hide raw internal stack trace from API client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "message": "An internal server error occurred while processing the request.",
                "type": "InternalServerError",
                "details": str(exc) if False else {},  # Security requirement: do not expose internal traces
            },
        },
    )
