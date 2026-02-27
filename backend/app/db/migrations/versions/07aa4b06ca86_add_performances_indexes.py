"""add performances indexes

Revision ID: 07aa4b06ca86
Revises: b421960f39bb
Create Date: 2026-02-27 07:02:35.820528

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '07aa4b06ca86'
down_revision: Union[str, Sequence[str], None] = 'b421960f39bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "idx_forecast_errors_lookup",
        "forecast_errors",
        ["hospital_id", "horizon_hours", "evaluated_at"],
    )
    op.create_index(
        "idx_snapshots_hospital_time",
        "er_snapshots",
        ["hospital_id", "snapshot_time"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_forecast_errors_lookup", table_name="forecast_errors")
    op.drop_index("idx_snapshots_hospital_time", table_name="er_snapshots")
