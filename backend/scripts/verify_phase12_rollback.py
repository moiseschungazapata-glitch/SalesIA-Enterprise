"""Exercise all phase 12 report types against Supabase and roll them back."""

from sqlalchemy import select

from app.core.security import ADMIN_ROLE
from app.db.session import SessionLocal
from app.models.identity import Role, User
from app.schemas.reports import ReportGenerateRequest
from app.services.reports import REPORT_TITLES, ReportService


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
            service = ReportService(session, admin.company_id, admin.id)
            for report_type in REPORT_TITLES:
                report = service.generate(ReportGenerateRequest(report_type=report_type))
                print(
                    f"OK: {report_type} reporte={report['id']} filas={report['row_count']}"
                )
            session.flush()
            print("OK: los cinco reportes son compatibles con Supabase")
        finally:
            session.rollback()
            print("OK: transaccion revertida; no se conservaron reportes de prueba")


if __name__ == "__main__":
    main()
