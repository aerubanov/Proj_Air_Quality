import time
import datetime
from marshmallow import ValidationError

from src.web.loader.sensor_loading import load_sensors
from src.web.loader.weather_loading import parse_weather
from src.web.models.model import Sensors, Weather
from src.web.loader.validation import SensorSchema

sensor_schema = SensorSchema()


def sensor_task(session, logger=None):
    """request sensor api data and save in database"""

    # getting data
    start_time = time.time()
    avg_data = load_sensors()
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
    row = Sensors(date=datetime.datetime.now(), p1=avg_data['p1'], p2=avg_data['p2'], temperature=avg_data['temp'],
                  humidity=avg_data['hum'], pressure=avg_data['press'])
    session.add(row)
    session.commit()
    resp_time = (time.time() - start_time) * 1000  # time in milliseconds
    if logger is not None:
        logger.info('%s %s', 'sensor data saved in database', f'timing: {resp_time}')


def weather_task(session, logger=None):
    """download weather forecast and save in database"""
    # get data
    start_time = time.time()
    data = parse_weather()
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
