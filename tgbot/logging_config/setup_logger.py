__all__ = ('redis_logger', 'utils_logger', 'handlers_logger', 'waster_queries', 'navigation', 'mailing', 'database',
           'middleware_debug')

import logging

from config.settings import DEBUG


logging_level = logging.DEBUG if DEBUG else logging.WARNING
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
