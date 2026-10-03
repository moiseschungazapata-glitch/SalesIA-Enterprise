"""Authentication request and response schemas."""

from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator


class LoginRequest(BaseModel):
    email: EmailStr
    password: SecretStr

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: SecretStr) -> SecretStr:
        length = len(value.get_secret_value())
        if length < 12 or length > 128:
            raise ValueError("La contraseña debe tener entre 12 y 128 caracteres")
        return value


class AuthUser(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str


class SessionUser(AuthUser):
    active: bool


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(gt=0)
    user: AuthUser
