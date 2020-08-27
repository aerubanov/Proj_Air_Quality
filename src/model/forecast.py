import pandas as pd
import datetime
from typing import List
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.linear_model import Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import QuantileTransformer
import pickle
import json
import os

from src.features.preproc_forecast import DataTransform

pd.options.mode.chained_assignment = None  # disable SettingWithCopyWarning

# Build models for PM2.5 and PM10 forecast for next 24-hours, separate model for each hour. We use model
# ansamble from two models. Firstly, Linear model take sensor data from previous 24-hours and predict PM. Next,
# Random Forest take this prediction and weather forecast (from external source) as input and make final prediction.


# ------------------- constants ----------------------------------------------------------------------------
# columns of dataset which will be used
columns = ['P1_filtr_mean', 'P2_filtr_mean', 'humidity_filtr_mean', 'temperature_filtr_mean', 'pres_meteo',
           'temp_meteo', 'hum_meteo', 'wind_direction', 'wind_speed', 'prec_amount', 'prec_time']
# columns with numerical features
num_colunms = ['humidity_filtr_mean', 'temperature_filtr_mean', 'pres_meteo', 'temp_meteo', 'hum_meteo',
               'wind_speed', 'prec_amount', 'prec_time']
CHUNK_LEN = 48  # in hours
TEST_LEN = 24  # in hours
TEST_NUM_SAMPLES = 300  # number of chunks which will be used for validation
# features which will be used for meta model training
features = ['pres_meteo', 'temp_meteo', 'hum_meteo', 'wind_speed', 'prec_amount',
            'sin_day', 'cos_day', 'sin_hour', 'cos_hour', 'wind_sin', 'wind_cos', 'temp_diff', 'humidity_diff',
            'pressure_diff', 'temp_diff3', 'humidity_diff3',
            'pressure_diff3']
DATASET_START = '2019-04-02 00:00:00+00:00'

model_path = 'models/forecast'
metric_path = 'DATA/metrics/forecast_metrics.json'
data_path = 'DATA/processed/dataset.csv'
# -------------------------------------------------------------------------------------------------------------


class Chunk:
    """Chunk of time-series data. Each chunk consist train and test part."""

    def __init__(self, train_part, test_part, feature_names, target):
        self.train = train_part
        self.test = test_part
        self.features = feature_names
        self.target = target

    def get_x(self, forward_time):
        """return X - sensor values from previous 24-hours"""
        x = list(self.train[self.target].values)
        x += list(self.train.P_diff1.values)
        x += list(self.train.P_diff2.values)
        x += list(self.train.P_diff3.values)

        x += list(self.train.temperature_filtr_mean.values)
        x += list(self.train.t_diff.values)
        x += list(self.train.t_diff1.values)
        x += list(self.train.t_diff2.values)
        for feature in self.features:
            x.append(self.test[feature].values[forward_time])
        return x

    def get_y(self, forward_time, orig=False):
        """return target value for some forvard time in next 24-hours"""
        if orig:
            return self.test.P_original.values[forward_time]
        y = self.test[self.target].values[forward_time]
        return y


def pp(start: pd.DatetimeIndex, end: pd.DatetimeIndex, n: int) -> pd.DatetimeIndex:
    """Generate random DatetimeIndex with n items in [start, end] period
    Courtesy of: https://stackoverflow.com/questions/50559078/generating-random-dates-within-a-given-range-in-pandas
    """
    start_u = start.value // 10 ** 9
    end_u = end.value // 10 ** 9

    return pd.DatetimeIndex((10 ** 9 * np.random.randint(start_u, end_u, n, dtype=np.int64)).view('M8[ns]'))


def generate_chunks(series: pd.DataFrame, n: int, start: pd.DatetimeIndex, end: pd.DatetimeIndex,
                    chunk_len: int, test_len: int, features_list: List[str], target) -> List[Chunk]:
    """
    generate list of chunks from dataframe
    :param target: name of target column
    :param series: initial dataframe
    :param n: number of chunks
    :param start: start date
    :param end: end date (must be with offset = chunk_len from the series end)
    :param chunk_len: len of chunks (in hours)
    :param test_len: len of test part inside chunk (in hours)
    :param features_list: features names columns (will be added in X_train during meta-model training)
    :return: list of chunks
    """
    chunks = []
    for idx in pp(start, end, n):
        train_part = series[str(idx):str(idx + datetime.timedelta(hours=chunk_len - test_len))]
        test_part = series[str(idx + datetime.timedelta(hours=chunk_len - test_len)):str(
            idx + datetime.timedelta(hours=chunk_len))]
        chunk = Chunk(train_part, test_part, features_list, target)
        chunks.append(chunk)
    return chunks


def prepare_x(data: pd.DataFrame, chunk_len: int,
              test_len: int, target, num_chunks_factor=3.2,
              test_dataset_len=50) -> (List[Chunk], List[Chunk], List[Chunk]):
    """
    Prepare X_train, X_meta_train, X_validation
    :param target: name of target column
    :param data: dataset
    :param chunk_len: len of single chunk in hourse
    :param test_len: len of test part of single chunk in hourse
    :param num_chunks_factor: factor for relative determination of chunks number based on dataset len
    :param meta_train_fraction: fraction of train to meta-model training
    :param test_dataset_len: len of validation dataset (in days)
    :return:
    """
    train_data = data[DATASET_START:str(data.index[-1] - datetime.timedelta(days=test_dataset_len))]
    test_data = data[str(data.index[-1] - datetime.timedelta(days=test_dataset_len)):]

    train_start_idx = train_data.index[0]
    train_end_idx = train_data.index[-1] - datetime.timedelta(hours=chunk_len)
    train_num_samples = round(len(train_data) / num_chunks_factor)
    np.random.seed(42)
    train_chunks = generate_chunks(train_data, train_num_samples,
                                   train_start_idx, train_end_idx,
                                   chunk_len, test_len, features, target)

    test_start_idx = test_data.index[0]
    test_end_idx = test_data.index[-1] - datetime.timedelta(hours=chunk_len)
    validation = generate_chunks(test_data, TEST_NUM_SAMPLES,
                                 test_start_idx, test_end_idx,
                                 chunk_len, test_len,
                                 features, target)

    return train_chunks, validation


class Model:

    def __init__(self, target_transform, models=None, target='P1_filtr_mean'):
        self.target_transform = target_transform
        self.models = models
        self.target = target

    def fit(self, x_train):
        model = GradientBoostingRegressor(random_state=42, n_estimators=50, verbose=0, n_iter_no_change=4)
        self._train_models(model, x_train, TEST_LEN)

    def predict(self, chunk: Chunk):
        predictions = []
        for i in range(len(self.models)):
            x = [chunk.get_x(i)]
            local_model = self.models[i]
            prediction = local_model.predict(x)
            prediction = self.target_transform.inverse_transform(prediction.reshape(-1, 1))[0][0]
            predictions.append(prediction)
        return predictions

    def get_metric(self, chunks: List[Chunk], metric) -> List[float]:
        scores = []
        for i in range(len(self.models)):
            x = [chunk.get_x(i) for chunk in chunks]
            local_model = self.models[i]
            prediction = local_model.predict(x)
            prediction = self.target_transform.inverse_transform(prediction.reshape(-1, 1))
            y = [chunk.get_y(i, orig=True) for chunk in chunks]
            mae = metric(y, prediction)
            scores.append(mae)
        return scores

    def _train_models(self, model, chunks: List[Chunk], num_models):
        self.models = []
        for i in range(num_models):
            x = [chunk.get_x(i) for chunk in chunks]
            local_model = clone(model)
            y = [chunk.get_y(i) for chunk in chunks]
            local_model.fit(x, y)
            self.models.append(local_model)


def train_model(target):
    """train models for PM2.5 and PM10 and save it with pickle"""
    data = pd.read_csv(data_path, parse_dates=['date'])
    data = data.set_index('date')
    data_transform = QuantileTransformer(output_distribution='normal')
    target_transform = QuantileTransformer(output_distribution='normal')
    transform = DataTransform(data_transform, target_transform, columns, num_colunms, target)
    data = transform.fit_transform(data)
    x_train, x_val = prepare_x(data, CHUNK_LEN, TEST_LEN, target)

    model = Model(transform.target_transform)
    model.fit(x_train)

    mae = model.get_metric(x_val, mean_absolute_error)
    mse = model.get_metric(x_val, mean_squared_error)

    print('MAE: ;', np.mean(mae))
    print('MSE: ;', np.mean(mse))

    prefix = target.split('_')[0]
    with open(os.path.join(model_path, prefix+'_models.obj'), 'wb') as f:
        pickle.dump(model.models, f)
    with open(os.path.join(model_path, prefix+'_data_transform.obj'), 'wb') as f:
        pickle.dump(transform.train_transform, f)
    with open(os.path.join(model_path, prefix+'_target_transform.obj'), 'wb') as f:
        pickle.dump(transform.target_transform, f)

    return mae, mse


if __name__ == '__main__':
    try:
        os.mkdir('models/forecast/')
    except FileExistsError:
        pass
    p1_mae, p1_mse = train_model(target='P1_filtr_mean')
    p2_mae, p2_mse = train_model(target='P2_filtr_mean')
    with open(metric_path, 'w') as file:
        json.dump({'p1_mae': p1_mae, 'p1_mse': p1_mse,
                   'p2_mae': p2_mae, 'p2_mse': p2_mse}, file)
