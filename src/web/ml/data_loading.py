import datetime
import pandas as pd
import re

from src.web.models.model import Sensors, Weather


def get_sensor_data(session, date=None, delta=datetime.timedelta(days=1)) -> pd.DataFrame:
    """get sensor data for time interval [date-delta, date]"""
    if date is None:
        date = datetime.datetime.utcnow()

    # get sensor data for Chunk.train
    result = session.query(Sensors).filter(Sensors.date.between(date-delta, date)).all()
    data = [i.serialize for i in result]
    print(data)
    data = pd.DataFrame(data)
    data = data.rename(columns={'p1': 'P1_filtr_mean', 'p2': 'P2_filtr_mean', 'temperature': 'temperature_filtr_mean',
                                'humidity': 'humidity_filtr_mean', 'pressure': 'pressure_filtr_mean'})
    data['date'] = pd.to_datetime(data.date)
    data = data.set_index('date')
    return data.resample('5T').mean()


def transform_prec_amount(x):
    """extract precipitations amount from string stored in database"""
    numbers = re.findall(r'\d*\.\d+|\d+', x)
    if len(numbers) > 0:
        return float(numbers[0])
    else:
        return 0


wind_dir = {'В': 'Ветер, дующий с востока',
            'С-В': 'Ветер, дующий с северо-востока',
            'С': 'Ветер, дующий с севера',
            'С-З': 'Ветер, дующий с северо-запада',
            'З': 'Ветер, дующий с запада',
            'Ю-З': 'Ветер, дующий с юго-запада',
            'Ю': 'Ветер, дующий с юга',
            'Ю-В': 'Ветер, дующий с юго-востока',
            'ШТЛ': 'Штиль, безветрие',
            }


def get_weather_data(session, date=None, delta=datetime.timedelta(days=1)) -> pd.DataFrame:
    """ get weather data for time interval [date-delta, date]"""
    if date is None:
        date = datetime.datetime.utcnow()
    res = session.query(Weather).filter(Weather.date.between(date-delta, date)).all()
    data = [i.serialize for i in res]
    data = pd.DataFrame(data)
    data['date'] = pd.to_datetime(data.date)
    data = data.rename(columns={'temp': 'temp_meteo', 'press': 'pres_meteo',
                                'prec': 'prec_amount', 'wind_speed': 'wind_speed',
                                'wind_dir': 'wind_direction', 'hum': 'hum_meteo'})
    data['prec_amount'] = data.prec_amount.apply(transform_prec_amount).astype(float)
    data['prec_time'] = 3.0  # time step of weather forecast from rp5.ru
    data['wind_direction'] = data.wind_direction.map(wind_dir)
    data = data.set_index('date')
    return data.resample('5T').bfill()
