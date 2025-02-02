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
from user_commands import *
from button_handler import btn_handler

conv_sys_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(btn_handler),
                  MessageHandler(filters.Regex("Поиск треков"), get_artist_name_tracks),
                  MessageHandler(filters.Regex("Статистика"), get_artist_name_stats),
                  MessageHandler(filters.Regex("Добавить артиста"), get_artist_name_create),
                  ],
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

        11: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_artists_conv)],

        12: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_statistics_main_menu)],
        13: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_statistics)],

        14: [CallbackQueryHandler(btn_handler)],

        15: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_agreement_create)],
        16: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_agreement_file_create)],
        17: [MessageHandler(filters.Document.ALL, process_document_conv)],

        18: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_user_agreement)],
        19: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_message_to_admin)]
    },
    fallbacks=[CommandHandler("cancel", cancel), CallbackQueryHandler(btn_handler)],
)


