import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from tgbot.utils import on_startup, on_shutdown
from tgbot.routers import basic_handlers, contact_support_handlers, purchase_handlers, tech_support_handlers
from tgbot.middleware import DbSessionMiddleware
from tgbot.database import get_connection_pool

from config import settings

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    bot = Bot(token=settings.TG_BOT_TOKEN, parse_mode='html')

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_routers(
        tech_support_handlers.router,
        purchase_handlers.router,
        contact_support_handlers.router,
        basic_handlers.router,
    )

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.message.middleware(DbSessionMiddleware(get_connection_pool()))
    dp.callback_query.middleware(DbSessionMiddleware(get_connection_pool()))

    await bot.delete_webhook(drop_pending_updates=True)  # Do i need this?
    try:
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        ...
