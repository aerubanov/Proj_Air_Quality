import src.dataset.accessor  # noqa: F401


def test_time_indexing(test_dataset):
    ds = test_dataset
    init_len = len(ds)

    ds1 = ds.geo.tloc['2021-03-01']
    assert len(ds1) == 1
    assert len(ds) == init_len

    ds1 = ds.geo.tloc['2021-03-01':'2021-03-03']
    assert len(ds1) == 2

    ds1 = ds.geo.tloc[:'2021-03-02']
    assert len(ds1) == 1

    ds1 = ds.geo.tloc['2021-03-01':]
    assert len(ds1) == 3


def test_spatial_indexing(test_dataset):
    ds = test_dataset
    init_len = len(ds)

    ds1 = ds.geo.sploc[3, 6]
    assert len(ds1) == 1
    assert len(ds) == init_len

    ds1 = ds.geo.sploc[3:5, :]
    assert len(ds1) == 2
