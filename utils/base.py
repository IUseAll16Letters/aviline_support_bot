from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State


async def on_startup(bot: Bot):
    print('starting', bot)


async def on_shutdown(bot: Bot):
    print('Stopping', bot)


async def user_history_update(state: FSMContext, current_state: State):
    data = await state.get_data()

    if 'history' not in data:
        data['history'] = []

    data['history'].append(current_state)
    print('data_updated', data)
    await state.update_data(data)
