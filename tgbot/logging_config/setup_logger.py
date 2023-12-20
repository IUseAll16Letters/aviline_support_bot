__all__ = ('redis_logger', 'utils_logger', 'handlers_logger', 'waster_queries', 'navigation', 'mailing', 'database',
           'middleware_debug')

import logging
import logging.handlers as handlers

from config.settings import DEBUG, LOG_FILE_LOCATION, LOGGING_FORMATTER

# log_queue = asyncio.Queue()
# qh = handlers.QueueHandler(log_queue)

logging_level = logging.DEBUG if DEBUG else logging.WARNING
# logging_level = logging.DEBUG
logging.basicConfig(level=logging_level)

base_logger = logging.Logger(name='tgbot', level=logging_level)

middleware_debug = base_logger.getChild('middleware_get_name')
middleware_debug.setLevel(logging_level)

redis_logger = base_logger.getChild('redis')
redis_logger.setLevel(logging_level)

utils_logger = base_logger.getChild('utils')
utils_logger.setLevel(logging_level)

handlers_logger = base_logger.getChild('handlers')
handlers_logger.setLevel(logging_level)

waster_queries = base_logger.getChild('wasted_basic')
waster_queries.setLevel(logging_level)

navigation = base_logger.getChild('navigation')
navigation.setLevel(logging_level)

mailing = base_logger.getChild('mailing')
mailing.setLevel(logging_level)

database = base_logger.getChild('database')
mailing.setLevel(logging_level)

file_rotation_handler = handlers.TimedRotatingFileHandler(
    filename=LOG_FILE_LOCATION,
    encoding='utf-8',
    interval=1,
    when='midnight',
    backupCount=7,
)
file_rotation_formatter = logging.Formatter(LOGGING_FORMATTER)
file_rotation_handler.setLevel(logging.DEBUG)
file_rotation_handler.setFormatter(file_rotation_formatter)

# event.addHandler(file_rotation_handler)
# dispatcher.addHandler(file_rotation_handler)
# middlewares.addHandler(file_rotation_handler)


# middleware_debug.addHandler(qh)
# redis_logger.addHandler(qh)
# utils_logger.addHandler(qh)
# waster_queries.addHandler(qh)
# navigation.addHandler(qh)
# mailing.addHandler(qh)
# database.addHandler(qh)
# handlers_logger.addHandler(qh)
