from functools import wraps
from typing import Union, Callable

from aiogram import Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

from ..logging_config import handlers_logger


def state_control(state: Union[State, None]):
    def wrapper(fnc: Callable):
        @wraps(fnc)
        async def wrapped(*args, **kwargs):
            try:
                res = await fnc(*args, **kwargs)
                return res
            except Exception as e:
                msg = f'Error occurred during {fnc.__name__} handler. ERR: {e}'
                handlers_logger.error(msg=msg)

                if 'bot' in kwargs:
                    bot: Bot = kwargs['bot']

                    query = None
                    for arg in args:
                        if isinstance(arg, CallbackQuery):
                            query = arg
                            break
                    if query is None:
                        handlers_logger.critical(msg=f'Configuration error at {fnc.__name__}. {args = } | {kwargs = }')

                    await bot.answer_callback_query(
                        callback_query_id=query.id,
                        text=f'Возникла ошибка при исполнении команды: {query.data}.\n'
                             'Приносим извинения. Пожалуйста перезапустите бота через /start',
                    )
                if 'state' in kwargs:
                    state_object: FSMContext = kwargs['state']
                    if state is None:
                        await state_object.clear()
                    else:
                        await state_object.set_state(state)
        return wrapped
    return wrapper
