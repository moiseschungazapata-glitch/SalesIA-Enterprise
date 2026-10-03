"""Create the safe reference records required by a fresh SalesIA database."""

from argparse import ArgumentParser

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db.session import engine
from app.models.catalog import Category
from app.models.company import Company
from app.models.identity import Role

ROLES = (
    {
        "code": "administrator",
        "name": "Administrador",
        "description": "Configura usuarios, catalogos, inventario y ventas.",
    },
    {
        "code": "seller",
        "name": "Vendedor",
        "description": "Registra ventas y consulta sus propias operaciones.",
    },
    {
        "code": "manager",
        "name": "Gerente",
        "description": "Consulta ventas, inventario e indicadores comerciales.",
    },
)


def seed(company_name: str, company_slug: str) -> None:
    with Session(engine) as session, session.begin():
        session.execute(
            insert(Company)
            .values(
                name=company_name,
                slug=company_slug,
                currency="PEN",
                timezone="America/Lima",
                active=True,
            )
            .on_conflict_do_nothing(index_elements=[Company.slug])
        )

        company_id = session.scalar(select(Company.id).where(Company.slug == company_slug))
        if company_id is None:
            raise RuntimeError("No se pudo obtener la empresa inicial")

        for role in ROLES:
            session.execute(
                insert(Role)
                .values(**role, active=True)
                .on_conflict_do_update(
                    index_elements=[Role.code],
                    set_={
                        "name": role["name"],
                        "description": role["description"],
                        "active": True,
                    },
                )
            )

        session.execute(
            insert(Category)
            .values(
                company_id=company_id,
                name="General",
                description="Categoria inicial para productos sin clasificacion especifica.",
                active=True,
            )
            .on_conflict_do_nothing()
        )


def parse_args():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--company-name", default="SalesIA Demo")
    parser.add_argument("--company-slug", default="salesia-demo")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    seed(arguments.company_name, arguments.company_slug)
    print("Datos de referencia creados o actualizados correctamente.")
