import re

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.keyboards import get_inline_keyboard_builder
from tgbot.states import ContactSupportState
from tgbot.constants import CLEAN_PHONE_PATTERN, GET_PHONE_PATTERN, GET_EMAIL_PATTERN, GET_NAME_PATTERN, \
    CONFIRMATION_MESSAGE, AVILINE_CHAT_ID
from tgbot.utils.base import get_client_message, get_client_media
from tgbot.utils.template_engine import render_template

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
    await message.delete()


@router.message(ContactSupportState.enter_name)
async def user_sent_bad_name(message: Message, state: FSMContext):
    state_data = await state.get_data()
    core_message: Message = state_data['message']
    await core_message.edit_text(
        text=f'По каким-то приичнам {message.text} - невалидное имя. Попробуйте ещё раз (a-z, а-я)',
        reply_markup=get_inline_keyboard_builder().as_markup(),
    )
    await message.delete()


@router.message(
    ContactSupportState.enter_contact,
    F.text.func(lambda s: re.search(GET_PHONE_PATTERN, re.sub(CLEAN_PHONE_PATTERN, '', s)) is not None) |
    F.text.func(lambda s: re.search(GET_EMAIL_PATTERN, s.strip()) is not None),
)
async def user_sent_valid_contact(message: Message, state: FSMContext):
    await state.set_state(ContactSupportState.enter_message)
    await state.update_data({'user_contact': message.text})
    data = await state.get_data()
    core_message: Message = data['message']
    text = render_template('client_enter_message.html', values=data)
    await core_message.edit_text(
        text=text,
        reply_markup=get_inline_keyboard_builder().as_markup(),
    )
    await message.delete()


@router.message(ContactSupportState.enter_contact)
async def user_sent_invalid_contact(message: Message, state: FSMContext):
    await state.update_data({'user_contact': message.text})
    data = await state.get_data()
    core_message: Message = data['message']
    text = render_template('client_bad_contact.html', values=data)
    await core_message.edit_text(
        text=text,
        reply_markup=get_inline_keyboard_builder().as_markup(),
    )
    await message.delete()


@router.message(ContactSupportState.enter_message)
async def user_message_confirm(message: Message, state: FSMContext):
    await state.set_state(ContactSupportState.entry_confirmation)
    # print(f'{message = }')
    # print(f'{message.caption_entities = }')
    # print(f'{message.entities = }')
    # print(f'{message.caption = }')
    # print(f'{message.document = }')
    # print(f'{message.photo = } {message.photo[0].file_id = }')
    # print(f'{message.video = }')
    # print(f'{message.animation = }')
    # print(f'{message.audio = }')

    data_to_update = {"user_message": get_client_message(message), "user_media": get_client_media(message)}
    data = await state.update_data(data_to_update)

    core_message: Message = data['message']
    text = render_template('client_message_sent.html', values=data)
    await core_message.edit_text(
        text=text,
        reply_markup=get_inline_keyboard_builder([CONFIRMATION_MESSAGE, ]).as_markup(),
    )
    await message.delete()


@router.callback_query(F.data == CONFIRMATION_MESSAGE, ContactSupportState.entry_confirmation)
async def user_confirmed_the_message(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    print('User confirmed his choice, redirect to global chat')
    data = await state.get_data()
    for k, v in data.items():
        print(f'{k = }, {v = }')
    data['user_id'] = callback_query.from_user.id
    user_message = f"from_user: {data['username']}" \
                   f"user_contact: {data['user_contact']}" \
                   f"message: {data['user_message']}"

    # TODO re-implement logic
    if data.get('user_media') is not None:
        new_user_caption = f"from_user: {data['username']}\n" \
                           f"user_contact: {data['user_contact']}\n" \
                           f"message: {data['user_message']}\n" \
                           f"system_data: {data['branch'] = }|{data['product'] = }"
        message = await bot.send_photo(
            chat_id=AVILINE_CHAT_ID,
            photo=data.get('user_media'),
            caption=new_user_caption,
        )
        print(f"User message id {message.message_id = }")
    else:
        await bot.send_message(chat_id=AVILINE_CHAT_ID, text=user_message)

    core_message: Message = data['message']
    await core_message.edit_text(
        text=render_template('message_sent_success.html', values=data),
        reply_markup=get_inline_keyboard_builder().as_markup(),
    )
    await state.clear()
