"""
    Telegram event handlers
"""
import sys
import logging
from typing import Dict

import telegram.error
from telegram import Bot, Update, BotCommand
from telegram.ext import (
    Updater, Dispatcher, Filters,
    CommandHandler, MessageHandler,
    CallbackQueryHandler,
)

from dtb.celery import app  # event processing in async mode
from dtb.settings import TELEGRAM_TOKEN, DEBUG

from tgbot.handlers.utils import files, error

from tgbot.handlers.admin import handlers as admin_handlers
from tgbot.handlers.onboarding import handlers as onboarding_handlers
from tgbot.handlers.broadcast_message import handlers as broadcast_handlers
from tgbot.handlers.contract import handlers as contract_handlers
from tgbot.handlers.personal_data import handlers_edit_pd as pd_edit_handlers
from tgbot.handlers.personal_data import handlers_init_pd as pd_init_handlers

from tgbot.handlers.admin import manage_data as admin_manage_data
from tgbot.handlers.personal_data.manage_data import BASE_FOR_PD_MENU
from tgbot.handlers.onboarding.manage_data import SECRET_LEVEL_BUTTON

from tgbot.handlers.broadcast_message.manage_data import \
    CONFIRM_DECLINE_BROADCAST
from tgbot.handlers.broadcast_message.static_text import broadcast_command


def setup_dispatcher(dp):
    """
    Adding handlers for events from Telegram
    """
    # onboarding
    dp.add_handler(CommandHandler("start", onboarding_handlers.command_start))

    # admin commands
    dp.add_handler(CommandHandler("admin", admin_handlers.admin_start))
    dp.add_handler(CommandHandler("stats", admin_handlers.stats))
    dp.add_handler(
        CallbackQueryHandler(admin_handlers.admin_menu_handler,
                             pattern=f'^{admin_manage_data.BASE_ADMIN_MENU}')
    )
    dp.add_handler(
        CallbackQueryHandler(
            admin_handlers.admin_commands_handler,
            pattern=f'^{admin_manage_data.BASE_ADMIN_COMMANDS}'))

    # dp.add_handler(CommandHandler('export_users', admin_handlers.export_users))

    # contract
    dp.add_handler(contract_handlers.get_conversation_handler_for_contract())

    # personal data
    dp.add_handler(CommandHandler(
        'personal_data',
        pd_edit_handlers.get_my_personal_data_handler))
    dp.add_handler(CallbackQueryHandler(
        pd_edit_handlers.main_menu_edit_pd_handler,
        pattern=f"^{BASE_FOR_PD_MENU}"))
    dp.add_handler(pd_edit_handlers.get_pd_edit_conversation_handler())
    dp.add_handler(pd_init_handlers.get_conversation_handler_for_init_pd())

    # secret level
    dp.add_handler(CallbackQueryHandler(onboarding_handlers.secret_level,
                                        pattern=f"^{SECRET_LEVEL_BUTTON}"))

    # broadcast message
    dp.add_handler(
        MessageHandler(Filters.regex(rf'^{broadcast_command}(/s)?.*'),
                       broadcast_handlers.broadcast_command_with_message)
    )
    dp.add_handler(
        CallbackQueryHandler(broadcast_handlers.broadcast_decision_handler,
                             pattern=f"^{CONFIRM_DECLINE_BROADCAST}")
    )

    # files
    dp.add_handler(MessageHandler(
        Filters.animation, files.show_file_id,
    ))

    # Unknown messages
    dp.add_handler(
        MessageHandler(Filters.all, onboarding_handlers.answer_to_unknown)
    )

    # handling errors
    dp.add_error_handler(error.send_stacktrace_to_tg_chat)

    # EXAMPLES FOR HANDLERS
    # dp.add_handler(CallbackQueryHandler(<function_handler>, pattern="^r\d+_\d+"))
    # dp.add_handler(MessageHandler(
    #     Filters.chat(chat_id=int(TELEGRAM_FILESTORAGE_ID)),
    #     # & Filters.forwarded & (Filters.photo | Filters.video | Filters.animation),
    #     <function_handler>,
    # ))

    return dp


def run_pooling():
    """ Run bot in pooling mode """
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp = setup_dispatcher(dp)

    bot_info = Bot(TELEGRAM_TOKEN).get_me()
    bot_link = f"https://t.me/" + bot_info["username"]

    print(f"Pooling of '{bot_link}' started")
    # it is really useful to send '👋' emoji to developer
    # when you run local test
    # bot.send_message(text='👋', chat_id=<YOUR TELEGRAM ID>)

    updater.start_polling()
    updater.idle()


# Global variable - best way I found to init Telegram bot
bot = Bot(TELEGRAM_TOKEN)
try:
    TELEGRAM_BOT_USERNAME = bot.get_me()["username"]
except telegram.error.Unauthorized:
    logging.error(f"Invalid TELEGRAM_TOKEN.")
    sys.exit(1)


@app.task(ignore_result=True)
def process_telegram_event(update_json):
    update = Update.de_json(update_json, bot)
    dispatcher.process_update(update)


def set_up_commands(bot_instance: Bot) -> None:
    langs_with_commands: Dict[str, Dict[str, str]] = {
        'en': {
            'contract': 'All about contract 📝',
            'personal_data': 'My personal data 🗂',
            'cancel': 'Cancel the current operation ❌',
            'admin': 'Show admin info ℹ️',
            'broadcast': 'Broadcast message 📨',
            # 'export_users': 'Export users.csv 👥',
        },
        'ru': {
            'contract': 'Договор 📝',
            'personal_data': 'Мои данные 🗂',
            'cancel': 'Отменить текущее действие ❌',
            'admin': 'Показать информацию для админов ℹ️',
            'broadcast': 'Отправить сообщение 📨',
            # 'export_users': 'Экспорт users.csv 👥',
        }
    }

    bot_instance.delete_my_commands()
    for language_code in langs_with_commands:
        bot_instance.set_my_commands(
            language_code=language_code,
            commands=[
                BotCommand(command, description) for command, description in
                langs_with_commands[language_code].items()
            ]
        )


# WARNING: it's better to comment the line below in DEBUG mode.
# Likely, you'll get a flood limit control error, when restarting bot too often
set_up_commands(bot)

n_workers = 0 if DEBUG else 4
dispatcher = setup_dispatcher(
    Dispatcher(bot, update_queue=None, workers=n_workers, use_context=True))
