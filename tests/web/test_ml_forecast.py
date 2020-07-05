import pandas as pd
import pickle

from src.web.ml.forecast import perform_forecast, get_transforms, get_model, get_chunk
from src.features.preproc_forecast import DataTransform
from src.web.models.model import Forecast
from src.model.forecast import Model, Chunk, features, columns

test_data = 'tests/web/data/forecast_prepared.csv'


def test_get_model():
    from src.web.ml.forecast import p1_target_trans_file, p2_target_trans_file

    def helper(file, target):
        with open(file, 'rb') as f:
            target_trans = pickle.load(f)
        model = get_model(target, target_trans)

        assert isinstance(model, Model)
        assert model.target == target

        data = pd.read_csv(test_data, parse_dates=['date'])
        data = data.set_index('date')
        train_part = data['2020-02-03']
        test_part = data['2020-02-04']
        chunk = Chunk(train_part, test_part, features, target)
        prediction = model.predict(chunk)
        assert len(prediction) == 24

    helper(p1_target_trans_file, 'P1_filtr_mean')
    helper(p2_target_trans_file, 'P2_filtr_mean')


def test_get_transform():
    targets = ['P1_filtr_mean', 'P2_filtr_mean']
    for targ in targets:
        tranform = get_transforms(targ)
        data = pd.read_csv(test_data, parse_dates=['date'])
        data = data.set_index('date')
        data = data['2020-02-03':'2020-02-04']

        data = tranform.transform(data)
        new_features = ['day_of_week', 'hour', 'sin_day', 'cos_day', 'sin_hour', 'cos_hour', 'P_diff1', 'P_diff2',
                        'P_diff3', 't_diff', 't_diff1', 't_diff2', 'h_diff', 'h_diff1', 'h_diff2', 'wind_direction',
                        "wind_sin", "wind_cos", 'wind_sin', 'wind_cos', 'temp_diff', 'humidity_diff', 'pressure_diff',
                        'wind_sin_diff', 'wind_cos_diff', 'temp_diff3', 'humidity_diff3', 'pressure_diff3',
                        'wind_sin_diff3', 'wind_cos_diff3']

        assert set(data.columns) == set(new_features + columns + ['P_original'])


def test_get_chunk(monkeypatch):
    data = pd.read_csv(test_data, parse_dates=['date'])
    data = data.set_index('date')

    def mock_get_sensor(*args, **kwargs):
        df = data['2020-02-03']
        return df[['P1_filtr_mean', 'P2_filtr_mean', 'humidity_filtr_mean', 'temperature_filtr_mean']]

    def mock_get_weather(session, date=None, delta=None):
        if date is None:
            df = data['2020-02-03']
        else:
            df = data['2020-02-04']
        return df[['pres_meteo', 'temp_meteo', 'hum_meteo', 'wind_direction',
                   'wind_speed', 'prec_amount', 'prec_time']]

    class MockTransform(DataTransform):
        @staticmethod
        def transform(d):
            return d

    monkeypatch.setattr('src.web.ml.forecast.get_sensor_data', mock_get_sensor)
    monkeypatch.setattr('src.web.ml.forecast.get_weather_data', mock_get_weather)

    chunk = get_chunk(None, MockTransform, 'P1_filtr_mean')

    assert len(chunk.train) == 24
    assert len(chunk.test) == 24


    targets = ['P1_filtr_mean', 'P2_filtr_mean']
    predictions = []
    for targ in targets:
        transform = get_transforms(targ)
        model = get_model(targ, transform.target_transform)
        pred = model.predict(chunk)
        predictions.append(pred)
    assert len(predictions[0]) == 24
    assert len(predictions[1]) == 24


def test_perform_forecast(database_session, monkeypatch):
    def mock_get_chunk(*args, **kwargs):
        return None

    class MockTransform:
        target_transform = None

    def mock_get_transform(*args, **kwargs):
        return MockTransform()

    class MockModel:
        @staticmethod
        def predict(data):
            return [i for i in range(24)]

    def mock_get_model(*args, **kwargs):
        return MockModel()

    monkeypatch.setattr('src.web.ml.forecast.get_transforms', mock_get_transform)
    monkeypatch.setattr('src.web.ml.forecast.get_chunk', mock_get_chunk)
    monkeypatch.setattr('src.web.ml.forecast.get_model', mock_get_model)

    perform_forecast(database_session)

    result = database_session.query(Forecast).all()
    data = [i.serialize for i in result]
    assert len(data) == 24
