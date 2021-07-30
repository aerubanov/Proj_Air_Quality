import os
import pandas as pd
import yaml

from src.data.utils import (get_sensors_loc, combine_sensors,
                            get_weather_data, get_sealevel_alt)
from src.data.opentopodata import add_surface_altitude
from src.data.osmdata import add_osm_data

with open("params.yaml", 'r') as fd:
    params = yaml.safe_load(fd)

SENSOR_DATA_FOLDER = params['data']['paths']['sensor_data']
WEATHER_DATA_FOLDER = params['data']['paths']['weather_data']
WEATHER_FILE = params['data']['paths']['weather_filename']
SENSORS_FILE = params['data']['paths']['sensors_file']


def sensors_locations() -> pd.DataFrame:
    """Combine sds011 and bme280 sensors together and add spatial features"""
    meteo_data = get_weather_data(
            os.path.join(WEATHER_DATA_FOLDER, WEATHER_FILE)
            )
    sensors_file_list = [
            os.path.join(SENSOR_DATA_FOLDER, i)
            for i in os.listdir(SENSOR_DATA_FOLDER)
            ]
    sensors = get_sensors_loc(sensors_file_list)
    sensors = combine_sensors(sensors)
    sealevels_alt = [
            get_sealevel_alt(
                int(row['bme_sensor']),
                meteo_data.pres_meteo
                )
            for _, row in sensors.iterrows()]
    sensors['sealevel_alt'] = sealevels_alt
    sensors = add_surface_altitude(sensors)
    sensors = add_osm_data(sensors)
    return sensors


if __name__ == '__main__':
    sensors = sensors_locations()
    sensors.to_csv(SENSORS_FILE)
