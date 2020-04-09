import pandas as pd

from src.features.preproc_anom import prepare_features
from src.model.anom_clustering import sel_columns

test_data = 'tests/model/data/test_dataset.csv'


def test_prepare_features_smoke():
    data = pd.read_csv(test_data, parse_dates=['date'])
    data = data.set_index('date')
    data = prepare_features(data)
    for c in ['P1', 'P2', 'humidity', 'temperature', 'pressure']:
        assert not data[c].isnull().values.any()
