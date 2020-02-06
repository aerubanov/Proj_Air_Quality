from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time
import schedule
import datetime
import logging.config

from src.web.models.model import Base, Sensors, Weather
from src.web.loader.sensor_loading import read_sensor_id, load_data, average_data
from src.web.loader.config import sensor_file, sensor_time_interval, weather_time_interval
from src.web.loader.weather_loading import parse_weather
from src.web.loader.logging_config import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('LoaderLogger')


def sensor_task(session):
    """request sensor api data and save in database"""
    start_time = time.time()
    sensor_id = read_sensor_id(sensor_file)
    data = load_data(sensor_id)
    avg_data = average_data(data)
    resp_time = (time.time() - start_time) * 1000  # time in milliseconds
    logger.info('%s %s', 'sensors api request', f'timing: {resp_time}')
    start_time = time.time()
    row = Sensors(date=datetime.datetime.now(), p1=avg_data['p1'], p2=avg_data['p1'], temperature=avg_data['temp'],
                  humidity=avg_data['hum'], pressure=avg_data['press'])
    session.add(row)
    session.commit()
    resp_time = (time.time() - start_time) * 1000  # time in milliseconds
    logger.info('%s %s', 'sensor data saved in database', f'timing: {resp_time}')


def weather_task(session):
    """download weather forecast and save in database"""
    start_time = time.time()
    data = parse_weather()
    resp_time = (time.time() - start_time) * 1000  # time in milliseconds
    logger.info('%s %s', 'weather forecast request', f'timing: {resp_time}')
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
    logger.info('%s %s', 'weather data saved in database', f'timing: {resp_time}')


def print_db(session):
    result = session.query(Weather)
    result = result.order_by('date')
    for i in result:
        print(f'{i.date} | {i.temp} | {i.press} | {i.prec} | {i.wind_speed} | {i.wind_dir} | {i.hum}', flush=True)


if __name__ == '__main__':
    time.sleep(5)  # wait postgres image loading
    engine = create_engine('postgresql://postgres:postgres@PostgreSQL/pgdb')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    sess = Session()
    schedule.every(sensor_time_interval).minutes.do(sensor_task, session=sess)
    schedule.every(weather_time_interval).minutes.do(weather_task, session=sess)
    # schedule.every(0.2).minutes.do(print_db, session=sess)
    logger.info('%s', 'loader started')

    while True:
        schedule.run_pending()
        time.sleep(1)
