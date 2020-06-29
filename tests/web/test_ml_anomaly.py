import datetime
import pandas as pd

from src.web.models.model import Anomaly
from src.model.anom_clustering import sensor_columns, meteo_columns
from src.web.ml.anomaly import clear_anomalies_table, write_data, perform_anomaly_detection


def test_clear_table(database_session):
    a1 = Anomaly(start_date=datetime.datetime(2020, 3, 18, 10, 00, 0),
                 end_date=datetime.datetime(2020, 3, 18, 10, 10, 0), cluster=1)
    a2 = Anomaly(start_date=datetime.datetime(2020, 3, 18, 10, 20, 0),
                 end_date=datetime.datetime(2020, 3, 18, 10, 40, 0), cluster=1)
    a3 = Anomaly(start_date=datetime.datetime(2020, 3, 18, 10, 45, 0),
                 end_date=datetime.datetime(2020, 3, 18, 11, 00, 0), cluster=1)
    a4 = Anomaly(start_date=datetime.datetime(2020, 3, 18, 11, 10, 0),
                 end_date=datetime.datetime(2020, 3, 18, 11, 30, 0), cluster=1)
    a5 = Anomaly(start_date=datetime.datetime(2020, 3, 18, 12, 00, 0),
                 end_date=datetime.datetime(2020, 3, 18, 12, 30, 0), cluster=1)
    database_session.add(a1)
    database_session.add(a2)
    database_session.add(a3)
    database_session.add(a4)
    database_session.add(a5)
    database_session.commit()
    clear_anomalies_table(datetime.datetime(2020, 3, 18, 10, 30, 0), datetime.datetime(2020, 3, 18, 11, 20, 0),
                          database_session)
    res = database_session.query(Anomaly).order_by(Anomaly.start_date).all()
    assert len(res) == 2
    data = [i.serialize for i in res]
    assert data[0]['start_date'] == datetime.datetime(2020, 3, 18, 10, 00, 0).isoformat('T')
    assert data[0]['end_date'] == datetime.datetime(2020, 3, 18, 10, 10, 0).isoformat('T')
    assert data[1]['start_date'] == datetime.datetime(2020, 3, 18, 12, 00, 0).isoformat('T')
    assert data[1]['end_date'] == datetime.datetime(2020, 3, 18, 12, 30, 0).isoformat('T')


def test_write_data(database_session):
    d = {'start_date': [datetime.datetime(2020, 3, 1, 4, 15), datetime.datetime(2020, 3, 2, 10, 35),
                           datetime.datetime(2020, 3, 2, 20, 25)],
            'end_date': [datetime.datetime(2020, 3, 1, 7, 5), datetime.datetime(2020, 3, 2, 15, 5),
                         datetime.datetime(2020, 3, 3, 0, 25)],
            'cluster': [1, 1, 0]}
    anomalies = pd.DataFrame(data=d)
    write_data(database_session, anomalies)
    res = database_session.query(Anomaly).order_by(Anomaly.start_date).all()
    data = [i.serialize for i in res]
    assert len(data) == 3
    assert data[0]['start_date'] == datetime.datetime(2020, 3, 1, 4, 15).isoformat('T')
    assert data[1]['start_date'] == datetime.datetime(2020, 3, 2, 10, 35).isoformat('T')
    assert data[2]['start_date'] == datetime.datetime(2020, 3, 2, 20, 25).isoformat('T')


def test_perform_anomaly_detection(monkeypatch, database_session):
    def mock_sensor(*args, **kwargs):
        data = pd.read_csv('tests/model/data/anomalies_prepared.csv', parse_dates=['date'])
        data = data.set_index('date')
        data = data['2020-03-01':'2020-03-07']
        return data[sensor_columns]

    def mock_meteo(*args, **kwargs):
        data = pd.read_csv('tests/model/data/anomalies_prepared.csv', parse_dates=['date'])
        data = data.set_index('date')
        data = data['2020-03-01':'2020-03-07']
        return data[meteo_columns]

    monkeypatch.setattr('src.web.ml.anomaly.get_weather_data', mock_meteo)
    monkeypatch.setattr('src.web.ml.anomaly.get_sensor_data', mock_sensor)
    perform_anomaly_detection(database_session)
    result = database_session.query(Anomaly).all()
    assert len(result) > 0
