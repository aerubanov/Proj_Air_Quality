import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

from src.web.models.model import Base, LoaderLog


class LogDBHandler(logging.Handler):

    def __init__(self):
        super().__init__()
        engine = create_engine('postgresql://postgres:postgres@PostgreSQL/pgdb')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def emit(self, record):
        dt = datetime.datetime.fromtimestamp(record.created, tz=datetime.timezone.utc)
        entry = LoaderLog(
            date=dt,
            level=record.levelname,
            name=record.name,
            message=record.message
        )
        self.session.add(entry)
        self.session.commit()
