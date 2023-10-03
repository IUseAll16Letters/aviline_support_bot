import logging
import logging.handlers as handlers
from aiogram.loggers import event, dispatcher


from tgbot.constants import LOG_FILE_LOCATION


logging.basicConfig(level=logging.INFO)
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
