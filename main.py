#!/usr/bin/python3.8
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,

    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from user_commands import *
from admin_commands import *
from config import token
from conversation import conv_handler


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def main():

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(MessageHandler(filters.Regex("Начать работу"), register))
    app.add_handler(CommandHandler("help", help_me))
    app.add_handler(MessageHandler(filters.Regex("Помощь"), help_me))
    app.add_handler(CommandHandler("profile", get_profile))
    app.add_handler(MessageHandler(filters.Regex("Профиль"), get_profile))
    app.add_handler(MessageHandler(filters.Regex("Связаться с менеджером"), call_maxim))
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("admin", reg_admin))
    app.add_handler(CommandHandler("user", user))
    app.add_handler(MessageHandler(filters.Regex("Настроить данные приложения"), change_loyalty))
    app.add_handler(MessageHandler(filters.Regex("Управлять пользователями"), call_user_menu))
    app.add_handler(CallbackQueryHandler(reduce_sum))
    app.add_handler(MessageHandler(filters.Regex("Настроить данные приложения"), change_loyalty))
    app.add_handler(CommandHandler("get_tracks", get_tracks_command))
    app.add_handler(MessageHandler(filters.TEXT,unknown_text))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    logger.info("text")
    main()