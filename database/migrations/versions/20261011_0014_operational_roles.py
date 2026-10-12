"""Add analyst and warehouse operational roles.

Revision ID: 20261011_0014
Revises: 20261011_0013
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261011_0014"
down_revision: str | None = "20261011_0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        sa.text("""
        INSERT INTO roles (code, name, description)
        VALUES
            ('analyst', 'Analista', 'Consulta de indicadores, probabilidad, insights y reportes'),
            (
                'warehouse',
                'Almacén',
                'Gestión del catálogo, existencias y movimientos de inventario'
            )
        ON CONFLICT (code) DO UPDATE
        SET name = EXCLUDED.name, description = EXCLUDED.description
        """)
    )


def downgrade() -> None:
    op.execute(
        sa.text("""
        DELETE FROM roles r
        WHERE r.code IN ('analyst', 'warehouse')
          AND NOT EXISTS (SELECT 1 FROM users u WHERE u.role_id = r.id)
        """)
    )
