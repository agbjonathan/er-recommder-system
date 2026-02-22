"""placeholder for missing migration

Revision ID: 4ba70d58d1e3
Revises: cf70a6e4621a
Create Date: 2026-02-22 15:29:08.555977

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ba70d58d1e3'
down_revision: Union[str, Sequence[str], None] = 'cf70a6e4621a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
