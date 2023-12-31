

AVAILABLE_SERVICES = ['purchase', 'support']
AVAILABLE_PRODUCTS = ['видеорегистратор', 'электропривод багажника', 'парковочные системы', 'камера заднего вида',
                      'система контроля слепых зон', 'CANA-PRO']

PRODUCT_DESCRIPTION = ['versions', 'price', 'details', 'manual']

KNOWN_PROBLEMS = {
    'видеорегистратор': [
        'На экране надпись AVILINE',
        'Утерян брелок-активатор',
        'Не работает или завис',
        'Видеорегистратор работает нестабильно',
        'Видеорегистратор работает нестабильно',
    ],
    'электропривод багажника': [
        'С салонной кнопки электропривод не открывает',
        'багажник открывается при снятии а/м с охраны',
    ],
    'парковочные системы': [
        'Какой инструмент необходим для установки датчиков  парковочной системе',
    ],
    'CANA-PRO': [
        'Как сменить прошивку в CANA -PRO адаптере',
        'Какие автомобили  совместимы с CANA-PRO адаптером',
    ],
    'камера заднего вида': [],
}

GET_NAME_PATTERN = r'([a-zа-яA-ZА-Я]+[-\s.]*)*[a-zа-яA-ZА-Я]{2,}$'

CLEAN_PHONE_PATTERN = r'[^\d]'
GET_PHONE_PATTERN = r'\d{7,11}'
GET_EMAIL_PATTERN = r''
