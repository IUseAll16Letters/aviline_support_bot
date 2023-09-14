import re

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.keyboards import get_inline_keyboard_builder
from tgbot.states import ContactSupportState
from tgbot.constants import CLEAN_PHONE_PATTERN, GET_PHONE_PATTERN, GET_EMAIL_PATTERN, GET_NAME_PATTERN, \
    CONFIRMATION_MESSAGE, AVILINE_CHAT_ID
from tgbot.utils import render_template, get_client_message, parse_message_media, edit_base_message
from tgbot.crud import create_ticket, create_user_media_attached

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
    data = await state.update_data({'user_contact': message.text})
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
    data = await state.get_data()

    print(message.photo, message.video)
    user_message = data.get('user_message')
    if user_message is None:
        data['user_message'] = get_client_message(message)  # TODO update message if client enters something else!

    new_media = parse_message_media(message)
    if new_media is not None:
        data['user_media'] = data.get('user_media', [])
        data['user_media'].append(new_media)
        data['media_counter'] = len(data['user_media'])

    print(data)

    await state.update_data(data)

    core_message: Message = data['message']

    try:
        text = render_template('client_message_confirm.html', values=data)

        if data['user_message'] is None:
            kb = get_inline_keyboard_builder()
        else:
            kb = get_inline_keyboard_builder(iterable=[CONFIRMATION_MESSAGE, ], )
        await edit_base_message(
            message=core_message,
            text=text,
            keyboard=kb,
        )
    except Exception as e:
        print(f'\033[35;4m{e}\033[0m')

    await message.delete()


@router.callback_query(F.data == CONFIRMATION_MESSAGE)
async def user_confirmed_the_message(callback_query: CallbackQuery, state: FSMContext, db_session: AsyncSession, bot: Bot):
    """Client has finished entering message, message is sent - show notification message"""
    data = await state.get_data()

    data['user_telegram_id'] = callback_query.from_user.id
    # user_message = f"from_user: {data['user_telegram_id']}" \
    #                f"user_contact: {data['user_contact']}" \
    #                f"message: {data['user_message']}"

    user_message = data['user_message']
    user_telegram_id = data['user_telegram_id']
    created_at = callback_query.message.date
    ticket = await create_ticket(
        db_session=db_session,
        question=user_message,
        user_telegram_id=user_telegram_id,
        created_at=created_at,
    )
    print(ticket, f'\033[34;4m{ticket.id = }\033[0m')
    media = data.get('user_media')
    if media is not None:
        for media_item in media:
            media_item.caption = user_message

        messages = await bot.send_media_group(
            chat_id=AVILINE_CHAT_ID,
            media=media,
        )
        print(messages)
        await create_user_media_attached(
            db_session=db_session,
            media=media,
            ticket_id=ticket.id,
        )
    else:
        await bot.send_message(
            chat_id=AVILINE_CHAT_ID,
            text=user_message,
        )

    core_message: Message = data['message']
    text = render_template('message_sent_success.html', values=data)

    await edit_base_message(
        message=core_message,
        text=text,
        keyboard=get_inline_keyboard_builder(),
    )
    await state.clear()
