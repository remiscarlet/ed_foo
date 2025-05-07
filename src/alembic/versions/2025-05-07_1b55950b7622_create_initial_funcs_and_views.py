"""Create initial functions and views

Revision ID: 1b55950b7622
Revises: 4b0be5c0bf46
Create Date: 2025-05-07 00:14:47.127403

"""

from typing import Sequence, Union

from alembic import op
from src.common.constants import SQL_DIR

functions_sql_dir = SQL_DIR / "functions"
views_sql_dir = SQL_DIR / "views"


# revision identifiers, used by Alembic.
revision: str = "1b55950b7622"
down_revision: Union[str, None] = "4b0be5c0bf46"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with open(views_sql_dir / "hotspot_ring_view_v1.sql") as f:
        op.execute(f.read())
    with open(functions_sql_dir / "get_hotspots_in_system_by_commodities_v1.sql") as f:
        op.execute(f.read())
    with open(functions_sql_dir / "get_hotspots_in_system_v1.sql") as f:
        op.execute(f.read())


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("drop function if exists api.get_hotspots_in_system")
    op.execute("drop function if exists api.get_hotspots_in_system_by_commodities")
    op.execute("drop view if exists derived.hotspot_ring_view")
