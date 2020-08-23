import datetime
import pandas as pd

from src.web.client.application.helper_functions import aqi_level, pm25_to_aqius,\
    get_sensor_data, get_anomaly_data, get_forecast_data
from tests.web.test_web_client import sensor_data, anomaly_data, forec_data


def test_aqi_level():
    assert aqi_level(25) == 'green'
    assert aqi_level(50) == 'green'
    assert aqi_level(51) == 'gold'
    assert aqi_level(100) == 'gold'
    assert aqi_level(101) == 'orange'
    assert aqi_level(150) == 'orange'
    assert aqi_level(151) == 'red'
    assert aqi_level(200) == 'red'
    assert aqi_level(201) == 'purple'
    assert aqi_level(300) == 'purple'
    assert aqi_level(301) == 'brown'


def test_pm25_to_aqius():
    assert round(pm25_to_aqius(12)) == 50
    assert round(pm25_to_aqius(30)) == 88
    assert round(pm25_to_aqius(50)) == 136
    assert round(pm25_to_aqius(60)) == 152
    assert round(pm25_to_aqius(160)) == 210
    assert round(pm25_to_aqius(270)) == 316


def test_get_sensor_data(requests_mock):
    requests_mock.get('http://api:8000/sensor_data', text=sensor_data)
    df = get_sensor_data(datetime.datetime(2020, 4, 7), datetime.datetime(2020, 4, 8))
    assert len(df) == 3
    assert 'p1' in df.columns
    assert 'p2' in df.columns


def test_get_anomaly_data(requests_mock):
    requests_mock.get('http://api:8000/anomaly', text=anomaly_data)
    df = pd.DataFrame({'date': [datetime.datetime(2020, 4, 7, 0, 40,),
                                datetime.datetime(2020, 4, 7, 6, 40,),
                                datetime.datetime(2020, 4, 7, 9, 20,)],
                       'p1': [1, 2, 3],
                       'p2': [4, 5, 6]})
    df = df.set_index('date')
    anomaly = get_anomaly_data(datetime.datetime(2020, 4, 7), datetime.datetime(2020, 4, 8), df)
    assert len(anomaly) == 2
    assert 'p1' in anomaly.columns
    assert 'cluster' in anomaly.columns


def test_get_forecast(requests_mock):
    requests_mock.get('http://api:8000/forecast', text=forec_data)
    forec = get_forecast_data()
    assert len(forec) == 24
    assert 'p1' in forec.columns
    assert 'p2' in forec.columns
