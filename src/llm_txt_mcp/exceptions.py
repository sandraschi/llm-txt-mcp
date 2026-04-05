"""Custom exception classes for LLM.txt MCP server."""

from typing import Any, Dict, Optional


class LLMTextMCPError(Exception):
    """Base exception for LLM.txt MCP errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize exception.

        Args:
            message: Error message
            error_code: Optional error code for programmatic handling
            details: Optional additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for structured logging."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class ValidationError(LLMTextMCPError):
    """Raised when validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize validation error.

        Args:
            message: Error message
            field: Field that failed validation
            value: Invalid value
            details: Additional error details
        """
        error_details = details or {}
        if field:
            error_details["field"] = field
        if value is not None:
            error_details["value"] = str(value)

        super().__init__(message, error_code="VALIDATION_ERROR", details=error_details)


class FileOperationError(LLMTextMCPError):
    """Raised when file operations fail."""

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize file operation error.

        Args:
            message: Error message
            file_path: Path to file that caused the error
            operation: Operation that failed (read, write, delete, etc.)
            details: Additional error details
        """
        error_details = details or {}
        if file_path:
            error_details["file_path"] = file_path
        if operation:
            error_details["operation"] = operation

        super().__init__(message, error_code="FILE_OPERATION_ERROR", details=error_details)


class ProjectAnalysisError(LLMTextMCPError):
    """Raised when project analysis fails."""

    def __init__(
        self,
        message: str,
        project_path: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize project analysis error.

        Args:
            message: Error message
            project_path: Path to project that caused the error
            details: Additional error details
        """
        error_details = details or {}
        if project_path:
            error_details["project_path"] = project_path

        super().__init__(message, error_code="PROJECT_ANALYSIS_ERROR", details=error_details)


class GenerationError(LLMTextMCPError):
    """Raised when content generation fails."""

    def __init__(
        self,
        message: str,
        generation_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize generation error.

        Args:
            message: Error message
            generation_type: Type of generation that failed
            details: Additional error details
        """
        error_details = details or {}
        if generation_type:
            error_details["generation_type"] = generation_type

        super().__init__(message, error_code="GENERATION_ERROR", details=error_details)


class ServiceError(LLMTextMCPError):
    """Raised when service operations fail."""

    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize service error.

        Args:
            message: Error message
            service_name: Name of service that failed
            details: Additional error details
        """
        error_details = details or {}
        if service_name:
            error_details["service_name"] = service_name

        super().__init__(message, error_code="SERVICE_ERROR", details=error_details)

