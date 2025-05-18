"""add ON DELETE CASCADE to cognitive_assessments.patient_id FK

Revision ID: 20250518_add_cascade_to_assessments_fk
Revises: e5cd09f6983f
Create Date: 2025-05-18 14:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# replace with your actual revision identifiers
revision = '20250518_add_cascade_to_assessments_fk'
down_revision = 'e5cd09f6983f'
branch_labels = None
depends_on = None

def upgrade():
    # drop old FK
    op.drop_constraint(
        'cognitive_assessments_patient_id_fkey',
        'cognitive_assessments',
        type_='foreignkey'
    )
    # add new FK with ON DELETE CASCADE
    op.create_foreign_key(
        'cognitive_assessments_patient_id_fkey',
        'cognitive_assessments', 'patients',
        ['patient_id'], ['patient_id'],
        ondelete='CASCADE'
    )

def downgrade():
    # revert to FK without cascade
    op.drop_constraint(
        'cognitive_assessments_patient_id_fkey',
        'cognitive_assessments',
        type_='foreignkey'
    )
    op.create_foreign_key(
        'cognitive_assessments_patient_id_fkey',
        'cognitive_assessments', 'patients',
        ['patient_id'], ['patient_id']
    )
