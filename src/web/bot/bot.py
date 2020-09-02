from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from functools import partial
import requests
import datetime
import json

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from src.web.bot.token import TELEGRAM_TOKEN
from src.web.bot.model import User, Base
from src.web.utils.aqi import pm25_to_aqius, aqi_level

API_HOST = 'http://93.115.20.79:8000'


def create_session():
    engine = create_engine('sqlite:///bot.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def get_concentration():
    start_date = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    end_date = datetime.datetime.utcnow()
    r = requests.get(API_HOST + '/sensor_data',
                     json={"end_time": end_date,
                           "start_time": start_date,
                           "columns": ['date', 'p1', 'p2']}
                     )
    data = json.loads(r.text)
    p1 = data[-1]['p1']
    p2 = data[-1]['p2']
    aqi = pm25_to_aqius(p1)
    levels = {
        'green': 'Good',
        'gold': 'Moderate',
        'orange': 'Unhealthy for Sensitive Groups',
        'red': 'Unhealthy',
        'purple': 'Very Unhealthy',
        'brown': 'Hazardous'}
    level = levels[aqi_level(aqi)]
    return f'PM2.5: {p1} PM10: {p2} AQIUS: {aqi} {level}'


def get_forecast():
    r = requests.get(API_HOST + '/forecast', json={})
    data = json.loads(r.text)
    s = ''
    for item in data:
        s += f''


def start(update, context):
    keyboard = [
        InlineKeyboardButton('Концентрация частиц сейчас', callback_data='now'),
        InlineKeyboardButton('Прогнроз концентрации частиц', callback_data='forecast'),
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


def button(update, context, session):
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    option = query.data

    if option == 'subscribe':
        user = User(id=update.message.from_user.id, chat_id=update.message.chat.id)
        session.add(user)
        session.commit()
        query.edit_message_text(text='Вы подписались на получение уведомлений.')
    if option == 'unsubscribe':
        session.query.filter(User.id == update.message.from_user.id).delete()
        session.commit()
        query.edit_message_text(text='Вы отписались от получения уведомлений.')
    if option == 'now':
        query.edit_message_text(text=get_concentration())


class Bot:

    def __init__(self):
        self.updater = Updater(TELEGRAM_TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(CommandHandler('start', start))
        session = create_session()
        self.dispatcher.add_handler(CallbackQueryHandler(partial(button, session=session)))

    def start(self):
        self.updater.start_polling()
