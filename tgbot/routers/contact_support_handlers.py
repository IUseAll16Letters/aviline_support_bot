import re

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.keyboards import get_inline_keyboard_builder
from tgbot.states import ContactSupportState
from tgbot.constants import CLEAN_PHONE_PATTERN, GET_PHONE_PATTERN, GET_EMAIL_PATTERN, GET_NAME_PATTERN, \
    CONFIRMATION_MESSAGE, AVILINE_CHAT_ID
from tgbot.utils import render_template, get_client_message, get_client_media, edit_base_message

router = Router()


@router.callback_query(F.data == 'contact_support')
async def user_enters_name(callback_query: CallbackQuery, state: FSMContext) -> None:
    """Contact support initial message, client must enter valid name
    state before: Any
    state after: Contact -> enter_name
    after message input - it must be removed in order to save client's chat space and convenience"""
    data = await state.update_data({"message": callback_query.message})
    await state.set_state(ContactSupportState.enter_name)
    text = render_template('client_enter_name.html', values=data)
    await edit_base_message(
        message=callback_query.message,
        text=text,
        keyboard=get_inline_keyboard_builder()
    )


@router.message(F.text.regexp(GET_NAME_PATTERN), ContactSupportState.enter_name)
async def user_enters_contact(message: Message, state: FSMContext):
    """Client must enter valid contact (email/phone)
    state before: Contact -> enter_name
    state after: Contact -> enter_name -> enter_contact
    after message input - it must be removed in order to save client's chat space and convenience"""
    await state.set_state(ContactSupportState.enter_contact)
    data = await state.update_data({"username": message.text})
    state_data = await state.get_data()
    core_message: Message = state_data['message']
    text = render_template('client_enter_contact.html', values=data)
    await edit_base_message(
        message=core_message,
        text=text,
        keyboard=get_inline_keyboard_builder(),
    )
    await message.delete()


@router.message(ContactSupportState.enter_name)
async def user_sent_bad_name(message: Message, state: FSMContext):
    """Client enter invalid name that has numbers or symbols
    FIGURE OUT IF IT IS NEEDED AT ALL"""
    state_data = await state.get_data()
    core_message: Message = state_data['message']
    text = f'По каким-то приичнам {message.text} - невалидное имя. Попробуйте ещё раз (a-z, а-я)'
    await edit_base_message(
        message=core_message,
        text=text,
        keyboard=get_inline_keyboard_builder(),
    )
    await message.delete()


@router.message(
    ContactSupportState.enter_contact,
    F.text.func(lambda s: re.search(GET_PHONE_PATTERN, re.sub(CLEAN_PHONE_PATTERN, '', s)) is not None) |
    F.text.func(lambda s: re.search(GET_EMAIL_PATTERN, s.strip()) is not None),
)
async def user_sent_valid_contact(message: Message, state: FSMContext):
    """Client must enter valid contact (email/phone)
    state before: Contact -> enter_name -> enter_contact
    state after: Contact -> enter_name -> enter_contact -> enter_message
    """
    await state.set_state(ContactSupportState.enter_message)
    await state.update_data({'user_contact': message.text})
    data = await state.get_data()
    core_message: Message = data['message']
    text = render_template('client_enter_message.html', values=data)
    await edit_base_message(
        message=core_message,
        text=text,
        keyboard=get_inline_keyboard_builder(),
    )
    await message.delete()


@router.message(ContactSupportState.enter_contact)
async def user_sent_invalid_contact(message: Message, state: FSMContext):
    await state.update_data({'user_contact': message.text})
    data = await state.get_data()
    core_message: Message = data['message']
    text = render_template('client_bad_contact.html', values=data)
    await edit_base_message(
        message=core_message,
        text=text,
        keyboard=get_inline_keyboard_builder(),
    )
    await message.delete()


@router.message(ContactSupportState.enter_message)
async def user_message_confirm(message: Message, state: FSMContext):
    """Confirmation of clients input data
        state before: Contact -> enter_name -> enter_contact -> enter_message
        state after: Contact -> enter_name -> enter_contact -> enter_message -> entry_confirmation
    """
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
    await edit_base_message(
        message=core_message,
        text=text,
        keyboard=get_inline_keyboard_builder([CONFIRMATION_MESSAGE, ]),
    )

    await message.delete()


@router.callback_query(F.data == CONFIRMATION_MESSAGE, ContactSupportState.entry_confirmation)
async def user_confirmed_the_message(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    """Client has finished entering message, message is sent - show notification message"""
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
    text = render_template('message_sent_success.html', values=data)
    await edit_base_message(
        message=core_message,
        text=text,
        keyboard=get_inline_keyboard_builder(),
    )

    await state.clear()
