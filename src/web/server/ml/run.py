from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import schedule
import time
import logging.config

from src.web.server.ml.application.forecast import perform_forecast
from src.web.server.ml.application.anomaly import perform_anomaly_detection
from src.web.server.common.model import Base
from src.web.server.logging_config import LOGGING_CONFIG
from src.web.server import config

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('MLLogger')

if __name__ == '__main__':
    engine = create_engine(config.dbstring)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    sess = Session()
    schedule.every(20).minutes.do(perform_forecast, session=sess, logger=logger)
    schedule.every().hour.at(":02").do(perform_anomaly_detection, session=sess, logger=logger)
    logger.info("ml started")
    while True:
        schedule.run_pending()
        time.sleep(1)
