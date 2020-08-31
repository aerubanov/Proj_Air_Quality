from sqlalchemy import create_engine

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from src.web.bot.token import TELEGRAM_TOKEN


def start(update, context):
    keyboard = [
        [InlineKeyboardButton('Подписаться', callback_data='subscribe'),
         InlineKeyboardButton('Отписаться', callback_data='unsubscribe'),
         ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.massege.reply_text(
        'Чтобы получать уведомления об измении концентрации'
        ' частиц в воздухе, подпишитесь на бота',
        reply_markup=reply_markup,
    )


class Bot:

    def __init__(self):
        self.updater = Updater(TELEGRAM_TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(CommandHandler('start', start))

    def start(self):
        self.updater.start_polling()
