"""Application errors and their safe HTTP representations."""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base error for expected business and application failures."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.headers = headers


def error_payload(
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        }
    }


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload(exc.code, exc.message, exc.details),
        headers=exc.headers,
    )


async def validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    business_validation_codes = {
        "empty_sale": ("EMPTY_SALE", "La venta debe incluir productos"),
        "invalid_quantity": ("INVALID_QUANTITY", "La cantidad debe ser mayor que cero"),
        "invalid_payment_method": (
            "INVALID_PAYMENT_METHOD",
            "El metodo de pago no es valido",
        ),
    }
    fields = [
        {
            "field": ".".join(str(part) for part in error["loc"] if part != "body"),
            "message": error["msg"],
            "type": error["type"],
        }
        for error in exc.errors()
    ]
    for error in exc.errors():
        business_error = business_validation_codes.get(error["type"])
        if business_error is not None:
            code, message = business_error
            return JSONResponse(
                status_code=422,
                content=error_payload(code, message, {"fields": fields}),
            )
    return JSONResponse(
        status_code=422,
        content=error_payload(
            "VALIDATION_ERROR",
            "Uno o mas campos son invalidos",
            {"fields": fields},
        ),
    )


async def http_error_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    codes = {
        401: ("INVALID_TOKEN", "El token es invalido, vencio o no fue enviado"),
        403: ("FORBIDDEN", "No tiene permiso para realizar esta operacion"),
        404: ("NOT_FOUND", "El recurso solicitado no existe"),
        405: ("METHOD_NOT_ALLOWED", "El metodo HTTP no esta permitido"),
    }
    code, message = codes.get(
        exc.status_code,
        ("HTTP_ERROR", str(exc.detail) if exc.detail else "La solicitud no pudo procesarse"),
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload(code, message),
        headers=exc.headers,
    )


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "Unexpected error while processing %s %s",
        request.method,
        request.url.path,
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content=error_payload("INTERNAL_ERROR", "Ocurrio un error interno inesperado"),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, http_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unexpected_error_handler)
