import os

from dotenv import load_dotenv


load_dotenv('./storage/.env')
TOKEN = os.getenv("BOT_TOKEN")
