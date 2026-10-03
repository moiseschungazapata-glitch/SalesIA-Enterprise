"""Exercise phase 09 persistence against the configured database and roll it back."""

from decimal import Decimal

from sqlalchemy import select

from app.core.security import ADMIN_ROLE
from app.db.session import SessionLocal
from app.models.identity import Role, User
from app.schemas.statistics import NumericSeriesRequest
from app.services.analytics import AnalyticsService


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
            result = AnalyticsService(session, admin.company_id, admin.id).analyze_series(
                NumericSeriesRequest(
                    name="Verificacion temporal fase 09",
                    variable_name="verification_value",
                    variable_label="Valor de verificacion",
                    values=[Decimal("10"), Decimal("20"), Decimal("30")],
                ),
                "comparison",
            )
            session.flush()
            print(f"OK: dataset temporal {result['dataset_id']}")
            print(f"OK: analisis temporal {result['analysis_id']}")
            print("OK: persistencia estadistica compatible con Supabase")
        finally:
            session.rollback()
            print("OK: transaccion revertida; no se conservaron datos de prueba")


if __name__ == "__main__":
    main()
