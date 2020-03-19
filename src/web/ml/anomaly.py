import re
import pandas as pd
import datetime
import pickle

from src.web.models.model import Sensors, Weather, Anomaly
from src.model.anom_clustering import AnomalyCluster

pca_model_file = 'models/pca.obj'
kmean_model_file = 'models/kmean.obj'

wind_dir = {'В': 'Ветер, дующий с востока',
            'С-В': 'Ветер, дующий с северо-востока',
            'С': 'Ветер, дующий с севера',
            'С-З': 'Ветер, дующий с северо-запада',
            'З': 'Ветер, дующий с запада',
            'Ю-З': 'Ветер, дующий с юго-запада',
            'Ю': 'Ветер, дующий с юга',
            'Ю-В': 'Ветер, дующий с юго-востока',
            }


def get_sensor_data(session, date=datetime.datetime.utcnow()) -> pd.DataFrame:
    """load sensor data from database"""
    res = session.query(Sensors).filter(Sensors.date >= date - datetime.timedelta(days=7)).all()
    data = [i.serialize for i in res]
    data = pd.DataFrame(data)
    data = data.rename(columns={'p1': 'P1', 'p2': 'P2'})
    data['date'] = pd.to_datetime(data.date)
    data = data.set_index('date')
    data = data.resample('5T').mean()
    return data


def transform_prec_amount(x):
    numbers = re.findall(r'\d*\.\d+|\d+', x)
    if len(numbers) > 0:
        return numbers[0]
    else:
        return 0


def get_weather_data(session, date=datetime.datetime.utcnow()) -> pd.DataFrame:
    """load weather data from database"""
    res = session.query(Weather).filter(Weather.date >= date - datetime.timedelta(days=7)).all()
    data = [i.serialize for i in res]
    data = pd.DataFrame(data)
    data['date'] = pd.to_datetime(data.date)
    data = data.rename(columns={'temp': 'temp_meteo', 'press': 'pres_meteo',
                                'prec': 'prec_amount', 'wind_speed': 'wind_speed',
                                'wind_dir': 'wind_direction', 'hum': 'hum_meteo'})
    data['prec_amount'] = data.prec_amount.apply(transform_prec_amount).astype(float)
    data['prec_time'] = 3.0
    data['wind_direction'] = data.wind_direction.map(wind_dir)
    data = data.set_index('date')
    data = data.resample('5T').bfill()
    return data


def combine_data(sensor_data: pd.DataFrame, weather_data: pd.DataFrame) -> (pd.DataFrame, datetime.datetime,
                                                                            datetime.datetime):
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
    return weather_data, start_date, end_date


def extract_anomalies(data):
    with open(kmean_model_file, 'rb') as km_file, open(pca_model_file, 'rb') as pca_file:
        pca = pickle.load(pca_file)
        kmean = pickle.load(km_file)
        model = AnomalyCluster(kmean, pca)
        anomalies = model.get_anomaly(data)
        clusters = model.get_clusters(anomalies)
        anom_list = []
        for i in range(len(anomalies)):
            anom_list.append({'start_date': anomalies[i].index[0].to_pydatetime(),
                              'end_date': anomalies[i].index[-1].to_pydatetime(),
                              'cluster': clusters[i]})
        return anom_list


def clear_anomalies_table(start_date: datetime.datetime, end_date: datetime.datetime, session):
    session.query(Anomaly).filter(Anomaly.end_date >= start_date).filter(Anomaly.start_date <= end_date).delete()
    session.commit()


def write_data(session, anom_list):
    for anomaly in anom_list:
        entry = Anomaly(start_date=anomaly['start_date'], end_date=anomaly['end_date'], cluster=anomaly['cluster'])
        session.add(entry)
        session.commit()


def perform_anomaly_detection(session, logger=None):
    weather_data = get_weather_data(session)
    sensor_data = get_sensor_data(session)
    data, start_date, end_date = combine_data(sensor_data, weather_data)
    anom_list = extract_anomalies(data)
    clear_anomalies_table(start_date, end_date, session)
    write_data(session, anom_list)
    if logger is not None:
        logger.info("Perform anomaly detection")
