import pandas as pd
import datetime
from sklearn.model_selection import train_test_split
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error
from sklearn.linear_model import Lasso

from src.features.preproc_forecast import prepare_features, generate_chunks, prepare_data_from_chunks

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


def get_mae(models, X_test, y_test, y_columns):
    scores = []
    for i in range(len(y_columns)):
        local_model = models[i]
        prediction = local_model.predict(X_test)
        mae = mean_absolute_error(y_test[y_columns[i]], prediction)
        scores.append(mae)
    return scores


def train_forecast(dataset_file: str, target_column: str):
    # prepare data
    data = pd.read_csv(dataset_file, parse_dates=['date'])
    data = data.set_index('date')
    data = data[columns]
    data = prepare_features(data)

    # split chunks
    start_idx = data.index[0]
    end_idx = data.index[-1] - datetime.timedelta(days=2)
    chunks = generate_chunks(data, num_samples, start_idx, end_idx)
    df = prepare_data_from_chunks(chunks, target_column, columns)

    # prepare test and train
    x_columns = [i for i in df.columns if 'P1_forec_' not in i]
    y_columns = [i for i in df.columns if 'P1_forec_' in i]
    X, y = df[x_columns], df[y_columns]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # train and evaluate models
    mod = Lasso(alpha=0.2, max_iter=2000)
    models = train_models(mod, X_train, y_train, y_columns)
    mae = get_mae(models, X_test, y_test, y_columns)
    return models, mae


if __name__ == '__main__':
    data_file = 'DATA/processed/dataset.csv'
    _, mae = train_forecast(data_file, 'P1')
    print(mae)
