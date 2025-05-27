"""add_cascade_delete_to_audio_recordings

Revision ID: 4a2583dfa321
Revises: 45ec1e521775
Create Date: 2025-05-23 18:05:37.171351

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a2583dfa321'
down_revision: Union[str, None] = '45ec1e521775'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
