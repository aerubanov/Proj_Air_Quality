from __future__ import annotations
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import typing
import numpy as np

from src.dataset.indexers import TimeIndexer, LocIndexer


@pd.api.extensions.register_dataframe_accessor("spat")
class GeoAccessor:
    necessary_columns = ['timestamp', 'lat', 'lon', 'sds_sensor']  # need to get data by time and location

    def __init__(self, pandas_obj: pd.DataFrame):
        self._validate(pandas_obj)
        self.data = pandas_obj
        self.x_column = None
        self.y_column = 'P1'

    @staticmethod
    def _validate(obj: pd.DataFrame):
        for col in GeoAccessor.necessary_columns:
            if col not in obj.columns:
                raise AttributeError(f"Must have {col} column")

    @property
    def x(self) -> pd.DataFrame:
        col = self.x_column + self.necessary_columns \
            if self.x_column is not None else self.necessary_columns
        return self.data[col]

    @property
    def y(self) -> pd.DataFrame:
        return self.data[[self.y_column]]

    def set_x_col(self, columns: typing.List[str]):
        self.x_column = columns

    def set_y_col(self, y_column: str):
        self.y_column = y_column

    @property
    def tloc(self) -> TimeIndexer:
        """
        Time-based indexing for items selection by timestemp
        Usage:
        dataset.tloc['2020-07-23'] # get dataset items with selected timestamp value"
        dataset.tloc['2020-07-23':'2020-07-24'] # get dataset items from timestamp range
        dataset.tloc['2020-07-23':] # get all dataset items starting from specified timestamp
        """
        return TimeIndexer(self.data)

    @property
    def sploc(self) -> LocIndexer:
        """
        Location-based indexing for items selection by lat and lon
        Usage:
        dataset.sploc[55.850951, 37.348591] # get dataset item with specified location
        dataset.sploc[55.3:55.8, :] # get dataset items with locations in specified ranges
        """
        return LocIndexer(self.data)

    def random_sensors(self, n: int, random_seed=42) -> pd.DataFrame:
        """
        Select random sds_sensors id. If n >= len(dataset), return full dataset
        """
        np.random.seed(random_seed)
        all_ids = self.data.sds_sensor.unique()
        if len(all_ids) <= n:
            return self.data
        selected = np.random.choice(all_ids, n, replace=False)
        data = self.data[self.data['sds_sensor'].isin(selected)]
        return data

    def plot_series(self,  column: str):
        """
        Plot column values changes in time after group by sensors
        """
        series = [(i, x)
                  for i, x in self.data[self.necessary_columns+[column]].groupby(self.data['sds_sensor'])]
        _, ax = plt.subplots()
        for i, x in series:
            x.plot(x='timestamp', y=column, ax=ax, label=i)
        ax.set_xlabel('timestamp')
        ax.set_ylabel(column)
        plt.show()

    def plot_locations(self, ax=None):
        """Plot sensors spatial locations"""
        data = self.data.groupby(self.data['sds_sensor']).last()
        gdata = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data.lon, data.lat))
        gdata['geometry'] = gdata.geometry.set_crs(epsg=4326)
        gdata.plot(ax=ax, color='black')
        plt.show()
