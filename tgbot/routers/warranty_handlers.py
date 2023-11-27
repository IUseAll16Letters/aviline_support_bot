import datetime

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.cache import RedisAdapter
from tgbot.constants import WARRANTY_CHANGE_CARD, WARRANTY_CHANGE_CONTACTS, WARRANTY_CONFIRM_MAIL, \
    VERIFY_ENTRY, VERIFY_SENDING
from config.settings import SMTP_MAIL_PARAMS
from tgbot.keyboards import get_inline_keyboard_builder
from tgbot.states import WarrantyState
from tgbot.utils import render_template, edit_base_message, get_client_message, \
    send_email_to_aviline, download_file_from_telegram_file_id, get_allowed_media_id
from tgbot.utils.shortcuts import refresh_message_data_from_callback_query
from tgbot.logging_config import mailing


router = Router()


@router.callback_query(F.data == 'warranty')
async def enter_problem(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    """ask to describe problem"""
    data = await refresh_message_data_from_callback_query(callback_query, state)
    text = render_template('warranty_describe_problem.html')
    await state.set_state(WarrantyState.describe_problem)
    await edit_base_message(
        chat_id=data['chat_id'],
        message_id=data['message_id'],
        text=text,
        keyboard=get_inline_keyboard_builder(),
        bot=bot,
    )


@router.message(WarrantyState.describe_problem)
async def enter_purchase_location(message: Message, state: FSMContext, bot: Bot):
    """ask to enter where buy product"""
    data = await state.update_data({"client_problem": message.text})  # if not message text: raise error
    text = render_template('warranty_where_when_buy.html')
    await state.set_state(WarrantyState.where_when_buy)
    await edit_base_message(
        chat_id=data['chat_id'],
        message_id=data['message_id'],
        text=text,
        keyboard=get_inline_keyboard_builder(),
        bot=bot,
    )
    await message.delete()


@router.message(WarrantyState.where_when_buy)
async def enter_client_location(message: Message, state: FSMContext, bot: Bot):
    """ask to enter his location"""
    data = await state.update_data({"client_where_buy": message.text})  # if not message text: raise error
    text = render_template('warranty_location.html')

    await state.set_state(WarrantyState.location)
    await edit_base_message(
        chat_id=data['chat_id'],
        message_id=data['message_id'],
        text=text,
        keyboard=get_inline_keyboard_builder(),
        bot=bot,
    )
    await message.delete()


@router.message(WarrantyState.location)
async def enter_car_brand(message: Message, state: FSMContext, bot: Bot):
    """enters his car brand"""
    await state.set_state(WarrantyState.car_brand)
    data = await state.update_data({"client_city": message.text})  # if not message text: raise error
    text = render_template('warranty_client_car.html')

    await edit_base_message(
        chat_id=data['chat_id'],
        message_id=data['message_id'],
        text=text,
        keyboard=get_inline_keyboard_builder(),
        bot=bot,
    )
    await message.delete()


@router.message(WarrantyState.car_brand)
async def confirm_warranty_entry(message: Message, state: FSMContext, bot: Bot):
    """confirms all data correct"""
    await state.set_state(WarrantyState.confirm_entry)
    data = await state.update_data({"client_car": message.text})
    text = render_template("warranty_confirm_entry.html", values=data)

    await edit_base_message(
        chat_id=data['chat_id'],
        message_id=data['message_id'],
        text=text,
        keyboard=get_inline_keyboard_builder([VERIFY_ENTRY]),
        bot=bot,
    )
    await message.delete()


@router.callback_query(F.data == VERIFY_ENTRY, WarrantyState.confirm_entry)
async def enter_contact_warranty_coupon(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    """confirmed input data correct, now enter contact + warranty card"""
    await state.set_state(WarrantyState.approval_docs_contact)
    data = await state.get_data()

    img_ttl = await RedisAdapter.check_client_warranty_image_exists(user_id=callback_query.from_user.id)
    user_message = data.get('user_warranty_message')

    keyboard_buttons = {}
    if img_ttl > 0:
        keyboard_buttons.update(WARRANTY_CHANGE_CARD)
    else:
        if 'user_warranty_card' in data:
            data.pop('user_warranty_card')
            await state.set_data(data)

    if user_message is not None:
        keyboard_buttons.update(WARRANTY_CHANGE_CONTACTS)
    if user_message is not None and img_ttl > 0:
        keyboard_buttons.update(WARRANTY_CONFIRM_MAIL)

    text = render_template('warranty_enter_approval_docs.html', values=data)
    await edit_base_message(
        chat_id=data['chat_id'],
        message_id=data['message_id'],
        text=text,
        keyboard=get_inline_keyboard_builder(iterable=keyboard_buttons, row_col=(1, 1)),
        bot=bot,
    )


@router.message(WarrantyState.approval_docs_contact)
async def client_need_to_confirm(message: Message, state: FSMContext, bot: Bot):
    """enters his contacts and approval contact after callback"""
    data = await state.get_data()

    user_message = data.get('user_warranty_message')
    new_user_message = get_client_message(message)
    keyboard_buttons = {}

    if new_user_message is not None:
        if user_message is not None:
            data['user_warranty_message'] += f" {new_user_message}"
        else:
            data['user_warranty_message'] = new_user_message

    if data.get('user_warranty_message'):
        keyboard_buttons.update(WARRANTY_CHANGE_CONTACTS)

    file_saved_to_redis = await RedisAdapter.check_client_warranty_image_exists(message.from_user.id)
    if not data.get('user_warranty_card', False) or file_saved_to_redis < 0:
        file_id, ext = get_allowed_media_id(message)
        if file_id == -1:
            data['err'] = "!Размер Вашего файла превышает 10 МБ. " \
                          "Вы можете уменьшить качество или обрезать несущественную информацию с изображения."
        elif file_id != -2:
            user_warranty_card = await download_file_from_telegram_file_id(bot_instance=bot, telegram_file_id=file_id)
            await RedisAdapter.save_client_warranty_image(user_id=message.from_user.id, file=user_warranty_card)
            data['user_warranty_card'] = ext
            keyboard_buttons.update(WARRANTY_CHANGE_CARD)
    else:
        keyboard_buttons.update(WARRANTY_CHANGE_CARD)

    data = await state.update_data(data)

    if data.get('user_warranty_card', False) and data.get('user_warranty_message') is not None:
        keyboard_buttons.update(WARRANTY_CONFIRM_MAIL)

    text = render_template("warranty_enter_approval_docs.html", values=data)
    await edit_base_message(
        chat_id=data['chat_id'],
        message_id=data['message_id'],
        text=text,
        keyboard=get_inline_keyboard_builder(iterable=keyboard_buttons, row_col=(1, 1)),
        bot=bot,
    )

    await message.delete()


@router.callback_query(
    F.data.in_(("change_warranty_card", "change_client_contact")),
    WarrantyState.approval_docs_contact,
)
async def clear_field(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()

    if callback_query.data == "change_warranty_card":
        try:
            await RedisAdapter.clear_client_warranty_image(user_id=callback_query.from_user.id)
        except Exception as e:
            msg = f"Could not delete the file for user: {callback_query.from_user.id}. Error: {e}"
            mailing.error(msg=msg)
        data["user_warranty_card"] = False
    else:
        data["user_warranty_message"] = None

    keyboard_buttons = {}
    if data.get('user_warranty_card'):
        keyboard_buttons.update(WARRANTY_CHANGE_CARD)
    if data.get('user_warranty_message') is not None:
        keyboard_buttons.update(WARRANTY_CHANGE_CONTACTS)

    data = await state.update_data(data)
    text = render_template("warranty_enter_approval_docs.html", values=data)

    await edit_base_message(
        chat_id=data['chat_id'],
        message_id=data['message_id'],
        text=text,
        keyboard=get_inline_keyboard_builder(iterable=keyboard_buttons, row_col=(1, 1)),
        bot=bot,
    )


@router.callback_query(F.data == VERIFY_SENDING, WarrantyState.approval_docs_contact)
async def send_mail(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await edit_base_message(
        chat_id=data['chat_id'],
        message_id=data['message_id'],
        text=render_template("warranty_message_is_sending.html"),
        keyboard=get_inline_keyboard_builder(),
        bot=bot,
    )

    file = await RedisAdapter.get_client_warranty_image(callback_query.from_user.id)

    if file:
        text = render_template("warranty_email_template.html", values=data)
        base_name = f'warranty_{callback_query.from_user.id}_' \
                    f'{datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.' \
                    f'{data.get("user_warranty_card", "jpg")}'
        await send_email_to_aviline(
            subject=SMTP_MAIL_PARAMS['subject'].replace("%u%", str(callback_query.from_user.id)),
            text=text,
            warranty_card=file,
            warranty_basename=base_name,
        )
        try:
            await RedisAdapter.clear_client_warranty_image(user_id=callback_query.from_user.id)
        except Exception as e:
            msg = f"Could not delete the file for user: {callback_query.from_user.id}. Error: {e}"
            mailing.error(msg=msg)
        await edit_base_message(
            chat_id=data['chat_id'],
            message_id=data['message_id'],
            text=render_template("warranty_message_OK.html"),
            keyboard=get_inline_keyboard_builder(),
            bot=bot,
        )
        await state.clear()

    else:
        data['err'] = 'Срок хранения изображения гарантийного талона прошел и оно было удалено,' \
                      ' либо произошел системный сбой.\nПожалуйста повторно загрузите изображение.'
        data['user_warranty_card'] = False
        keyboard_buttons = {}

        if data.get('user_warranty_message') is not None:
            keyboard_buttons.update(WARRANTY_CHANGE_CONTACTS)

        await edit_base_message(
            chat_id=data['chat_id'],
            message_id=data['message_id'],
            text=render_template('warranty_enter_approval_docs.html', values=data),
            keyboard=get_inline_keyboard_builder(iterable=keyboard_buttons),
            bot=bot,
        )
