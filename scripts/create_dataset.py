import pandas as pd
import os

from scripts.config import SENSOR_ID_FILE, SENSOR_DATA_FOLDER, WATHER_FILE, WATHER_DATA_FOLDER

# This script create dataset with sensor average data and wather data from raw downloaded data


def average_sensors(data_folder: str):
    """
    Average data from all sensors
    :param data_folder: path to folder with raw sensor data
    :return: (average sensor data: pd.DataFrame, senors data: pd.DataFrame)
    """
    files = os.listdir(data_folder)
    sds_files = [i for i in files if 'sds011' in i]
    bme_files = [i for i in files if 'bme280' in i]
    with open(SENSOR_ID_FILE, 'r') as sensors:
        sensor_list = sensors.read().splitlines()
        indoor_sensors = [i for i in sensor_list if 'indoor' in i]
    sds_files = [i for i in sds_files if i.split('_')[0] not in indoor_sensors]
    bme_files = [i for i in bme_files if i.split('_')[0] not in indoor_sensors]

    sensors_data = []
    idx = pd.date_range('2019-04-01', '2019-12-08', freq='5T')
    sds_data = pd.DataFrame(idx, columns=['date'])
    sds_data = sds_data.set_index('date')
    bme_data = pd.DataFrame(idx, columns=['date'])
    bme_data = bme_data.set_index('date')
    from pandas.errors import EmptyDataError
    for f in bme_files:
        try:
            data = pd.read_csv(os.path.join(data_folder, f), delimiter=';', parse_dates=['timestamp'], index_col=5)
            s_id = data.iloc[0].sensor_id
            s_type = data.iloc[0].sensor_type
            lat = data.iloc[0].lat
            lon = data.iloc[0].lon
            sensors_data.append([s_id, s_type, lat, lon])
            data['pressure'] = data.pressure.replace('unavailable', None)
            data['temperature'] = data.temperature.replace('unavailable', None)
            data['humidity'] = data.humidity.replace('unavailable', None)
            data['pressure'] = data.pressure.astype(float)
            data['temperature'] = data.temperature.astype(float)
            data['humidity'] = data.humidity.astype(float)
            new_data = data['2019-04':].resample('5T').mean()
            new_data.reindex(idx, fill_value=None)
            bme_data['pressure_' + str(s_id)] = new_data.pressure
            bme_data['temperature_' + str(s_id)] = new_data.temperature
            bme_data['humidity_' + str(s_id)] = new_data.humidity
        except EmptyDataError:
            pass
    from pandas.errors import EmptyDataError
    for f in sds_files:
        try:
            data = pd.read_csv(os.path.join(data_folder, f), delimiter=';', parse_dates=['timestamp'], index_col=5)
            s_id = data.iloc[0].sensor_id
            s_type = data.iloc[0].sensor_type
            lat = data.iloc[0].lat
            lon = data.iloc[0].lon
            sensors_data.append([s_id, s_type, lat, lon])
            data['P1'] = data.P1.replace('unavailable', None)
            data['P2'] = data.P2.replace('unavailable', None)
            data['P1'] = data.P1.astype(float)
            data['P2'] = data.P2.astype(float)
            new_data = data['2019-04':].resample('5T').mean()
            new_data.reindex(idx, fill_value=None)
            sds_data['P1_' + str(s_id)] = new_data.P1
            sds_data['P2_' + str(s_id)] = new_data.P2
        except EmptyDataError:
            pass

    sensors = pd.DataFrame(sensors_data, columns=['sensor_id', 'sensor_type', 'lat', 'lon'])
    p1_col = [i for i in sds_data.columns if 'P1_' in i]
    p2_col = [i for i in sds_data.columns if 'P2_' in i]
    temp_col = [i for i in bme_data.columns if 'temperature_' in i]
    pres_col = [i for i in bme_data.columns if 'pressure_' in i]
    hum_col = [i for i in bme_data.columns if 'humidity_' in i]

    avg_data = pd.DataFrame(idx, columns=['date'])
    avg_data = avg_data.set_index('date')
    avg_data['P1'] = sds_data[p1_col].mean(axis=1, skipna=True)
    avg_data['P2'] = sds_data[p2_col].mean(axis=1, skipna=True)
    avg_data['pressure'] = bme_data[pres_col].mean(axis=1, skipna=True)
    avg_data['temperature'] = bme_data[temp_col].mean(axis=1, skipna=True)
    avg_data['humidity'] = bme_data[hum_col].mean(axis=1, skipna=True)
    # avg_data['P1_std'] = sds_data[p1_col].std(axis=1, skipna=True)
    # avg_data['P2_std'] = sds_data[p2_col].std(axis=1, skipna=True)
    # avg_data['pressure_std'] = bme_data[pres_col].std(axis=1, skipna=True)
    # avg_data['temperature_std'] = bme_data[temp_col].std(axis=1, skipna=True)
    # avg_data['humidity_std'] = bme_data[hum_col].std(axis=1, skipna=True)
    return avg_data, sensors


def get_wather_data(wather_file: str):
    """
    Select and resample wather data
    :param wather_file: path to raw data file
    :return: pd.DataFrame
    """
    data = pd.read_csv(wather_file, delimiter=';', parse_dates=['Местное время в Москве (центр, Балчуг)'],
                       index_col=False)
    data = data.rename(columns={'Местное время в Москве (центр, Балчуг)': 'date'})
    data = data.set_index('date')
    sel_data = pd.DataFrame(index=data.index)
    sel_data['temp_meteo'] = data['T']
    sel_data['pres_meteo'] = data.Po *133.322 # transfor mmHg in Pa
    sel_data['hum_meteo'] = data.U
    sel_data['wind_direction'] = data.DD
    sel_data['wind_speed'] = data.Ff
    sel_data['precipitation'] = data.W1
    sel_data['prec_amount'] = data.RRR
    sel_data['visibility'] = data.VV
    sel_data['dew_point_temp'] = data.Td
    meteo_data = sel_data.resample('5T').pad()
    return meteo_data


if __name__ == '__main__':
    avg_data, sensors = average_sensors(SENSOR_DATA_FOLDER)
    meteo_data = get_wather_data(os.path.join(WATHER_DATA_FOLDER, WATHER_FILE))
    for c in meteo_data.columns:
        avg_data[c] = meteo_data[c]
    avg_data.to_csv('dataset.csv')
    sensors.to_csv('sensors.csv')

