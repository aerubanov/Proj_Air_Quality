import datetime
import pandas as pd

from src.web.models.model import Sensors, Weather
from src.web.ml.anomaly import get_sensor_data, get_weather_data, combine_data


def test_get_sensor_data(database_session):
    date = datetime.datetime.utcnow()
    s1 = Sensors(date=date-datetime.timedelta(days=6, hours=5), p1=1.0, p2=2.0, temperature=20.0,
                 humidity=50.0, pressure=98513.23)
    s2 = Sensors(date=date - datetime.timedelta(days=6, hours=4), p1=2.0, p2=3.0, temperature=19.0,
                 humidity=49.0, pressure=98578.5)
    s3 = Sensors(date=date - datetime.timedelta(days=7, hours=4), p1=2.0, p2=3.0, temperature=19.0,
                 humidity=49.0, pressure=98578.5)
    database_session.add(s1)
    database_session.add(s2)
    database_session.add(s3)
    database_session.commit()

    data = get_sensor_data(database_session)
    assert len(data) == 60//5 + 1   # data after resampling with step 5 minutes
    assert 'P1' in data.columns
    assert 'P2' in data.columns
    assert 'temperature' in data.columns
    assert 'humidity' in data.columns
    assert 'pressure' in data.columns


def test_get_weather_data(database_session):
    date = datetime.datetime.utcnow()
    w1 = Weather(date=date-datetime.timedelta(days=6, hours=5), temp=22.0, press=98654.30,
                 prec='Обложной дождь (0.7 мм воды за 3 часа с 00:00 до 03:00)', wind_speed=2.1,
                 wind_dir='СВ', hum=61.0)
    w2 = Weather(date=date - datetime.timedelta(days=6, hours=4), temp=22.0, press=98654.30,
                 prec='Обложной дождь (0.7 мм воды за 3 часа с 00:00 до 03:00)', wind_speed=2.1,
                 wind_dir='СВ', hum=61.0)
    w3 = Weather(date=date - datetime.timedelta(days=7, hours=4), temp=22.0, press=98654.30,
                 prec='Обложной дождь (0.7 мм воды за 3 часа с 00:00 до 03:00)', wind_speed=2.1,
                 wind_dir='СВ', hum=61.0)
    database_session.add(w1)
    database_session.add(w2)
    database_session.add(w3)
    database_session.commit()
    data = get_weather_data(database_session)
    assert len(data) == 60//5 + 1   # data after resampling with step 5 minutes
    assert 'temp_meteo' in data.columns
    assert 'pres_meteo' in data.columns
    assert 'hum_meteo' in data.columns
    assert 'wind_speed' in data.columns
    assert 'wind_direction' in data.columns
    assert 'prec_amount' in data.columns
    assert 'prec_time' in data.columns
    assert data.prec_amount.dtypes == float


def test_combine_data():
    dti_1 = pd.date_range('2020-03-17 00:00:00', periods=5, freq='5T')
    dti_2 = pd.date_range('2020-03-17 00:10:00', periods=5, freq='5T')
    sensor_data = pd.DataFrame(index=dti_1)
    sensor_data['col_1'] = 1
    sensor_data['col_2'] = 2
    weather_data = pd.DataFrame(index=dti_2)
    weather_data['col_3'] = 3
    weather_data['col_4'] = 4
    weather_data['col_5'] = 5
    data = combine_data(sensor_data, weather_data)
    assert data.index[0].to_pydatetime() == datetime.datetime(2020, 3, 17, 0, 10, 0)
    assert data.index[-1].to_pydatetime() == datetime.datetime(2020, 3, 17, 0, 20, 0)
    assert 'col_1' in data.columns
    assert 'col_2' in data.columns
    assert 'col_3' in data.columns
    assert 'col_4' in data.columns
    assert 'col_5' in data.columns
