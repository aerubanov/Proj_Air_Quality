import pickle
import pandas as pd
import datetime

from src.model.anom_clustering import AnomalyCluster
from src.features.preproc_anom import prepare_features


def extract_anom(data_file: str, pca_model, kmean_model):
    anom_clustering = AnomalyCluster(kmean_model, pca_model)
    data = pd.read_csv(data_file, parse_dates=['date'])
    data = data.set_index('date')
    data = prepare_features(data)
    anom_list = list()
    weeks = [g for n, g in data.groupby(pd.Grouper(freq='7D'))]  # split dataset by 7 days series
    for week in weeks[:-2]:
        anom = anom_clustering.get_anomaly(week)
        clusters = anom_clustering.get_clusters(anom)
        for i in range(len(anom)):
            anom_list.append({'start_date': anom[i].index[0].to_pydatetime(),
                              'end_date': anom[i].index[-1].to_pydatetime(),
                              'cluster': clusters[i]})
    return anom_list


if __name__ == '__main__':
    data_path = 'DATA/processed/dataset.csv'
    pca_model_file = 'models/pca.obj'
    kmean_model_file = 'models/kmean.obj'
    with open(pca_model_file, 'rb') as pca_f, open(kmean_model_file, 'rb') as km_f:
        km = pickle.load(km_f)
        pca = pickle.load(pca_f)
        anomalies = extract_anom(data_path, pca, km)
        df = pd.DataFrame(anomalies)
        df.to_csv('DATA/processed/anomalies.csv')
