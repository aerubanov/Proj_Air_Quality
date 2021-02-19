import pandas as pd

from src.data.sensors_data import load_data, get_sensor_data, add_weather_data


def test_load_data(monkeypatch):
    monkeypatch.setattr('src.data.sensors_data.SENSOR_DATA_FOLDER', 'tests/data/data/sensors')
    data = load_data('20216_bme280_sensor_.csv')
    assert isinstance(data, pd.DataFrame)
    assert isinstance(data.index, pd.DatetimeIndex)


def test_get_sensor_data(monkeypatch):
    def mock(filename):
        if 'bme280' in filename:
            return pd.DataFrame(data={'pressure': [1, 2, 3],
                                      'temperature': [1, 2, 3],
                                      'humidity': [1, 2, 3],
                                      })
        if 'sds011' in filename:
            return pd.DataFrame(data={'P1': [1, 2, 3],
                                      'P2': [1, 2, 3],
                                      })

    monkeypatch.setattr('src.data.sensors_data.load_data', mock)
    sensors = pd.DataFrame(data = {'sds_sensor': [1], 'lat': [1], 'lon': [1], 'sealevel_alt': [1],
                                   'surface_alt': [1], 'nearest_park': [1], 'nearest_road': [1],
                                   'nearest_indust': [1]})
    result = get_sensor_data(2, 1, sensors)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3
