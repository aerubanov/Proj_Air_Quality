import pandas as pd
import os
import multiprocessing
from functools import partial

from src.data.config import SENSOR_DATA_FOLDER, WEATHER_DATA_FOLDER, WEATHER_FILE
from src.data.utils import get_weather_data


def load_data(filename: str) -> pd.DataFrame:
    """load sensor data from file into pandas dataframe"""
    data = pd.read_csv(os.path.join(SENSOR_DATA_FOLDER, filename), sep=';', parse_dates=['timestamp'])
    data['timestamp'] = pd.to_datetime(data.timestamp, errors='coerce')
    data = data.set_index("timestamp")
    for col in data.columns:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    data = data.resample("1H").mean()
    return data


def get_sensor_data(bme_sensor_id: int, sds_sensor_id: int, sensors: pd.DataFrame) -> pd.DataFrame:
    """Get combined data from bme280 and sds011. Add spatial features for sensor location"""
    file_name = f'{bme_sensor_id}_bme280_sensor_.csv'
    bme_data = load_data(file_name)
    file_name = f'{sds_sensor_id}_sds011_sensor_.csv'
    sds_data = load_data(file_name)
    bme_data = bme_data[["pressure", "temperature", "humidity"]]
    sds_data = sds_data[["P1", "P2"]]
    data = sds_data.join(bme_data)
    for c in ['lat', 'lon', 'sealevel_alt',
              'surface_alt', 'nearest_park', 'nearest_road', 'nearest_indust']:
        data[c] = sensors[sensors.sds_sensor == sds_sensor_id][c].values[0]
    return data


def add_weather_data(sensor_data: pd.DataFrame, weather_data: pd.DataFrame) -> pd.DataFrame:
    """add weather data from meteo station"""
    sensor_data.index = sensor_data.index.tz_localize(tz="UTC")
    return sensor_data.join(weather_data)


def worker(bme_id: int, sds_id: int, weather_data: pd.DataFrame, sensors: pd.DataFrame) -> pd.DataFrame:
    """Using to run data collection im multiple processes"""
    sensor_data = get_sensor_data(bme_id, sds_id, sensors)
    sensor_data = add_weather_data(sensor_data, weather_data)
    return sensor_data.reset_index()


if __name__ == '__main__':
    sens = pd.read_csv("DATA/processed/sensors.csv")
    bme_sensor = sens.bme_sensor.values
    sds_sensor = sens.sds_sensor.values
    weather = get_weather_data(os.path.join(WEATHER_DATA_FOLDER, WEATHER_FILE))
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.starmap(partial(worker, weather_data=weather, sensors=sens), zip(bme_sensor, sds_sensor))
    dataset = pd.concat(results)
    dataset.to_csv('DATA/processed/dataset.csv')
    print(dataset.head())
