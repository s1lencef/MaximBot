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

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from user_commands import *
from admin_commands import *
from config import token
from conversation import *

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

TZ = timezone("Europe/Moscow")


def update_year():
    artists = ArtistModel.select()
    for artist in artists:
        for i in range(1, 5):
            statistics = Statistics(artist_id=artist.id, year=datetime.now().year, quarter=i, state=0)
            statistics.save()


def schedule():
    scheduler = BackgroundScheduler(timezone=TZ)  # Указываем временную зону
    scheduler.add_job(update_year, CronTrigger(month=1, day=1, hour=0, minute=0, timezone=TZ))
    scheduler.start()


def create_uploads_folder():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def main():
    create_uploads_folder()
    schedule()
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(MessageHandler(filters.Regex("Начать работу"), register))
    app.add_handler(CommandHandler("help", help_me))
    app.add_handler(MessageHandler(filters.Regex("Помощь"), help_me))
    app.add_handler(CommandHandler("profile", get_profile))
    app.add_handler(MessageHandler(filters.Regex("Профиль"), get_profile))
    app.add_handler(MessageHandler(filters.Regex("Связаться с менеджером"), call_maxim))
    app.add_handler(conv_sys_handler)

    app.add_handler(CommandHandler("admin", reg_admin))
    app.add_handler(CommandHandler("user", user))
    app.add_handler(MessageHandler(filters.Regex("Настроить данные приложения"), change_loyalty))
    app.add_handler(MessageHandler(filters.Regex("Управлять пользователями"), call_user_menu))
    app.add_handler(CallbackQueryHandler(reduce_sum))
    app.add_handler(MessageHandler(filters.Regex("Настроить данные приложения"), change_loyalty))
    app.add_handler(CommandHandler("get_tracks", get_tracks_command))
    app.add_handler(CommandHandler("get_artist", get_artists_command))
    app.add_handler(CommandHandler("upload_statistics", upload_statistics))
    app.add_handler(MessageHandler(filters.Document.ALL, process_document))
    app.add_handler(MessageHandler(filters.TEXT, unknown_text))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    logger.info("text")
    main()
