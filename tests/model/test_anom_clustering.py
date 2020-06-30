import pandas as pd
import pickle

from src.model.anom_clustering import anom_detector, detect_anomalies, get_anomaly_features, sel_columns,\
    Model, kmean, pca
test_data = 'tests/model/data/anomalies_prepared.csv'


def test_anom_detector():
    data = pd.read_csv(test_data, parse_dates=['date'])
    data = data.set_index('date')
    result = anom_detector(data['2020-03-01':'2020-03-07'])
    for item in result:
        assert 'trend' in item.columns
        assert 'seasonal' in item.columns
        assert 'resid' in item.columns


def test_detect_anomalies():
    data = pd.read_csv(test_data, parse_dates=['date'])
    data = data.set_index('date')
    result = detect_anomalies(data)
    with open('tests/model/data/anomalies.obj', 'wb') as file:
        pickle.dump(result, file)
    for item in result:
        assert 'trend' in item.columns
        assert 'seasonal' in item.columns
        assert 'resid' in item.columns


def test_get_anomalies_features():
    with open('tests/model/data/anomalies.obj', 'rb') as file:
        data = pickle.load(file)
    result = get_anomaly_features(data)
    for c in ['resid_change', 'hum', 'temp', 'prec', 'wind_speed', 'wind_sin', 'wind_cos']:
        assert c in result.columns
    result.to_csv('tests/model/data/anom_features.csv', index=False)


def test_model():
    data = pd.read_csv(test_data, parse_dates=['date'])
    data = data.set_index('date')
    data = data['2020-03']
    model = Model(pca, kmean)
    scores = model.train(data)
    assert len(scores) == 3
    clusters, anomalies = model.predict(data['2020-03-01':'2020-03-07'])
    assert len(clusters) == len(anomalies)
    for c in ['start_date', 'end_date', 'cluster']:
        assert c in clusters.columns
