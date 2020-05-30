from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
import pandas as pd

from src.web.models.model import Base, Sensors, Anomaly
try:
    from src.web.config import DATABASE
except ModuleNotFoundError:
    print("Missing config file!!!")

dataset = 'data/dataset.csv'
anomalies = 'data/anomalies.csv'


def load_sensor_data(file: str) -> pd.DataFrame:
    """read columns from dataset"""
    df = pd.read_csv(file, parse_dates=['date'])
    data = pd.DataFrame(index=df.index)
    data['date'] = df.date
    data['p1'] = df.P1_filtr_mean
    data['p2'] = df.P2_filtr_mean
    data['temperature'] = df.temperature_filtr_mean
    data['humidity'] = df.humidity_filtr_mean
    data['pressure'] = df.pressure_filtr_mean
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
    """write data from dataframe to table"""
    eng = session.get_bind()
    data.to_sql(table, con=eng, if_exists='append')


def fill_sensors(session):
    """fill sensor table of database"""
    data = load_sensor_data(dataset)
    end_date = get_last_date_sensors(data)
    clear_sensors_table(end_date, session)
    write_data(data, session, 'sensors')


def fill_anomalies(session):
    """fill anomalies table of database"""
    data = pd.read_csv(anomalies, parse_dates=['start_date', 'end_date'])
    end_date = get_last_date_anomalies(data)
    clear_anomalies_table(end_date, session)
    eng = session.get_bind()
    data.to_sql('anomalies', con=eng, if_exists='append', index=False)


if __name__ == '__main__':
    engine = create_engine(DATABASE)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    sess = Session()
    fill_sensors(sess)
    fill_anomalies(sess)
