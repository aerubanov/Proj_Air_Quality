from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time
import schedule
import logging.config

from src.web.models.model import Base, Sensors, Weather, LoaderLog
from src.web.loader.config import sensor_time_interval, weather_time_interval
from src.web.loader.logging_config import LOGGING_CONFIG
from src.web.loader.tasks import sensor_task, weather_task

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('LoaderLogger')


def print_db(session):
    result = session.query(LoaderLog)
    result = result.order_by('date')
    for i in result:
        print(f'{i.date} | {i.level} | {i.name} | {i.message}', flush=True)


if __name__ == '__main__':
    time.sleep(5)  # wait postgres image loading
    engine = create_engine('postgresql://postgres:postgres@PostgreSQL/pgdb')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    sess = Session()
    schedule.every(sensor_time_interval).minutes.do(sensor_task, session=sess, logger=logger)
    schedule.every(weather_time_interval).minutes.do(weather_task, session=sess, logger=logger)
    # schedule.every(0.1).minutes.do(print_db, session=sess)
    logger.info('%s', 'loader started')

    while True:
        schedule.run_pending()
        time.sleep(1)
