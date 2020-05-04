import datetime
import pandas as pd
import numpy as np

from src.data.create_dataset import get_file_list, combine_data, filtered_average, calc_percentiles, get_sensors_loc,\
    get_weather_data


def test_get_file_list(tmpdir, monkeypatch):
    d2 = tmpdir.mkdir('test_id')
    test_id_file = d2.join('sensor_id.csv')
    test_id_file.write(
        '''_sds011_sensor_19649.csv
           _sds011_sensor_19836.csv
           _bme280_sensor_20216.csv
           _bme280_sensor_20228.csv'''
    )

    monkeypatch.setattr('src.data.create_dataset.SENSOR_ID_FILE', test_id_file)

    result = get_file_list('tests/data/data/sensors/', 'sds011')
    assert len(result) == 2
    assert 'tests/data/data/sensors/19649_sds011_sensor_.csv' in result
    assert 'tests/data/data/sensors/19836_sds011_sensor_.csv'


def test_combine_data():
    files_list = ['tests/data/data/sensors/19649_sds011_sensor_.csv',
                  'tests/data/data/sensors/19836_sds011_sensor_.csv']
    data = combine_data(files_list, 'P1')
    assert len(data.columns) == 2


def test_filtered_avarage():
    test_data = pd.DataFrame({'A': [0, 10, 11, 12, None, 25]})
    assert filtered_average(test_data['A']) == 11


def test_calc_percentiles():
    test_data = [[0, None, 5, 6, 7, 12, 5, 22],
                 [None, 4, None, 10, 3, 3, 2, 5]]
    df = pd.DataFrame(test_data)
    result = calc_percentiles(df, 'P1')
    assert len(result.columns) == 7
    for i in ['P1_p10', 'P1_p25', 'P1_p50', 'P1_p75', 'P1_p90', 'P1', 'P1_filtr_mean']:
        assert i in result.columns
    d = [0, 5, 6, 7, 12, 5, 22]
    assert np.isclose(np.quantile(d, q=0.1), result.loc[0, 'P1_p10'])
    assert np.isclose(np.quantile(d, q=0.25), result.loc[0, 'P1_p25'])
    assert np.isclose(np.quantile(d, q=0.50), result.loc[0, 'P1_p50'])
    assert np.isclose(np.quantile(d, q=0.75), result.loc[0, 'P1_p75'])
    assert np.isclose(np.quantile(d, q=0.9), result.loc[0, 'P1_p90'])
    assert np.isclose(np.mean(d), result.loc[0, 'P1'])


def test_get_sensor_loc():
    files_list = ['tests/data/data/sensors/19649_sds011_sensor_.csv',
                  'tests/data/data/sensors/19836_sds011_sensor_.csv']
    location = get_sensors_loc(files_list)
    assert len(location) == 2
    for i in ['sensor_id', 'sensor_type', 'lat', 'lon']:
        assert i in location.columns


def test_get_weather_data():
    data = get_weather_data('tests/data/data/weather/weather_centr.csv')
    assert set(data.columns) == {'temp_meteo', 'pres_meteo', 'hum_meteo', 'wind_direction', 'wind_speed',
                                 'precipitation', 'prec_amount', 'visibility', 'dew_point_temp', 'prec_time'}
    assert data.index.min().date() == datetime.date(2019, 4, 1)
    assert data.index.max().date() == datetime.date(2019, 5, 2)
