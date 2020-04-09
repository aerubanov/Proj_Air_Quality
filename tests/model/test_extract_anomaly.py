import pickle

from src.model.extract_anomalies import extract_anom
from src.model.anom_clustering import num_clusters

test_data = 'tests/model/data/test_dataset.csv'
pca_model_file = 'models/pca.obj'
kmean_model_file = 'models/kmean.obj'


def test_extract_anom_smoke():
    with open(pca_model_file, 'rb') as pca_f, open(kmean_model_file, 'rb') as km_f:
        km = pickle.load(km_f)
        pca = pickle.load(pca_f)
        anomalies = extract_anom(test_data, pca, km)
        for anom in anomalies:
            assert anom['start_date'] < anom['end_date']
            assert anom['cluster'] >= 0
            assert anom['cluster'] < num_clusters
