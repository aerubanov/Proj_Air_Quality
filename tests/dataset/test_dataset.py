from src.dataset.datasets import Dataset


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
