from django.core.exceptions import ValidationError


def product_name_lte_64_bytes(value: str):
    value = value.encode('utf-8')
    if len(value) > 63:
        raise ValidationError(
            f'''Строка "{value.decode('utf-8')}" размера больше 64 байта: {len(value)}. '''
            'ВАЖНО! НЕ более 32-х символов кириллицей, иначе не поместиться в кнопку телеги.'
        )
