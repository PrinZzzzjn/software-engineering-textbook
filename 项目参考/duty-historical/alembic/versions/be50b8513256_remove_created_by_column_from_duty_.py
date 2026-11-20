"""Remove created_by column from duty_records table (manual)

Revision ID: be50b8513256
Revises: 695e1bc8da30
Create Date: 2025-11-11 15:32:21.788752

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'be50b8513256'
down_revision = '695e1bc8da30'
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
