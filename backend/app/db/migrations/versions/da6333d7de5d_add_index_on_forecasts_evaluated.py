"""add index on forecasts.evaluated

Revision ID: da6333d7de5d
Revises: 07aa4b06ca86
Create Date: 2026-03-03 16:31:02.900999

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da6333d7de5d'
down_revision: Union[str, Sequence[str], None] = '07aa4b06ca86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index('ix_forecasts_evaluated', 'forecasts', ['evaluated'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_forecasts_evaluated', table_name='forecasts')
