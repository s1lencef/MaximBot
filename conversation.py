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


conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(btn_handler), MessageHandler(filters.Regex("Поиск треков"), get_artist_name)],
    states={
        0: [MessageHandler(filters.TEXT & ~filters.COMMAND,sum_level)],
        1: [MessageHandler(filters.TEXT & ~filters.COMMAND,coeff_level)],
        2: [MessageHandler(filters.TEXT & ~filters.COMMAND,edit_sum)],
        3: [MessageHandler(filters.TEXT & ~filters.COMMAND,edit_coeff)],
        4:  [MessageHandler(filters.Regex("\d")& ~filters.COMMAND,delete_user)],
        5:  [MessageHandler(filters.Regex("\d")& ~filters.COMMAND,change_user)],
        6:  [MessageHandler(filters.TEXT & ~filters.COMMAND,extend_sum)],
        7:  [MessageHandler(filters.TEXT & ~filters.COMMAND,reduce_sum)],
        8:[MessageHandler(filters.TEXT & ~filters.COMMAND,add_points)],
        9:[MessageHandler(filters.TEXT & ~filters.COMMAND,remove_points)],
        10:[MessageHandler(filters.Regex("\d")& ~filters.COMMAND,ban_user)],
        11:[MessageHandler(filters.TEXT & ~filters.COMMAND,get_tracks_conv)]
    },
    fallbacks=[CommandHandler("cancel", cancel),CallbackQueryHandler(btn_handler)],
)