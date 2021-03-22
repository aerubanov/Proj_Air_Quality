import pandas as pd
import pytest

from src.dataset.dataset import Dataset


@pytest.fixture
def test_dataset(tmp_path):
    data = pd.DataFrame(data={
        'timestamp': [1, 2, 3],
        'lat': [3, 4, 5],
        'lon': [6, 7, 8],
        'sds_sensor': [9, 10, 11],
        'x': [12, 13, 14],
        'y': [15, 16, 17],
        'other': [100, 101, 102]
    })
    test_file = tmp_path / 'test'
    data.to_csv(test_file)
    ds = Dataset(test_file, ['x'], 'y')
    yield ds
    del ds


def test_dataset_init(test_dataset):
    ds = test_dataset
    assert ds.x_columns == ['x']
    assert ds.y_column == 'y'
    assert 'other' not in ds.data.columns


def test_dataset_x(test_dataset):
    ds = test_dataset
    x = ds.x
    assert {'timestamp', 'lat', 'lon', 'sds_sensor', 'x'} == set(x.columns)


def test_dataset_y(test_dataset):
    ds = test_dataset
    y = ds.y
    assert {'y'} == set(y.columns)


def test_dataset_loc(test_dataset):
    ds = test_dataset
    assert isinstance(ds.tloc[1], Dataset)
    assert isinstance(ds.sploc[3, 6], Dataset)


def test_dataset_random_sensors(test_dataset):
    ds = test_dataset
    ds1 = ds.random_sensors(2)
    assert len(ds1) == 2
    assert len(ds) == 3
    ds1 = ds.random_sensors(4)
    assert len(ds1) == 3
