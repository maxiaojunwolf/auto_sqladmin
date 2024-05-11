import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from apps.core.db import Base, DynamicBase
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# 是否仅加载动态类
dynamic_only = True
if dynamic_only:
    target_metadata = DynamicBase.metadata
else:
    target_metadata = Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def include_object(object, name, type_, reflected, compare_to):
    """
    自定义函数，指定需要包含在比较中的对象
    :param object: SQLAlchemy对象
    :param name: 对象名称
    :param type_: 对象类型（如表、索引等）
    :param reflected: 如果为True，则对象是从数据库反射的
    :param compare_to: 如果为None，则该对象不存在于目标数据库中
    :return: 如果返回True，则包含该对象在比较中，否则排除
    """
    core_tables = [t for t in Base.metadata.tables]
    if type_ == "table":
        table_name = name
    else:
        table_name = object.table.name
    if table_name in core_tables:
        print("in---",object,name,type_,reflected,compare_to)
        return not dynamic_only
    else:
        print("not in---", object, name, type_,reflected,compare_to)
        if type_ == "table" and reflected and compare_to is None:
            # 避免删除表，需要手动删除表
            return False
        else:
            return dynamic_only


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


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection,
                      target_metadata=target_metadata,
                      transactional_ddl=True,
                      include_object=include_object
                      )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # 动态生成ORM
    if dynamic_only:
        from apps.core.compile import load
        await load.LoadORM.load()

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
