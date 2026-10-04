"""Authentication and user-management business services."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.security import hash_password, verify_password_or_dummy
from app.models.company import Company
from app.models.identity import Role, User
from app.schemas.users import UserCreate, UserUpdate


@dataclass(frozen=True)
class UserRecord:
    id: int
    company_id: int
    name: str
    email: str
    role: str
    active: bool
    created_at: datetime
    updated_at: datetime


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _to_record(user: User, role_code: str) -> UserRecord:
    return UserRecord(
        id=user.id,
        company_id=user.company_id,
        name=user.name,
        email=user.email,
        role=role_code,
        active=user.active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def authenticate_user(session: Session, email: str, password: str) -> UserRecord:
    normalized_email = _normalize_email(email)
    row = session.execute(
        select(User, Role.code, Role.active, Company.active)
        .join(Role, Role.id == User.role_id)
        .join(Company, Company.id == User.company_id)
        .where(func.lower(User.email) == normalized_email)
        .order_by(User.id)
    ).first()

    user = row[0] if row else None
    password_is_valid = verify_password_or_dummy(
        password,
        user.password_hash if user is not None else None,
    )
    if user is None or not password_is_valid:
        if user is not None:
            if user.locked_until is not None:
                locked_until = user.locked_until
                if locked_until.tzinfo is None:
                    locked_until = locked_until.replace(tzinfo=UTC)
                if locked_until <= datetime.now(UTC):
                    user.locked_until = None
                    user.failed_login_attempts = 0
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.login_max_failed_attempts:
                user.locked_until = datetime.now(UTC) + timedelta(
                    minutes=settings.login_lock_minutes
                )
                user.failed_login_attempts = 0
            session.info["login_failure"] = {
                "company_id": user.company_id,
                "user_id": user.id,
                "locked": user.locked_until is not None,
            }
            session.flush()
        raise AppError(
            "INVALID_CREDENTIALS",
            "El correo o la contraseña son incorrectos",
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"},
        )

    now = datetime.now(UTC)
    locked_until = user.locked_until
    if locked_until is not None:
        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=UTC)
        if locked_until > now:
            session.info["login_failure"] = {
                "company_id": user.company_id,
                "user_id": user.id,
                "locked": True,
            }
            raise AppError(
                "ACCOUNT_LOCKED",
                "La cuenta esta bloqueada temporalmente por seguridad",
                status_code=423,
            )

    role_code, role_is_active, company_is_active = row[1], row[2], row[3]
    if not user.active:
        raise AppError("USER_INACTIVE", "El usuario esta inactivo", status_code=403)
    if not role_is_active or not company_is_active:
        raise AppError("FORBIDDEN", "El acceso del usuario no esta disponible", status_code=403)

    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = now
    session.flush()
    return _to_record(user, role_code)


class UserService:
    def __init__(self, session: Session, company_id: int) -> None:
        self.session = session
        self.company_id = company_id

    def list(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        active: bool | None = None,
        role: str | None = None,
    ) -> tuple[list[UserRecord], int]:
        filters = [User.company_id == self.company_id]
        if search:
            normalized_search = search.strip().lower()
            filters.append(
                or_(
                    func.lower(User.name).contains(normalized_search, autoescape=True),
                    func.lower(User.email).contains(normalized_search, autoescape=True),
                )
            )
        if active is not None:
            filters.append(User.active.is_(active))
        if role is not None:
            filters.append(Role.code == role)

        statement = (
            select(User, Role.code)
            .join(Role, Role.id == User.role_id)
            .where(*filters)
            .order_by(User.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = self.session.execute(statement).all()
        total = self.session.scalar(
            select(func.count(User.id)).join(Role, Role.id == User.role_id).where(*filters)
        )
        return [_to_record(user, role_code) for user, role_code in rows], int(total or 0)

    def get(self, user_id: int) -> UserRecord:
        user, role_code = self._get_user_row(user_id)
        return _to_record(user, role_code)

    def create(self, payload: UserCreate) -> UserRecord:
        email = _normalize_email(str(payload.email))
        if self._email_exists(email):
            raise AppError(
                "EMAIL_ALREADY_EXISTS",
                "El correo ya esta registrado",
                status_code=409,
            )

        role = self._get_role(payload.role.value)
        user = User(
            company_id=self.company_id,
            role_id=role.id,
            name=payload.name,
            email=email,
            password_hash=hash_password(payload.password.get_secret_value()),
            active=True,
        )
        self.session.add(user)
        self._flush_or_email_conflict()
        return _to_record(user, role.code)

    def update(self, user_id: int, payload: UserUpdate) -> UserRecord:
        user, current_role = self._get_user_row(user_id)

        if payload.name is not None:
            user.name = payload.name
        if payload.email is not None:
            email = _normalize_email(str(payload.email))
            if email != user.email.lower() and self._email_exists(email, exclude_user_id=user.id):
                raise AppError(
                    "EMAIL_ALREADY_EXISTS",
                    "El correo ya esta registrado",
                    status_code=409,
                )
            user.email = email
        if payload.role is not None:
            role = self._get_role(payload.role.value)
            user.role_id = role.id
            current_role = role.code
        if payload.active is not None:
            user.active = payload.active
        if payload.new_password is not None:
            user.password_hash = hash_password(payload.new_password.get_secret_value())

        self._flush_or_email_conflict()
        return _to_record(user, current_role)

    def _get_user_row(self, user_id: int) -> tuple[User, str]:
        row = self.session.execute(
            select(User, Role.code)
            .join(Role, Role.id == User.role_id)
            .where(User.id == user_id, User.company_id == self.company_id)
        ).one_or_none()
        if row is None:
            raise AppError("USER_NOT_FOUND", "El usuario no existe", status_code=404)
        return row[0], row[1]

    def _get_role(self, code: str) -> Role:
        role = self.session.scalar(select(Role).where(Role.code == code, Role.active.is_(True)))
        if role is None:
            raise AppError("INVALID_ROLE", "El rol indicado no esta disponible", status_code=422)
        return role

    def _email_exists(self, email: str, exclude_user_id: int | None = None) -> bool:
        statement = select(User.id).where(
            User.company_id == self.company_id,
            func.lower(User.email) == email,
        )
        if exclude_user_id is not None:
            statement = statement.where(User.id != exclude_user_id)
        return self.session.scalar(statement) is not None

    def _flush_or_email_conflict(self) -> None:
        try:
            self.session.flush()
        except IntegrityError as exc:
            self.session.rollback()
            raise AppError(
                "EMAIL_ALREADY_EXISTS",
                "El correo ya esta registrado",
                status_code=409,
            ) from exc
