import pandas as pd
import datetime
from typing import List
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.linear_model import Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import QuantileTransformer
import pickle
import json

from src.features.preproc_forecast import DataTransform

# columns that which will be used
columns = ['P1_filtr_mean', 'humidity_filtr_mean', 'temperature_filtr_mean', 'pres_meteo', 'temp_meteo',
           'hum_meteo', 'wind_direction',
           'wind_speed', 'prec_amount', 'prec_time']
# columns with numerical features
num_colunms = ['humidity_filtr_mean', 'temperature_filtr_mean', 'pres_meteo', 'temp_meteo', 'hum_meteo',
               'wind_speed', 'prec_amount', 'prec_time']
target_col = ['P1_filtr_mean']
CHUNK_LEN = 48  # in hours
TEST_LEN = 24  # in hours
TEST_NUM_SAMPLES = 300  # number of chunks which will be used for validation
# features which will be used for meta model training
features = ['pres_meteo', 'temp_meteo', 'hum_meteo', 'wind_speed', 'prec_amount',
            'sin_day', 'cos_day', 'sin_hour', 'cos_hour', 'wind_sin', 'wind_cos', 'temp_diff', 'humidity_diff',
            'pressure_diff', 'temp_diff3', 'humidity_diff3',
            'pressure_diff3']


class Chunk:
    """Chunk of time-series data. Each chunk consist train and test part."""

    def __init__(self, train_part, test_part, feature_names):
        self.train = train_part
        self.test = test_part
        self.features = feature_names

    def get_x(self):
        x = list(self.train.P1_filtr_mean.values)
        x += list(self.train.P1_diff1.values)
        x += list(self.train.P1_diff2.values)
        x += list(self.train.P1_diff3.values)

        x += list(self.train.temperature_filtr_mean.values)
        x += list(self.train.t_diff.values)
        x += list(self.train.t_diff1.values)
        x += list(self.train.t_diff2.values)

        return x

    def get_y(self, forward_time, orig=False):
        if orig:
            return self.test.P1_original.values[forward_time]
        y = self.test.P1_filtr_mean.values[forward_time]
        return y

    def get_meta_x(self, forward_time, models):
        x = self.get_x()
        model = models[forward_time]
        prediction = model.predict([x])[0]
        x_meta = [prediction]
        for feature in self.features:
            x_meta.append(self.test[feature].values[forward_time])
        return x_meta


def pp(start: datetime.datetime, end: datetime.datetime, n: int) -> pd.DatetimeIndex:
    """Generate random DatetimeIndex with n items in [start, end] period
    Courtesy of: https://stackoverflow.com/questions/50559078/generating-random-dates-within-a-given-range-in-pandas
    """
    start_u = start.value // 10 ** 9
    end_u = end.value // 10 ** 9

    return pd.DatetimeIndex((10 ** 9 * np.random.randint(start_u, end_u, n, dtype=np.int64)).view('M8[ns]'))


def generate_chunks(series: pd.DataFrame, n: int, start: datetime.datetime, end: datetime.datetime,
                    chunk_len: int, test_len: int, features: List[str]) -> List[Chunk]:
    """
    generate list of chunks from dataframe
    :param series: initial dataframe
    :param n: number of chunks
    :param start: start date
    :param end: end date (must be with offset = chunk_len from the series end)
    :param chunk_len: len of chunks (in hours)
    :param test_len: len of test part inside chunk (in hours)
    :param features: features names columns (will be added in X_train during meta-model training)
    :return: list of chunks
    """
    chunks = []
    for idx in pp(start, end, n):
        train_part = series[str(idx):str(idx + datetime.timedelta(hours=chunk_len - test_len))]
        test_part = series[str(idx + datetime.timedelta(hours=chunk_len - test_len)):str(
            idx + datetime.timedelta(hours=chunk_len))]
        chunk = Chunk(train_part, test_part, features)
        chunks.append(chunk)
    return chunks


def prepare_x(data: pd.DataFrame, chunk_len: int,
              test_len: int, num_chunks_factor=3.2,
              test_dataset_len=50, meta_train_fraction=0.5) -> (List[Chunk], List[Chunk], List[Chunk]):
    """
    Prepare X_train, X_meta_train, X_validation
    :param data: dataset
    :param chunk_len: len of single chunk in hourse
    :param test_len: len of test part of single chunk in hourse
    :param num_chunks_factor: factor for relative determination of chunks number based on dataset len
    :param meta_train_fraction: fraction of train to meta-model training
    :param test_dataset_len: len of validation dataset (in days)
    :return:
    """
    train_data = data['2019-04-02 00:00:00+00:00':str(data.index[-1] - datetime.timedelta(days=50))]
    test_data = data[str(data.index[-1] - datetime.timedelta(days=test_dataset_len)):]

    train_start_idx = train_data.index[0]
    train_end_idx = train_data.index[-1] - datetime.timedelta(hours=chunk_len)
    train_num_samples = round(len(train_data) / num_chunks_factor)
    np.random.seed(42)
    train_chunks = generate_chunks(train_data, train_num_samples,
                                   train_start_idx, train_end_idx,
                                   chunk_len, test_len, features)

    test_start_idx = test_data.index[0]
    test_end_idx = test_data.index[-1] - datetime.timedelta(hours=chunk_len)
    validation = generate_chunks(test_data, TEST_NUM_SAMPLES,
                                 test_start_idx, test_end_idx,
                                 chunk_len, test_len,
                                 features)

    train, train_meta = train_test_split(train_chunks, test_size=meta_train_fraction, random_state=42)
    return train, train_meta, validation


class Model:

    def __init__(self, data_transform: DataTransform, models=None, meta_models=None):
        self.data_transform = data_transform
        self.models = models
        self.meta_models = meta_models

    def fit(self, x_train, x_meta_train):
        model = Lasso(alpha=0.005, random_state=42, max_iter=3000)
        self._train_models(model, x_train, TEST_LEN)
        meta_model = RandomForestRegressor(min_samples_leaf=3, random_state=42)
        self._train_meta_models(meta_model, x_meta_train, TEST_LEN)

    def predict(self, chunk: Chunk):
        predictions = []
        for i in range(len(self.models)):
            x = [chunk.get_meta_x(i, self.models)]
            local_model = self.meta_models[i]
            prediction = local_model.predict(x)
            prediction = self.data_transform.target_transform.inverse_transform(prediction.reshape(-1, 1))[0][0]
            predictions.append(prediction)
        return predictions

    def get_metric(self, chunks: List[Chunk], metric) -> List[float]:
        scores = []
        for i in range(len(self.models)):
            x = [chunk.get_x() for chunk in chunks]
            local_model = self.models[i]
            prediction = local_model.predict(x)
            prediction = self.data_transform.target_transform.inverse_transform(prediction.reshape(-1, 1))
            y = [chunk.get_y(i, orig=True) for chunk in chunks]
            mae = metric(y, prediction)
            scores.append(mae)
        return scores

    def get_meta_metric(self, chunks: List[Chunk], metric) -> List[float]:
        scores = []
        for i in range(len(self.models)):
            x = [chunk.get_meta_x(i, self.models) for chunk in chunks]
            local_model = self.meta_models[i]
            prediction = local_model.predict(x)
            prediction = self.data_transform.target_transform.inverse_transform(prediction.reshape(-1, 1))
            y = [chunk.get_y(i, orig=True) for chunk in chunks]
            mae = metric(y, prediction)
            scores.append(mae)
        return scores

    def _train_models(self, model, chunks: List[Chunk], num_models):
        self.models = []
        for i in range(num_models):
            x = [chunk.get_x() for chunk in chunks]
            local_model = clone(model)
            y = [chunk.get_y(i) for chunk in chunks]
            local_model.fit(x, y)
            self.models.append(local_model)

    def _train_meta_models(self, meta_model, chunks: List[Chunk], num_models):
        self.meta_models = []
        for i in range(num_models):
            x = [chunk.get_meta_x(i, self.models) for chunk in chunks]
            local_model = clone(meta_model)
            y = [chunk.get_y(i) for chunk in chunks]
            local_model.fit(x, y)
            self.meta_models.append(local_model)


def main():
    data = pd.read_csv('DATA/processed/dataset.csv', parse_dates=['date'])
    data = data.set_index('date')
    data_transform = QuantileTransformer(output_distribution='normal')
    target_transform = QuantileTransformer(output_distribution='normal')
    transform = DataTransform(data_transform, target_transform, columns, num_colunms, target_col)
    data = transform.fit_transform(data)
    x_train, x_meta_train, x_val = prepare_x(data, CHUNK_LEN, TEST_LEN)
    model = Model(transform)
    model.fit(x_train, x_meta_train)
    print('MAE: ;', model.get_metric(x_val, mean_absolute_error))
    print('MSE: ;', model.get_metric(x_val, mean_squared_error))
    print('meta_MAE: ;', model.get_meta_metric(x_val, mean_absolute_error))
    print('meta_MSE: ;', model.get_meta_metric(x_val, mean_squared_error))


if __name__ == '__main__':
    main()