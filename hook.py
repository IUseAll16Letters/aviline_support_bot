import asyncio
import logging
import sys

from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from tgbot.cache.connection import get_redis_or_mem_storage
from tgbot.database import get_connection_pool
from tgbot.middleware import DbSessionMiddleware
from tgbot.utils import webhook_on_startup, webhook_on_shutdown
from tgbot.routers import basic_handlers, contact_support_handlers, purchase_handlers, tech_support_handlers, \
    warranty_handlers, debug_handlers
from config import settings


logging.basicConfig(level=logging.INFO)


# IT DOESN'T WORK! NOTE!
async def main(lp) -> None:
    storage = await lp.run_until_complete(get_redis_or_mem_storage)

    dp = Dispatcher(storage=storage)

    dp.include_routers(
        basic_handlers.router,
        tech_support_handlers.router,
        purchase_handlers.router,
        contact_support_handlers.router,
        warranty_handlers.router,
        debug_handlers.router,
    )

    dp.startup.register(webhook_on_startup)
    dp.shutdown.register(webhook_on_shutdown)

    dp.message.middleware(DbSessionMiddleware(get_connection_pool()))
    dp.callback_query.middleware(DbSessionMiddleware(get_connection_pool()))

    bot = Bot(token=settings.TG_BOT_TOKEN, parse_mode=ParseMode.HTML)

    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.WEBHOOK_SECRET,
    )
    # Register webhook handler on application
    webhook_requests_handler.register(app, path=settings.WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    try:
        web.run_app(app, host=settings.WEB_SERVER_HOST, port=settings.WEB_SERVER_PORT)
    finally:
        await dp.storage.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    loop = asyncio.new_event_loop()
    print(loop)
    asyncio.run(main(loop))
