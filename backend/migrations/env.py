from alembic import context

from app.core.config import get_settings
from app.db.base import Base
from app.db import models  # noqa: F401 -- register all tables in Base.metadata
from app.db.session import get_engine

# 模型必须在读取 metadata 前导入；迁移历史独立于当前模型定义。
target_metadata = Base.metadata


def reject_empty_autogenerate():
    options = getattr(context.config, "cmd_opts", None)
    if getattr(options, "autogenerate", False) and not target_metadata.tables:
        raise RuntimeError("请先在 migrations/env.py 注册你已有的 ORM 模型，再生成迁移")


def run_migrations_offline():
    context.configure(
        url=get_settings().database_url.get_secret_value(),
        target_metadata=target_metadata, literal_binds=True,
        dialect_opts={"paramstyle": "named"}, compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    reject_empty_autogenerate()
    with get_engine().connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
