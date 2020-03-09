import pandas as pd
import pickle

from src.model.forecast import ForecastModel

p1_file = 'models/p1_forecast.obj'
p2_file = 'models/p2_forecast.obj'
data_file = 'src/model/tests/data/test_dataset_2.csv'


def test_forecast_model_smoke():
    data = pd.read_csv(data_file, parse_dates=['date'])
    with open(p1_file, 'rb') as p1_f, open(p2_file, 'rb') as p2_f:
        model_p1 = pickle.load(p1_f)
        model_p2 = pickle.load(p2_f)
        model = ForecastModel(model_p1, model_p2)
        pred_p1, pred_p2 = model.predict(data)
        assert len(model_p1) == len(pred_p1)
        assert len(model_p2) == len(pred_p2)
        for i in pred_p1:
            assert 0 < i < 100
        for i in pred_p2:
            assert 0 < i < 100
