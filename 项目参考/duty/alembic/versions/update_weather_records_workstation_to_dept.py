"""Update weather_records table: rename workstation_id to dept_code and add foreign key

Revision ID: update_weather_records_workstation_to_dept
Revises: b9ef8ff2d202
Create Date: 2024-04-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


# revision identifiers, used by Alembic.
revision = 'update_weather_records_workstation_to_dept'
down_revision = 'b9ef8ff2d202'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### SQLite兼容的数据库迁移步骤 ###
    from sqlalchemy import inspect, text
    
    # 获取数据库引擎和连接
    connection = op.get_bind()
    insp = inspect(connection)
    
    # 1. 创建一个新表，包含dept_code字段（非空）和外键约束
    op.create_table('weather_records_new',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='记录ID'),
        sa.Column('record_time', sa.DateTime(timezone=True), nullable=False, comment='记录时间（精确到小时）'),
        sa.Column('dept_code', sa.String(length=50), nullable=False, comment='部门编码'),
        sa.Column('temperature', sa.Float(), nullable=False, comment='气温(摄氏度)'),
        sa.Column('humidity', sa.Float(), nullable=False, comment='相对湿度(%)'),
        sa.Column('rainfall', sa.Float(), nullable=True, comment='降雨量(mm)'),
        sa.Column('snowfall', sa.Float(), nullable=True, comment='降雪量(cm)'),
        sa.Column('wind_speed', sa.Float(), nullable=True, comment='风速(m/s)'),
        sa.Column('create_time', sa.DateTime(timezone=True), nullable=True, comment='创建时间'),
        sa.Column('update_time', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.Column('weather_conditions', sa.String(length=500), nullable=True, comment='天气状况描述(JSON格式)'),
        sa.ForeignKeyConstraint(['dept_code'], ['dept.dept_code'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 复制数据到新表，将workstation_id的值赋给dept_code
    connection.execute(text('''
        INSERT INTO weather_records_new 
        (id, record_time, dept_code, temperature, humidity, rainfall, snowfall, wind_speed, create_time, update_time, weather_conditions)
        SELECT id, record_time, workstation_id, temperature, humidity, rainfall, snowfall, wind_speed, create_time, update_time, weather_conditions
        FROM weather_records
    '''))
    
    # 3. 删除旧表的索引
    op.drop_index('idx_workstation_time', table_name='weather_records')
    op.drop_index('idx_record_time', table_name='weather_records')
    op.drop_index('ix_weather_records_record_time', table_name='weather_records')
    
    # 4. 删除旧表
    op.drop_table('weather_records')
    
    # 5. 重命名新表为原表名
    op.rename_table('weather_records_new', 'weather_records')
    
    # 6. 创建新索引
    op.create_index('idx_record_time', 'weather_records', ['record_time'], unique=False)
    op.create_index('idx_dept_time', 'weather_records', ['dept_code', 'record_time'], unique=False)
    op.create_index(op.f('ix_weather_records_record_time'), 'weather_records', ['record_time'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### SQLite兼容的回滚步骤 ###
    from sqlalchemy import text
    
    # 获取数据库引擎和连接
    connection = op.get_bind()
    
    # 1. 创建一个新表，恢复workstation_id字段
    op.create_table('weather_records_new',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='记录ID'),
        sa.Column('record_time', sa.DateTime(timezone=True), nullable=False, comment='记录时间（精确到小时）'),
        sa.Column('workstation_id', sa.String(length=50), nullable=False, comment='工作站ID'),
        sa.Column('temperature', sa.Float(), nullable=False, comment='气温(摄氏度)'),
        sa.Column('humidity', sa.Float(), nullable=False, comment='相对湿度(%)'),
        sa.Column('rainfall', sa.Float(), nullable=True, comment='降雨量(mm)'),
        sa.Column('snowfall', sa.Float(), nullable=True, comment='降雪量(cm)'),
        sa.Column('wind_speed', sa.Float(), nullable=True, comment='风速(m/s)'),
        sa.Column('create_time', sa.DateTime(timezone=True), nullable=True, comment='创建时间'),
        sa.Column('update_time', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.Column('weather_conditions', sa.String(length=500), nullable=True, comment='天气状况描述(JSON格式)'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 2. 复制数据到新表，将dept_code的值赋给workstation_id
    connection.execute(text('''
        INSERT INTO weather_records_new 
        (id, record_time, workstation_id, temperature, humidity, rainfall, snowfall, wind_speed, create_time, update_time, weather_conditions)
        SELECT id, record_time, dept_code, temperature, humidity, rainfall, snowfall, wind_speed, create_time, update_time, weather_conditions
        FROM weather_records
    '''))
    
    # 3. 删除旧表的索引
    op.drop_index('idx_dept_time', table_name='weather_records')
    op.drop_index('idx_record_time', table_name='weather_records')
    op.drop_index('ix_weather_records_record_time', table_name='weather_records')
    
    # 4. 删除旧表
    op.drop_table('weather_records')
    
    # 5. 重命名新表为原表名
    op.rename_table('weather_records_new', 'weather_records')
    
    # 6. 创建旧索引
    op.create_index('idx_record_time', 'weather_records', ['record_time'], unique=False)
    op.create_index('idx_workstation_time', 'weather_records', ['workstation_id', 'record_time'], unique=False)
    op.create_index(op.f('ix_weather_records_record_time'), 'weather_records', ['record_time'], unique=False)
    # ### end Alembic commands ###