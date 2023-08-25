import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards import get_inline_keyboard_builder
from states import ContactSupportState
from constants import CLEAN_PHONE_PATTERN, GET_PHONE_PATTERN, GET_EMAIL_PATTERN, GET_NAME_PATTERN
from utils.template_engine import render_template


router = Router()


@router.callback_query(F.data == 'contact_support')
async def contact_support_initial_message(callback_query: CallbackQuery, state: FSMContext) -> None:
    data = await state.update_data({"message": callback_query.message})
    await state.set_state(ContactSupportState.enter_name)
    text = render_template('client_enter_name.html', values=data)
    await callback_query.message.edit_text(
        text=text,
        reply_markup=get_inline_keyboard_builder().as_markup(),
    )


@router.message(F.text.regexp(GET_NAME_PATTERN), ContactSupportState.enter_name)
async def user_sent_name(message: Message, state: FSMContext):
    await state.set_state(ContactSupportState.enter_contact)
    data = await state.update_data({"username": message.text})
    state_data = await state.get_data()
    core_message: Message = state_data['message']
    text = render_template('client_enter_contact.html', values=data)
    await core_message.edit_text(
        text=text,
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
    F.text.func(lambda s: re.search(GET_EMAIL_PATTERN, s.strip())),
)
async def user_sent_valid_contact(message: Message, state: FSMContext):
    await state.set_state(ContactSupportState.enter_message)
    await state.update_data({'contact': message.text})
    data = await state.get_data()
    core_message: Message = data['message']
    text = render_template('client_enter_message.html', values=data)
    await core_message.edit_text(
        text=text,
        reply_markup=get_inline_keyboard_builder().as_markup(),
    )


@router.message(ContactSupportState.enter_contact)
async def user_sent_invalid_contact(message: Message, state: FSMContext):
    print('invalid contact')


@router.message(ContactSupportState.enter_message)
async def user_message_confirm(message: Message, state: FSMContext):
    data = await state.update_data({"user_message": message.text})
    print(data)
    core_message: Message = data['message']
    text = render_template('client_message_sent.html', values=data)
    await core_message.edit_text(
        text=text,
        reply_markup=get_inline_keyboard_builder(['✅ да', ]).as_markup(),
    )
    await state.clear()
