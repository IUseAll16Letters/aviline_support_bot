import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from tgbot.utils import polling_on_startup, polling_on_shutdown
from tgbot.routers import basic_handlers, contact_support_handlers, purchase_handlers, tech_support_handlers, \
    warranty_handlers, debug_handlers
from tgbot.middleware import DbSessionMiddleware
from tgbot.database import get_connection_pool
from tgbot.cache.connection import get_redis_storage


from config import settings

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    bot = Bot(token=settings.TG_BOT_TOKEN, parse_mode='html')
    await bot.delete_webhook(drop_pending_updates=True)

    redis = await get_redis_storage()
    if redis is None:
        storage = MemoryStorage()
        logging.info(msg='Redis connection is none - using MemoryStorage')
    else:
        storage = RedisStorage(
            redis=redis,
            state_ttl=settings.MEMSTORAGE_DATA_TTL,
            data_ttl=settings.MEMSTORAGE_STATE_TTL,
        )

    dp = Dispatcher(storage=storage)

    dp.include_routers(
        basic_handlers.router,
        tech_support_handlers.router,
        purchase_handlers.router,
        contact_support_handlers.router,
        warranty_handlers.router,
        debug_handlers.router,
    )

    dp.startup.register(polling_on_startup)
    dp.shutdown.register(polling_on_shutdown)

    dp.message.middleware(DbSessionMiddleware(get_connection_pool()))
    dp.callback_query.middleware(DbSessionMiddleware(get_connection_pool()))

    try:
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        ...
