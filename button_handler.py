from black import nullcontext
from pyexpat.errors import messages
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, ConversationHandler
from telegram.constants import ParseMode
import os
import user_commands
from admin_commands import modify_result, get_artist_query, save_artist
from core import *
from models import *
from config import *
from menu import *
from core import checkadmin
from yandex_music_service import *
from prettytable import PrettyTable, ALL
from excel_parser import process


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
                    text += f"    {user.username} - <code>{user.card_id}</code>/<code>{user.username}</code>\n"
                await query.edit_message_text(text=text, parse_mode=ParseMode.HTML, reply_markup=cancel_reply_markup)
                return 5
    elif args[0] == "artists":
        if args[2] == "back":
            await get_artist_query(query, args[1])
            return ConversationHandler.END
        else:
            if args[1] == "statistics":
                if args[2] == "True":
                    await query.edit_message_text("Отправьте документ в формате .XLSX",
                                                  reply_markup=cancel_reply_markup)
                    context.user_data["document_type"] = "statistics"
                    return 17
                else:
                    await query.edit_message_text(await save_artist(context))
                    try:
                        print(context.user_data["reply_markup"])
                        fill_statistics(context.user_data["artist_name"])
                        await query.message.reply_text("Меню обновлено", reply_markup=get_menu(
                            context.user_data["reply_markup"]).reply_markup)
                    except Exception as e:
                        print(e)

                    context.user_data.clear()
                    return ConversationHandler.END
            elif args[1] == "asigne":
                if args[2] == "True":
                    await query.edit_message_text("Введите id пользователя или username в телеграм", )
                    return 20
                elif args[2] == "False":
                    context.user_data["asigned_user"] = None
                    await query.edit_message_text("Хотите отправить данные о статистике?",
                                                  reply_markup=get_menu("create_statistics").reply_markup)
                    return 14
                else:
                    context.user_data["asigned_user"] = args[2]
                    await query.edit_message_text("Хотите отправить данные о статистике?",
                                                  reply_markup=get_menu("create_statistics").reply_markup)
                    return 14
            elif args[1] == "change_year":
                if args[2] == "True":
                    menu = build_menu(
                        [InlineKeyboardButton(str(year), callback_data=f"artists#change_year#{year}") for
                         year in
                         range(2020, datetime.now().year + 1)],
                        footer_buttons=[InlineKeyboardButton('Отмена', callback_data='cancel')],
                        n_cols=4)
                    await query.edit_message_text("Укажите год начала отсчета статистики", reply_markup=InlineKeyboardMarkup(menu))
                    return 14
                elif args[2] == "False":
                    context.user_data["year"] = None
                    await query.edit_message_text("Хотите привязать пользователя телеграм?",
                                                  reply_markup=get_menu("asigne_artist").reply_markup)
                    return 14
                else:
                    print("chnage_year")
                    context.user_data["year"] = args[2]
                    await query.edit_message_text("Хотите привязать пользователя телеграм?",
                                                  reply_markup=get_menu("asigne_artist").reply_markup)
                    return 14

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
            if args[1] == "change_year":
                try:
                    artist = ArtistModel.get(id=int(args[2]))
                except Exception:
                    await query.edit_message_text(f"Чета сломалась")
                    return ConversationHandler.END
                artist.start_year = int(args[3])
                artist.save()
                await query.edit_message_text(f"Год обновлен")
            else:
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
                    await query.edit_message_text("Подождите...")
                    context.user_data["artist_id"] = None
                    await query.edit_message_text(
                        "Создание отменено.\n Введите имя артиста повторно", reply_markup=cancel_reply_markup,
                        parse_mode=ParseMode.HTML)

                    context.user_data["update"] = 2
                    return 12
                else:
                    await query.edit_message_text("Подождите...")
                    context.user_data["return_statistics"] = True
                    context.user_data["artist_name"] = args[2]
                    await query.message.reply_text("Введите номер договора с артистом в формате <code>Х-ХХХ</code>",
                                                   parse_mode=ParseMode.HTML)
                    return 16
            elif args[1] == "change_year":
                menu = build_menu(
                    [InlineKeyboardButton(str(year), callback_data=f"statistics#change_year#{args[2]}#{year}") for year
                     in
                     range(2020, datetime.now().year + 1)],
                    footer_buttons=[InlineKeyboardButton('Отмена', callback_data='cancel')],
                    n_cols=4)
                await query.edit_message_text(f"Выберите стартовый год", reply_markup=InlineKeyboardMarkup(menu))
            else:
                buttons = [InlineKeyboardButton(states_names[i], callback_data=query.data + "#" + str(i)) for i in
                           range(0, 3)]
                print(query.data)
                menu = build_menu(buttons, n_cols=3,
                                  footer_buttons=[InlineKeyboardButton("Назад", callback_data=args[0] + "#" + args[1]),
                                                  InlineKeyboardButton('Отмена', callback_data='cancel')])

                await query.edit_message_text(text="Статус квартала", parse_mode=ParseMode.HTML,
                                              reply_markup=InlineKeyboardMarkup(menu))
                return 14

        elif len(args) == 2:
            buttons = [InlineKeyboardButton(f"Квартал {i}", callback_data=query.data + "#" + str(i)) for i in
                       range(1, 5)]
            menu = build_menu(buttons, n_cols=4, footer_buttons=[InlineKeyboardButton("Назад", callback_data=args[0]),
                                                                 InlineKeyboardButton('Отмена',
                                                                                      callback_data='cancel')])
            await query.edit_message_text(text="Выберите квартал", parse_mode=ParseMode.HTML,
                                          reply_markup=InlineKeyboardMarkup(menu))
            return 14
        else:
            try:
                artist = ArtistModel.get(id=int(context.user_data["artist_id"]))
                start_year = artist.start_year
            except Exception as e:
                print(e)
                start_year = 2020
            menu = build_menu([InlineKeyboardButton(str(year), callback_data="statistics#" + str(year)) for year in
                               range(start_year, datetime.now().year + 1)],
                              footer_buttons=[InlineKeyboardButton('Отмена', callback_data='cancel')], n_cols=4)
            await query.edit_message_text(f"Выберите год", reply_markup=InlineKeyboardMarkup(menu))

            return 14

    elif args[0] == "user":
        if len(args) == 2:
            if args[1] == "get_agreement" or args[1] == "get_statistics":
                artists = ArtistModel.select().where(ArtistModel.linked_user == update.effective_user.id,
                                                     ArtistModel.is_user_approved == True)
                buttons = [InlineKeyboardButton(artist.name, callback_data=query.data + "#" + str(artist.id)) for artist
                           in artists]
                if len(buttons) == 0:
                    await query.edit_message_text("У вас пока нет связанных артистов!", reply_markup=None)
                    return ConversationHandler.END
                await query.edit_message_text("Выберите артиста", reply_markup=InlineKeyboardMarkup(
                    build_menu(buttons, n_cols=2,
                               footer_buttons=[InlineKeyboardButton('Отмена', callback_data='cancel')])))
            else:
                await query.edit_message_text("Введите ник артиста:", reply_markup=cancel_reply_markup)
                return 18
        if len(args) == 3:

            if args[1] == "get_agreement":
                artist = ArtistModel.get(int(args[2]))
                await query.edit_message_text("Загружаем документ, подождите ...(это может занять до 30 секунд)")
                file_path = artist.agreement_path
                if not os.path.exists(file_path):
                    await query.message.reply_text("Файл не найден.")
                    return ConversationHandler.END
                await query.message.reply_document(document=open(file_path, "rb"),
                                                   filename=f"Договор {artist.agreement} {artist.name}.pdf")
            elif args[1] == "get_statistics":
                await query.edit_message_text("Подождите...")
                await query.edit_message_text(get_statistics(int(args[2])), parse_mode=ParseMode.HTML)
                return ConversationHandler.END
            elif args[1] == "help":
                if args[2] == "back":
                    help_menu = get_menu('help').reply_markup
                    await query.edit_message_text(help_message, parse_mode=ParseMode.HTML, reply_markup=help_menu)
                elif args[2] == "loyalty":
                    help_menu = get_menu('help_back').reply_markup
                    await query.edit_message_text(help_lolyalty_message, parse_mode=ParseMode.HTML,
                                                  reply_markup=help_menu)
                elif args[2] == "statistics":
                    help_menu = get_menu('help_back').reply_markup
                    await query.edit_message_text(help_statistics_message, parse_mode=ParseMode.HTML,
                                                  reply_markup=help_menu)
    elif args[0] == "permite":
        artist = ArtistModel.get(id=int(args[2]))
        artist.is_user_approved = True
        artist.save()
        await query.edit_message_text("Артист добавлен")
        await context.bot.send_message(chat_id=int(args[1]), text=f"Артист {artist.name} добавлен")
        return ConversationHandler.END
    elif args[0] == "forbide":
        artist = ArtistModel.get(id=int(args[2]))
        artist.linked_user = None
        artist.is_user_approved = False
        artist.save()
        await query.edit_message_text("Отказано")
        await context.bot.send_message(chat_id=int(args[1]),
                                       text=f"К сожалению вам отказано в добавлении артиста {artist.name}\nДля подробностей свяжитесь с менеджером")
        return ConversationHandler.END
    elif args[0] == "cancel":
        artist = None
        try:
            artist = context.user_data["artist_id"]
        except Exception:
            pass
        context.user_data["artist_id"] = None
        await query.edit_message_text(text="Действие отменено!", parse_mode=ParseMode.HTML)
        n = ConversationHandler.END
        try:
            context.user_data["update"]
            await query.message.reply_text(text="Меню обновлено", reply_markup=get_menu("admin_global").reply_markup,
                                           parse_mode=ParseMode.HTML)
            context.user_data["reply_markup"] = "admin_global"
            del context.user_data["update"]

        except Exception:
            try:
                reply_markup = get_menu(context.user_data["reply_markup"]).reply_markup
                if context.user_data["reply_markup"] == "statistics":
                    if artist:
                        context.user_data["artist_id"] = artist
                        n = 13
                    else:
                        reply_markup = get_menu("admin_global").reply_markup
                        n = ConversationHandler.END
            except Exception:
                reply_markup = None

            await update.callback_query.message.reply_text("Меню обновлено", reply_markup=reply_markup)

        return n


def build_users_list():
    buttons = [InlineKeyboardButton(user.name, callback_data="artists#asigne#" + str(user.id)) for user in
               User.select()]
    return InlineKeyboardMarkup(
        build_menu(buttons, n_cols=2, footer_buttons=[InlineKeyboardButton('Отмена', callback_data='cancel')]))
