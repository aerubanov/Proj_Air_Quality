import pickle
import pandas as pd
import datetime

from src.web.models.model import Sensors, Weather


def get_sensor_data(session):
    res = session.query(Sensors).filter(Sensors.date >= datetime.datetime.utcnow() - datetime.timedelta(days=7)).all()
    data = [i.serialize for i in res]
    data = pd.DataFrame(data)
    data = data.rename(columns={'p1': 'P1', 'p2': 'P2'})
    data['date'] = pd.to_datetime(data.date)
    return data


def get_weather_data(session):
    res = session.query(Sensors).filter(Sensors.date >= datetime.datetime.utcnow() - datetime.timedelta(days=7)).all()
    data = [i.serialize for i in res]
    data = pd.DataFrame(data)
    data['date'] = pd.to_datetime(data.date)
    data = data.rename(columns={'temp': 'temp_meteo', 'press': 'press_meteo'})
    return data
