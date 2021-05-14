import pytest
import pandas as pd
import src.dataset.accessor  # noqa: F401


def test_dataset_init(test_dataset):
    ds = test_dataset
    assert ds.geo
    ds1 = test_dataset
    ds1 = ds1.drop(columns=['lat'])
    with pytest.raises(AttributeError):
        assert ds1.geo


def test_dataset_x(test_dataset):
    ds = test_dataset
    ds.geo.set_x_col(['x'])
    x = ds.geo.x
    assert {'timestamp', 'lat', 'lon', 'sds_sensor', 'x'} == set(x.columns)


def test_dataset_y(test_dataset):
    ds = test_dataset
    ds.geo.set_y_col('y')
    y = ds.geo.y
    assert {'y'} == set(y.columns)


def test_dataset_loc(test_dataset):
    ds = test_dataset
    assert isinstance(ds.geo.tloc[1], pd.DataFrame)
    assert isinstance(ds.geo.sploc[3, 6], pd.DataFrame)


def test_dataset_random_sensors(test_dataset):
    ds = test_dataset
    ds1 = ds.geo.random_sensors(2)
    assert len(ds1) == 2
    assert len(ds) == 3
    ds1 = ds.geo.random_sensors(4)
    assert len(ds1) == 3
