import re
import pandas as pd
import datetime


from src.web.models.model import Sensors, Weather


def get_sensor_data(session) -> pd.DataFrame:
    """load sensor data from database"""
    res = session.query(Sensors).filter(Sensors.date >= datetime.datetime.utcnow() - datetime.timedelta(days=7)).all()
    data = [i.serialize for i in res]
    data = pd.DataFrame(data)
    data = data.rename(columns={'p1': 'P1', 'p2': 'P2'})
    data['date'] = pd.to_datetime(data.date)
    data = data.set_index('date')
    data = data.resample('5T').mean()
    return data


def get_weather_data(session) -> pd.DataFrame:
    """load weather data from database"""
    res = session.query(Weather).filter(Weather.date >= datetime.datetime.utcnow() - datetime.timedelta(days=7)).all()
    data = [i.serialize for i in res]
    data = pd.DataFrame(data)
    data['date'] = pd.to_datetime(data.date)
    data = data.rename(columns={'temp': 'temp_meteo', 'press': 'pres_meteo',
                                'prec': 'prec_amount', 'wind_speed': 'wind_speed',
                                'wind_dir': 'wind_direction', 'hum': 'hum_meteo'})
    data['prec_amount'] = data.prec_amount.apply(lambda x: re.findall(r'\d*\.\d+|\d+', x)[0]).astype(float)
    data['prec_time'] = 3.0
    data = data.set_index('date')
    data = data.resample('5T').bfill()
    return data


def combine_data(sensor_data: pd.DataFrame, weather_data: pd.DataFrame) -> pd.DataFrame:
    """combine sensor and weather data"""
    # select start and end date (some data possible missing)
    sensor_start_date = sensor_data.index[0].to_pydatetime()
    weather_start_date = sensor_data.index[0].to_pydatetime()
    start_date = max(sensor_start_date, weather_start_date)
    sensor_end_date = sensor_data.index[-1].to_pydatetime()
    weather_end_date = weather_data.index[-1].to_pydatetime()
    end_date = min(sensor_end_date, weather_end_date)

    sensor_data = sensor_data[str(start_date):str(end_date)]
    weather_data = weather_data[str(start_date):str(end_date)]
    for c in sensor_data.columns:
        weather_data[c] = sensor_data[c]
    return weather_data
