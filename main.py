import logging

import pytz

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from conversation import *

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

TZ = pytz.timezone("Europe/Moscow")  # Это уже правильно


def update_year():
    artists = ArtistModel.select()
    current_year = datetime.now(TZ).year  # Используйте TZ для получения текущего года
    for artist in artists:
        for i in range(1, 5):
            statistics = Statistics(artist_id=artist.id, year=current_year, quarter=i, state=0)
            statistics.save()


# def schedule():
#     scheduler = BackgroundScheduler(timezone=TZ)  # Указываем временную зону явно
#     cron_trigger = CronTrigger(month=1, day=1, hour=0, minute=0, timezone=TZ)
#     scheduler.add_job(update_year, cron_trigger)
#     scheduler.start()


def create_uploads_folder():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def main():
    create_uploads_folder()
    # schedule()
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(MessageHandler(filters.Regex(r"Начать работу"), register))
    app.add_handler(CommandHandler("help", help_me))
    app.add_handler(MessageHandler(filters.Regex(r"Помощь"), help_me))
    app.add_handler(CommandHandler("profile", get_profile))
    app.add_handler(MessageHandler(filters.Regex(r"Профиль"), get_profile))
    app.add_handler(MessageHandler(filters.Regex(r"Связаться с менеджером"), call_maxim))
    app.add_handler(CommandHandler("manager", call_maxim))
    app.add_handler(CommandHandler("agreement", get_user_agreement))
    app.add_handler(CommandHandler("statistics", get_user_statistics))
    app.add_handler(CommandHandler("add_artist", get_artist_name_user_create))
    app.add_handler(conv_sys_handler)
    app.add_handler(CommandHandler("admin", reg_admin))
    app.add_handler(CommandHandler("user", user))
    app.add_handler(MessageHandler(filters.Regex(r"Настроить данные приложения"), change_loyalty))
    app.add_handler(MessageHandler(filters.Regex(r"Управлять пользователями"), call_user_menu))
    app.add_handler(CallbackQueryHandler(reduce_sum))
    app.add_handler(MessageHandler(filters.Regex(r"Работа с артистами"), get_artist_menu))
    app.add_handler(MessageHandler(filters.Regex(r"Назад"), get_main_menu))
    app.add_handler(MessageHandler(filters.Regex(r"Список артистов"), get_artists_list))
    app.add_handler(CommandHandler("get_tracks", get_tracks_command))
    app.add_handler(CommandHandler("get_artist", get_artists_command))
    app.add_handler(CommandHandler("upload_statistics", upload_statistics))
    app.add_handler(MessageHandler(filters.Document.ALL, process_document))
    app.add_handler(MessageHandler(filters.TEXT, unknown_text))

    app.run_polling()


if __name__ == "__main__":
    logger.info("text")
    main()
