"""Application-level exceptions shared by the API and services."""

from typing import Any


class AppError(Exception):
    """Base error for expected business and application failures."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}
