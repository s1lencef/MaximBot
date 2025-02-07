import telegram
from prettytable import PrettyTable, ALL

from models import *
from peewee import DoesNotExist
from telegram.constants import ParseMode
from menu import *
import re

cancel_reply_markup = InlineKeyboardMarkup(build_menu([InlineKeyboardButton('Отмена', callback_data='cancel')]))

def is_valid_format(s):
    pattern = r"^\d-\d{3}$"  # ^ - начало строки, \d - одна цифра, {3} - три цифры, $ - конец строки
    return bool(re.fullmatch(pattern, s))

class DoesNotExist(Exception):
    def __int__(self, text="User Not Found"):
        self.txt = text


class NegativeSumError(Exception):
    def __init__(self, text="Too much money to remove!!!!!!!"):
        self.txt = text


def is_user_exist(id):
    try:
        user = User.get(id=id)
    except Exception as e:
        return False
    else:
        return True


def checkuser(function):
    async def check(update, context):
        menu = get_menu('main')
        if not is_user_exist(id=update.effective_user.id):
            message = ("Вас приветствует <b>PhantomTrackBot</b>!\n\n"
                       "<i>Здесь вы можете принять участие в программе лояльности PhantomTrack.\n"
                       "За покупки вам будут</i> <b>начисляться баллы</b>, "
                       "<i>которыми можно будет оплачивать последующие заказы.\n<b>1 балл = 1 рубль.</b>\n\n"
                       "В боте вы сможете ознакомиться с </i><b>условиями проведения программы лояльности</b><i> и</i>"
                       " <b>количеством баллов</b>, "
                       "<i>которые имеются на вашем аккаунте.\n\n</i>"
                       "<b>Для продолжения введите команду <code>/register</code> и следуйте инструкциям бота</b>\n\n")

            reply_markup = menu.reply_markup
            await update.message.reply_text(message, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        else:
            user = User.get(id=update.effective_user.id)
            if user.status:
                await function(update, context)
            else:
                message = ("Ваша учетная запись заблокирована!")

                await update.message.reply_text(message, parse_mode=ParseMode.HTML)

    return check


def checkadmin(function):
    async def check(update, context):
        try:
            user = User.get(id=update.message.from_user.id)
            print(f'User = {user}')
            if user.role == Role.get(1):
                print(True)
                if user.status:
                    await function(update, context)
                else:
                    message = ("Ваша учетная запись заблокирована!")

                    await update.message.reply_text(message, parse_mode=ParseMode.HTML)
            else:
                print(False)
                raise DoesNotExist
        except Exception as e:
            print(e)
            await update.message.reply_text("Неизвестная команда", parse_mode=ParseMode.HTML)

    return check


def generate_unique_id(id):
    while (is_user_exist(id)):
        id += 1
        id %= 10000
    return id


def how_much(id, curr):
    try:
        next = Loyalty_level.get(int(id) + 1)
        print(id)
    except Exception as e:
        print(e)
        return f"<b>У вас максимальный уровень лояльности!</b>"
    money = next.sum - curr
    return f"<i>Для достижения следующего уровня надо потратить</i> <b>{money} руб.</b>"


def does_level_exist(id):
    try:
        Loyalty_level.get(id)
    except Exception:
        return False

    return True


def write_loyalty():
    levels = Loyalty_level.select()
    text = "<b>Уровни лояльности:</b>\n"
    for level in levels:
        text += f"<b>{level.id} уровень</b>\n    Cумма для достижения: {level.sum}руб\n    {round(level.loyalty_coeff * 100, 1)}% начисляются баллами\n"
    return text


states = {
    0: "⚪️",
    1: "🟠",
    2: "🟢"
}
states_names = {
    0: "Нет действий",
    1: "Предоставлена",
    2: "Выплачено"
}

def get_statistics(artist_id):
    statistics = (
        Statistics
        .select()
        .where(Statistics.artist_id == artist_id)
        .order_by(Statistics.year, Statistics.quarter)
    )

    if not statistics:  # Если данных нет
        return "Нет данных для отображения."

    # Создаем таблицу
    table = PrettyTable()
    table.field_names = ["Год", "Кв. 1", "Кв. 2", "Кв. 3", "Кв. 4"]
    table.align = "c"  # Выравнивание по центру
    table.header = True
    table.hrules = ALL  # Добавляем горизонтальные линии между строками

    # Устанавливаем одинаковую ширину для всех колонок
    column_width = 5
    for field in table.field_names:
        table.min_width[field] = column_width

    # Группируем данные по годам
    grouped_statistics = {}
    for statistic in statistics:
        year = statistic.year
        if year not in grouped_statistics:
            grouped_statistics[year] = ["⚪️"] * 4  # По умолчанию — ⚪️ для каждого квартала
        grouped_statistics[year][statistic.quarter - 1] = f" {states[statistic.state]} "

    # Заполняем таблицу данными
    for year, quarters in grouped_statistics.items():
        table.add_row([year] + quarters)

    # Возвращаем таблицу как строку
    return f"<pre>{table}</pre>"

def fill_statistics(artist_name):
    artist = ArtistModel.get(name = artist_name)
    for i in range(2020, datetime.now().year+1):
        for j in range(1, 5):
            staistics = Statistics(artist_id=artist.id, year=i, quarter=j, state=0)
            staistics.save()