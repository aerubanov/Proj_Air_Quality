import datetime

from telegram import InlineKeyboardMarkup, Update, Message, Chat, CallbackQuery, User

from src.web.bot.application.bot import get_concentration, get_forecast, get_anomaly, keyboard, \
    API_HOST, start, button, level_tracker_callback
from src.web.bot.application.config import FORECAST_LOOK_UP_INTERVAL
from src.web.bot.application.model import User as DbUser
from tests.web.data.api_test_data import sensor_data, forec_data, anomaly_data


def test_get_concentration(requests_mock):
    requests_mock.get(API_HOST + '/sensor_data', text=sensor_data)
    answer = get_concentration()
    assert answer.split()[1] == '11.23'
    assert answer.split()[3] == '5.42'
    assert answer.split()[5] == '46.80'
    assert answer.split()[6] == 'Good'


def test_get_forecast(requests_mock):
    requests_mock.get(API_HOST + '/forecast', text=forec_data)
    answer = get_forecast()
    assert len(answer.splitlines()) == 25


def test_get_anomaly(requests_mock):
    requests_mock.get(API_HOST + '/anomaly', text=anomaly_data)
    answer = get_anomaly(date=datetime.datetime(2020, 4, 7, 5))
    assert answer == "Повышение значений концентрации частиц при повышенной влажности"


def test_keyboard():
    kb = keyboard()
    assert isinstance(kb, InlineKeyboardMarkup)
    assert len(kb.inline_keyboard) == 2
    assert len(kb.inline_keyboard[0]) == 2
    assert len(kb.inline_keyboard[1]) == 2


class MyBot:
    def __init__(self):
        self.response = None
        self.markup = None
        self.defaults = None

    def send_message(self, chat_id, text, parse_mode=None, disable_web_page_preview=None,
                     disable_notification=False, reply_to_message_id=None,
                     reply_markup=None, timeout=None, **kwargs):
        self.response = text
        self.markup = reply_markup

    def answer_callback_query(self, callback_query_id, text=None, show_alert=False, url=None, cache_time=None,
                              timeout=None, **kwargs):
        pass

    def edit_message_text(self, text, chat_id=None, message_id=None, inline_message_id=None,
                          parse_mode=None, disable_web_page_preview=None, reply_markup=None,
                          timeout=None, **kwargs):
        self.response = text
        self.markup = reply_markup


def create_update(text: str, bot: MyBot, query=None):
    user = User(id=1, first_name='Anatoly', is_bot=False)
    message = Message(message_id=1, from_user=user, date=datetime.datetime.utcnow(),
                      text=text, chat=Chat(id=1, type='chat'), bot=bot)

    if query is not None:
        cb = CallbackQuery(id='1', from_user=user, chat_instance='chat', data=query, bot=bot, message=message)
    else:
        cb = None
    update = Update(update_id=1, message=message, callback_query=cb)
    return update


def test_start():
    bot = MyBot()
    update = create_update('/start', bot)
    start(update, context=None)
    assert bot.response == 'Чтобы получать уведомления об измении концентрации частиц в воздухе, подпишитесь на бота'
    assert isinstance(bot.markup, InlineKeyboardMarkup)


def test_button_now(bot_db_session, monkeypatch):
    bot = MyBot()
    update = create_update('now', bot, query='now')
    monkeypatch.setattr('src.web.bot.application.bot.get_concentration', lambda: 'sensor_values')
    monkeypatch.setattr('src.web.bot.application.bot.get_anomaly', lambda x: 'anomalies text')
    button(update, None, bot_db_session)
    assert bot.response == 'sensor_values' + ' ' + 'anomalies text'


def test_button_forecast(bot_db_session, monkeypatch):
    bot = MyBot()
    update = create_update('forecast', bot, query='forecast')
    monkeypatch.setattr('src.web.bot.application.bot.get_forecast', lambda: 'forecast_values')
    button(update, None, bot_db_session)
    assert bot.response == 'forecast_values'


def test_button_subscribe(bot_db_session, monkeypatch):
    bot = MyBot()
    update = create_update('subscribe', bot, query='subscribe')
    button(update, None, bot_db_session)
    assert bot.response == 'Вы подписались на получение уведомлений.'


def test_button_subscribe_exist(bot_db_session, monkeypatch):
    bot = MyBot()
    update = create_update('subscribe', bot, query='subscribe')
    user = DbUser(id=1, chat_id=1)
    bot_db_session.add(user)
    bot_db_session.commit()
    button(update, None, bot_db_session)
    assert bot.response == 'Вы уже подписаны.'


def test_button_unsubscribe(bot_db_session, monkeypatch):
    bot = MyBot()
    update = create_update('unsubscribe', bot, query='unsubscribe')
    user = DbUser(id=1, chat_id=1)
    bot_db_session.add(user)
    bot_db_session.commit()
    button(update, None, bot_db_session)
    assert bot.response == 'Вы отписались от получения уведомлений.'


def test_button_unsubscribe_not_exist(bot_db_session, monkeypatch):
    bot = MyBot()
    update = create_update('unsubscribe', bot, query='unsubscribe')

    button(update, None, bot_db_session)
    assert bot.response == 'Вы не подписаны.'


def test_level_tracker_callback(bot_db_session):
    class Bot:

        def __init__(self):
            self.chat_id = None
            self.text = ''

        def send_message(self, chat_id, text):
            self.text = text
            self.chat_id = chat_id

    bot = Bot()
    user = DbUser(id=1, chat_id=2)
    sess = bot_db_session()
    sess.add(user)
    sess.commit()

    level_tracker_callback(bot_db_session, bot, event_type='concentration', aqi_level='Good')
    assert bot.text == "Измение концентрации частиц до уровня AQI US 'Good'."
    assert bot.chat_id == 2

    level_tracker_callback(bot_db_session, bot, event_type='forecast', aqi_level='Good')
    assert bot.text == f"В течении {FORECAST_LOOK_UP_INTERVAL} часов ожидается измение концентрации частиц до" \
                       f" уровня AQI US: 'Good'."

    level_tracker_callback(bot_db_session, bot, event_type='anomalies', cluster=0)
    assert bot.text == "Обнаружена аномалия: снижение или сохранение невысокого уровня концентрации частиц."
