import pytest
import pandas as pd
import src.dataset.accessor  # noqa: F401


def test_dataset_init(test_dataset):
    ds = test_dataset
    assert ds.spat
    ds1 = test_dataset
    ds1 = ds1.drop(columns=['lat'])
    with pytest.raises(AttributeError):
        assert ds1.spat


def test_dataset_x(test_dataset):
    ds = test_dataset
    ds.spat.set_x_col(['x'])
    x = ds.spat.x
    assert {'timestamp', 'lat', 'lon', 'sds_sensor', 'x'} == set(x.columns)


def test_dataset_x_set(test_dataset):
    ds = test_dataset
    x = ds.spat.x
    x.loc[:, 'lon'] = 1
    ds.spat.x = x
    assert ds['lon'].values[0] == 1


def test_dataset_y(test_dataset):
    ds = test_dataset
    ds.spat.set_y_col('y')
    y = ds.spat.y
    assert {'y'} == set(y.columns)


def test_dataset_y_set(test_dataset):
    ds = test_dataset
    ds.spat.set_y_col('y')
    val = [0, 0, 0]
    ds.spat.y = val
    assert ds['y'].values[0] == 0


def test_dataset_loc(test_dataset):
    ds = test_dataset
    assert isinstance(ds.spat.tloc[1], pd.DataFrame)
    assert isinstance(ds.spat.sploc[3, 6], pd.DataFrame)


def test_dataset_random_sensors(test_dataset):
    ds = test_dataset
    ds1 = ds.spat.random_sensors(2)
    assert len(ds1) == 2
    assert len(ds) == 3
    ds1 = ds.spat.random_sensors(4)
    assert len(ds1) == 3
