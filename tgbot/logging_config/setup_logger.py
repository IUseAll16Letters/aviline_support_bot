__all__ = ("waster_queries", "navigation", "mailing", "database", "utils_logger")

import logging
import logging.handlers as handlers
from aiogram.loggers import event, dispatcher, middlewares


from tgbot.constants import LOG_FILE_LOCATION
from config.settings import DEBUG


logging.basicConfig(level=logging.DEBUG if DEBUG else logging.WARNING)
base_logger = logging.Logger(name='tgbot', level=logging.DEBUG if DEBUG else logging.WARNING)

utils_logger = base_logger.getChild("utils")
utils_logger.setLevel(logging.DEBUG if DEBUG else logging.WARNING)

waster_queries = base_logger.getChild("wasted_basic_logger")
waster_queries.setLevel(logging.DEBUG if DEBUG else logging.WARNING)

navigation = base_logger.getChild("navigation")
navigation.setLevel(logging.DEBUG if DEBUG else logging.WARNING)

mailing = base_logger.getChild("mailing")
mailing.setLevel(logging.DEBUG if DEBUG else logging.WARNING)

database = base_logger.getChild("database")
mailing.setLevel(logging.DEBUG if DEBUG else logging.WARNING)

file_rotation_handler = handlers.TimedRotatingFileHandler(
    filename=LOG_FILE_LOCATION,
    encoding='utf-8',
    interval=1,
    when='midnight',
    backupCount=7,
)
file_rotation_formatter = logging.Formatter("%(asctime)s %(levelname)s:%(name)s: %(message)s")
file_rotation_handler.setLevel(logging.INFO)
file_rotation_handler.setFormatter(file_rotation_formatter)

event.addHandler(file_rotation_handler)
dispatcher.addHandler(file_rotation_handler)
middlewares.addHandler(file_rotation_handler)

utils_logger.addHandler(file_rotation_handler)
waster_queries.addHandler(file_rotation_handler)
navigation.addHandler(file_rotation_handler)
mailing.addHandler(file_rotation_handler)
database.addHandler(file_rotation_handler)
