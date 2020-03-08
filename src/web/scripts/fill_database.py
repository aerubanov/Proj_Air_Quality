from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
import pandas as pd

from src.web.models.model import Base, Sensors, Anomaly

dataset = '../../../DATA/processed/dataset.csv'
anomalies = '../../../DATA/processed/anomalies.csv'


def load_sensor_data(file: str) -> pd.DataFrame:
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


def get_last_date_sensors(data: pd.DataFrame) -> datetime.datetime:
    """get last available date from dataset """
    return data.index[-1].to_pydatetime()


def get_last_date_anomalies(data: pd.DataFrame) -> datetime.datetime:
    """get last available date from anomalies """
    return data.iloc[-1].start_date.to_pydatetime()


def clear_sensors_table(end_date: datetime.datetime, session):
    """remove all entries from sensors table before end_date"""
    session.query(Sensors).filter(Sensors.date <= end_date).delete()
    session.commit()


def clear_anomalies_table(end_date: datetime.datetime, session):
    """remove all entries from anomalies table before end_date"""
    session.query(Anomaly).filter(Anomaly.start_date <= end_date).delete()
    session.commit()


def write_data(data: pd.DataFrame, session, table):
    eng = session.get_bind()
    data.to_sql(table, con=eng, if_exists='append')


def fill_sensors(session):
    data = load_sensor_data(dataset)
    end_date = get_last_date_sensors(data)
    clear_sensors_table(end_date, session)
    write_data(data, session, 'sensors')


def fill_anomalies(session):
    data = pd.read_csv(anomalies, parse_dates=['start_date', 'end_date'])
    end_date = get_last_date_anomalies(data)
    clear_anomalies_table(end_date, session)
    write_data(data, session, 'anomalies')


if __name__ == '__main__':
    engine = create_engine('postgresql://postgres:postgres@0.0.0.0/pgdb')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    sess = Session()
    fill_sensors(sess)
    fill_anomalies(sess)
