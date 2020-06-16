import datetime
import pandas as pd
import pickle
import re

from src.web.models.model import Sensors, Weather, Forecast
from src.model.forecast import Model, Chunk, columns, num_colunms, features
from src.features.preproc_forecast import DataTransform

p1_models_file = "models/forecast/P1_models.obj"
p1_meta_models_file = "models/forecast/P1_meta_models.obj"
p1_data_trans_file = "models/forecast/P1_data_transform.obj"
p1_target_trans_file = "models/forecast/P1_target_transform.obj"

p2_models_file = "models/forecast/P2_models.obj"
p2_meta_models_file = "models/forecast/P2_meta_models.obj"
p2_data_trans_file = "models/forecast/P2_data_transform.obj"
p2_target_trans_file = "models/forecast/P2_target_transform.obj"


def get_sensor_data(session, date=None) -> pd.DataFrame:
    """get sensor data for time interval [date-1day, date]"""
    if date is None:
        date = datetime.datetime.utcnow()

    # get sensor data for Chunk.train
    result = session.query(Sensors).filter(Sensors.date >= date - datetime.timedelta(days=1))
    result = [i.serialize for i in result]
    data = pd.DataFrame(result)
    data = data.rename(columns={'p1': 'P1_filtr_mean', 'p2': 'P2_filtr_mean', 'temperature': 'temperature_filtr_mean',
                                'humidity': 'humidity_filtr_mean'})
    data['date'] = pd.to_datetime(data.date)
    data = data.set_index('date')
    return data.resample('5T').mean()


def transform_prec_amount(x):
    """extract precipitations amount from string stored in database"""
    numbers = re.findall(r'\d*\.\d+|\d+', x)
    if len(numbers) > 0:
        return numbers[0]
    else:
        return 0


wind_dir = {'В': 'Ветер, дующий с востока',
            'С-В': 'Ветер, дующий с северо-востока',
            'С': 'Ветер, дующий с севера',
            'С-З': 'Ветер, дующий с северо-запада',
            'З': 'Ветер, дующий с запада',
            'Ю-З': 'Ветер, дующий с юго-запада',
            'Ю': 'Ветер, дующий с юга',
            'Ю-В': 'Ветер, дующий с юго-востока',
            'ШТЛ': 'Штиль, безветрие',
            }


def get_weather_data(session, date=None) -> pd.DataFrame:
    """ get weather data for time interval [date-1day, date]"""
    res = session.query(Weather).filter(Weather.date >= date - datetime.timedelta(days=1)).all()
    data = [i.serialize for i in res]
    data = pd.DataFrame(data)
    data['date'] = pd.to_datetime(data.date)
    data = data.rename(columns={'temp': 'temp_meteo', 'press': 'pres_meteo',
                                'prec': 'prec_amount', 'wind_speed': 'wind_speed',
                                'wind_dir': 'wind_direction', 'hum': 'hum_meteo'})
    data['prec_amount'] = data.prec_amount.apply(transform_prec_amount).astype(float)
    data['prec_time'] = 3.0
    data['wind_direction'] = data.wind_direction.map(wind_dir)
    data = data.set_index('date')
    return data.resample('5T').bfill()


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
    weather_data = get_sensor_data(session)
    train_part = pd.concat((sensor_data, weather_data), axis=1)
    train_part = transform.transform(train_part)
    test_part = get_weather_data(session, date=datetime.datetime.utcnow()+datetime.timedelta(days=1))
    for c in ['P1_filtr_mean', 'P2_filtr_mean', 'humidity_filtr_mean', 'temperature_filtr_mean']:
        test_part[c] = train_part[c].mean()
    test_part = transform.transform(test_part)
    chunk = Chunk(train_part, test_part, features, target)
    return chunk


def get_model(target: str, target_transform) -> Model:
    """construct Model from pickled objects"""
    if target == 'P1_filtr_mean':
        file1 = p1_models_file
        file2 = p1_meta_models_file
    else:
        file1 = p2_models_file
        file2 = p2_meta_models_file
    with open(file1, 'rb') as models_file, open(file2, 'rb') as meta_models_file:
        models = pickle.load(models_file)
        meta_models = pickle.load(meta_models_file)
    model = Model(target_transform, models, meta_models, target)
    return model


def perform_forecast(session, date=None, logger=None):
    """make forecast for date + 24 hours and write it in database"""
    targets = ['P1_filtr_mean, P2_filtr_mean']
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
