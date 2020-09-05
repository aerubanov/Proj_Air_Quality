from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from functools import partial
import requests
import datetime
import json

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from src.web.bot.token import TELEGRAM_TOKEN
from src.web.bot.model import User, Base
from src.web.utils.aqi import pm25_to_aqius, aqi_level

API_HOST = 'http://93.115.20.79:8000'
MSK_TIMEZONE = datetime.timezone(datetime.timedelta(hours=3))
aqi_levels = {
            'green': 'Good',
            'gold': 'Moderate',
            'orange': 'Unhealthy for Sensitive Groups',
            'red': 'Unhealthy',
            'purple': 'Very Unhealthy',
            'brown': 'Hazardous'}


def create_session():
    engine = create_engine('sqlite:///database/botbot.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def get_concentration():
    start_date = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    end_date = datetime.datetime.utcnow()
    r = requests.get(API_HOST + '/sensor_data',
                     json={"end_time": end_date.isoformat('T'),
                           "start_time": start_date.isoformat('T'),
                           "columns": ['date', 'p1', 'p2']}
                     )
    data = json.loads(r.text)
    p1 = data[-1]['p1']
    p2 = data[-1]['p2']
    aqi = pm25_to_aqius(p1)
    level = aqi_levels[aqi_level(aqi)]
    return f'PM2.5: {p1:.2f} PM10: {p2:.2f} AQIUS: {aqi:.2f} {level}'


def get_forecast():
    r = requests.get(API_HOST + '/forecast', json={})
    data = json.loads(r.text)
    s = 'Время   PM2.5   PM10   AQIUS \n'
    for item in data:
        s += f''
        date = datetime.datetime.fromisoformat(item['date']) + \
               datetime.timedelta(hours=item['forward_time'])
        date = date.replace(tzinfo=datetime.timezone.utc).astimezone(tz=MSK_TIMEZONE)
        p1 = item['p1']
        p2 = item['p2']
        aqi = pm25_to_aqius(p1)
        level = aqi_levels[aqi_level(aqi)]
        s += f'{date.time().strftime("%H:%M")}  {p1:.2f}  {p2:.2f}  {aqi:.2f}  {level} \n'
    return s


def keyboard():
    kb = [
        [InlineKeyboardButton('Концентрация частиц сейчас', callback_data='now'),
         InlineKeyboardButton('Прогноз концентрации частиц', callback_data='forecast')],
        [InlineKeyboardButton('Подписаться', callback_data='subscribe'),
         InlineKeyboardButton('Отписаться', callback_data='unsubscribe'),
         ],
    ]
    reply_markup = InlineKeyboardMarkup(kb)
    return reply_markup


def start(update: Update, context):
    update.message.reply_text(
        'Чтобы получать уведомления об измении концентрации'
        ' частиц в воздухе, подпишитесь на бота',
        reply_markup=keyboard(),
    )


def button(update: Update, context, session):
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    option = query.data

    if option == 'subscribe':
        if session.query(User).filter(User.id == query.from_user.id).scalar() is not None:
            query.edit_message_text(text='Вы уже подписаны.', reply_markup=keyboard())
            return
        user = User(id=query.from_user.id, chat_id=query.message.chat.id)
        session.add(user)
        session.commit()
        query.edit_message_text(text='Вы подписались на получение уведомлений.', reply_markup=keyboard())
    if option == 'unsubscribe':
        if session.query(User).filter(User.id == query.from_user.id).scalar() is None:
            query.edit_message_text(text='Вы не подписаны.', reply_markup=keyboard())
            return
        session.query(User).filter(User.id == query.from_user.id).delete()
        session.commit()
        query.edit_message_text(text='Вы отписались от получения уведомлений.', reply_markup=keyboard())
    if option == 'now':
        query.edit_message_text(text=get_concentration(), reply_markup=keyboard())
    if option == 'forecast':
        query.edit_message_text(text=get_forecast(), reply_markup=keyboard())


class Bot:

    def __init__(self):
        self.updater = Updater(TELEGRAM_TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(CommandHandler('start', start))
        session = create_session()
        self.dispatcher.add_handler(CallbackQueryHandler(partial(button, session=session)))

    def start(self):
        self.updater.start_polling()
        self.updater.idle()


if __name__ == '__main__':
    Bot().start()
