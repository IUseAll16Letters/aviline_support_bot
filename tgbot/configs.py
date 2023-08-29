import os

from dotenv import load_dotenv
from tgbot.constants import ENV_PATH


loaded = load_dotenv(ENV_PATH)
TOKEN = os.getenv("BOT_TOKEN")
