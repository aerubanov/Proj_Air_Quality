import pandas as pd

from src.features.preproc_anom import prepare_meteo_data, prepare_sensors_data, add_features
from src.model.anom_clustering import meteo_columns, sensor_columns

test_data = 'tests/features/data/test_dataset.csv'


def test_prepare_sensors_data():
    data = pd.read_csv(test_data, parse_dates=['date'])
    data = data.set_index('date')
    result = prepare_sensors_data(data, sensor_columns)
    for c in sensor_columns:
        assert not result[c].isnull().values.any()


def test_prepare_meteo_data():
    data = pd.read_csv(test_data, parse_dates=['date'])
    data = data.set_index('date')
    result = prepare_meteo_data(data, meteo_columns)
    for c in meteo_columns:
        assert not result[c].isnull().values.any()


def test_add_features():
    data = pd.read_csv(test_data, parse_dates=['date'])
    data = data.set_index('date')
    data = prepare_sensors_data(data, sensor_columns)
    data = prepare_meteo_data(data, meteo_columns)
    result = add_features(data)
    for c in ['dew_point_diff', "wind_sin", "wind_cos"]:
        assert c in result.columns