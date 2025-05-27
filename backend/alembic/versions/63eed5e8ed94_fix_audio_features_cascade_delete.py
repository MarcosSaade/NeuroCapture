"""fix_audio_features_cascade_delete

Revision ID: 63eed5e8ed94
Revises: 621d69a8da6d
Create Date: 2025-05-23 19:47:48.943479

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63eed5e8ed94'
down_revision: Union[str, None] = '621d69a8da6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop existing foreign key constraint on audio_features
    op.drop_constraint('audio_features_recording_id_fkey', 'audio_features', type_='foreignkey')
    
    # Add new foreign key constraint with CASCADE delete
    op.create_foreign_key(
        'audio_features_recording_id_fkey',
        'audio_features',
        'audio_recordings',
        ['recording_id'],
        ['recording_id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop CASCADE foreign key constraint
    op.drop_constraint('audio_features_recording_id_fkey', 'audio_features', type_='foreignkey')
    
    # Add back original foreign key constraint without CASCADE
    op.create_foreign_key(
        'audio_features_recording_id_fkey',
        'audio_features',
        'audio_recordings',
        ['recording_id'],
        ['recording_id']
    )
