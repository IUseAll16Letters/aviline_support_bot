from typing import Any

from redis.asyncio.client import Redis
from redis.exceptions import ConnectionError

from config import settings
from tgbot.logging_config import redis_logger
from tgbot.types import KeyLike


async def get_redis_storage():
    host = settings.CACHE[settings.DEBUG]['HOST']
    port = settings.CACHE[settings.DEBUG]['PORT']
    db = settings.CACHE[settings.DEBUG]['DBS']['memstorage']
    redis = Redis(host=host, port=port, db=db)
    for i in range(1, 4):
        try:
            await redis.ping()
            msg = f'Redis successfully connected to: redis:///{host}:{port}/{db}, from {i} attempt'
            redis_logger.info(msg=msg)
            return redis
        except ConnectionError as e:
            msg = f'Cant connect to redis storage at redis:///{host}:{port}/{db}, from {i} attempt. ERR: {e}'
            redis_logger.error(msg=msg)
        except Exception as e:
            redis_logger.critical(msg=f"Unknown exception handled: {e}")

    return None
