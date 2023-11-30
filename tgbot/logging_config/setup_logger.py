__all__ = ('redis_logger', 'utils_logger', 'handlers_logger', 'waster_queries', 'navigation', 'mailing', 'database')

import logging
import logging.handlers as handlers
from aiogram.loggers import event, dispatcher, middlewares


from config.settings import DEBUG, LOG_FILE_LOCATION, LOGGING_FORMATTER


logging.basicConfig(level=logging.DEBUG if DEBUG else logging.WARNING)
base_logger = logging.Logger(name='tgbot', level=logging.DEBUG if DEBUG else logging.WARNING)

redis_logger = base_logger.getChild('redis')
redis_logger.setLevel(logging.DEBUG if DEBUG else logging.WARNING)

utils_logger = base_logger.getChild('utils')
utils_logger.setLevel(logging.DEBUG if DEBUG else logging.WARNING)

handlers_logger = base_logger.getChild('handlers')
handlers_logger.setLevel(logging.DEBUG if DEBUG else logging.WARNING)

waster_queries = base_logger.getChild('wasted_basic')
waster_queries.setLevel(logging.DEBUG if DEBUG else logging.WARNING)

navigation = base_logger.getChild('navigation')
navigation.setLevel(logging.DEBUG if DEBUG else logging.WARNING)

mailing = base_logger.getChild('mailing')
mailing.setLevel(logging.DEBUG if DEBUG else logging.WARNING)

database = base_logger.getChild('database')
mailing.setLevel(logging.DEBUG if DEBUG else logging.WARNING)

file_rotation_handler = handlers.TimedRotatingFileHandler(
    filename=LOG_FILE_LOCATION,
    encoding='utf-8',
    interval=1,
    when='midnight',
    backupCount=7,
)
file_rotation_formatter = logging.Formatter(LOGGING_FORMATTER)
file_rotation_handler.setLevel(logging.INFO)
file_rotation_handler.setFormatter(file_rotation_formatter)

event.addHandler(file_rotation_handler)
dispatcher.addHandler(file_rotation_handler)
middlewares.addHandler(file_rotation_handler)

redis_logger.addHandler(file_rotation_handler)
utils_logger.addHandler(file_rotation_handler)
waster_queries.addHandler(file_rotation_handler)
navigation.addHandler(file_rotation_handler)
mailing.addHandler(file_rotation_handler)
database.addHandler(file_rotation_handler)
handlers_logger.addHandler(file_rotation_handler)
