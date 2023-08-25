import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards import get_inline_keyboard_builder
from states import TechSupportState, PurchaseState, ContactSupportState
from constants import CLEAN_PHONE_PATTERN, GET_PHONE_PATTERN, GET_EMAIL_PATTERN
from utils.base import user_history_update

router = Router()


@router.callback_query(F.data == 'contact_support')
async def contact_support_initial_message(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.update_data({"message": callback_query.message})
    await state.set_state(ContactSupportState.enter_name)
    await user_history_update(state, ContactSupportState.enter_name)
    await callback_query.message.edit_text(
        text="Как мы к Вам обращаться?\n",
        reply_markup=get_inline_keyboard_builder().as_markup(),
    )


@router.message(F.text.regexp(r'([a-zа-яA-ZА-Я]+[-\s.]*)*[a-zа-яA-ZА-Я]{2,}$'), ContactSupportState.enter_name)
async def user_sent_name(message: Message, state: FSMContext):
    await state.set_state(ContactSupportState.enter_contact)
    await state.update_data({"username": message.text})
    await user_history_update(state, ContactSupportState.enter_contact)
    state_data = await state.get_data()
    core_message: Message = state_data['message']
    await core_message.edit_text(
        text=f'{message.text}, как с Вами связаться? Введите email, phone или поделитесь контактом',
        reply_markup=get_inline_keyboard_builder().as_markup(),
    )


@router.message(ContactSupportState.enter_name)
async def user_sent_bad_name(message: Message, state: FSMContext):
    state_data = await state.get_data()
    core_message: Message = state_data['message']
    await core_message.edit_text(
        text=f'По каким-то приичнам {message.text} - невалидное имя. Попробуйте ещё раз (a-z, а-я)',
        reply_markup=get_inline_keyboard_builder().as_markup(),
    )


@router.message(
    ContactSupportState.enter_contact,
    F.text.func(lambda s: re.search(GET_PHONE_PATTERN, re.sub(CLEAN_PHONE_PATTERN, '', s)) is not None) |
    F.text.func(lambda s: re.search(GET_EMAIL_PATTERN, s)),
)
async def user_sent_valid_contact(message: Message, state: FSMContext):
    await state.set_state(ContactSupportState.enter_message)
    await user_history_update(state, ContactSupportState.enter_message)
    data = await state.get_data()
    basic_message: Message = data['message']
    await basic_message.edit_text(
        text=f'Ok, {data["username"]}, your contact is: {message.text}, now enter message: ',
        reply_markup=get_inline_keyboard_builder().as_markup(),
    )


@router.message(ContactSupportState.enter_contact)
async def user_sent_invalid_contact(message: Message, state: FSMContext):
    print('invalid contact')


@router.message(ContactSupportState.enter_message)
async def user_sent_message(message: Message, state: FSMContext):
    ...
