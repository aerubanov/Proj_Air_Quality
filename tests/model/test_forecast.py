import pandas as pd
import pickle
import datetime
import os

from src.model.forecast import pp, Chunk, features, generate_chunks, prepare_x, Model, model_path

test_data = 'tests/model/data/forecast_prepared.csv'


def test_pp():
    start_date = datetime.datetime(2020, 1, 1)
    end_date = datetime.datetime(2020, 1, 31)
    n = 42
    df = pd.DataFrame({'date': [start_date, end_date]})
    dates = pp(df.iloc[0].date, df.iloc[-1].date, n)
    assert len(dates) == n
    for d in dates:
        assert d > start_date
        assert d < end_date


def test_chunk():
    data = pd.read_csv(test_data, parse_dates=['date'])
    data = data.set_index('date')
    train_part = data['2020-02-03']
    test_part = data['2020-02-04']
    targets = ['P1_filtr_mean', 'P2_filtr_mean']
    for t in targets:
        chunk = Chunk(train_part, test_part, features, t)
        assert len(chunk.get_x(1)) == 8 * 24 + len(features)

        for i in range(len(test_part)):
            assert chunk.get_y(forward_time=i) == test_part[t].values[i]
            assert chunk.get_y(forward_time=i, orig=True) == test_part.P_original.values[i]


def test_generate_chunks(monkeypatch):
    data = pd.read_csv(test_data, parse_dates=['date'])
    data = data.set_index('date')

    class MockChunk:
        def __init__(self, *args, **kwargs):
            pass

    monkeypatch.setattr('src.model.forecast.Chunk', MockChunk)

    targets = ['P1_filtr_mean', 'P2_filtr_mean']
    for t in targets:
        n = 42
        chunks = generate_chunks(data, n, data.index[0], data.index[-48], 48, 24, features, t)
        assert len(chunks) == n


def test_prepare_x(monkeypatch):
    data = pd.read_csv(test_data, parse_dates=['date'])
    data = data.set_index('date')

    test_len = 5
    monkeypatch.setattr('src.model.forecast.TEST_NUM_SAMPLES', test_len)
    monkeypatch.setattr('src.model.forecast.DATASET_START', '2019-02-01 00:00:00+00:00')

    factor = 5

    targets = ['P1_filtr_mean', 'P2_filtr_mean']
    for t in targets:
        x_train, x_test = prepare_x(data, chunk_len=48, test_len=24,
                                    test_dataset_len=5, num_chunks_factor=factor, target=t)
        assert len(x_test) == 5
        assert len(x_train) == round((len(data) - test_len * 24) / factor)


def test_model():
    targets = ['P1_filtr_mean', 'P2_filtr_mean']
    data = pd.read_csv(test_data, parse_dates=['date'])
    data = data.set_index('date')
    train_part = data['2020-02-03']
    test_part = data['2020-02-04']

    for t in targets:
        pref = t.split('_')[0]

        with open(os.path.join(model_path, pref + '_models.obj'), 'rb') as f:
            models = pickle.load(f)
        with open(os.path.join(model_path, pref + '_target_transform.obj'), 'rb') as f:
            target_transform = pickle.load(f)

        model = Model(target_transform, models)
        chunk = Chunk(train_part, test_part, features, t)
        prediction = model.predict(chunk)
        assert len(prediction) == 24
        for i in prediction:
            assert i > 0
            assert i < 150
