from telegram import Update,ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application,ContextTypes,ConversationHandler
from telegram.constants import ParseMode
from core import *
from models import *
from telegram import Update
from menu import get_menu

from config import ADMIN_ID

@checkuser
async def start(update,context):
    
    message = "welcom back"
    reply_markup = get_menu('main_simple').reply_markup
    await update.message.reply_text(message,parse_mode= ParseMode.HTML,reply_markup = reply_markup)


async def register(update,context):
    
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
            message = (( f"Добро пожаловать,<b>{user.name}</b>\n"
                        f"<i>Вам начисленно </i><b>{user.loyalty_points} приветственных баллов</b>"
                        f"<i>\nСумма заказов:  </i><b>{user.money_paid} руб.</b>"
                        f"<i>\nУ вас  </i><b>{loyalty.id}</b><i>  уровень лояльности \n</i>"
                        f"<i>Коэффициент начисления баллов:  </i><b>{round(loyalty.loyalty_coeff*100,1)}%</b>\n"
                        f"<i>Ваш ID:</i>  <code>{user.card_id}</code>\n")
                       +how_much(user.loyalty_level.id,user.money_paid))
            
    else:
        message = "Вы уже зарегистрированны!"


    await update.message.reply_text(message, parse_mode=ParseMode.HTML,reply_markup =  get_menu('main_simple').reply_markup)

@checkuser
async def help_me(update,context):
    message =  (("Вас приветствует <b>PhantomTrackBot</b>!\n\n<i>Здесь вы можете принять участие в программе лояльности PhantomTrack.\n"
                "За покупки вам будут</i> <b>начисляться баллы</b>, "
                "<i>которыми можно будет оплачивать последующие заказы.\n<b>1 балл = 1 рубль.</b>\n\n"
                "В боте вы сможете ознакомиться с </i><b>условиями проведения программы лояльности</b><i> и</i> <b>количеством баллов</b>, "
                "<i>которые имеются на вашем аккаунте.</i>\n\n")+write_loyalty()+(
                "<b>\nСписок доступных команд:</b>\n"
                "    ⧫<code>/register</code> - Зарегистрироваться в системе\n"
                "    ⧫<code>/profile</code> - Посмотреть свой профиль\n\n"
                "<b>Или воспользуйтесь кнопками меню</b>\n"
                ))
    help_menu = get_menu('help').reply_markup
    await update.message.reply_text(message, parse_mode=ParseMode.HTML,reply_markup=help_menu)

@checkuser
async def call_maxim(update,context):
    help_menu = get_menu('call').reply_markup
    await update.message.reply_text('Телеграмм менеджера',parse_mode=ParseMode.HTML, reply_markup=help_menu)

@checkuser
async def get_profile(update,context):
    
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
            f"<i>Коэффициент начисления баллов:  </i><b>{round(loyalty.loyalty_coeff * 100,1)}%</b>\n"
            f"<i>Ваш ID:  </i><code>{user.card_id}</code>\n")
            +how_much(user.loyalty_level.id,user.money_paid)
            +"\n<i>Привязанные артисты:  </i>" +names)
        
        
        await update.message.reply_text(message, parse_mode=ParseMode.HTML,reply_markup= get_menu("user_artists").reply_markup)



async def user(update, context):
    user = User.get(update.effective_user.id)
    user.role = 2
    user.save()
    menu = get_menu('main')
    reply_markup = menu.reply_markup
    await update.message.reply_text("Просмотр от лица пользователя", parse_mode=ParseMode.HTML, reply_markup=reply_markup)


@checkuser
async def cancel(update, context):
    
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text("Смена имени отменена")
    
    return ConversationHandler.END

async def unknown_text(update,context):
    await update.message.reply_text("Неизвестное действие! Проверьте, что вы не допустили ошибку!")

async def get_user_agreement(update, context):
    try:
        artist = ArtistModel.get(name = update.message.text)
    except Exception:
        await update.message.reply_text("Такого артиста пока нет в нашей базе")
        return ConversationHandler.END
    context.user_data["new_artist_name"] = update.message.text
    await update.message.reply_text("Введите номер договора в формате <code>X-XXX</code>",reply_markup=cancel_reply_markup, parse_mode=ParseMode.HTML)
    return 19
async def send_message_to_admin(update,context):
    artist = ArtistModel()
    try:
        artist = ArtistModel.get(name = context.user_data["new_artist_name"] , agreement = update.message.text)
        context.user_data["new_artist_agreement"] = update.message.text
        print(context.user_data)
        await update.message.reply_text(
            "Сообщение о вашей регистрации отправилено администратору, ждите, пока он подтвердит вашу личность")
        context.user_data.clear()
        artist.linked_user = update.effective_user.id
        artist.save()

    except Exception as e:
        print(e)
        await update.message.reply_text("Проверьте, что правильно указали номер договора и попробуйте еще раз",reply_markup=cancel_reply_markup)
        return 19
    user = artist.linked_user
    message = f"Пользователь {user.username} хочет привязать артиста {artist.name}"
    reply_markup = InlineKeyboardMarkup(build_menu([InlineKeyboardButton("Разрешить", callback_data=f"permite#{user.id}#{artist.id}"), InlineKeyboardButton("Запретить", callback_data=f"forbide#{user.id}#{artist.id}")], n_cols=2))
    await context.bot.send_message(chat_id=ADMIN_ID, text=message, reply_markup = reply_markup)
    return ConversationHandler.END




# async def start_change_name(update,context):
#     if not(is_user_exist(update.effective_user.id)):
#         await update.message.reply_text("Сначала зарегистрируйтесь!")
#         return ConversationHandler.END
#     await update.message.reply_text("Как к вам обращаться?")
#     print(0)
#     print(update.message.text)
#     return 1
#
# async def change_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     try:
#         user = User.get(id=update.effective_user.id)
#     except Exception as e:
#         print(e)
#         message = "Сервис сейчас не доступен, попробуйте позже"
#     else:
#         new_name = update.message.text
#         if new_name == "":
#             message = "Имя не может быть пустым"
#         else:
#             user.name = new_name
#             user.save()
#             message = f"Имя успешно изменено на {new_name}"
#     await update.message.reply_text(message, parse_mode=ParseMode.HTML)
#
#     return ConversationHandler.END
