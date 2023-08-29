from aiogram import Bot
from aiogram.types import Message


async def on_startup(bot: Bot):
    print('starting', bot)


async def on_shutdown(bot: Bot):
    print('Stopping', bot)


def get_product_problems(product: str, problems: dict):
    problems_list = [i[0] for i in problems.get(product, [])]
    return problems_list


def get_client_message(message: Message):
    user_message = ""
    user_message = message.text or user_message
    user_message = message.caption or user_message
    return user_message


def get_client_media(message: Message):
    # TODO figure
    try:
        media_sources = ['']
        media = message.photo[0].file_id
        print(f"{media = }")
        return media
    except Exception:
        return None

