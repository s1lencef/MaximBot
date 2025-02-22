from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from collections import namedtuple

menus = {
    'main': {
        'type': 'reply',
        'body': [
            {
                'text': 'Main Menu',
                'buttons': [
                    KeyboardButton("🧾 Начать работу"),
                    KeyboardButton("👤 Профиль"),
                    KeyboardButton("❓ Помощь"),
                ],
                'header': None,
                'footer': None,
                'n_cols': 1
            },
        ]
    },
    'main_simple': {
        'type': 'reply',
        'body': [
            {
                'text': 'Main Menu',
                'buttons': [
                    KeyboardButton("👤 Профиль"),
                    KeyboardButton("❓ Помощь"),
                    KeyboardButton("💬 Связаться с менеджером"),
                ],
                'header': None,
                'footer': None,
                'n_cols': 1
            },
        ]
    },
    'admin_global': {
        'type': 'reply',
        'body': [
            {
                'text': 'Admin Menu',
                'buttons': [
                    KeyboardButton('📋 Настроить данные приложения'),
                    KeyboardButton("👥 Управлять пользователями"),
                    KeyboardButton("🎹 Работа с артистами"),
                ],
                'header': None,
                'footer': None,
                'n_cols': 1
            },
        ]
    },
    'admin_artist': {
        'type': 'reply',
        'body': [
            {
                'text': 'Admin Menu',
                'buttons': [
                    KeyboardButton("🔍 Поиск треков"),
                    KeyboardButton("📊 Статистика"),
                    KeyboardButton("🎤 Добавить артиста"),
                    KeyboardButton("📃 Список артистов"),
                ],
                'header': None,
                'footer': [KeyboardButton('↩️ Назад'),],
                'n_cols': 2
            },
        ]
    },


    'user_change_main': {
        'type': 'inline',
        'body': [
            {
                'text': 'User Change',
                'buttons': [
                    InlineKeyboardButton("❌ Удалить", callback_data="users#delete_user"),
                    InlineKeyboardButton("🚫 Заблок./Разблок.", callback_data="users#ban_user"),
                    InlineKeyboardButton("📖 Посмотреть список пользователей", callback_data="users#see_users"),
                ],
                'header': [InlineKeyboardButton("✍ Отредактировать данные", callback_data="users#change_user")],
                'footer': [InlineKeyboardButton("Отмена", callback_data="cancel")],
                'n_cols': 2
            },
        ]
    },
    'call': {
        'type': 'inline',
        'body': [
            {
                'text': 'Call Maxim Lukin',
                'buttons': [
                    InlineKeyboardButton("Открыть чат", url="https://t.me/PhantomTrack"),

                ],
                'header': None,
                'footer': None,
                'n_cols': 1
            },
        ]
    },
    'help': {
        'type': 'inline',
        'body': [
            {
                'text': 'Call Maxim Lukin',
                'buttons': [
                    InlineKeyboardButton("Программа лояльности", callback_data="user#help#loyalty"),
                    InlineKeyboardButton("Артистам издательства", callback_data="user#help#statistics"),

                ],
                'header': None,
                'footer': [
                    InlineKeyboardButton("Группа Вк", url="https://vk.com/fantomtrack"),
                    InlineKeyboardButton("Открыть чат с менеджером", url="https://t.me/PhantomTrack"),

                ],
                'n_cols': 2
            },
        ]
    },
    'help_back': {
        'type': 'inline',
        'body': [
            {
                'text': 'Call Maxim Lukin',
                'buttons': [
                    InlineKeyboardButton("<", callback_data="user#help#back")
                ],
                'header': None,
                'footer':None ,
                'n_cols': 1
            },
        ]
    },
    "statistics":{
        'type': 'reply',
        'body': [
            {
                'text': 'Statistics manu',
                'buttons': [
                    KeyboardButton('📈 Посмотреть статистику'),
                    KeyboardButton('✍️ Внести данные о статистике'),
                    KeyboardButton('🔄 Другой артист'),
                    KeyboardButton('❌ Завершить'),
                ],
                'header': None,
                'footer': None,
                'n_cols': 1
            },
        ]
    },
    "create_statistics": {
        'type': 'inline',
        'body': [
            {
                'text': 'Adding statistics to artist',
                'buttons': [
                    InlineKeyboardButton('Да', callback_data="artists#statistics#True"),
                    InlineKeyboardButton('Нет', callback_data="artists#statistics#False"),
                ],
                'header': None,
                'footer': [InlineKeyboardButton('Отмена', callback_data='cancel')],
                'n_cols': 2
            },
        ]
    },
    "asigne_artist": {
        'type': 'inline',
        'body': [
            {
                'text': 'Adding user to artist',
                'buttons': [
                    InlineKeyboardButton('Да', callback_data="artists#asigne#True"),
                    InlineKeyboardButton('Нет', callback_data="artists#asigne#False"),
                ],
                'header': None,
                'footer': [InlineKeyboardButton('Отмена', callback_data='cancel')],
                'n_cols': 2
            },
        ]
    },
    "user_artists": {
        'type': 'inline',
        'body': [
            {
                'text': 'Adding user to artist',
                'buttons': [
                    InlineKeyboardButton('Показать договор', callback_data="user#get_agreement"),
                    InlineKeyboardButton('Показать статистику', callback_data="user#get_statistics"),
                    InlineKeyboardButton('Привязать артиста', callback_data="user#add_artist"),
                ],
                'header': None,
                'footer': None,
                'n_cols': 2
            },
        ]
    },
    "change_start_year": {
        'type': 'inline',
        'body': [
            {
                'text': 'Хотите задать год начала отсчета статистики?\nГод по умолчанию: <b>2023</b>',
                'buttons': [
                    InlineKeyboardButton('Да', callback_data="artists#change_year#True"),
                    InlineKeyboardButton('Нет', callback_data="artists#change_year#False"),
                ],
                'header': None,
                'footer': [InlineKeyboardButton('Отмена', callback_data='cancel')],
                'n_cols': 2
            },
        ]
    },

}


def build_menu(buttons, n_cols=1, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def get_menu(tag):
    try:
        menu_name = tag.split("#")[1]
    except:
        menu_name = tag
    try:
        menu_page = int(tag.split("#")[2])
    except:
        menu_page = 0

    try:
        cur_menu = menus[menu_name]['body'][menu_page]
        if menus[menu_name]['body'][menu_page]['text']:
            text = menus[menu_name]['body'][menu_page]['text']
        else:
            text = None
    except Exception as e:
        return False

    markup = build_menu(buttons=cur_menu['buttons'],
                        n_cols=cur_menu['n_cols'],
                        header_buttons=cur_menu['header'],
                        footer_buttons=cur_menu['footer'])

    menu = namedtuple('menu', 'reply_markup text tag page type')
    menu.tag = tag
    menu.page = menu_page
    menu.type = menus[menu_name]['type']
    menu.text = text

    if menus[menu_name]['type'] == 'inline':
        menu.reply_markup = InlineKeyboardMarkup(markup)
    if menus[menu_name]['type'] == 'reply':
        menu.reply_markup = ReplyKeyboardMarkup(keyboard=markup, resize_keyboard=True)

    return menu
