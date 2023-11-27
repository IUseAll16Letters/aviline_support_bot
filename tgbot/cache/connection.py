__all__ = ("get_redis_storage", "get_redis_or_mem_storage")

from typing import Union

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio.client import Redis
from redis.exceptions import ConnectionError

from config import settings
from tgbot.logging_config import redis_logger


async def get_redis_storage():
    host = settings.CACHE[settings.DEBUG]['HOST']
    port = settings.CACHE[settings.DEBUG]['PORT']
    db = settings.CACHE[settings.DEBUG]['DBS']['memstorage']
    redis = Redis(host=host, port=port, db=db)
    for i in range(1, 4):
        try:
            await redis.ping()
            msg = f'Redis successfully connected to: redis:///{host}:{port}/{db}, from {i} attempt'
            print(msg)
            redis_logger.info(msg=msg)
            return redis
        except ConnectionError as e:
            msg = f'Cant connect to redis storage at redis:///{host}:{port}/{db}, from {i} attempt. ERR: {e}'
            redis_logger.error(msg=msg)
        except Exception as e:
            redis_logger.critical(msg=f"Unknown exception handled: {e}")

    return None


async def get_redis_or_mem_storage() -> Union[MemoryStorage, RedisStorage]:
    redis = await get_redis_storage()
    if redis is None:
        storage = MemoryStorage()
        redis_logger.info(msg='Redis connection is none - using MemoryStorage')
    else:
        storage = RedisStorage(
            redis=redis,
            state_ttl=settings.MEMSTORAGE_DATA_TTL,
            data_ttl=settings.MEMSTORAGE_STATE_TTL,
        )
    return storage
