from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from functools import partial
import requests
import datetime
import json
import schedule
import time
import graphyte
from appmetrics import metrics, reporter
import logging.config
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

try:
    from src.web.bot.token import TELEGRAM_TOKEN
except ModuleNotFoundError:
    pass
from src.web.bot.model import User, Base
from src.web.utils.aqi import pm25_to_aqius, aqi_level
from src.web.bot.level_tracker import ConcentrationTracker, AnomaliesTracker, ForecastTracker
from src.web.bot.config import API_HOST, ANOMALY_LOOK_UP_INTERVAL, FORECAST_LOOK_UP_INTERVAL
from src.web.config import metrics_host
from src.web.utils.metrics_reporter import GraphyteReporter
from src.web.logger.logging_config import LOGGING_CONFIG

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
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    return Session


graphyte.init(metrics_host, prefix='bot')
graphite_reporter = GraphyteReporter(graphyte)
reporter.register(graphite_reporter, reporter.fixed_interval_scheduler(5 * 60))  # send metrics every 5 minutes
user_counter = metrics.new_counter('bot_users')


@metrics.with_meter('concentration')
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


@metrics.with_meter('forecast')
def get_forecast():
    r = requests.get(API_HOST + '/forecast', json={})
    data = json.loads(r.text)
    s = 'Время   PM2.5   PM10   AQIUS \n'
    for item in data:
        s += f''
        date = datetime.datetime.fromisoformat(item['date']) + datetime.timedelta(hours=item['forward_time'])
        date = date.replace(tzinfo=datetime.timezone.utc).astimezone(tz=MSK_TIMEZONE)
        p1 = item['p1']
        p2 = item['p2']
        aqi = pm25_to_aqius(p1)
        level = aqi_levels[aqi_level(aqi)]
        s += f'{date.time().strftime("%H:%M")}  {p1:.2f}  {p2:.2f}  {aqi:.2f}  {level} \n'
    return s


def get_anomaly(date: datetime.datetime):
    start_date = date - datetime.timedelta(hours=ANOMALY_LOOK_UP_INTERVAL)
    r = requests.get(API_HOST + '/anomaly',
                     json={"end_time": date.isoformat('T'),
                           "start_time": start_date.isoformat('T'),
                           }
                     )
    data = json.loads(r.text)
    if data:
        cluster = data[0]['cluster']
        text = {0: "Аномалия со снижением концентрации частиц или сохранием невысокого уровня",
                1: "Повышение концентрации частиц из-за ухудшения условий рассеивания",
                2: "Повышение значений концентрации частиц при повышенной влажности"}[cluster]
        return text
    return ''


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


def button(update: Update, context, sess, with_metrics=False, logger=None):
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    option = query.data

    session = sess()
    if option == 'subscribe':
        if session.query(User).filter(User.id == query.from_user.id).scalar() is not None:
            query.edit_message_text(text='Вы уже подписаны.', reply_markup=keyboard())
            return
        user = User(id=query.from_user.id, chat_id=query.message.chat.id)
        session.add(user)
        session.commit()
        query.edit_message_text(text='Вы подписались на получение уведомлений.', reply_markup=keyboard())
        if with_metrics:
            user_counter.notify(1)
        if logger is not None:
            logger.info(f'subscribe button - user_id: {query.from_user.id} - chat_id: {query.message.chat.id}')
    if option == 'unsubscribe':
        if session.query(User).filter(User.id == query.from_user.id).scalar() is None:
            query.edit_message_text(text='Вы не подписаны.', reply_markup=keyboard())
            return
        session.query(User).filter(User.id == query.from_user.id).delete()
        session.commit()
        query.edit_message_text(text='Вы отписались от получения уведомлений.', reply_markup=keyboard())
        if with_metrics:
            user_counter.notify(-1)
        if logger is not None:
            logger.info(f'unsubscribe button - user_id: {query.from_user.id} - chat_id: {query.message.chat.id}')
    if option == 'now':
        query.edit_message_text(text=get_concentration() + ' ' + get_anomaly(datetime.datetime.utcnow()),
                                reply_markup=keyboard())
    if option == 'forecast':
        query.edit_message_text(text=get_forecast(), reply_markup=keyboard())


@metrics.with_meter('notification')
def level_tracker_callback(sess, bot, logger=None, **kwargs):
    session = sess()
    event_type = kwargs['event_type']
    message = ''
    if event_type == 'concentration':
        message = f"Измение концентрации частиц до уровня AQI US '{aqi_levels[kwargs['aqi_level']]}'."
    if event_type == 'anomalies':
        msq = f"Обнаружена аномалия: "
        cluster_msg = {
            0: "снижение или сохранение невысокого уровня концентрации частиц.",
            1: "повышение концентрации частиц из-за ухудшения условий рассеивания.",
            2: "повышение концентрации частиц при повышении влажности.",
        }[kwargs['cluster']]
        message = msq + cluster_msg
    if event_type == 'forecast':
        message = f"В течении {FORECAST_LOOK_UP_INTERVAL} ожидается измение концентрации частиц до" \
                  f" уровня AQI US: '{aqi_levels[kwargs['aqi_level']]}'."

    users = session.query(User).all()
    for user in users:
        bot.send_message(chat_id=user.chat_id, text=message)
    if logger is not None:
        logger.info(f'notification: {message}')


class ConcentrationBot:

    def __init__(self):
        logging.config.dictConfig(LOGGING_CONFIG)
        logger = logging.getLogger()

        self.updater = Updater(TELEGRAM_TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(CommandHandler('start', start))
        session = create_session()
        self.dispatcher.add_handler(CallbackQueryHandler(partial(button, sess=session, logger=logger)))

        bot = Bot(token=TELEGRAM_TOKEN)
        callback = partial(level_tracker_callback, sess=session, bot=bot, logger=logger)
        concentration_tracker = ConcentrationTracker(callback)
        anomalies_tracker = AnomaliesTracker(callback)
        forecast_tracker = ForecastTracker(callback)

        schedule.every(20).minutes.do(concentration_tracker.check)
        schedule.every().hour.at(':10').do(forecast_tracker.check)
        schedule.every().hour.at(':15').do(anomalies_tracker.check)

        sess = session()
        num_user = len(sess.query(User).all())
        user_counter.notify(num_user)

    def start(self):
        self.updater.start_polling()
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == '__main__':
    ConcentrationBot().start()
