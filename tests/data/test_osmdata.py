import geopandas as gpd
import pandas as pd
from pyrosm import get_data
from shapely.geometry import Point, MultiPoint

from src.data.osmdata import get_osm_gata, CRS, nearest, add_osm_data


def test_get_osm_data():
    fp = get_data("test_pbf")
    parks, drive, indust = get_osm_gata(fp)
    assert isinstance(parks, gpd.GeoDataFrame)
    assert parks.crs == CRS
    assert isinstance(drive, gpd.GeoDataFrame)
    assert drive.crs == CRS
    assert isinstance(indust, gpd.GeoDataFrame)
    assert indust.crs == CRS


def test_nearest():
    orig = Point(1, 1.67)
    dest1, dest2, dest3 = Point(0, 1.45), Point(2, 2), Point(0, 2.5)
    destinations = MultiPoint([dest1, dest2, dest3])
    near = nearest(orig, destinations)
    assert near == dest1


def test_add_osm_data(monkeypatch):
    sensors = pd.DataFrame(data={'lat': [55.0, 57.0, 59.5], 'lon': [36.0, 37.5, 38.5]})
    fp = get_data("test_pbf")
    monkeypatch.setattr('src.data.osmdata.fp', fp)
    result = add_osm_data(sensors)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert 'nearest_park' in result.columns
    assert 'nearest_road' in result.columns
    assert 'nearest_indust' in result.columns
