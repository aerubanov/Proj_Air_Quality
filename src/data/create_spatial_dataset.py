import os

from src.data.utils import get_sensors_loc, combine_sensors, get_weather_data, get_sealevel_alt
from src.data.config import SENSOR_DATA_FOLDER, WEATHER_DATA_FOLDER, WEATHER_FILE


def main():
    meteo_data = get_weather_data(os.path.join(WEATHER_DATA_FOLDER, WEATHER_FILE))
    sensors_file_list = [os.path.join(SENSOR_DATA_FOLDER, i) for i in os.listdir(SENSOR_DATA_FOLDER)]
    sensors = get_sensors_loc(sensors_file_list)
    sensors = combine_sensors(sensors)
    sealevels_alt = [get_sealevel_alt(int(row['bme_sensor']), meteo_data.pres_meteo) for _, row in sensors.iterrows()]
    sensors['sealevel_alt'] = sealevels_alt
    print(sensors.head())


if __name__ == '__main__':
    main()
