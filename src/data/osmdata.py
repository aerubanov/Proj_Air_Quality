import pandas as pd
import geopandas as gpd
from pyrosm import OSM
import typing
from shapely.ops import nearest_points
import yaml

with open("params.yaml", 'r') as fd:
    params = yaml.safe_load(fd)

CRS = "EPSG:3395"
fp = params['data']['paths']['osm_dump']


def get_osm_gata(protobuf: str) -> typing.Tuple:
    """get osm-data from protobuf for parks, roads, industrials areas"""
    osm = OSM(protobuf)
    msk_parks = osm.get_data_by_custom_criteria(
        custom_filter={'leisure': ['park', 'garden'], 'natural': ['wood']},
        filter_type='keep',
        keep_nodes=False,
        keep_ways=True,
        keep_relations=True
    )
    msk_parks = msk_parks[msk_parks.to_crs("EPSG:3395").area > 100000]
    drive_net = osm.get_data_by_custom_criteria(custom_filter={"highway": ["trunk", "primary", "secondary"]})
    indust = osm.get_data_by_custom_criteria(custom_filter={"landuse": ["industrial"]})
    return msk_parks.to_crs(CRS), drive_net.to_crs(CRS), indust.to_crs(CRS)


def nearest(row, geom):
    """get nearest point to row from geom"""
    nearest = nearest_points(row, geom)[1]
    return nearest


def add_osm_data(sensors: pd.DataFrame) -> pd.DataFrame:
    """add osm features to pandas dataframe"""
    sensors = sensors[37.1 <= sensors.lon]
    sensors = sensors[sensors.lon <= 38.05]
    sensors = sensors[55.48 <= sensors.lat]
    sensors = sensors[sensors.lat <= 59.03]
    sensors = gpd.GeoDataFrame(sensors, geometry=gpd.points_from_xy(sensors.lon, sensors.lat))
    sensors['geometry'] = sensors.geometry.set_crs(epsg=4326)
    sensors = sensors.to_crs(CRS)
    parks, roads, indust = get_osm_gata(fp)
    sensors['nearest_park'] = sensors.geometry.distance(
        sensors.geometry.apply(nearest, geom=parks.centroid.unary_union))
    sensors['nearest_road'] = sensors.geometry.distance(
        sensors.geometry.apply(nearest, geom=roads.geometry.unary_union))
    sensors['nearest_indust'] = sensors.geometry.distance(
        sensors.geometry.apply(nearest, geom=indust.centroid.unary_union))
    sensors = pd.DataFrame(sensors.drop(columns='geometry'))
    return sensors
