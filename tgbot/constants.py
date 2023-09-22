from aiogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAudio, InputMediaAnimation

AVILINE_CHAT_ID = -1001948597816

AVAILABLE_SERVICES = {
    'О продукции': 'purchase',
    'Техподдержка': 'support'
}

PRODUCT_DESCRIPTION = ['versions', 'price', 'details', 'manual']

GET_NAME_PATTERN = r'([a-zа-яA-ZА-Я]+[-\s.]*)*[a-zа-яA-ZА-Я]{2,}$'

MIME_TYPES_ALLOWED = {'image/jpeg', 'image/png', 'video/mp4', 'audio/mpeg', 'audio/ogg'}

CLEAN_PHONE_PATTERN = r'[^\d]'
GET_PHONE_PATTERN = r'\d{7,11}'
GET_EMAIL_PATTERN = r'(\w+\.)*\w+@([a-zA-Z]+\.)+[a-zA-Z]{2,}'

CONFIRMATION_MESSAGE = '✅ да'

MEDIA_TYPES = {
    InputMediaPhoto: 1,
    InputMediaVideo: 2,
    InputMediaAudio: 3,
    InputMediaDocument: 4,
    InputMediaAnimation: 5,
}
