import pandas as pd
from sklearn.preprocessing import QuantileTransformer

from src.features.preproc_forecast import prepare_data, add_features, DataTransform
from src.model.forecast import columns as model_columns, num_colunms

test_data = 'tests/features/data/test_dataset.csv'

new_features = ['day_of_week', 'hour', 'sin_day', 'cos_day', 'sin_hour', 'cos_hour', 'P_diff1', 'P_diff2',
                'P_diff3', 't_diff', 't_diff1', 't_diff2', 'h_diff', 'h_diff1', 'h_diff2', 'wind_direction',
                "wind_sin", "wind_cos", 'wind_sin', 'wind_cos', 'temp_diff', 'humidity_diff', 'pressure_diff',
                'wind_sin_diff', 'wind_cos_diff', 'temp_diff3', 'humidity_diff3', 'pressure_diff3',
                'wind_sin_diff3', 'wind_cos_diff3']


def test_prepare_data():
    data = pd.read_csv(test_data, parse_dates=['date'])
    data = data.set_index('date')
    data = prepare_data(data)

    for c in model_columns:
        assert c in data.columns

    for c in model_columns:
        assert not data[c].isna().any()


def test_add_features():
    data = pd.read_csv(test_data, parse_dates=['date'])
    data = data.set_index('date')

    data = add_features(data.iloc[:2], target='P1_filtr_mean')
    assert set(data.columns) == set(new_features + model_columns + ['dew_point_temp'])

    data = add_features(data.iloc[:2], target='P2_filtr_mean')
    assert set(data.columns) == set(new_features + model_columns + ['dew_point_temp'])


def test_data_transform():
    data = pd.read_csv(test_data, parse_dates=['date'])
    data = data.set_index('date')
    target = ['P1_filtr_mean', 'P2_filtr_mean']

    for t in target:
        n_samples = data[[t]].shape[0]
        data_transform = QuantileTransformer(output_distribution='normal', n_quantiles=n_samples)
        target_transform = QuantileTransformer(output_distribution='normal', n_quantiles=n_samples)

        transform = DataTransform(data_transform, target_transform, model_columns, num_colunms, t)
        data = transform.fit_transform(data)
        assert set(data.columns) == set(new_features + model_columns + ['P_original'])

        data = pd.read_csv(test_data, parse_dates=['date'])
        data = data.set_index('date')

        data = transform.transform(data)
        assert set(data.columns) == set(new_features + model_columns + ['P_original'])