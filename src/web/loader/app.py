from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time
import schedule
import logging.config

from src.web.models.model import Base
from src.web.loader.config import sensor_time_interval, weather_time_interval
from src.web.logger.logging_config import LOGGING_CONFIG
from src.web.loader.tasks import sensor_task, weather_task, mosecom_task, traffic_task
from src.web.config import DATABASE

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('LoaderLogger')


if __name__ == '__main__':
    time.sleep(5)  # wait postgres image loading
    engine = create_engine(DATABASE)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    sess = Session()
    schedule.every(sensor_time_interval).minutes.do(sensor_task, session=sess, logger=logger)
    schedule.every(weather_time_interval).minutes.do(weather_task, session=sess, logger=logger)
    schedule.every().hour.at(":16").do(mosecom_task, logger=logger)
    # schedule.every().hour.at(":01").do(traffic_task, logger=logger)
    logger.info('%s', 'loader started')

    while True:
        schedule.run_pending()
        time.sleep(1)
