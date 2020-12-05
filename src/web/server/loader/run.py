from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time
import schedule
import logging.config

from src.web.server.common.model import Base
from src.web.server.loader.config import sensor_time_interval
from src.web.logger.logging_config import LOGGING_CONFIG
from src.web.server.loader.application.tasks import sensor_task, weather_task, mosecom_task
from src.web.config import DATABASE

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('LoaderLogger')


if __name__ == '__main__':
    time.sleep(5)  # wait postgres image loading
    engine = create_engine(DATABASE)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    sess = Session()
    schedule.every(sensor_time_interval).minutes.do(sensor_task, session=sess, logger=logger, metrics=True)
    schedule.every().hour.at(":30").do(weather_task, session=sess, logger=logger, metrics=True)
    schedule.every().hour.at(":16").do(mosecom_task, logger=logger, metrics=True)
    logger.info('%s', 'loader started')

    while True:
        schedule.run_pending()
        time.sleep(1)
