from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from src.web.bot.token import TELEGRAM_TOKEN
from src.web.bot.model import User, Base


def create_session():
    engine = create_engine('sqlite:///bot.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


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


def button(update, context):
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    option = query.data

    if option == 'subscribe':
        user = User(id=update.message.from_user.id, chat_id=)

class Bot:

    def __init__(self):
        self.updater = Updater(TELEGRAM_TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(CommandHandler('start', start))

    def start(self):
        self.updater.start_polling()
