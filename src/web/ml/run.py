from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import schedule
import time
import logging.config

from src.web.ml.forecast import perform_forecast
from src.web.ml.anomaly import perform_anomaly_detection
from src.web.models.model import Base
from src.web.logger.logging_config import LOGGING_CONFIG
from src.web.config import DATABASE

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('MLLogger')

if __name__ == '__main__':
    engine = create_engine(DATABASE)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    sess = Session()
    schedule.every().hour.at(":01").do(perform_forecast, session=sess, logger=logger)
    schedule.every().minute.at(":02").do(perform_anomaly_detection, session=sess, logger=logger)
    logger.info("ml started")
    while True:
        schedule.run_pending()
        time.sleep(1)
