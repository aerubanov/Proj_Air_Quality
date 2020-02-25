from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
import pandas as pd

from src.web.models.model import Base, Sensors

engine = create_engine('postgresql://postgres:postgres@0.0.0.0/pgdb')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
sess = Session()

dataset = '../../../DATA/processed/dataset.csv'


def load_data(file: str) -> pd.DataFrame:
    """read columns from dataset"""
    df = pd.read_csv(file, parse_dates=['date'])
    data = pd.DataFrame(index=df.index)
    data['date'] = df.date
    data['p1'] = df.P1
    data['p2'] = df.P2
    data['temperature'] = df.temperature
    data['humidity'] = df.humidity
    data['pressure'] = df.pressure
    data = data.set_index('date')
    return data


def get_last_date(data: pd.DataFrame) -> datetime.datetime:
    """get last available date from dataset """
    return data.index[-1].to_pydatetime()


def clear_database(end_date: datetime.datetime, session=sess):
    """remove all entries from database before end_date"""
    session.query(Sensors).filter(Sensors.date <= end_date).delete()
    session.commit()


def write_data(data: pd.DataFrame, session=sess):
    eng = session.get_bind()
    data.to_sql('sensors', con=eng, if_exists='append')


if __name__ == '__main__':
    data = load_data(dataset)
    end_date = get_last_date(data)
    clear_database(end_date)
    write_data(data)
