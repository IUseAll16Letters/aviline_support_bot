import re
from typing import Union

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, InputMediaDocument, InputMediaVideo, InputMediaAudio, \
    InputMediaAnimation
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.crud import create_user_media_attached, create_ticket, create_ticket_message, get_customer_id_from_message, \
    close_ticket
from tgbot.keyboards import get_inline_keyboard_builder
from tgbot.models import Ticket
from tgbot.states import ContactSupportState
from tgbot.constants import CLEAN_PHONE_PATTERN, GET_PHONE_PATTERN, GET_EMAIL_PATTERN, GET_NAME_PATTERN, \
    CONFIRMATION_MESSAGE, AVILINE_CHAT_ID
from tgbot.utils import render_template, get_client_message, parse_message_media, edit_base_message, \
    add_caption_to_media


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
async def user_sent_message_or_media(message: Message, state: FSMContext):
    """Confirmation of clients input data
        state before: Contact -> enter_name -> enter_contact -> enter_message
        state after: Contact -> enter_name -> enter_contact -> enter_message -> entry_confirmation
    """
    data = await state.get_data()

    user_message = data.get('user_message')

    if user_message is None:
        data['user_message'] = get_client_message(message)      # TODO Wrap this mess in one function
    else:
        new_message = get_client_message(message)
        if new_message:
            data['user_message'] += f'\n{new_message}'

    media_is_document, new_media = parse_message_media(message)
    if new_media is not None:
        data['user_media'] = data.get('user_media', [])
        data['user_media'].append(new_media)
        data['media_counter'] = len(data['user_media'])

    await state.update_data(data)

    try:
        core_message: Message = data['message']
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


@router.callback_query(F.data == CONFIRMATION_MESSAGE, ContactSupportState.enter_message)
async def user_confirmed_message(
        callback_query: CallbackQuery, state: FSMContext, db_session: AsyncSession, bot: Bot
):
    """Client has finished entering message, message is sent - show notification message"""
    data = await state.get_data()
    data['user_telegram_id'] = callback_query.from_user.id

    user_message = data['user_message']
    user_telegram_id = data['user_telegram_id']

    ticket: Ticket = await create_ticket(
        db_session=db_session,
        question=user_message,
        user_telegram_id=user_telegram_id,
    )

    print(ticket, f'\033[34;4m{ticket.id = }\033[0m')
    media = data.get('user_media')

    if media:
        add_caption_to_media(media, user_message)
        media_to_send = [i for i in media if isinstance(i, (InputMediaPhoto, InputMediaVideo))]
        documents_to_send = [i for i in media if isinstance(i, InputMediaDocument)]
        audio_to_send = [i for i in media if isinstance(i, InputMediaAudio)]

        print(f"{media_to_send = }")
        print(f"{documents_to_send = }")
        print(f"{audio_to_send = }")

        messages = []
        if media_to_send:
            messages.extend(await bot.send_media_group(chat_id=AVILINE_CHAT_ID, media=media_to_send))
        print('media OK')
        if documents_to_send:
            messages.extend(await bot.send_media_group(chat_id=AVILINE_CHAT_ID, media=documents_to_send))
        print('documents OK')
        if audio_to_send:
            messages.extend(await bot.send_media_group(chat_id=AVILINE_CHAT_ID, media=audio_to_send))
        print('audio OK')

        saved_medias = await create_user_media_attached(
            db_session=db_session,
            media=media,
            ticket_id=ticket.id,
        )
        print(f"{saved_medias.all() = }")

        saved_messages = await create_ticket_message(
            db_session=db_session,
            messages=messages,
            ticket_id=ticket.id,
        )
        print(f"{saved_messages.all() = }")

    else:
        await bot.send_message(
            chat_id=AVILINE_CHAT_ID,
            text=user_message,
        )
    await db_session.commit()

    core_message: Message = data['message']
    text = render_template('message_sent_success.html', values=data)

    await edit_base_message(
        message=core_message,
        text=text,
        keyboard=get_inline_keyboard_builder(),
    )
    await state.clear()


@router.message(F.chat.id == AVILINE_CHAT_ID)
async def hostage_message(message: Message, state: FSMContext, db_session: AsyncSession, bot: Bot):
    if message.reply_to_message:
        print(f'has reply, {message.reply_to_message = }')
        quoted_message = message.reply_to_message.message_id
        print(f'{quoted_message = }')
        ticket = await get_customer_id_from_message(
            db_session=db_session,
            message_id=quoted_message,
        )
        print(ticket.__class__)
        print(f"{ticket.customer = }")
        response = await bot.send_message(
            chat_id=ticket.customer,
            text=f"Your question was: {ticket.question}\n"
                 f"Your answer is: {message.text}",
        )
        print(response)
        if response:
            print("#Closing ticket")
            closed = await close_ticket(
                db_session=db_session,
                ticket_id=ticket.id,
            )
            print(f'{closed = }')
        await db_session.commit()
