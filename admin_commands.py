from black import nullcontext
from pyexpat.errors import messages
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, ConversationHandler
from telegram.constants import ParseMode
import os
import user_commands
from core import *
from models import *
from config import *
from menu import *
from core import checkadmin
from yandex_music_service import *
from prettytable import PrettyTable, ALL
from parser import process

cancel_reply_markup = InlineKeyboardMarkup(build_menu([InlineKeyboardButton('Отмена', callback_data='cancel')]))


async def reg_admin(update, context):
    reply_markup = None
    id = update.effective_user.id
    message = ("Неизвестная команда")
    if len(context.args) == 1:

        password = context.args[0]

        if password == adminpass:

            if is_user_exist(id):

                user = User.get(id)

                if user.role == Role.get(1):
                    message = "Вы уже зарегистрированны!"
                else:
                    message = "Новоиспеченный администратор, добро пожаловать!"
                    user.role = Role.get(1)
                    user.save()

                reply_markup = get_menu('admin_global').reply_markup
            else:
                if update.effective_user.username:

                    username = update.effective_user.username

                else:

                    username = 'default_admin'

                user = User.create(
                    id=update.effective_user.id,
                    name=update.effective_user.first_name,
                    username=username,
                    role=1,
                    status=True,
                    card_id=generate_unique_id(update.effective_user.id % 10000),
                    loyalty_points=30,
                    money_paid=0,
                    loyalty_level=1
                )
                user.save()

                message = "Вы успешно зарегистрированны в системе"

            reply_markup = get_menu('admin_global').reply_markup

    await update.message.reply_text(message, parse_mode=ParseMode.HTML, reply_markup=reply_markup)


@checkadmin
async def change_loyalty(update, context):
    levels = Loyalty_level.select()

    message = "Изменение уровней лояльности:\n"
    buttons = [InlineKeyboardButton(str(level.id), callback_data="loyalty_level#" + str(level.id)) for level in levels]
    buttons.append(InlineKeyboardButton("➕", callback_data="loyalty_level#+"))
    buttons.append(InlineKeyboardButton("➖", callback_data="loyalty_level#-"))

    menu = build_menu(buttons, 3, footer_buttons=[InlineKeyboardButton("Закончить", callback_data="cancel")])

    reply_markup = InlineKeyboardMarkup(menu)

    await update.message.reply_text(message, parse_mode=ParseMode.HTML, reply_markup=reply_markup)


async def btn_handler(update, context):
    query = update.callback_query
    args = query.data.split('#')
    print(args)

    if args[0] == 'loyalty_level':
        if args[1] == '+':
            text = "Введите сумму, которая должна быть на этом уровне:"
            await query.edit_message_text(text=text, reply_markup=cancel_reply_markup, parse_mode=ParseMode.HTML)
            return 0
        elif args[1] == '-':
            if len(args) == 2:
                levels = Loyalty_level.select()
                text = "Выберите уровень для удаления:"
                buttons = [InlineKeyboardButton(str(level.id), callback_data="loyalty_level#-#" + str(level.id)) for
                           level
                           in levels]
                menu = build_menu(buttons, 4,
                                  footer_buttons=[
                                      InlineKeyboardButton("Вернуться", callback_data="loyalty_level#back")])

                reply_markup = InlineKeyboardMarkup(menu)

                await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            else:
                if does_level_exist(int(args[2]) - 1):
                    users = User.select().where(User.loyalty_level == Loyalty_level.get(int(args[2])))
                    for user in users:
                        user.loyalty_level_id = Loyalty_level.get(int(args[2]) - 1)
                        user.save()
                    level = Loyalty_level.get(int(args[2]))
                    level.delete_instance()
                    message = f"Уровень {args[2]} удален"
                else:
                    message = "Невозможно удалить самый нижний уровень!"
                await query.edit_message_text(text=message, reply_markup=None, parse_mode=ParseMode.HTML)
        elif args[1] == "back":

            levels = Loyalty_level.select()

            message = "Изменение уровней лояльности:\n"
            buttons = [InlineKeyboardButton(str(level.id), callback_data="loyalty_level#" + str(level.id)) for level in
                       levels]
            buttons.append(InlineKeyboardButton("➕", callback_data="loyalty_level#+"))
            buttons.append(InlineKeyboardButton("➖", callback_data="loyalty_level#-"))

            menu = build_menu(buttons, 3, footer_buttons=[InlineKeyboardButton("Закончить", callback_data="cancel")])

            reply_markup = InlineKeyboardMarkup(menu)

            await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

        else:
            if (len(args) == 2):
                buttons = [InlineKeyboardButton("Изменить сумму", callback_data=f"loyalty_level#{args[1]}#edit_sum"),
                           InlineKeyboardButton("Изменить процент",
                                                callback_data=f"loyalty_level#{args[1]}#edit_coeff")]
                menu = build_menu(buttons, 2, footer_buttons=[
                    InlineKeyboardButton("Вернуться", callback_data="loyalty_level#back")])
                reply_markup = InlineKeyboardMarkup(menu)
                level = Loyalty_level.get(int(args[1]))
                text = f"<i>Уровень:</i> <b>{args[1]}</b>\n<i>Сумма:</i> <b>{level.sum}</b>\n<i>Процент начисления:</i> <b>{round(level.loyalty_coeff * 100)}</b>"

                await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            else:

                context.user_data['level_id'] = int(args[1])
                if args[2] == "edit_sum":
                    await query.edit_message_text(text="Введите сумму:", reply_markup=cancel_reply_markup,
                                                  parse_mode=ParseMode.HTML)
                    return 2
                elif args[2] == "edit_coeff":
                    await query.edit_message_text(text="Введите процент:", reply_markup=cancel_reply_markup,
                                                  parse_mode=ParseMode.HTML)
                    return 3
    elif args[0] == "users":
        if args[1] == "delete_user":
            await query.edit_message_text(text="Введите id пользователя:", reply_markup=cancel_reply_markup,
                                          parse_mode=ParseMode.HTML)
            return 4
        if args[1] == 'change_user':

            if len(args) == 3:
                try:
                    id = int(context.user_data['user_id'])
                except Exception as e:
                    await query.edit_message_text("Время действия команды вышло!")
                    return ConversationHandler.END
                if args[2] == "extend_sum":
                    await query.edit_message_text("Укажите сумму покупки: ", reply_markup=cancel_reply_markup)
                    return 6
                if args[2] == "reduce_sum":
                    await query.edit_message_text("Укажите сумму покупки: ", reply_markup=cancel_reply_markup)
                    return 7
                if args[2] == "add_points":
                    await query.edit_message_text("Укажите количество баллов: ", reply_markup=cancel_reply_markup)
                    return 8
                if args[2] == "remove_points":
                    await query.edit_message_text("Укажите количество баллов: ", reply_markup=cancel_reply_markup)
                    return 9
                if args[2] == "remove_all_points":
                    reply_markup = InlineKeyboardMarkup(build_menu(
                        [InlineKeyboardButton('Отмена', callback_data='cancel'),
                         InlineKeyboardButton('Списать', callback_data='users#change_user#apply_point')], 2))
                    await query.edit_message_text(
                        f"Пользователь найден", reply_markup=reply_markup,
                        parse_mode=ParseMode.HTML)
                else:
                    user = User.get(card_id=int(context.user_data['user_id']))
                    if args[2] == "delete":
                        user.delete_instance()
                        await query.edit_message_text(
                            f"Пользователь<b> {context.user_data['user_id']} </b>удален!",
                            parse_mode=ParseMode.HTML)
                    elif args[2] == "apply_point":
                        points = user.loyalty_points
                        user.loyalty_points = 0
                        user.save()
                        await query.edit_message_text(
                            f"Списано <b>{points}</b> баллов. Теперь у пользователя <b>{user.loyalty_points}</b> баллов",
                            parse_mode=ParseMode.HTML)
                    elif args[2] == "ban":
                        user.status = not (user.status)
                        user.save()

                        status = "заблокирован"
                        if user.status:
                            status = "разблокирован"

                        await query.edit_message_text(f"Пользователь {user.username} {status}")

                    return ConversationHandler.END


            else:

                await query.edit_message_text(text="Введите id пользователя:", reply_markup=cancel_reply_markup,
                                              parse_mode=ParseMode.HTML)
                return 5
        if args[1] == "ban_user":
            await query.edit_message_text(text="Введите id пользователя:", reply_markup=cancel_reply_markup,
                                          parse_mode=ParseMode.HTML)
            return 10
        if args[1] == "see_users":

            text = "<b>Список пользователей</b>\n"
            try:
                users = User.select()

            except Exception as e:
                print(e)
                await query.edit_message_text(text="Сервис не доступен")
            else:
                text = text + f"Всего найдено: {len(users)}\n\n"
                for user in users:
                    text += f"    {user.username} - <code>{user.card_id}</code>\n"
                await query.edit_message_text(text=text, parse_mode=ParseMode.HTML)
                return 5
    elif args[0] == "artists":
        if args[2] == "back":
            await get_artist_query(query, args[1])
        else:
            try:
                menu = build_menu([
                    InlineKeyboardButton("<", callback_data="artists#" + args[1] + "#back")], 1)
                reply_markup = InlineKeyboardMarkup(menu)
                service = YandexMusicService()
                tracks = service.get_artist_tracks(int(args[2]))
                print(tracks.keys())
                result = modify_result(tracks)

                await query.edit_message_text(text=result, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
            except Exception as e:
                result = e.__str__()
                await query.edit_message_text(text=result, parse_mode=ParseMode.HTML)
        return ConversationHandler.END
    elif args[0] == "statistics":
        print(context.user_data)
        if len(args) == 4:
            statistics = Statistics(artist_id=int(context.user_data["artist_id"]), year=int(args[1]),
                                    quarter=int(args[2]), state=int(args[3]))
            statistics.save()
            await query.edit_message_text(
                text=f"Добавлена информация \n Артист: <i>{statistics.artist_id.name}</i>\n Год: <i>{statistics.year}</i>\n Квартал: <i>{statistics.quarter}</i>\n Статус: <i>{states_names[statistics.state]}</i>",
                parse_mode=ParseMode.HTML)
            return 13
        elif len(args) == 3:
            if args[1] == "create":
                if args[2] == "cancel":
                    context.user_data["artist_id"] = None
                    await query.edit_message_text(
                        "Создание отменено.\n Введите имя артиста повторно", reply_markup = cancel_reply_markup, parse_mode=ParseMode.HTML)

                    context.user_data["update"] = 2
                    return 12
                else:
                    artist = ArtistModel(name=args[2])
                    try:
                        artist.save()
                        context.user_data["artist_id"] = artist.id
                    except Exception as e:
                        await update.message.reply_text(e.__str__())
                        return ConversationHandler.END

                    for year in range(2020, datetime.now().year + 1):
                        for i in range(1, 5):
                            statistics = Statistics(artist_id=artist.id, year=year, quarter=i, state=0)
                            statistics.save()
                    await query.message.reply_text("Выберите действие",
                                                   reply_markup=get_menu("statistics").reply_markup)
                    return 13
            else:
                buttons = [InlineKeyboardButton(states_names[i], callback_data=query.data + "#" + str(i)) for i in
                           range(0, 3)]
                print(query.data)
                menu = build_menu(buttons, n_cols=3,
                                  footer_buttons=[InlineKeyboardButton("Назад", callback_data=args[0] + "#" + args[1])])

                await query.edit_message_text(text="Статус квартала", parse_mode=ParseMode.HTML,
                                              reply_markup=InlineKeyboardMarkup(menu))
                return 14

        elif len(args) == 2:
            buttons = [InlineKeyboardButton(f"Квартал {i}", callback_data=query.data + "#" + str(i)) for i in
                       range(1, 5)]
            menu = build_menu(buttons, n_cols=4, footer_buttons=[InlineKeyboardButton("Назад", callback_data=args[0])])
            await query.edit_message_text(text="Выберите квартал", parse_mode=ParseMode.HTML,
                                          reply_markup=InlineKeyboardMarkup(menu))
            return 14
        else:
            menu = build_menu([InlineKeyboardButton(year, callback_data="statistics#" + str(year)) for year in
                               range(2020, datetime.now().year + 1)], n_cols=4)
            await query.edit_message_text(f"Выберите год", reply_markup=InlineKeyboardMarkup(menu))

            return 14
    elif args[0] == "cancel":
        context.user_data["artist_id"] = None
        await query.edit_message_text(text="Действие отменено!", parse_mode=ParseMode.HTML)
        try:
            context.user_data["update"]
            await query.message.reply_text(text="Меню обновлено", reply_markup =  get_menu("admin_global").reply_markup, parse_mode=ParseMode.HTML)
            del context.user_data["update"]
        except Exception:
            pass


        return ConversationHandler.END


async def sum_level(update, context):
    cancel_reply_markup = InlineKeyboardMarkup(build_menu([InlineKeyboardButton('Отмена', callback_data='cancel')]))
    try:
        context.user_data['level_sum'] = int(update.message.text)
    except Exception as e:
        print(e)
        await update.message.reply_text(text="Укажите целое число", reply_markup=cancel_reply_markup,
                                        parse_mode=ParseMode.HTML)
        return 0

    await update.message.reply_text(text="Введите процент ", reply_markup=cancel_reply_markup,
                                    parse_mode=ParseMode.HTML)
    return 1


async def coeff_level(update, context):
    cancel_reply_markup = InlineKeyboardMarkup(build_menu([InlineKeyboardButton('Отмена', callback_data='cancel')]))
    try:
        coeff = int(update.message.text) / 100
    except Exception as e:
        print(e)
        await update.message.reply_text(text="Укажите целое число", reply_markup=cancel_reply_markup,
                                        parse_mode=ParseMode.HTML)
        return 1
    level = Loyalty_level.create(
        loyalty_coeff=coeff,
        sum=int(context.user_data['level_sum'])
    )
    level.save()

    await update.message.reply_text(text="Новый уровень создан", reply_markup=None, parse_mode=ParseMode.HTML)
    return ConversationHandler.END


async def edit_sum(update, context):
    cancel_reply_markup = InlineKeyboardMarkup(build_menu([InlineKeyboardButton('Отмена', callback_data='cancel')]))
    level = Loyalty_level.get(int(context.user_data['level_id']))
    try:
        level.sum = int(update.message.text)
    except Exception as e:
        print(e)
        await update.message.reply_text(text="Укажите целое число", reply_markup=cancel_reply_markup,
                                        parse_mode=ParseMode.HTML)
        return 2

    level.save()
    await update.message.reply_text(text="Данные изменены", parse_mode=ParseMode.HTML)
    return ConversationHandler.END


async def edit_coeff(update, context):
    cancel_reply_markup = InlineKeyboardMarkup(build_menu([InlineKeyboardButton('Отмена', callback_data='cancel')]))
    level = Loyalty_level.get(int(context.user_data['level_id']))

    try:
        level.loyalty_coeff = int(update.message.text) / 100
    except Exception as e:
        print(e)
        await update.message.reply_text(text="Укажите целое число", reply_markup=cancel_reply_markup,
                                        parse_mode=ParseMode.HTML)
        return 3

    level.save()
    await update.message.reply_text(text="Данные изменены", parse_mode=ParseMode.HTML)
    return ConversationHandler.END


@checkadmin
async def call_user_menu(update, context):
    text = "Выберите действие:"
    menu = get_menu("user_change_main")
    reply_markup = menu.reply_markup
    await update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)


async def change_user(update, context):
    cancel_reply_markup = InlineKeyboardMarkup(build_menu([InlineKeyboardButton('Отмена', callback_data='cancel')]))
    roles = {1: "Администратор", 2: "Пользователь"}
    levels = Loyalty_level.select()
    try:
        id = int(update.message.text)
        context.user_data['user_id'] = id
    except Exception as e:
        await update.message.reply_text("Укажите число", parse_mode=ParseMode.HTML, reply_markup=cancel_reply_markup)
        return 5
    try:
        user = User.get(card_id=id)
    except Exception as e:
        await update.message.reply_text("Пользователь с таким id не найден!\nВведите id:", parse_mode=ParseMode.HTML,
                                        reply_markup=InlineKeyboardMarkup(build_menu(
                                            [InlineKeyboardButton('Отмена', callback_data='cancel')], 1)))
        return 5

    message = (f"Пользователь: {id}\nUsername: {user.username}\nИмя: {user.name}\nРоль: {roles[user.role.id]}"
               f"\nБаллов лояльности: {user.loyalty_points}\nПотраченная сумма: {user.money_paid}"
               f"\nУровень лояльности: {user.loyalty_level_id}\nПроцент начисления баллов: {round(user.loyalty_level.loyalty_coeff * 100, 1)}%")
    header = [InlineKeyboardButton('✅ Добавить покупку', callback_data="users#change_user#extend_sum"),
              ]

    buttons = [
        InlineKeyboardButton('➕ Начислить баллы', callback_data="users#change_user#add_points"),
        InlineKeyboardButton('➖ Списать баллы', callback_data="users#change_user#remove_points"),
        InlineKeyboardButton("🤑 Списать все баллы", callback_data="users#change_user#remove_all_points"),
    ]
    footer = [
        InlineKeyboardButton('❌Оформить возврат', callback_data="users#change_user#reduce_sum"),
    ]

    menu = build_menu(buttons, 2, footer_buttons=footer, header_buttons=header)

    reply_markup = InlineKeyboardMarkup(menu)

    await update.message.reply_text(message, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    return ConversationHandler.END


async def delete_user(update, context):
    reply_markup = InlineKeyboardMarkup(build_menu(
        [InlineKeyboardButton('Отмена', callback_data='cancel'),
         InlineKeyboardButton('Удалить', callback_data='users#change_user#delete')], 2))
    try:
        id = int(update.message.text)
    except Exception as e:
        print(e)
        await update.message.reply_text("Укажите число")
        return 4
    try:
        user = User.get(card_id=id)
    except Exception as e:
        print(e)
        await update.message.reply_text("Пользователь с таким id не найден!\nВведите id:",
                                        reply_markup=InlineKeyboardMarkup(build_menu(
                                            [InlineKeyboardButton('Отмена', callback_data='cancel')], 1)))
        return 4
    context.user_data['user_id'] = id
    await update.message.reply_text("Пользователь найден.\nУдалить?", reply_markup=reply_markup)
    return ConversationHandler.END


async def extend_sum(update, context):
    try:
        sum = int(update.message.text)
    except Exception as e:
        await update.message.reply_text("Укажите число")
        return 6
    user = User.get(card_id=int(context.user_data['user_id']))
    user.money_paid = user.money_paid + sum
    level = Loyalty_level.get(user.loyalty_level_id)
    points = sum * level.loyalty_coeff
    user.loyalty_points = user.loyalty_points + points
    user_text = f"Вам начисленно<b> {points} балллов</b> за покупку!"
    await context.bot.send_message(chat_id=user.id, text=user_text, parse_mode=ParseMode.HTML)
    try:
        print(type(user.loyalty_level_id))
        level = Loyalty_level.get(user.loyalty_level_id + 1)
    except Exception as e:
        print(e)
    else:
        while (user.money_paid >= level.sum):
            user.loyalty_level_id = level
            try:
                level = Loyalty_level.get(user.loyalty_level_id + 1)
            except Exception as e:
                print(e)
                break
    user.save()
    await update.message.reply_text("Сумма покупок пользователя увеличена")
    return ConversationHandler.END


async def reduce_sum(update, context):
    try:
        sum = int(update.message.text)
    except Exception as e:
        await update.message.reply_text("Укажите число")
        return 7
    user = User.get(card_id=int(context.user_data['user_id']))
    try:
        money = user.money_paid - sum
        if money < 0:
            raise NegativeSumError
    except NegativeSumError:
        await update.message.reply_text("Вы ввели слишком большую сумму возврата!\nОперация отменена")
        return ConversationHandler.END
    else:
        user.money_paid = money

    level = Loyalty_level.get(user.loyalty_level_id)
    try:
        print(type(user.loyalty_level_id))
        level = Loyalty_level.get(user.loyalty_level_id - 1)
    except Exception as e:
        print(e)
    else:
        while (user.money_paid < Loyalty_level.get(user.loyalty_level_id).sum):
            user.loyalty_level_id = level
            try:
                level = Loyalty_level.get(user.loyalty_level_id - 1)
            except Exception as e:
                print(e)
                break
    user.save()
    await update.message.reply_text("Сумма покупок пользователя уменьшена")
    return ConversationHandler.END


async def add_points(update, context):
    try:
        points = int(update.message.text)
    except Exception as e:
        await update.message.reply_text("Укажите число!")
        return 8
    user_text = f"Вам начисленно <b>{points} балллов!</b>"

    user = User.get(card_id=context.user_data['user_id'])
    user.loyalty_points += points
    user.save()
    await context.bot.send_message(chat_id=user.id, text=user_text, parse_mode=ParseMode.HTML)
    await update.message.reply_text(f"Теперь у пользователя <b>{user.loyalty_points}</b> баллов",
                                    parse_mode=ParseMode.HTML)
    return ConversationHandler.END


async def remove_points(update, context):
    try:
        points = int(update.message.text)
    except Exception as e:
        await update.message.reply_text("Укажите число!")
        return 9

    user = User.get(card_id=context.user_data['user_id'])
    if points < user.loyalty_points:
        user.loyalty_points -= points
    else:
        await update.message.reply_text("Невозможно списать больше баллов, чем есть у пользователя\n Операция отменена")
        return ConversationHandler.END
    user.save()
    user_text = f"У вас списано <b>{points} балллов!</b>"
    await context.bot.send_message(chat_id=user.id, text=user_text, parse_mode=ParseMode.HTML)
    await update.message.reply_text(f"Теперь у пользователя <b>{user.loyalty_points}</b> баллов",
                                    parse_mode=ParseMode.HTML)
    return ConversationHandler.END


async def ban_user(update, context):
    try:
        id = int(update.message.text)
        context.user_data['user_id'] = id
    except Exception as e:
        await update.message.reply_text("Укажите число!")
        return 10
    try:
        user = User.get(card_id=id)
        ban_text = "Заблокировать" if user.status else "Разблокировать"
        reply_markup = InlineKeyboardMarkup(build_menu(
            [InlineKeyboardButton('Отмена', callback_data='cancel'),
             InlineKeyboardButton(ban_text, callback_data='users#change_user#ban')], 2))
    except Exception as e:
        await update.message.reply_text("Пользователь с таким id не найден!\nВведите id:",
                                        reply_markup=InlineKeyboardMarkup(build_menu(
                                            [InlineKeyboardButton('Отмена', callback_data='cancel')], 1)))
        return 10

    await update.message.reply_text(f"Пользователь найден. \n Заблокировать?", reply_markup=reply_markup)

    return ConversationHandler.END


async def cancel(update, context):
    await update.message.reply_text("Редактирование отменено")
    return ConversationHandler.END


@checkadmin
async def get_tracks_command(update, context):
    if (context.args):
        await get_tracks(update, context, context.args[0])
    else:
        await update.message.reply_text("Не введено имя артиста")


async def get_tracks(update, context, artist_name):
    service = YandexMusicService()
    try:
        tracks = service.get_tracks(artist_name)
        result = modify_result(tracks)

        menu = build_menu([
            InlineKeyboardButton("<", callback_data="artists#back")
        ], 1, )
        reply_markup = InlineKeyboardMarkup(menu)

        await update.message.reply_text(result, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    except Exception as e:
        await update.message.reply_text(e.__str__())


def modify_result(result):
    total = "total"
    title = "title"

    answ = ""
    for k in list(result.keys())[0:-1]:
        answ += f"<b><i>{k}</i></b>\n"
        releases = result[k]["releases"]
        print("temp = " + str(releases))
        if releases:
            for release in releases:
                tracks = " - сингл";
                if release['count'] > 1:
                    tracks = " - альбом" + "".join(["\n   - " + track for track in release['tracks']])
                answ += f"<b>{release[title]}</b>{tracks}\n"
            answ += f"<u><i>Всего: {result[k][total]}</i></u>\n\n"
        else:
            answ += f"Треки отсуствуют\n\n"
    answ += f"<u><i>Всего: {result[total]}</i></u>"

    return answ


async def get_artist_name(update, context):
    try:
        check_admin(update, context)
    except Exception as e:
        await update.message.reply_text(e.__str__())
        return ConversationHandler.END
    await update.message.reply_text("Введите имя артиста")


async def get_artist_name_tracks(update, context):
    await get_artist_name(update, context)
    return 11


async def get_artist_name_stats(update, context):
    await get_artist_name(update, context)
    return 12


async def get_tracks_conv(update, context):
    if update.message.text:
        await get_tracks(update, context, update.message.text)
    else:
        await update.message.reply_text("Вы не ввели имя артиста")
    return ConversationHandler.END


def check_admin(update, context):
    try:
        user = User.get(id=update.message.from_user.id)
    except Exception:
        raise RuntimeError("Вы не зарегистрированны в системе! ")
    print(f'User = {user}')
    if user.role == Role.get(1):
        if user.status:
            pass
        else:
            raise RuntimeError("Ваша учетная запись заблокирована!")
    else:
        raise RuntimeError("Неизвестное действие")


async def get_artist(update, artist_name):
    service = YandexMusicService()

    try:
        artists = service.get_artists(artist_name)

        buttons = []
        text = "Найдены артисты:\n"
        i = 1
        for artist in artists:
            text += str(i) + ". " + artist.get_uri() + "\n"
            buttons.append(InlineKeyboardButton(str(i) + ". " + artist.name,
                                                callback_data="artists#" + artist.name + "#" + str(artist.id)))
            i += 1

        menu = build_menu(buttons, 2, footer_buttons=[
            InlineKeyboardButton("Закончить", callback_data="cancel")
        ])
        reply_markup = InlineKeyboardMarkup(menu)

        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

    except Exception as e:
        await update.message.reply_text(e.__str__())


async def get_artist_query(query, artist_name):
    service = YandexMusicService()

    try:
        artists = service.get_artists(artist_name)

        buttons = []
        text = "Найдены артисты:\n"
        i = 1
        for artist in artists:
            text += str(i) + ". " + artist.get_uri() + "\n"
            buttons.append(InlineKeyboardButton(str(i) + ". " + artist.name,
                                                callback_data="artists#" + artist.name + "#" + str(artist.id)))
            i += 1

        menu = build_menu(buttons, 2, footer_buttons=[
            InlineKeyboardButton("Закончить", callback_data="cancel")
        ])
        reply_markup = InlineKeyboardMarkup(menu)

        await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

    except Exception as e:
        await query.edit_message_text(e.__str__())


async def get_artists_conv(update, context):
    if update.message.text:

        await get_artist(update, update.message.text)
    else:
        await update.message.reply_text("Вы не ввели имя артиста")
    return ConversationHandler.END


@checkadmin
async def get_artists_command(update, context):
    if context.args:
        await get_artist(update, context.args[0])
    else:
        await update.message.reply_text("Вы не ввели имя артиста")


async def get_statistics_main_menu(update, context):
    print(update.message.text)
    if "Завершить" in update.message.text:
        n = ConversationHandler.END
        text = "Завершено."
        reply_markup = get_menu("admin_global").reply_markup
    else:
        artist_name = update.message.text
        try:
            artist = ArtistModel.get(ArtistModel.name == artist_name)
            context.user_data["artist_id"] = artist.id
            reply_markup = get_menu('statistics').reply_markup
            text = "Выберите действие"
            n = 13
        except ArtistModel.DoesNotExist:
            reply_markup = InlineKeyboardMarkup(build_menu([
                InlineKeyboardButton("Да", callback_data="statistics#create#" + artist_name),
                InlineKeyboardButton("Нет", callback_data="statistics#create#cancel"),
            ], n_cols=2))

            text = "Артист не найден в базе.\nСоздать нового артиста?"
            n = 14

    await update.message.reply_text(text=text, reply_markup=reply_markup)
    return n


async def choose_statistics(update, context):
    print(update.message.text)

    try:
        if context.user_data["artist_id"]:
            artist_id = context.user_data["artist_id"]
            if "Посмотреть статистику" in update.message.text:
                await update.message.reply_text(get_statistics(int(artist_id)), parse_mode=ParseMode.HTML)
                return 13
            elif "Внести данные о статистике" in update.message.text:
                menu = build_menu([InlineKeyboardButton(year, callback_data="statistics#" + str(year)) for year in
                                   range(2020, datetime.now().year + 1)], n_cols=4)
                await update.message.reply_text(f"Выберите год", reply_markup=InlineKeyboardMarkup(menu))
            elif 'Другой артист' in update.message.text or "Статистика" in update.message.text:
                context.user_data["artist_id"] = None
                await update.message.reply_text(f"Введите имя артиста:")
                return 12
            else:
                context.user_data["artist_id"] = None
                await update.message.reply_text(text="Завершено", reply_markup=get_menu('admin_global').reply_markup)
                return ConversationHandler.END
    except KeyError:
        context.user_data["artist_id"] = None
        if update.message.text:
            if "Статистика" in update.message.text:
                await update.message.reply_text(f"Введите имя артиста:")
                return 12
            else:
                await update.message.reply_text(
                    "Работа со статистикой завершена. Повторите команду",
                    reply_markup=get_menu('admin_global').reply_markup, parse_mode=ParseMode.HTML)
                return ConversationHandler.END
        else:
            await update.message.reply_text("Работа со статистикой завершена. Повторите команду",
                                            reply_markup=get_menu('admin_global').reply_markup,
                                            parse_mode=ParseMode.HTML)
            return ConversationHandler.END


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


async def upload_statistics(update, context):
    context.user_data["document_type"] = "statistics"
    await update.message.reply_text("Пожалуйста, отправьте XLSX файл с данными")


async def process_document(update, context):
    if not context.user_data["document_type"]:
        await update.message.reply_text("Я не знаю что сделать с этим файлом!")
        return
    if context.user_data["document_type"] == "statistics":
        try:
            await update.message.reply_text("Подождите...")
            message = await process_statistics_document(update.message.document)
            await update.message.reply_text(message)
            context.user_data["document_type"] = None
        except Exception as e:
            await update.message.reply_text(e.__str__())


async def process_statistics_document(document):
    if not document.file_name.endswith(".xlsx"):
        raise RuntimeError("Пожалуйста, отправьте файл в формате XLSX.")
    file_path = os.path.join(UPLOAD_FOLDER, document.file_name)
    new_file = await document.get_file()
    await new_file.download_to_drive(file_path)
    return process(file_path)
