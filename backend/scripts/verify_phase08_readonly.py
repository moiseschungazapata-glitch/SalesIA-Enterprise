"""Read-only phase 08 smoke test against the configured database."""

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.security import ADMIN_ROLE, create_access_token
from app.db.session import SessionLocal
from app.main import app
from app.models.identity import Role, User


def main() -> None:
    with SessionLocal() as session:
        admin_id = session.scalar(
            select(User.id)
            .join(Role, Role.id == User.role_id)
            .where(Role.code == ADMIN_ROLE, User.active.is_(True))
            .order_by(User.id)
        )
    if admin_id is None:
        raise SystemExit("No existe un administrador activo para la verificacion")

    token, _expires_in = create_access_token(admin_id)
    headers = {"Authorization": f"Bearer {token}"}
    paths = [
        "/api/v1/inventory?page=1&page_size=1",
        "/api/v1/inventory/movements?page=1&page_size=1",
        "/api/v1/sales?page=1&page_size=1",
    ]
    with TestClient(app, raise_server_exceptions=False) as client:
        for path in paths:
            response = client.get(path, headers=headers)
            payload = response.json()
            total = payload.get("total", "-") if isinstance(payload, dict) else "-"
            print(f"{path.split('?')[0]}: HTTP {response.status_code}, total={total}")
            if response.status_code != 200:
                raise SystemExit("La verificacion de lectura de fase 08 fallo")


if __name__ == "__main__":
    main()
