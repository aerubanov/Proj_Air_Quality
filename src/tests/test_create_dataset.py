import numpy as np
import datetime

from src.data.create_dataset import average_sensors, get_wather_data


def test_average_sensor():
    start_date = datetime.date(2019, 12, 1)
    end_date = datetime.date(2019, 12, 10)
    data, sensors = average_sensors('src/tests/data/sensors/', start_date, end_date)
    assert set(data.columns) == {'P1', 'P2', 'pressure', 'temperature', 'humidity'}
    step = np.diff(data.index.values)
    assert max(step) == min(step) == np.timedelta64(5, 'm')
    assert data.index.min().date() == start_date
    assert data.index.max().date() == end_date


def test_get_wather_data():
    data = get_wather_data('src/tests/data/wather/wather_centr.csv')
    assert set(data.columns) == {'temp_meteo', 'pres_meteo', 'hum_meteo', 'wind_direction', 'wind_speed',
                                 'precipitation', 'prec_amount', 'visibility', 'dew_point_temp', 'prec_time'}
    assert data.index.min().date() == datetime.date(2019, 4, 1)
    assert data.index.max().date() == datetime.date(2019, 5, 2)
