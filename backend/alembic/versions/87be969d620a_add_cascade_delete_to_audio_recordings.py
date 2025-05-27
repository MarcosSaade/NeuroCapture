"""add_cascade_delete_to_audio_recordings

Revision ID: 87be969d620a
Revises: 4a2583dfa321
Create Date: 2025-05-23 18:05:43.535572

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87be969d620a'
down_revision: Union[str, None] = '4a2583dfa321'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop existing foreign key constraint
    op.drop_constraint('audio_recordings_assessment_id_fkey', 'audio_recordings', type_='foreignkey')
    
    # Add new foreign key constraint with CASCADE delete
    op.create_foreign_key(
        'audio_recordings_assessment_id_fkey',
        'audio_recordings',
        'cognitive_assessments',
        ['assessment_id'],
        ['assessment_id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop CASCADE foreign key constraint
    op.drop_constraint('audio_recordings_assessment_id_fkey', 'audio_recordings', type_='foreignkey')
    
    # Add back original foreign key constraint without CASCADE
    op.create_foreign_key(
        'audio_recordings_assessment_id_fkey',
        'audio_recordings',
        'cognitive_assessments',
        ['assessment_id'],
        ['assessment_id']
    )
