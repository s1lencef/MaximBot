from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from admin_commands import *

conv_sys_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(btn_handler)],
    states={
        0: [MessageHandler(filters.TEXT & ~filters.COMMAND, sum_level)],
        1: [MessageHandler(filters.TEXT & ~filters.COMMAND, coeff_level)],
        2: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_sum)],
        3: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_coeff)],
        4: [MessageHandler(filters.Regex("\d") & ~filters.COMMAND, delete_user)],
        5: [MessageHandler(filters.Regex("\d") & ~filters.COMMAND, change_user)],
        6: [MessageHandler(filters.TEXT & ~filters.COMMAND, extend_sum)],
        7: [MessageHandler(filters.TEXT & ~filters.COMMAND, reduce_sum)],
        8: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_points)],
        9: [MessageHandler(filters.TEXT & ~filters.COMMAND, remove_points)],
        10: [MessageHandler(filters.Regex("\d") & ~filters.COMMAND, ban_user)],
    },
    fallbacks=[CommandHandler("cancel", cancel), CallbackQueryHandler(btn_handler)],
)
conv_tracks_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(btn_handler), MessageHandler(filters.Regex("Поиск треков"), get_artist_name)],
    states={
        1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_artists_conv)]
    },
    fallbacks=[CommandHandler("cancel", cancel), CallbackQueryHandler(btn_handler)],
)

conv_statistics_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(btn_handler), MessageHandler(filters.Regex("Статистика"), get_artist_name)],
    states={
        1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_statistics_main_menu)],
        2: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_statistics)],
        3: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_statistics)]
    },
    fallbacks=[CommandHandler("cancel", cancel), CallbackQueryHandler(btn_handler)]

)
