import pandas as pd
import datetime
import pickle

from src.web.models.model import Anomaly
from src.web.ml.data_loading import get_weather_data, get_sensor_data
from src.model.anom_clustering import Model

pca_model_file = 'models/anomalies/dim_red.obj'
kmean_model_file = 'models/anomalies/clustering.obj'
cluster_map_file = 'models/anaomalies/cluster_map.obj'


def clear_anomalies_table(start_date: datetime.datetime, end_date: datetime.datetime, session):
    session.query(Anomaly).filter(Anomaly.end_date >= start_date).filter(Anomaly.start_date <= end_date).delete()
    session.commit()


def write_data(session, anomalies: pd.DataFrame):
    for _, anomaly in anomalies.iterrows():
        entry = Anomaly(start_date=anomaly['start_date'], end_date=anomaly['end_date'], cluster=int(anomaly['cluster']))
        session.add(entry)
        session.commit()


def perform_anomaly_detection(session, logger=None):
    delta = datetime.timedelta(days=7)
    weather_data = get_weather_data(session, delta=delta)
    sensor_data = get_sensor_data(session, delta=delta)
    data = pd.concat((weather_data, sensor_data), axis=1)

    with open(pca_model_file, 'rb') as pca_file, open(kmean_model_file, 'rb') as km_file,\
            open(cluster_map_file, 'rb') as m_file:
        pca = pickle.load(pca_file)
        kmean = pickle.load(km_file)
        cluster_map = pickle.load(m_file)
        model = Model(pca, kmean, cluster_map)
    anomalies, _ = model.predict(data)
    end_date = datetime.datetime.utcnow()
    start_date = end_date - delta
    clear_anomalies_table(start_date, end_date, session)
    write_data(session, anomalies)
    if logger is not None:
        logger.info("Perform anomaly detection")
