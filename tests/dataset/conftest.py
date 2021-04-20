import pandas as pd
import pytest
import datetime


@pytest.fixture
def test_dataset(tmp_path):
    data = pd.DataFrame(data={
        'timestamp': [datetime.datetime(2021, 3, 1),
                      datetime.datetime(2021, 3, 2),
                      datetime.datetime(2021, 3, 3)],
        'lat': [3, 4, 5],
        'lon': [6, 7, 8],
        'sds_sensor': [9, 10, 11],
        'x': [12, 13, 14],
        'y': [15, 16, 17],
        'P1': [10, 15, 20],
        'other': [100, 101, 102]
    })
    ds = pd.DataFrame(data)
    yield ds
    del ds
