import pandas as pd
import os
import datetime
import typing
import numpy as np

from src.data.config import SENSOR_ID_FILE, SENSOR_DATA_FOLDER, WEATHER_FILE, WEATHER_DATA_FOLDER

# This script create dataset with sensor average data and weather data from raw downloaded data

START_DATE = datetime.date(2019, 4, 1)  # start date for dataset creation
END_DATE = datetime.date.today() - datetime.timedelta(days=1)  # end date for dataset reation


def combine_data(files_list: typing.List[str], column: str,
                 start_date=START_DATE, end_date=END_DATE) -> pd.DataFrame:
    """
    combine data from different sensor files in one dataframe
    :param files_list: paths to files
    :param column: selected data column
    :param start_date: first date in results dataframe
    :param end_date: last date in results dataframe
    :return: dataframe with data from all files in files_list
    """
    idx = pd.date_range(start_date, end_date, freq='5T')
    data_comb = pd.DataFrame(index=idx)
    for file in files_list:
        try:
            local_data = pd.read_csv(file, delimiter=';', parse_dates=['timestamp'], index_col=5)
            local_data = local_data[[column]]
            local_data = local_data[str(start_date):].resample('5T').mean()
            local_data = local_data.reindex(idx, fill_value=None)
            data_comb[file] = local_data[column]
        except (pd.errors.ParserError, pd.errors.EmptyDataError,
                pd.core.groupby.groupby.DataError, KeyError, AssertionError) as e:
            print(str(e), file)
    return data_comb


def filtered_average(row: pd.Series) -> float:
    """filter outliers and calculate mean"""
    data = row.values[~np.isnan(row.values)]
    q10 = np.quantile(data, q=0.1)
    q90 = np.quantile(data, q=0.9)
    data = data[data < q90]
    data = data[data > q10]
    return data.mean()


def calc_percentiles(data: pd.DataFrame, name: str) -> pd.DataFrame:
    """
    Calculate percentiles for each row in dataframe
    :param data: input data
    :param name: base name for columns in output
    :return: new dataframe
    """
    result = pd.DataFrame(index=data.index)
    result[name+'_p10'] = data.quantile(q=0.1, axis=1)
    result[name+'_p25'] = data.quantile(q=0.25, axis=1)
    result[name+'_p50'] = data.quantile(q=0.5, axis=1)
    result[name+'_p75'] = data.quantile(q=0.75, axis=1)
    result[name+'_p90'] = data.quantile(q=0.9, axis=1)
    result[name] = data.mean(axis=1)
    result[name+'_filtr_mean'] = data.dropna(how='all').apply(filtered_average, axis=1)
    return result


def get_file_list(data_folder: str, sensor_type: str):
    files = os.listdir(data_folder)
    sensor_list = [i for i in files if sensor_type in i]
    with open(SENSOR_ID_FILE, 'r') as sf:
        sensor_id_list = sf.read().splitlines()
        indoor_sensors = [i for i in sensor_id_list if 'indoor' in i]
    sensor_list = [i for i in sensor_list if i.split('_')[0] not in indoor_sensors]
    sensor_list = [os.path.join(data_folder, i) for i in sensor_list]
    return sensor_list


def get_sensors_loc(sensors_list: typing.List[str]) -> pd.DataFrame:
    """
    get location of sensors from sensors_list
    :param sensors_list: list of sensor file paths
    :return: dataframe with sensor locations
    """
    sensors_data = []
    for i in sensors_list:
        try:
            data = pd.read_csv(i, delimiter=';')
            s_id = data.iloc[-1].sensor_id
            s_type = data.iloc[-1].sensor_type
            lat = data.iloc[-1].lat
            lon = data.iloc[-1].lon
            sensors_data.append([s_id, s_type, lat, lon])
        except (pd.errors.ParserError, pd.errors.EmptyDataError,
                pd.core.groupby.groupby.DataError, KeyError, AssertionError):
            pass
    sens_loc = pd.DataFrame(sensors_data, columns=['sensor_id', 'sensor_type', 'lat', 'lon'])
    return sens_loc


def get_sensor_data(data_folder: str) -> (pd.DataFrame, pd.DataFrame):
    sds_files = get_file_list(data_folder, 'sds011')
    bme_files = get_file_list(data_folder, 'bme280')

    p1_data = combine_data(sds_files, 'P1')
    p2_data = combine_data(sds_files, 'P2')
    temp_data = combine_data(bme_files, 'temperature')
    press_data = combine_data(bme_files, 'pressure')
    hum_data = combine_data(bme_files, 'humidity')

    perc_p1 = calc_percentiles(p1_data, 'P1')
    perc_p2 = calc_percentiles(p2_data, 'P2')
    perc_press = calc_percentiles(press_data, 'pressure')
    perc_hum = calc_percentiles(hum_data, 'humidity')
    perc_temp = calc_percentiles(temp_data, 'temperature')

    sensor_data = pd.concat((perc_p1, perc_p2, perc_temp, perc_hum, perc_press), axis=1)
    sensors_location = get_sensors_loc(sds_files+bme_files)
    return sensor_data, sensors_location


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


def main():
    avg_data, sensors = get_sensor_data(SENSOR_DATA_FOLDER)
    avg_data.index = avg_data.index.tz_localize(tz="UTC")
    meteo_data = get_weather_data(os.path.join(WEATHER_DATA_FOLDER, WEATHER_FILE))
    data = pd.concat((avg_data, meteo_data), axis=1)
    data.index.name = 'date'
    data.to_csv('DATA/processed/dataset.csv')
    sensors.to_csv('DATA/processed/sensors.csv')


if __name__ == '__main__':
    main()
