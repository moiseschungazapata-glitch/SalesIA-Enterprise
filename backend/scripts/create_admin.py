"""Create the first SalesIA administrator with an interactive password prompt."""

from argparse import ArgumentParser, Namespace
from getpass import getpass

from email_validator import EmailNotValidError, validate_email
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import ADMIN_ROLE, hash_password
from app.db.session import engine
from app.models.company import Company
from app.models.identity import Role, User


def parse_args() -> Namespace:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="Administrador SalesIA")
    parser.add_argument("--email", help="Correo del administrador; se solicita si se omite")
    parser.add_argument("--company-slug", default="salesia-enterprise")
    return parser.parse_args()


def read_email(value: str | None) -> str:
    candidate = value or input("Correo del administrador: ").strip()
    try:
        return validate_email(candidate, check_deliverability=False).normalized.lower()
    except EmailNotValidError as exc:
        raise SystemExit(f"Correo invalido: {exc}") from exc


def read_password() -> str:
    password = getpass("Contraseña nueva (12-128 caracteres): ")
    confirmation = getpass("Repita la contraseña: ")
    if password != confirmation:
        raise SystemExit("Las contraseñas no coinciden.")
    if len(password) < 12 or len(password) > 128:
        raise SystemExit("La contraseña debe tener entre 12 y 128 caracteres.")
    return password


def create_admin(name: str, email: str, password: str, company_slug: str) -> int:
    normalized_name = " ".join(name.split())
    if len(normalized_name) < 2 or len(normalized_name) > 160:
        raise SystemExit("El nombre debe tener entre 2 y 160 caracteres.")

    with Session(engine) as session, session.begin():
        company = session.scalar(
            select(Company).where(Company.slug == company_slug, Company.active.is_(True))
        )
        if company is None:
            raise SystemExit(f"No existe una empresa activa con slug {company_slug!r}.")

        role = session.scalar(select(Role).where(Role.code == ADMIN_ROLE, Role.active.is_(True)))
        if role is None:
            raise SystemExit("No existe el rol administrator activo.")

        existing_id = session.scalar(
            select(User.id).where(
                User.company_id == company.id,
                func.lower(User.email) == email,
            )
        )
        if existing_id is not None:
            raise SystemExit(f"Ya existe un usuario con ese correo (id={existing_id}).")

        user = User(
            company_id=company.id,
            role_id=role.id,
            name=normalized_name,
            email=email,
            password_hash=hash_password(password),
            active=True,
        )
        session.add(user)
        session.flush()
        return user.id


if __name__ == "__main__":
    arguments = parse_args()
    admin_email = read_email(arguments.email)
    admin_password = read_password()
    admin_id = create_admin(
        arguments.name,
        admin_email,
        admin_password,
        arguments.company_slug,
    )
    print(f"Administrador creado correctamente con id={admin_id} y correo={admin_email}.")
