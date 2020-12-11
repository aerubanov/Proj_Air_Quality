import time
import datetime
from marshmallow import ValidationError
import graphyte

from src.web.server.loader.application.sensor_loading import load_sensors
from src.web.server.loader.application.weather_loading import parse_weather
from src.web.server.common.model import Sensors, Weather
from src.web.server.loader.application.validation import SensorSchema, WeatherSchema
from src.web.server.loader.application.mosecom_loading import load_data, write_processed, write_raw_data
from src.web import config

sensor_schema = SensorSchema()
weather_schema = WeatherSchema()
graphyte.init(config.metrichost, prefix='loader')


def sensor_task(session, logger=None, metrics=False):
    """request sensor api data and save in database"""

    # getting data
    start_time = time.time()
    avg_data, loaded = load_sensors()
    resp_time = (time.time() - start_time) * 1000  # time in milliseconds
    try:
        avg_data = sensor_schema.load(avg_data)
    except ValidationError as e:
        if logger is not None:
            logger.info(str(e))
        return

    if logger is not None:
        logger.info('%s %s', 'sensors api request', f'timing: {resp_time}')

    # write in database
    start_time = time.time()
    row = Sensors(date=datetime.datetime.utcnow(), p1=avg_data['p1'], p2=avg_data['p2'], temperature=avg_data['temp'],
                  humidity=avg_data['hum'], pressure=avg_data['press'])
    session.add(row)
    session.commit()
    resp_time = (time.time() - start_time) * 1000  # time in milliseconds
    if logger is not None:
        logger.info('%s %s', 'sensor data saved in database', f'timing: {resp_time}')
    if metrics:
        graphyte.send('sensors', loaded)


def weather_task(session, logger=None, metrics=False):
    """download weather forecast and save in database"""
    # get data
    start_time = time.time()
    data = parse_weather()
    try:
        data = weather_schema.load(data)
    except ValidationError as e:
        if logger is not None:
            logger.info(str(e))
        return
    resp_time = (time.time() - start_time) * 1000  # time in milliseconds
    if logger is not None:
        logger.info('%s %s', 'weather forecast request', f'timing: {resp_time}')

    # write in database
    start_time = time.time()
    for i in range(len(data['date'])):
        row = session.query(Weather).filter(Weather.date == data['date'][i]).first()
        if row is None:
            row = Weather(date=data['date'][i], temp=data['temp'][i], press=data['pressure'][i], prec=data['prec'][i],
                          wind_speed=data['wind_speed'][i], wind_dir=data['wind_dir'][i], hum=data['humidity'][i])
            session.add(row)
            session.commit()
        else:
            row.temp = data['temp'][i]
            row.press = data['pressure'][i]
            row.prec = data['prec'][i]
            row.wind_speed = data['wind_speed'][i]
            row.wind_dir = data['wind_dir'][i]
            row.hum = data['humidity'][i]
            session.commit()
    resp_time = (time.time() - start_time) * 1000  # time in milliseconds
    if logger is not None:
        logger.info('%s %s', 'weather data saved in database', f'timing: {resp_time}')
    if metrics:
        graphyte.send('weather', len(data['date']))


def mosecom_task(logger=None, metrics=False):
    p1_data, p2_data = load_data()
    write_raw_data(p1_data, 'P1')
    write_raw_data(p2_data, 'P2')
    write_processed(p1_data, p2_data)
    if logger is not None:
        logger.info('%s', 'write mosecom data in file')
    if metrics:
        graphyte.send('mosecom', len(p1_data))
