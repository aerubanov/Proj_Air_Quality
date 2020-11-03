import logging.config

from flask import g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.web.logger.logging_config import LOGGING_CONFIG
from src.web.models.model import Base


def get_logger():
    if 'log' not in g:
        logging.config.dictConfig(LOGGING_CONFIG)
        logger = logging.getLogger('ApiLogger')
        g.log = logger
    return g.log


def create_db(app):
    engine = create_engine(app.config['DATABASE'])
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)
    return session()


def get_db(app):
    if 'db' not in g:
        session = create_db(app)
        g.db = session
    return g.db
