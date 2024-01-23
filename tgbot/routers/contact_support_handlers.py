import re

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, InputMediaDocument, InputMediaVideo, InputMediaAudio
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.cache.shortcuts import RedisAdapter
from tgbot.crud import TicketRelatedQueries
from tgbot.keyboards import get_inline_keyboard_builder
from tgbot.states import ContactSupportState
from tgbot.constants import CLEAN_PHONE_PATTERN, GET_PHONE_PATTERN, GET_EMAIL_PATTERN, GET_NAME_PATTERN, \
    CONFIRMATION_MESSAGE, NEGATIVE_MESSAGE
from tgbot.utils import async_render_template, get_client_message, parse_message_media, edit_base_message
from tgbot.logging_config import handlers_logger
from tgbot.utils.shortcuts import refresh_message_data_from_callback_query
from config.settings import AVILINE_TECH_CHAT_ID, AVILINE_MANAGER_CHAT_ID

router = Router()


@router.callback_query(F.data == 'contact_support')
async def user_accept_policy(callback_query: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    minutes, seconds = await RedisAdapter().check_lock_ttl(user_id=callback_query.from_user.id)

    if minutes not in (-2, -1):
        await callback_query.answer(
            text=f"Вы можете создавать обращения не чаще чем 1 раз в 5 минут.\n"
                 f"След. обращение воможно через: {minutes} мин, {seconds} сек.",
        )
        return

    data = await refresh_message_data_from_callback_query(callback_query, state)
    text = await async_render_template('privacy_policy.html', values=data)
    await edit_base_message(
        chat_id=data['chat_id'],
        message_id=data['message_id'],
        text=text,
        keyboard=get_inline_keyboard_builder(iterable=[CONFIRMATION_MESSAGE]),
        bot=bot,
    )
    await state.set_state(ContactSupportState.confirm_policy)


@router.callback_query(F.data == CONFIRMATION_MESSAGE, ContactSupportState.confirm_policy)
async def user_enters_name(callback_query: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = await refresh_message_data_from_callback_query(callback_query, state)
    text = await async_render_template('client_enter_name.html', values=data)
    await edit_base_message(
        chat_id=data['chat_id'],
        message_id=data['message_id'],
        text=text,
        keyboard=get_inline_keyboard_builder(),
        bot=bot,
    )
    await state.set_state(ContactSupportState.enter_name)


@router.message(F.text.regexp(GET_NAME_PATTERN), ContactSupportState.enter_name)
async def user_sent_valid_name(message: Message, state: FSMContext, bot: Bot) -> None:
    """Client must enter valid contact (email/phone)
    state before: Contact -> enter_name
    state after: Contact -> enter_name -> enter_contact
    after message input - it must be removed in order to save client's chat space and convenience"""
    data = await state.update_data({"username": message.text})
    text = await async_render_template('client_enter_contact.html', values=data)
    await edit_base_message(
        chat_id=data['chat_id'],
        message_id=data['message_id'],
        text=text,
        keyboard=get_inline_keyboard_builder(),
        bot=bot,
    )
    await state.set_state(ContactSupportState.enter_contact)
    await message.delete()


@router.message(ContactSupportState.enter_name)
async def user_sent_bad_name(message: Message, state: FSMContext, bot: Bot) -> None:
    """Client enter invalid name that has numbers or symbols
    FIGURE OUT IF IT IS NEEDED AT ALL"""
    data = await state.get_data()
    text = f'По каким-то приичнам {message.text} - некорректное имя.\n' \
           f'Попробуйте ещё раз (Разрешены буквы латинского и кириллического алфавитов)'
    await edit_base_message(
        chat_id=data['chat_id'],
        message_id=data['message_id'],
        text=text,
        keyboard=get_inline_keyboard_builder(),
        bot=bot,
    )
    await message.delete()


@router.message(
    ContactSupportState.enter_contact,
    F.text.func(lambda s: re.search(GET_PHONE_PATTERN, re.sub(CLEAN_PHONE_PATTERN, '', s)) is not None) |
    F.text.func(lambda s: re.search(GET_EMAIL_PATTERN, s.strip()) is not None),
)
async def user_sent_valid_contact(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Client entered valid contact (email/phone). Must match regexps from constants.py package.
    State after validation = enter_message / add media
    """
    data = await state.update_data({'user_contact': message.text})
    text = await async_render_template('client_enter_message.html', values=data)
    await edit_base_message(
        chat_id=data['chat_id'],
        message_id=data['message_id'],
        text=text,
        keyboard=get_inline_keyboard_builder(),
        bot=bot,
    )
    await state.set_state(ContactSupportState.enter_message)
    await message.delete()


@router.message(ContactSupportState.enter_contact)
async def user_sent_invalid_contact(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    User send the contact that doesn't pass filter from user_sent_valid_contact func. Doesn't meet regexps.
    """
    data = await state.get_data()
    data['user_contact'] = message.text
    text = await async_render_template('client_bad_contact.html', values=data)
    await edit_base_message(
        chat_id=data['chat_id'],
        message_id=data['message_id'],
        text=text,
        keyboard=get_inline_keyboard_builder(),
        bot=bot,
    )
    await message.delete()


@router.message(ContactSupportState.enter_message)
async def user_sent_message_or_media(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Parse user message. Must be enter_message_state.
    """
    data = await state.get_data()

    user_message = data.get('user_message')
    new_user_message = get_client_message(message)

    if user_message is None:
        data['user_message'] = new_user_message
    else:
        data['user_message'] = f'{user_message}\n{new_user_message}' if new_user_message else user_message

    new_media = parse_message_media(message)
    if new_media is not None:
        data['user_media'] = data.get('user_media', [])
        data['user_media'].append(new_media)
        data['media_counter'] = len(data['user_media'])

    await state.update_data(data)

    try:
        text = await async_render_template('client_message_confirm.html', values=data)

        if data['user_message'] is None:
            kb = get_inline_keyboard_builder()
        else:
            kb = get_inline_keyboard_builder(iterable=[CONFIRMATION_MESSAGE])

        await edit_base_message(
            chat_id=data['chat_id'],
            message_id=data['message_id'],
            text=text,
            keyboard=kb,
            bot=bot,
        )
    except Exception as e:
        msg = f"Error while adding a message and media. ERR: {e}"
        handlers_logger.error(msg=msg)
        data['err'] = 'Возникла ошибка при отправке сообщения. ' \
                      'Пожалуйста вернитесь на шаг назад и повторите отправку данных заново'

        text = await async_render_template('client_message_confirm.html', values=data)
        kb = get_inline_keyboard_builder()
        await edit_base_message(
            chat_id=data['chat_id'],
            message_id=data['message_id'],
            text=text,
            keyboard=kb,
            bot=bot,
        )

    await message.delete()


@router.callback_query(F.data == CONFIRMATION_MESSAGE, ContactSupportState.enter_message)
async def user_confirmed_message(
        callback_query: CallbackQuery, state: FSMContext, db_session: AsyncSession, bot: Bot,
) -> None:
    """Client has finished entering message, message is sent - show notification message"""
    data = await state.get_data()
    data['user_telegram_id'] = callback_query.from_user.id

    media = data.get('user_media')
    aviline_chat_id = AVILINE_MANAGER_CHAT_ID if data['branch'] == 'purchase' else AVILINE_TECH_CHAT_ID

    if media:
        m, a, d = [], [], []
        for i in media:
            prefix, file_id = i.split('%%')
            if prefix == 'video' or prefix == 'img':
                m.append(InputMediaVideo(media=file_id) if prefix == 'video' else InputMediaPhoto(media=file_id))
            elif prefix == 'audio':
                a.append(InputMediaAudio(media=file_id))
            elif prefix == 'document':
                d.append(InputMediaDocument(media=file_id))

        if m:
            await bot.send_media_group(chat_id=aviline_chat_id, media=m)
        if d:
            await bot.send_media_group(chat_id=aviline_chat_id, media=d)
        if a:
            await bot.send_media_group(chat_id=aviline_chat_id, media=a)

    client_message_full_render = await async_render_template('support_client_message_with_contacts.html', values=data)
    message_created = await bot.send_message(chat_id=aviline_chat_id, text=client_message_full_render)
    user_message_text = data['user_message']
    await TicketRelatedQueries(db_session).create_ticket(
        question=user_message_text,
        user_telegram_id=data['user_telegram_id'],
        related_message_telegram_id=message_created.message_id,
    )
    await db_session.commit()

    text = await async_render_template('message_sent_success.html', values=data)
    await edit_base_message(
        chat_id=data['chat_id'],
        message_id=data['message_id'],
        text=text,
        keyboard=get_inline_keyboard_builder(),
        bot=bot,
    )
    await state.clear()
    await RedisAdapter().set_lock(user_id=callback_query.from_user.id)


@router.callback_query(F.data.in_({CONFIRMATION_MESSAGE, NEGATIVE_MESSAGE}))
async def client_replied(callback_query: CallbackQuery, bot: Bot) -> None:
    if callback_query.data == NEGATIVE_MESSAGE:
        phone = "8-800-555-09-20"
        text = f"Пожалуйста свяжитесь с нашей техподдержкой по телефону: {phone}"
    else:
        text = 'Благодарим Вас за Ваше обращение!'

    await edit_base_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=text,
        keyboard=get_inline_keyboard_builder(),
        bot=bot,
    )
