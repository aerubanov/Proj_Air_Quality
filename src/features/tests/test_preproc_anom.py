import pandas as pd

from src.features.preproc_anom import prepare_features

test_data = 'src/model/tests/data/test_dataset.csv'


def test_prepare_features_smoke():
    data = pd.read_csv(test_data, parse_dates=['date'])
    data = data.set_index('date')
    data = prepare_features(data)
    for c in data.columns:
        assert not data[c].isnull().values.any()
