import asyncio
import logging

from aiogram import Bot, Dispatcher
from configs import TOKEN
from utils.base import on_startup, on_shutdown
from handlers import basic_handlers, contact_support_handlers, purchase_handlers, tech_support_handlers


logging.basicConfig(level=logging.INFO)


async def main() -> None:
    bot = Bot(token=TOKEN, parse_mode='html')
    dp = Dispatcher()
    dp.include_routers(
        tech_support_handlers.router,
        purchase_handlers.router,
        contact_support_handlers.router,
        basic_handlers.router,
    )

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stop')
