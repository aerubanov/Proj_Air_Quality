import pandas as pd
import datetime
from sklearn.model_selection import train_test_split
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error
from sklearn.linear_model import Lasso
import pickle
import json

from src.features.preproc_forecast import prepare_features, generate_chunks, prepare_data_from_chunks,\
    prepare_test_sample

columns = [
    'P1', 'P2', 'pressure', 'temperature', 'humidity',
]
num_samples = 1500


def train_models(model, x_train, y_train, y_columns):
    models = []
    for i in range(len(y_columns)):
        local_model = clone(model)
        local_model.fit(x_train, y_train[y_columns[i]])
        models.append(local_model)
    return models


def get_mae(models, x_test, y_test, y_columns):
    scores = []
    for i in range(len(y_columns)):
        local_model = models[i]
        prediction = local_model.predict(x_test)
        mae = mean_absolute_error(y_test[y_columns[i]], prediction)
        scores.append(mae)
    return scores


def train_forecast(dataset_file: str, target_column: str):
    # prepare data
    data = pd.read_csv(dataset_file, parse_dates=['date'])
    data = data.set_index('date')
    data = data[columns]
    data = prepare_features(data)
    data = data.resample('1H').mean()

    # split chunks
    start_idx = data.index[0]
    end_idx = data.index[-1] - datetime.timedelta(days=2)
    chunks = generate_chunks(data, num_samples, start_idx, end_idx)
    df = prepare_data_from_chunks(chunks, target_column, columns)

    # prepare test and train
    x_columns = [i for i in df.columns if f'{target_column}_forec_' not in i]
    y_columns = [i for i in df.columns if f'{target_column}_forec_' in i]
    x, y = df[x_columns], df[y_columns]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)

    # train and evaluate models
    mod = Lasso(alpha=0.2, max_iter=2000)
    models = train_models(mod, x_train, y_train, y_columns)
    mae = get_mae(models, x_test, y_test, y_columns)
    return models, mae


def main(p1_model_file: str, p2_model_file: str, metrics_file: str):
    data_file = 'DATA/processed/dataset.csv'
    p1_models, p1_mae = train_forecast(data_file, 'P1')
    print('P1 mae: ', p1_mae)
    with open(p1_model_file, 'wb') as f:
        pickle.dump(p1_models, f)
    p2_models, p2_mae = train_forecast(data_file, 'P2')
    print('P2 mae: ', p2_mae)
    with open(p2_model_file, 'wb') as f:
        pickle.dump(p2_models, f)
    with open(metrics_file, "w") as f:
        json.dump({'p1_mae': p1_mae, 'p2_mae': p2_mae}, f)


class ForecastModel:
    """forecast trained model evaluation"""

    def __init__(self, models_p1, models_p2):
        self.p1_models = models_p1
        self.p2_models = models_p2

    @staticmethod
    def prepare_data(data: pd.DataFrame):
        data = data.set_index('date')
        data = data[columns]
        data = prepare_features(data)
        data = data.resample('1H').mean()
        x1 = prepare_test_sample(data, columns, 'P1')
        x2 = prepare_test_sample(data, columns, 'P2')
        return x1, x2

    def predict(self, x_test: pd.DataFrame):
        x1, x2 = self.prepare_data(x_test)
        p1_predictions = []
        for i in range(len(self.p1_models)):
            local_model = self.p1_models[i]
            prediction = local_model.predict(x1)[0]
            p1_predictions.append(prediction)
        p2_predictions = []
        for i in range(len(self.p2_models)):
            local_model = self.p2_models[i]
            prediction = local_model.predict(x2)[0]
            p2_predictions.append(prediction)
        return p1_predictions, p2_predictions


if __name__ == '__main__':
    model_p1 = 'models/p1_forecast.obj'
    model_p2 = 'models/p2_forecast.obj'
    metrics = 'DATA/metrics/forecast_metrics.json'
    main(model_p1, model_p2, metrics)
