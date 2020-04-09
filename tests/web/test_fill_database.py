import datetime
import math
import pandas as pd

from src.web.scripts.fill_database import load_sensor_data, get_last_date_sensors, clear_sensors_table, write_data,\
    get_last_date_anomalies, clear_anomalies_table
from src.web.models.model import Sensors, Anomaly


def test_load_data():
    data = load_sensor_data('tests/web/data/test_dataset_1.csv')
    assert data.index[0].to_pydatetime() == datetime.datetime(2019, 4, 1, 3, 0)
    assert math.isclose(data.p1[0], 6.647142857142856, rel_tol=1e-09)
    assert math.isclose(data.p2[0], 2.8817857142857144, rel_tol=1e-09)
    assert math.isclose(data.temperature[0], 4.99125, rel_tol=1e-09)
    assert math.isclose(data.humidity[0], 58.79375, rel_tol=1e-09)
    assert math.isclose(data.pressure[0], 98722.855, rel_tol=1e-09)


def test_last_date_sensors():
    data = load_sensor_data('tests/web/data/test_dataset_1.csv')
    last_date = get_last_date_sensors(data)
    assert last_date == datetime.datetime(2019, 4, 1, 3, 10)


def test_last_date_anomalies():
    data = pd.read_csv('tests/web/data/test_anomalies.csv', parse_dates=['start_date', 'end_date'])
    last_date = get_last_date_anomalies(data)
    assert last_date == datetime.datetime(2019, 4, 6, 8, 50)  # 2019-04-06 08:50:00


def test_clear_sensors_table(database_session):
    end_date = datetime.datetime(2020, 2, 24, 3, 7, 15)

    entr_1 = Sensors(date=end_date-datetime.timedelta(minutes=5))
    entr_2 = Sensors(date=end_date)
    entr_3 = Sensors(date=end_date + datetime.timedelta(minutes=5))
    database_session.add(entr_1)
    database_session.add(entr_2)
    database_session.add(entr_3)
    database_session.commit()

    clear_sensors_table(end_date, database_session)
    q = database_session.query(Sensors).all()
    dates = [i.date for i in q]
    assert dates == [end_date + datetime.timedelta(minutes=5)]


def test_clear_anomalies_table(database_session):
    date = datetime.datetime(2020, 3, 8, 23, 57)
    entr_1 = Anomaly(start_date=date-datetime.timedelta(minutes=5))
    entr_2 = Anomaly(start_date=date)
    entr_3 = Anomaly(start_date=date+datetime.timedelta(minutes=5))
    database_session.add(entr_1)
    database_session.add(entr_2)
    database_session.add(entr_3)
    database_session.commit()

    clear_anomalies_table(date, database_session)
    q = database_session.query(Anomaly).all()
    dates = [i.start_date for i in q]
    assert dates == [date + datetime.timedelta(minutes=5)]


def test_write_data(database_session):
    entry = Sensors(date=datetime.datetime(2019, 4, 1, 3, 10, 15))
    database_session.add(entry)
    database_session.commit()
    data = load_sensor_data('tests/web/data/test_dataset_1.csv')
    write_data(data, database_session, 'sensors')
    res = database_session.query(Sensors).all()
    assert len(res) == len(data) + 1
    res = database_session.query(Sensors).filter(Sensors.date == datetime.datetime(2019, 4, 1, 3, 10, 15)).first()
    assert res.date == datetime.datetime(2019, 4, 1, 3, 10, 15)
