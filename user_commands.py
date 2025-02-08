import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from core import *
from models import *
from telegram import Update
from menu import get_menu

from config import ADMIN_ID


@checkuser
async def start(update, context):
    message = "welcom back"
    reply_markup = get_menu('main_simple').reply_markup
    context.user_data["reply_markup"] = "main_simple"
    await update.message.reply_text(message, parse_mode=ParseMode.HTML, reply_markup=reply_markup)


async def register(update, context):
    if not is_user_exist(id=update.effective_user.id):

        if update.effective_user.username:

            username = update.effective_user.username
        else:
            username = 'none'

        user = User.create(
            id=update.effective_user.id,
            name=update.effective_user.first_name,
            username=username,
            role=2,
            status=True,
            card_id=generate_unique_id(update.effective_user.id % 10000),
            loyalty_points=30,
            money_paid=0,
            loyalty_level=1
        )

        user.save()

        try:
            loyalty = Loyalty_level.get(id=user.loyalty_level)

        except Exception as e:
            print(e)
            message = "Сервис сейчас не доступен, попробуйте позже"

        else:
            message = ((f"Добро пожаловать,<b>{user.name}</b>\n"
                        f"<i>Вам начисленно </i><b>{user.loyalty_points} приветственных баллов</b>"
                        f"<i>\nСумма заказов:  </i><b>{user.money_paid} руб.</b>"
                        f"<i>\nУ вас  </i><b>{loyalty.id}</b><i>  уровень лояльности \n</i>"
                        f"<i>Коэффициент начисления баллов:  </i><b>{round(loyalty.loyalty_coeff * 100, 1)}%</b>\n"
                        f"<i>Ваш ID:</i>  <code>{user.card_id}</code>\n")
                       + how_much(user.loyalty_level.id, user.money_paid))

    else:
        message = "Вы уже зарегистрированны!"
    context.user_data["reply_markup"] = "main_simple"
    await update.message.reply_text(message, parse_mode=ParseMode.HTML,
                                    reply_markup=get_menu('main_simple').reply_markup)


@checkuser
async def help_me(update, context):
    help_menu = get_menu('help').reply_markup
    await update.message.reply_text(help_message, parse_mode=ParseMode.HTML, reply_markup=help_menu)


@checkuser
async def call_maxim(update, context):
    help_menu = get_menu('call').reply_markup

    await update.message.reply_text('Телеграмм менеджера', parse_mode=ParseMode.HTML, reply_markup=help_menu)


@checkuser
async def get_profile(update, context):
    user = User.get(id=update.effective_user.id)

    try:
        loyalty = Loyalty_level.get(id=user.loyalty_level)

    except Exception as e:
        print(e)
        message = "Сервис сейчас не доступен, попробуйте позже"

    else:
        artists = ArtistModel.select().where(ArtistModel.linked_user == user, ArtistModel.is_user_approved == True)
        names = [artist.name for artist in artists]
        names = ", ".join(names) if names else "Нет привязанных артистов"

        message = ((
                       f"Добро пожаловать,<b>{user.name}</b>\n<i>Ваш баланс:  </i><b>{user.loyalty_points} баллов</b>"
                       f"<i>\nСумма заказов:  </i><b>{user.money_paid} руб.</b>"
                       f"<i>\nУ вас </i> <b>{loyalty.id}</b> <i> уровень лояльности \n</i>"
                       f"<i>Коэффициент начисления баллов:  </i><b>{round(loyalty.loyalty_coeff * 100, 1)}%</b>\n"
                       f"<i>Ваш ID:  </i><code>{user.card_id}</code>\n")
                   + how_much(user.loyalty_level.id, user.money_paid)
                   + "\n<i>Привязанные артисты:  </i>" + names)

        await update.message.reply_text(message, parse_mode=ParseMode.HTML,
                                        reply_markup=get_menu("user_artists").reply_markup)


async def user(update, context):
    user = User.get(update.effective_user.id)
    user.role = 2
    user.save()
    menu = get_menu('main_simple')
    reply_markup = menu.reply_markup
    context.user_data["reply_markup"] = "main_simple"
    await update.message.reply_text("Просмотр от лица пользователя", parse_mode=ParseMode.HTML,
                                    reply_markup=reply_markup)


@checkuser
async def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)

    try:
        reply_markup = get_menu(context.user_data["reply_markup"]).reply_markup
    except Exception:
        reply_markup = None

    await update.message.reply_text("Смена имени отменена", reply_markup=reply_markup)

    return ConversationHandler.END


async def unknown_text(update, context):
    await update.message.reply_text("Неизвестное действие! Проверьте, что вы не допустили ошибку!")


async def get_user_agreement(update, context):
    try:
        artist = ArtistModel.get(name=update.message.text)
    except Exception:
        await update.message.reply_text("Такого артиста пока нет в нашей базе")
        return ConversationHandler.END
    context.user_data["new_artist_name"] = update.message.text

    await update.message.reply_text("Введите номер договора в формате <code>X-XXX</code>",
                                    reply_markup=cancel_reply_markup, parse_mode=ParseMode.HTML)
    return 19


async def send_message_to_admin(update, context):
    artist = ArtistModel()
    try:
        artist = ArtistModel.get(name=context.user_data["new_artist_name"], agreement=update.message.text)
        context.user_data["new_artist_agreement"] = update.message.text
        print(context.user_data)
        context.user_data.clear()
        artist.linked_user = update.effective_user.id
        artist.save()
    except Exception as e:
        print(e)
        await update.message.reply_text("Проверьте, что правильно указали номер договора и попробуйте еще раз",
                                        reply_markup=cancel_reply_markup)
        return 19

    await update.message.reply_text(
        "Заявка на привязку артиста отправлена на согласование администратору.")
    user1 = artist.linked_user
    message = f"Пользователь {user1.username} хочет привязать артиста {artist.name}"
    reply_markup = InlineKeyboardMarkup(build_menu(
        [InlineKeyboardButton("Разрешить", callback_data=f"permite#{user1.id}#{artist.id}"),
         InlineKeyboardButton("Запретить", callback_data=f"forbide#{user1.id}#{artist.id}")], n_cols=2))
    await context.bot.send_message(chat_id=ADMIN_ID, text=message, reply_markup=reply_markup)
    return ConversationHandler.END


async def get_artist_name_user_create(update, context):
    await update("Введите ник артиста:", reply_markup=cancel_reply_markup)
    return 18


async def get_user_statistics(update, context):
    if context.args:
        if context.args[0]:

            artist_name = context.args[0]
            if len(context.args) > 1:
                artist_name = " ".join(context.args)
            try:
                artist = ArtistModel.get(name=artist_name)
            except Exception:
                await update.message.reply_text("Такой артист не найден")
                return ConversationHandler.END

            if artist.linked_user.id == update.effective_user.id and artist.is_user_approved:
                pass
            else:
                await update.message.reply_text("Этот артист не привязан к вашем аккаунту")
                return ConversationHandler.END

            await update.message.reply_text("Подождите...")
            await update.message.reply_text(get_statistics(artist.id), parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text("Вы не ввели ник артиста")
    else:
        await update.message.reply_text("Вы не ввели ник артиста")

    return ConversationHandler.END


async def get_user_agreement(update, context):
    if context.args:
        if context.args[0]:
            artist_name = context.args[0]
            if len(context.args)>1:
                artist_name = " ".join(context.args)

            print(artist_name)
            try:
                artist = ArtistModel.get(name=artist_name)
            except Exception :
                await update.message.reply_text("Такой артист не найден")
                return ConversationHandler.END

            if artist.linked_user and artist.linked_user.id == update.effective_user.id and artist.is_user_approved:
                pass
            else:
                await update.message.reply_text("Этот артист не привязан к вашему аккаунту")
                return ConversationHandler.END

            await update.message.reply_text("Загружаем документ, подождите ...(это может занять до 30 секунд)")
            file_path = artist.agreement_path
            if not os.path.exists(file_path):
                await update.message.reply_text("Файл не найден.")
                return ConversationHandler.END
            await update.message.reply_document(document=open(file_path, "rb"),
                                                filename=f"Договор {artist.agreement} {artist.name}.pdf")
        else:
            await update.message.reply_text("Вы не ввели ник артиста")
    else:
        await update.message.reply_text("Вы не ввели ник артиста")

