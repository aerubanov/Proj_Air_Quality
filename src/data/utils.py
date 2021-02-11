import typing
import pandas as pd
from datetime import timezone
import os

from src.data.config import SENSOR_DATA_FOLDER


def get_sensors_loc(sensors_list: typing.List[str]) -> pd.DataFrame:
    """
    get location of sensors from sensors_list
    :param sensors_list: list of sensor file paths
    :return: dataframe with sensor locations
    """
    sensors_data = []
    for i in sensors_list:
        try:
            data = pd.read_csv(i, delimiter=';', nrows=2)
            s_id = data.iloc[-1].sensor_id
            s_type = data.iloc[-1].sensor_type
            lat = data.iloc[-1].lat
            lon = data.iloc[-1].lon
            sensors_data.append([s_id, s_type, lat, lon])
        except (pd.errors.ParserError, pd.errors.EmptyDataError,
                pd.core.groupby.groupby.DataError, KeyError):
            pass
    sens_loc = pd.DataFrame(sensors_data, columns=['sensor_id', 'sensor_type', 'lat', 'lon'])
    return sens_loc


def combine_sensors(sensors: pd.DataFrame) -> pd.DataFrame:
    """combine sds and bme sensor with same location in one row"""
    sds_sensors = sensors[sensors.sensor_type == 'SDS011']
    bme_sensors = sensors[sensors.sensor_type == 'BME280']
    sensors = (sds_sensors.assign(dummy=1)
               .merge(bme_sensors.assign(dummy=1), on='dummy')
               .query('lat_x==lat_y and lon_x==lon_y')
               .drop('dummy', axis=1))[['sensor_id_x', 'sensor_id_y', 'lat_x', 'lon_x']]
    sensors = sensors.rename(columns={'sensor_id_x': 'sds_sensor',
                                      'sensor_id_y': 'bme_sensor',
                                      'lat_x': 'lat',
                                      'lon_x': 'lon'})
    return sensors


def get_sealevel_alt(bme_id: int, press_meteo: pd.Series) -> float:
    """
    Calculate sensor altitude based on ddifference in pressure.
    See details https://ru.wikipedia.org/wiki/Барометрическая_ступень"""
    file_name = f'{bme_id}_bme280_sensor_.csv'
    bme_data = pd.read_csv(os.path.join(SENSOR_DATA_FOLDER, file_name), sep=';', parse_dates=['timestamp'])
    bme_data = bme_data.set_index('timestamp').resample('5T').mean()
    bme_data = bme_data.tz_localize(timezone.utc)
    bme_data['press_diff'] = (bme_data['pressure'] - press_meteo) / 1000
    bme_data['Q'] = 8000/(bme_data.pressure/1000) * (1 + 0.00366*bme_data.temperature)
    bme_data['delta_h'] = - bme_data.Q * bme_data.press_diff
    delta_h = bme_data.delta_h.median()
    h = delta_h + 125  # высота метеостанции над уровнем моря
    return h


def get_weather_data(weather_file: str) -> pd.DataFrame:
    """
    Select and resample weather data
    :param weather_file: path to raw data file
    :return: processed data
    """
    def parser(date): return pd.to_datetime(date, format='%d.%m.%Y %H:%M')
    data = pd.read_csv(weather_file, delimiter=';', parse_dates=['Местное время в Москве (центр, Балчуг)'],
                       date_parser=parser,
                       index_col=False)
    data = data.rename(columns={'Местное время в Москве (центр, Балчуг)': 'date'})
    data = data.set_index('date')
    data.index = data.index.tz_localize(tz="Europe/Moscow").tz_convert('UTC')
    sel_data = pd.DataFrame(index=data.index)
    sel_data['temp_meteo'] = data['T']
    sel_data['pres_meteo'] = data.Po * 133.322  # transform mmHg in Pa
    sel_data['hum_meteo'] = data.U
    sel_data['wind_direction'] = data.DD
    sel_data['wind_speed'] = data.Ff
    sel_data['precipitation'] = data.W1
    sel_data['prec_amount'] = data.RRR
    sel_data['prec_time'] = data.tR
    sel_data['visibility'] = data.VV
    sel_data['dew_point_temp'] = data.Td
    meteo_data = sel_data.resample('5T').bfill()
    return meteo_data


def get_surface_level_alts(locations: typing.List[(float, float)]):


