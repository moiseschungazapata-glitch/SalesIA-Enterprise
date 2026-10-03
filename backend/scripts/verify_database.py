"""Verify a migrated SalesIA PostgreSQL database without modifying data."""

from argparse import ArgumentParser, Namespace

from sqlalchemy import inspect, text

from app.db.session import engine

EXPECTED_TABLES = {
    "audit_logs",
    "bayes_analyses",
    "categories",
    "companies",
    "customers",
    "dataset_variables",
    "datasets",
    "employees",
    "insights",
    "inventory",
    "inventory_movements",
    "observations",
    "payments",
    "products",
    "random_variables",
    "reports",
    "roles",
    "sale_details",
    "sales",
    "statistical_analyses",
    "statistical_results",
    "users",
}
EXPECTED_ROLES = {"administrator", "manager", "seller"}


def parse_args() -> Namespace:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--company-slug", default="salesia-enterprise")
    return parser.parse_args()


def verify(company_slug: str) -> None:
    errors: list[str] = []

    with engine.connect() as connection:
        tables = set(inspect(connection).get_table_names(schema="public"))
        application_tables = tables - {"alembic_version"}
        if application_tables != EXPECTED_TABLES:
            missing = sorted(EXPECTED_TABLES - application_tables)
            unexpected = sorted(application_tables - EXPECTED_TABLES)
            errors.append(f"Tablas faltantes={missing}; inesperadas={unexpected}")

        revision = connection.scalar(text("SELECT version_num FROM alembic_version"))
        if revision != "20261002_0001":
            errors.append(f"Revision Alembic inesperada: {revision!r}")

        company = connection.execute(
            text("SELECT name, currency, timezone FROM companies WHERE slug = :company_slug"),
            {"company_slug": company_slug},
        ).one_or_none()
        if company is None:
            errors.append(f"No existe la empresa con slug {company_slug!r}")

        roles = set(connection.scalars(text("SELECT code FROM roles")))
        if roles != EXPECTED_ROLES:
            errors.append(f"Roles inesperados: {sorted(roles)}")

        category_count = connection.scalar(
            text(
                "SELECT count(*) FROM categories c "
                "JOIN companies co ON co.id = c.company_id "
                "WHERE co.slug = :company_slug AND c.name = 'General'"
            ),
            {"company_slug": company_slug},
        )
        if category_count != 1:
            errors.append(f"Categorias General encontradas: {category_count}")

        rls_tables = set(
            connection.scalars(
                text(
                    "SELECT c.relname FROM pg_class c "
                    "JOIN pg_namespace n ON n.oid = c.relnamespace "
                    "WHERE n.nspname = 'public' AND c.relkind = 'r' "
                    "AND c.relrowsecurity"
                )
            )
        )
        missing_rls = EXPECTED_TABLES - rls_tables
        if missing_rls:
            errors.append(f"Tablas sin RLS: {sorted(missing_rls)}")

        public_policy_count = connection.scalar(
            text("SELECT count(*) FROM pg_policies WHERE schemaname = 'public'")
        )
        if public_policy_count != 0:
            errors.append(f"Politicas publicas inesperadas: {public_policy_count}")

    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))

    print(f"OK: revision {revision}")
    print(f"OK: {len(EXPECTED_TABLES)} tablas de aplicacion")
    print(f"OK: empresa {company[0]} ({company_slug})")
    print(f"OK: roles {', '.join(sorted(roles))}")
    print("OK: categoria General sin duplicados")
    print(f"OK: RLS activo en {len(EXPECTED_TABLES)} tablas")
    print("OK: ninguna politica publica habilita acceso directo")


if __name__ == "__main__":
    arguments = parse_args()
    verify(arguments.company_slug)
