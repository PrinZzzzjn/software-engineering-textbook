from logging.config import fileConfig
import os
import sys
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# 添加项目根目录到sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# 导入Base和所有模型，确保它们被注册到Base.metadata
from app.core.base_model import Base

# 导入所有模型
from app.api.v1.module_system.user.model import User
from app.api.v1.module_duty.dept.model import Department
from app.api.v1.module_duty.personnel.model import Personnel
from app.api.v1.module_duty.duty_record.model import DutyRecord
from app.api.v1.module_duty.inspection_record.model import InspectionRecord
from app.api.v1.module_duty.safe_record.model import SafeBoxRecord
from app.api.v1.module_duty.equipment_cabinet_record.model import EquipmentCabinetRecord
from app.api.v1.module_duty.workstation.model import Workstation
from app.api.v1.module_duty.weather_record.model import WeatherRecord
from app.api.v1.module_duty.holiday.models import Holiday

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# 从环境变量或配置文件获取数据库URL
from app.config.setting import settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
