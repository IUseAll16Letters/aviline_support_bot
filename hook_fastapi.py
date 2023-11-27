import logging

import uvicorn

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from fastapi import FastAPI

from tgbot.cache.connection import get_redis_or_mem_storage
from tgbot.database import get_connection_pool
from tgbot.middleware import DbSessionMiddleware
from tgbot.utils import webhook_on_startup, webhook_on_shutdown
from tgbot.routers import basic_handlers, contact_support_handlers, purchase_handlers, tech_support_handlers, \
    warranty_handlers, debug_handlers
from config import settings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
app = FastAPI()
main_bot = Bot(token=settings.TG_BOT_TOKEN, parse_mode="HTML")


class DPStorage:
    dp: Dispatcher = None
    bot: Bot = main_bot


@app.on_event("startup")
async def on_startup():
    storage = await get_redis_or_mem_storage()

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

    DPStorage.dp = dp
    await DPStorage.bot.set_webhook(
        url=f"{settings.BASE_WEBHOOK_URL}{settings.WEBHOOK_PATH[1:]}",
        drop_pending_updates=True,
        secret_token=settings.WEBHOOK_SECRET,
    )


@app.post(settings.WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = Update(**update)
    await DPStorage.dp.feed_update(bot=DPStorage.bot, update=telegram_update)


@app.on_event("shutdown")
async def on_shutdown():
    print("I stop this mess")
    logger.error(msg='Bot is stopping')
    await main_bot.session.close()


if __name__ == '__main__':
    while True:
        try:
            uvicorn.run(app, host='127.0.0.1', port=8895)
        except Exception as e:
            logger.critical(msg='error occured!')
