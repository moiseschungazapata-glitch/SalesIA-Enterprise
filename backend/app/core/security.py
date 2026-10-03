"""Password hashing and JWT helpers."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import settings
from app.core.exceptions import AppError

ADMIN_ROLE = "administrator"
SELLER_ROLE = "seller"
MANAGER_ROLE = "manager"
ALLOWED_ROLES = frozenset({ADMIN_ROLE, SELLER_ROLE, MANAGER_ROLE})

password_hash = PasswordHash.recommended()
DUMMY_PASSWORD_HASH = password_hash.hash("salesia-invalid-password-placeholder")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, encoded_hash: str) -> bool:
    return password_hash.verify(password, encoded_hash)


def verify_password_or_dummy(password: str, encoded_hash: str | None) -> bool:
    """Keep unknown-email login work comparable to a normal password check."""

    return verify_password(password, encoded_hash or DUMMY_PASSWORD_HASH)


def create_access_token(user_id: int) -> tuple[str, int]:
    issued_at = datetime.now(UTC)
    expires_in = settings.access_token_expire_minutes * 60
    payload = {
        "sub": str(user_id),
        "iat": issued_at,
        "exp": issued_at + timedelta(seconds=expires_in),
        "jti": str(uuid4()),
    }
    token = jwt.encode(
        payload,
        settings.secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )
    return token, expires_in


def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "iat", "exp", "jti"]},
        )
        user_id = int(payload["sub"])
        if user_id <= 0:
            raise ValueError
        return user_id
    except (InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise AppError(
            "INVALID_TOKEN",
            "El token es invalido o vencio",
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
