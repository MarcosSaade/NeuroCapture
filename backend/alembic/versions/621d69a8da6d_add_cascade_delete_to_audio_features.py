"""add_cascade_delete_to_audio_features

Revision ID: 621d69a8da6d
Revises: 87be969d620a
Create Date: 2025-05-23 19:27:28.973409

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '621d69a8da6d'
down_revision: Union[str, None] = '87be969d620a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
