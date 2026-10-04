"""Password hashing and JWT helpers."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
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


@dataclass(frozen=True)
class AccessToken:
    encoded: str
    expires_in: int
    jti: str
    expires_at: datetime


@dataclass(frozen=True)
class TokenClaims:
    user_id: int
    jti: str
    expires_at: datetime


def hash_token_jti(jti: str) -> str:
    return sha256(jti.encode("utf-8")).hexdigest()


def create_access_token(user_id: int) -> AccessToken:
    issued_at = datetime.now(UTC)
    expires_in = settings.access_token_expire_minutes * 60
    expires_at = issued_at + timedelta(seconds=expires_in)
    jti = str(uuid4())
    payload = {
        "sub": str(user_id),
        "iat": issued_at,
        "exp": expires_at,
        "jti": jti,
    }
    token = jwt.encode(
        payload,
        settings.secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )
    return AccessToken(token, expires_in, jti, expires_at)


def decode_access_token(token: str) -> TokenClaims:
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
        jti = str(payload["jti"])
        if not jti:
            raise ValueError
        return TokenClaims(
            user_id=user_id,
            jti=jti,
            expires_at=datetime.fromtimestamp(int(payload["exp"]), tz=UTC),
        )
    except (InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise AppError(
            "INVALID_TOKEN",
            "El token es invalido o vencio",
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
