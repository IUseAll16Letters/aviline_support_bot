import os
import aiofiles

from os.path import basename
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

# from sqlaclhemy ...
from tgbot.constants import CONFIRMATION_MESSAGE, WARRANTY_CHANGE_CARD, WARRANTY_CHANGE_CONTACTS, WARRANTY_CONFIRM_MAIL
from config.settings import SMTP_MAIL_PARAMS
from tgbot.keyboards import get_inline_keyboard_builder
from tgbot.states import WarrantyState
from tgbot.utils import render_template, parse_message_media, edit_base_message, get_client_message, \
    send_email_to_aviline, download_file_from_telegram_file_id
from tgbot.utils.base import get_allowed_media_id

router = Router()


@router.callback_query(F.data == 'warranty')
async def start_enter_problem(callback_query: CallbackQuery, state: FSMContext):
    """ask to describe problem"""
    await state.set_state(WarrantyState.describe_problem)
    data = await state.update_data({"message": callback_query.message})
    text = render_template('warranty_describe_problem.html')
    await edit_base_message(
        message=callback_query.message,
        text=text,
        keyboard=get_inline_keyboard_builder(),
    )


@router.message(WarrantyState.describe_problem)
async def enter_purchase_location(message: Message, state: FSMContext):
    """ask to enter where buy product"""
    await state.set_state(WarrantyState.where_when_buy)
    data = await state.update_data({"client_problem": message.text})  # if not message text: raise error
    text = render_template('warranty_where_when_buy.html')
    core_message: Message = data['message']
    await edit_base_message(
        message=core_message,
        text=text,
        keyboard=get_inline_keyboard_builder(),
    )
    await message.delete()


@router.message(WarrantyState.where_when_buy)
async def enter_client_location(message: Message, state: FSMContext):
    """ask to enter his location"""
    await state.set_state(WarrantyState.location)
    data = await state.update_data({"client_where_buy": message.text})  # if not message text: raise error
    text = render_template('warranty_location.html')
    core_message: Message = data['message']
    await edit_base_message(
        message=core_message,
        text=text,
        keyboard=get_inline_keyboard_builder(),
    )
    await message.delete()


@router.message(WarrantyState.location)
async def enter_car_brand(message: Message, state: FSMContext):
    """enters his car brand"""
    await state.set_state(WarrantyState.car_brand)
    data = await state.update_data({"client_city": message.text})  # if not message text: raise error
    text = render_template('warranty_client_car.html')
    core_message: Message = data['message']
    await edit_base_message(
        message=core_message,
        text=text,
        keyboard=get_inline_keyboard_builder(),
    )
    await message.delete()


@router.message(WarrantyState.car_brand)
async def confirm_warranty_entry(message: Message, state: FSMContext):
    """confirms all data correct"""
    await state.set_state(WarrantyState.confirm_entry)
    data = await state.update_data({"client_car": message.text})
    text = render_template("warranty_confirm_entry.html", values=data)
    core_message: Message = data['message']
    await edit_base_message(
        message=core_message,
        text=text,
        keyboard=get_inline_keyboard_builder([CONFIRMATION_MESSAGE, ])
    )
    await message.delete()


@router.callback_query(F.data == CONFIRMATION_MESSAGE, WarrantyState.confirm_entry)
async def enter_contact_warranty_coupon(callback_query: CallbackQuery, state: FSMContext):
    """confirmed input data correct, now enter contact + warranty card"""
    await state.set_state(WarrantyState.approval_docs_contact)
    data = await state.get_data()
    text = render_template('warranty_enter_approval_docs.html', values=data)
    core_message: Message = data['message']

    file_id, user_message = data.get('user_warranty_message'), data.get('user_warranty_card')
    iterable = {}
    if file_id is not None:
        iterable.update(WARRANTY_CHANGE_CARD)
    if user_message is not None:
        iterable.update(WARRANTY_CHANGE_CONTACTS)
    if user_message is not None and file_id is not None:
        iterable.update(WARRANTY_CONFIRM_MAIL)

    await edit_base_message(
        message=core_message,
        text=text,
        keyboard=get_inline_keyboard_builder(iterable=iterable, row_col=(1, 1)),
    )
    del iterable


@router.message(WarrantyState.approval_docs_contact)
async def client_need_to_confirm(message: Message, bot: Bot, state: FSMContext):
    """enters his contacts and approval contact after callback"""
    data = await state.get_data()

    user_message, file_id = data.get('user_warranty_message'), data.get('user_warranty_card')
    iterable = {}
    if user_message is None:
        user_message = get_client_message(message)
        if user_message is not None:
            data['user_warranty_message'] = user_message
            iterable.update(WARRANTY_CHANGE_CONTACTS)
    else:
        iterable.update(WARRANTY_CHANGE_CONTACTS)

    if file_id is None:
        file_id = get_allowed_media_id(message)
        if file_id is not None:
            user_warranty_card = await download_file_from_telegram_file_id(
                bot_instance=bot,
                telegram_file_id=file_id,
                telegram_user_id=message.from_user.id,
            )
            data['user_warranty_card'] = user_warranty_card
            iterable.update(WARRANTY_CHANGE_CARD)
    else:
        iterable.update(WARRANTY_CHANGE_CARD)

    data = await state.update_data(data)
    core_message: Message = data['message']
    text = render_template("warranty_enter_approval_docs.html", values=data)
    if file_id is not None and user_message is not None:
        iterable.update(WARRANTY_CONFIRM_MAIL)

    await edit_base_message(
        message=core_message,
        text=text,
        keyboard=get_inline_keyboard_builder(iterable=iterable, row_col=(1, 1))
    )

    await message.delete()


@router.callback_query(F.data.in_(("change_warranty_card", "change_client_contact")), WarrantyState.approval_docs_contact)
async def clear_field(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if callback_query.data == "change_warranty_card":
        try:
            os.remove(data["user_warranty_card"])
        except Exception as e:
            print('COULDNT DELETE FILE FROM CLEARFIELD BECAUSE OF E', e)
        data["user_warranty_card"] = None
    else:
        data["user_warranty_message"] = None
    iterable = {}

    if data.get('user_warranty_card') is not None:
        iterable.update(WARRANTY_CHANGE_CARD)
    if data.get('user_warranty_message') is not None:
        iterable.update(WARRANTY_CHANGE_CONTACTS)

    data = await state.update_data(data)
    text = render_template("warranty_enter_approval_docs.html", values=data)
    core_message: Message = data['message']
    await edit_base_message(
        message=core_message,
        text=text,
        keyboard=get_inline_keyboard_builder(iterable=iterable, row_col=(1, 1)),
    )
    del iterable


@router.callback_query(F.data == CONFIRMATION_MESSAGE, WarrantyState.approval_docs_contact)
async def send_mail(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    core_message = data['message']
    await edit_base_message(
        message=core_message,
        text=render_template("warranty_message_is_sending.html"),
        keyboard=get_inline_keyboard_builder(),
    )

    text = render_template("warranty_email_template.html", values=data)
    user_warranty_card = data['user_warranty_card']
    async with aiofiles.open(user_warranty_card, 'rb') as f:
        await send_email_to_aviline(
            subject=SMTP_MAIL_PARAMS['subject']
            .replace("%u%", data.get('default_user', 'tester'))
            .replace('%tgi%', str(callback_query.from_user.id)),
            text=text,
            warranty_card=(await f.read()),
            warranty_basename=basename(user_warranty_card),
        )

    try:
        os.remove(user_warranty_card)
    except Exception as e:
        print('COULDNT REMOVE FILE FROM SENDING MAIL BECAUSE OF: ', e)

    await edit_base_message(
        message=data['message'],
        text=render_template("warranty_message_OK.html"),
        keyboard=get_inline_keyboard_builder(),
    )

    await state.clear()
