__all__ = ("get_connection_pool",)

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config.settings import DATABASES, DEBUG


def get_connection_pool() -> async_sessionmaker:
    database_settings = DATABASES['default']
    if DEBUG:
        sqlalchemy_database_path = str(database_settings["NAME"])
        sqlalchemy_database_url = f'sqlite+aiosqlite:///{sqlalchemy_database_path}'
        engine = create_async_engine(
            sqlalchemy_database_url, echo=DEBUG, connect_args={"check_same_thread": False},
        )
    else:
        conn_data = f"{database_settings['USER']}:{database_settings['PASSWORD']}" \
                    f"@{database_settings['HOST']}:{database_settings['PORT']}/{database_settings['NAME']}"
        sqlalchemy_database_url = "postgresql+asyncpg://" + conn_data
        engine = create_async_engine(sqlalchemy_database_url, echo=DEBUG)

    sessions_local = async_sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return sessions_local
