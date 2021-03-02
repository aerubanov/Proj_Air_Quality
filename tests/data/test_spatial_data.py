import pandas as pd

from src.data.spatial_data import sensors_locations


def test_sensors_locations(monkeypatch, mocker):
    monkeypatch.setattr('src.data.spatial_data.SENSOR_DATA_FOLDER', 'tests/data/data/sensors')
    monkeypatch.setattr('src.data.spatial_data.WEATHER_DATA_FOLDER', 'tests/data/data/weather')
    monkeypatch.setattr('src.data.spatial_data.WEATHER_FILE', 'weather_centr.csv')
    sensors = pd.DataFrame(data={'sensor_id': [1, 2, 3, 4],
                                 'sensor_type': ['SDS011', 'BME280', 'SDS011', 'BME280'],
                                 'lat': [1, 1, 3, 4],
                                 'lon': [2, 2, 5, 6],
                                 'bme_sensor': [1, 2, 3, 4],
                                 },
                           )
    mocks = [
        mocker.patch('src.data.spatial_data.get_sensors_loc', return_value=sensors),
        mocker.patch('src.data.spatial_data.combine_sensors', return_value=sensors),
        mocker.patch('src.data.spatial_data.get_sealevel_alt', return_value=1),
        mocker.patch('src.data.spatial_data.add_surface_altitude', return_value=sensors),
        mocker.patch('src.data.spatial_data.add_osm_data', return_value=sensors),
    ]
    sensors_locations()
    for mock in mocks:
        mock.assert_called()
