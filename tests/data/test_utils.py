from numpy import isclose
import pandas as pd
import datetime

from src.data.utils import get_sensors_loc, combine_sensors, get_sealevel_alt, get_weather_data


def test_get_sensor_loc():
    files_list = ['tests/data/data/sensors/19649_sds011_sensor_.csv',
                  'tests/data/data/sensors/20216_bme280_sensor_.csv']
    location = get_sensors_loc(files_list)
    assert len(location) == 2
    for i in ['sensor_id', 'sensor_type', 'lat', 'lon']:
        assert i in location.columns
    assert location.sensor_id.values[0] == 19649
    assert location.sensor_id.values[1] == 20216
    assert location.sensor_type.values[0] == 'SDS011'
    assert location.sensor_type.values[1] == 'BME280'
    assert isclose(location.lat.values[0], 55.686)
    assert isclose(location.lat.values[1], 55.680)
    assert isclose(location.lon.values[0], 37.589)
    assert isclose(location.lon.values[1], 37.564)


def test_combine_sensors():
    data = pd.DataFrame(data={'sensor_id': [1, 2, 3, 4],
                              'sensor_type': ['SDS011', 'BME280', 'SDS011', 'BME280'],
                              'lat': [1, 1, 3, 4],
                              'lon': [2, 2, 5, 6],
                              },
                        )
    res = combine_sensors(data)
    assert len(res) == 1
    assert res.iloc[0].sds_sensor == 1
    assert res.iloc[0].bme_sensor == 2
    assert res.iloc[0].lat == 1
    assert res.iloc[0].lon == 2


def test_get_weather_data():
    data = get_weather_data('tests/data/data/weather/weather_centr.csv')
    assert set(data.columns) == {'temp_meteo', 'pres_meteo', 'hum_meteo', 'wind_direction', 'wind_speed',
                                 'precipitation', 'prec_amount', 'visibility', 'dew_point_temp', 'prec_time'}
    assert data.index.min().date() == datetime.date(2019, 4, 1)
    assert data.index.max().date() == datetime.date(2019, 5, 2)


def test_get_sealevel_alt(monkeypatch):
    monkeypatch.setattr('src.data.utils.SENSOR_DATA_FOLDER', 'tests/data/data/sensors')
    press_meteo = get_weather_data('tests/data/data/weather/weather_centr.csv').pres_meteo
    sealevel_alt = get_sealevel_alt(11111, press_meteo)
    assert round(sealevel_alt, 2) == 331.90
