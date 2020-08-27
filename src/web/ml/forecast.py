import datetime
import pandas as pd
import pickle

from src.web.models.model import Forecast
from src.model.forecast import Model, Chunk, columns, num_colunms, features
from src.features.preproc_forecast import DataTransform, add_features
from src.web.ml.data_loading import get_weather_data, get_sensor_data

p1_models_file = "models/forecast/P1_models.obj"
p1_data_trans_file = "models/forecast/P1_data_transform.obj"
p1_target_trans_file = "models/forecast/P1_target_transform.obj"

p2_models_file = "models/forecast/P2_models.obj"
p2_data_trans_file = "models/forecast/P2_data_transform.obj"
p2_target_trans_file = "models/forecast/P2_target_transform.obj"


def get_transforms(target: str) -> DataTransform:
    """construct DataTransform from pickled objects"""
    if target == 'P1_filtr_mean':
        file1 = p1_data_trans_file
        file2 = p1_target_trans_file
    else:
        file1 = p2_data_trans_file
        file2 = p2_target_trans_file
    with open(file1, 'rb') as data_tr, open(file2, 'rb') as target_tr:
        data_transform = pickle.load(data_tr)
        target_transform = pickle.load(target_tr)
        transform = DataTransform(data_transform, target_transform, columns, num_colunms, target)
    return transform


def get_chunk(session, transform: DataTransform, target: str) -> Chunk:
    """create chunk of time-series data for forecast model"""
    sensor_data = get_sensor_data(session)
    weather_data = get_weather_data(session)
    train_part = pd.concat((sensor_data, weather_data), axis=1)
    train_data = transform.transform(train_part)
    test_part = get_weather_data(session, date=datetime.datetime.utcnow()+datetime.timedelta(days=1))
    for c in ['P1_filtr_mean', 'P2_filtr_mean', 'humidity_filtr_mean', 'temperature_filtr_mean']:
        test_part[c] = train_part[c].mean()
    test_data = transform.transform(test_part)
    train_data = add_features(train_data, target)
    test_data = add_features(test_data, target)
    train_data = train_data.interpolate()
    test_data = test_data.interpolate()
    train_data = train_data.fillna(train_data.mean())
    train_data = train_data[:24]
    test_data = test_data.fillna(train_data.mean())
    chunk = Chunk(train_data, test_data, features, target)
    return chunk


def get_model(target: str, target_transform) -> Model:
    """construct Model from pickled objects"""
    if target == 'P1_filtr_mean':
        file = p1_models_file
    else:
        file = p2_models_file

    with open(file, 'rb') as models_file:
        models = pickle.load(models_file)
    model = Model(target_transform, models, target)
    return model


def perform_forecast(session, date=None, logger=None):
    """make forecast for date + 24 hours and write it in database"""
    if date is None:
        date = datetime.datetime.utcnow()
    targets = ['P1_filtr_mean', 'P2_filtr_mean']
    predictions = []
    for targ in targets:
        transform = get_transforms(targ)
        chunk = get_chunk(session, transform, targ)
        model = get_model(targ, transform.target_transform)
        pred = model.predict(chunk)
        predictions.append(pred)
    p1_predictions, p2_predictions = predictions
    for i in range(len(p1_predictions)):
        forec = Forecast(date=date, p1=p1_predictions[i],
                         p2=p2_predictions[i], forward_time=i + 1)
        session.add(forec)
        session.commit()
    if logger is not None:
        logger.info(f'Make forecast update')
