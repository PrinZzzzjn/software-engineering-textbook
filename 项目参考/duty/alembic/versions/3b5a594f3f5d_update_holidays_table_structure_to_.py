"""update holidays table structure to match model

Revision ID: 3b5a594f3f5d
Revises: be50b8513256
Create Date: 2025-11-11 15:37:42.318717

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b5a594f3f5d'
down_revision = 'be50b8513256'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加is_holiday字段
    op.add_column('holidays', sa.Column('is_holiday', sa.Boolean(), nullable=False, server_default='true'))
    
    # 重命名is_special为holiday_type
    # 先添加新字段
    op.add_column('holidays', sa.Column('holiday_type', sa.String(length=50), nullable=True))
    
    # 删除旧字段
    op.drop_index(op.f('ix_holidays_is_special'), table_name='holidays')
    op.drop_column('holidays', 'is_special')


def downgrade() -> None:
    # 添加回is_special字段
    op.add_column('holidays', sa.Column('is_special', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_holidays_is_special'), 'holidays', ['is_special'], unique=False)
    
    # 删除holiday_type字段
    op.drop_column('holidays', 'holiday_type')
    
    # 删除is_holiday字段
    op.drop_column('holidays', 'is_holiday')
