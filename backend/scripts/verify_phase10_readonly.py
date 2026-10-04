"""Read-only phase 10 dashboard smoke test against the configured database."""

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.company import Company
from app.services.dashboard import DashboardService


def main() -> None:
    with SessionLocal() as session:
        company = session.scalar(
            select(Company).where(Company.active.is_(True)).order_by(Company.id)
        )
        if company is None:
            raise SystemExit("No existe una empresa activa para la verificacion")

        summary = DashboardService(session, company.id).summary(
            date_from=None,
            date_to=None,
            branch="main",
            seller_id=None,
            category_id=None,
        )
        kpis = summary["kpis"]
        print("OK: resumen del dashboard calculado en modo lectura")
        print(f"OK: ventas confirmadas del periodo={kpis['transactions']}")
        print(f"OK: facturacion del periodo={kpis['sales_total']} PEN")
        print(f"OK: periodos generados={len(summary['sales_by_period'])}")
        print(f"OK: vendedores disponibles={len(summary['filter_options']['sellers'])}")
        print(f"OK: categorias disponibles={len(summary['filter_options']['categories'])}")


if __name__ == "__main__":
    main()
