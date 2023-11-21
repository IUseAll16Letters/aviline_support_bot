__all__ = ("get_connection_pool",)

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config.settings import DATABASES, DEBUG


def get_connection_pool() -> async_sessionmaker:
    """ASync connection pool
    :return session pool, to get conn from
    """
    if DEBUG:
        sqlalchemy_database_path = str(DATABASES['default']["NAME"])
        sqlalchemy_database_url = f'sqlite+aiosqlite:///{sqlalchemy_database_path}'
        engine = create_async_engine(
            sqlalchemy_database_url, echo=True, connect_args={"check_same_thread": False},
        )
    else:
        conn_data = f"{DATABASES['default']['USER']}:{DATABASES['default']['PASSWORD']}" \
                    f"@{DATABASES['default']['HOST']}:{DATABASES['default']['PORT']}/{DATABASES['default']['NAME']}"
        sqlalchemy_database_url = "postgresql+asyncpg://" + conn_data
        engine = create_async_engine(
            sqlalchemy_database_url, echo=True,
        )

    sessions_local = async_sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return sessions_local
