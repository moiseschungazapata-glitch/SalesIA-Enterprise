"""Exercise phase 11 persistence against Supabase and roll it back."""

from sqlalchemy import select

from app.core.security import ADMIN_ROLE
from app.db.session import SessionLocal
from app.models.identity import Role, User
from app.schemas.insights import InsightGenerationRequest
from app.services.insights import InsightService


def main() -> None:
    with SessionLocal() as session:
        admin = session.scalar(
            select(User)
            .join(Role, Role.id == User.role_id)
            .where(Role.code == ADMIN_ROLE, User.active.is_(True))
            .order_by(User.id)
        )
        if admin is None:
            raise SystemExit("No existe un administrador activo para la verificacion")

        try:
            result = InsightService(session, admin.company_id, admin.id).generate(
                InsightGenerationRequest(branch="main")
            )
            session.flush()
            print(f"OK: dataset temporal {result['dataset_id']}")
            print(f"OK: analisis temporal {result['analysis_id']}")
            print(f"OK: insights explicables generados={result['generated_count']}")
            print("OK: persistencia de fase 11 compatible con Supabase")
        finally:
            session.rollback()
            print("OK: transaccion revertida; no se conservaron datos de prueba")


if __name__ == "__main__":
    main()
