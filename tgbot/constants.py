

AVAILABLE_SERVICES = {
    'О продукции': 'purchase',
    'Техподдержка': 'support',
    'Гарантийная служба': 'warranty',
}

GET_NAME_PATTERN = r'([a-zа-яA-ZА-Я]+[-\s.]*)*[a-zа-яA-ZА-Я]{2,}$'

MIME_TYPES_ALLOWED = {'image/jpeg', 'image/png', 'video/mp4', 'audio/mpeg', 'audio/ogg'}

CLEAN_PHONE_PATTERN = r'[^\d]'  # not digits
GET_PHONE_PATTERN = r'\d{7,11}'  # 7 to 11 digits
GET_EMAIL_PATTERN = r'(\w+\.)*\w+@([a-zA-Z]+\.)+[a-zA-Z]{2,}'

CONFIRMATION_MESSAGE = '✅ да'
CONFIRM_POLICY = '✅ согласиться'
VERIFY_ENTRY = '✅ всё верно'
VERIFY_SENDING = '✅ отправить'
NEGATIVE_MESSAGE = '❌ Нет. У меня остались вопросы'

MEDIA_TYPES = {
    "img": 1,
    "video": 2,
    "audio": 3,
    "document": 4,
    "animation": 5,
}

WARRANTY_CHANGE_CARD = {"🔁 Изменить вложение": "change_warranty_card"}
WARRANTY_CHANGE_CONTACTS = {"🔁 Изменить контактные данные": "change_client_contact"}
WARRANTY_CONFIRM_MAIL = {"✅ Отправить сообщение": VERIFY_SENDING}
