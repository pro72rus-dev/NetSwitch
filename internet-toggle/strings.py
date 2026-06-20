_lang = 'en'

_strings = {
    'en': {
        'status': 'STATUS',
        'connected': 'Internet Connected',
        'disconnected': 'Internet Disconnected',
        'hotkey_label': 'HOTKEY',
        'change': 'Change',
        'confirm': '\u2713 Confirm',
        'cancel': '\u2715 Cancel',
        'press_keys': 'Press keys...',
        'click_confirm': 'Click \u2713 to confirm',
        'lang_btn': 'EN',
        'enabled': 'Enabled',
        'disabled': 'Disabled',
        'no_internet': 'No internet',
        'no_adapters': 'No adapters found',
        'error': 'Error',
        'enabling': 'Enabling...',
        'cancelled': 'Cancel',
        'hotkey_reset': 'Hotkey reset',
        'hotkey_changed': 'Hotkey changed',
        'invalid_hotkey': 'Invalid hotkey',
        'failed_register': 'Failed to register hotkey',
        'install_hint': 'Welcome to NetSwitch!',
        'show_window': 'Show window',
        'exit': 'Exit',
        'on': 'On',
        'off': 'Off',
    },
    'ru': {
        'status': 'СТАТУС',
        'connected': 'Интернет включён',
        'disconnected': 'Интернет выключен',
        'hotkey_label': 'ГОРЯЧАЯ КЛАВИША',
        'change': 'Изменить',
        'confirm': '\u2713 Подтвердить',
        'cancel': '\u2715 Отмена',
        'press_keys': 'Нажмите клавиши...',
        'click_confirm': 'Нажмите \u2713 для подтверждения',
        'lang_btn': 'RU',
        'enabled': 'Включено',
        'disabled': 'Отключено',
        'no_internet': 'Нет интернета',
        'no_adapters': 'Адаптеры не найдены',
        'error': 'Ошибка',
        'enabling': 'Включение...',
        'cancelled': 'Отмена',
        'hotkey_reset': 'Клавиша сброшена',
        'hotkey_changed': 'Клавиша изменена',
        'invalid_hotkey': 'Неверная комбинация',
        'failed_register': 'Не удалось зарегистрировать клавишу',
        'install_hint': 'Добро пожаловать в NetSwitch!',
        'show_window': 'Показать окно',
        'exit': 'Выход',
        'on': 'Вкл',
        'off': 'Выкл',
    },
}


def set_lang(lang: str) -> None:
    global _lang
    _lang = 'ru' if lang == 'ru' else 'en'


def get_lang() -> str:
    return _lang


def t(key: str) -> str:
    return _strings.get(_lang, _strings['en']).get(key, key)
