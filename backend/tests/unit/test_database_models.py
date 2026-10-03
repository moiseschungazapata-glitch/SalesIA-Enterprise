"""Structural checks for the phase 04 database model."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from sqlalchemy import CheckConstraint, Numeric
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from app import models  # noqa: F401
from app.core.config import Settings
from app.db.base import Base

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


def _migration_metadata():
    migration_path = (
        Path(__file__).resolve().parents[3]
        / "database"
        / "migrations"
        / "versions"
        / "20261002_0001_initial_schema.py"
    )
    spec = spec_from_file_location("initial_schema", migration_path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._build_schema()


def test_all_planned_tables_are_registered() -> None:
    assert set(Base.metadata.tables) == EXPECTED_TABLES


def test_every_foreign_key_resolves() -> None:
    for table in Base.metadata.sorted_tables:
        for foreign_key in table.foreign_keys:
            assert foreign_key.column.table.name in EXPECTED_TABLES


def test_models_compile_for_postgresql() -> None:
    dialect = postgresql.dialect()
    for table in Base.metadata.sorted_tables:
        ddl = str(CreateTable(table).compile(dialect=dialect))
        assert f"CREATE TABLE {table.name}" in ddl


def test_migration_snapshot_matches_model_tables_and_columns() -> None:
    migration_metadata = _migration_metadata()
    assert set(migration_metadata.tables) == set(Base.metadata.tables)

    for name, model_table in Base.metadata.tables.items():
        migration_table = migration_metadata.tables[name]
        assert set(migration_table.columns.keys()) == set(model_table.columns.keys())
        assert {(fk.parent.name, fk.target_fullname) for fk in migration_table.foreign_keys} == {
            (fk.parent.name, fk.target_fullname) for fk in model_table.foreign_keys
        }


def test_money_is_decimal_and_core_integrity_checks_exist() -> None:
    assert isinstance(Base.metadata.tables["products"].c.unit_price.type, Numeric)
    assert isinstance(Base.metadata.tables["sales"].c.total.type, Numeric)
    assert isinstance(Base.metadata.tables["payments"].c.amount.type, Numeric)

    check_names = {
        constraint.name
        for table in Base.metadata.tables.values()
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    }
    assert "ck_inventory_quantity_non_negative" in check_names
    assert "ck_sale_details_subtotal_matches" in check_names
    assert "ck_inventory_movements_sale_reference_matches_type" in check_names


def test_provider_postgres_urls_use_psycopg_driver() -> None:
    settings = Settings(
        database_url="postgresql://user:password@example.test:5432/postgres",
        _env_file=None,
    )
    assert settings.database_url.startswith("postgresql+psycopg://")
