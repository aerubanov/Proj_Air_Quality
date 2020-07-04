import pandas as pd
import pickle

from src.model.extract_anomalies import extract_anom, dim_red_file, clustering_file, map_file, main
from src.model.anom_clustering import Model


def test_extract_anomalies():
    data = pd.read_csv('tests/model/data/anomalies_prepared.csv', parse_dates=['date'])
    data = data.set_index('date')
    with open(dim_red_file, 'rb') as pca_file, open(clustering_file, 'rb') as km_file, open(map_file, 'rb') as m_file:
        pca = pickle.load(pca_file)
        kmean = pickle.load(km_file)
        cluster_map = pickle.load(m_file)
        model = Model(pca, kmean, cluster_map)
    result, anom_data = extract_anom(data, model)
    assert len(result) == len(anom_data)
    assert 'start_date' in result.columns
    assert 'end_date' in result.columns
    assert 'cluster' in result.columns


def test_main(tmpdir, monkeypatch):
    data_file = 'tests/model/data/test_dataset.csv'
    d1 = tmpdir.mkdir('data_out')
    d2 = tmpdir.mkdir('image_out')
    anom_file = d1.join('anomalies.csv')
    image_file = d2.join('image.png')
    monkeypatch.setattr('src.model.extract_anomalies.anomalies_file', anom_file)
    monkeypatch.setattr('src.model.extract_anomalies.image_file', image_file)
    monkeypatch.setattr('src.model.extract_anomalies.data_file', data_file)
    main()
    assert len(anom_file.read().splitlines()) > 0
