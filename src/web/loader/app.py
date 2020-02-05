from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time

from src.web.models.model import Base, Sensors, Weather


if __name__ == '__main__':
    time.sleep(5)
    engine = create_engine('postgresql://postgres:postgres@PostgreSQL/pgdb')
    Base.metadata.create_all(engine)
