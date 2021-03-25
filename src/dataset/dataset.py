from __future__ import annotations
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import typing
import numpy as np

from src.dataset.indexers import TimeIndexer, LocIndexer


class Dataset:
    def __init__(self, datafile: str, x_columns: typing.List[str], y_column: str):
        data = pd.read_csv(datafile, parse_dates=["timestamp"])
        self.default_columns = ['timestamp', 'lat', 'lon', 'sds_sensor']  # need to get data by time and location
        self.x_columns = x_columns
        self.y_column = y_column
        self.data = data[x_columns + [y_column] + self.default_columns]

    @property
    def x(self) -> pd.DataFrame:
        return self.data[self.x_columns + self.default_columns]

    @property
    def y(self) -> pd.DataFrame:
        return self.data[[self.y_column]]

    @property
    def tloc(self) -> TimeIndexer:
        """
        Time-based indexing for items selection by timestemp
        Usage:
        dataset.tloc['2020-07-23'] # get dataset items with selected timestamp value"
        dataset.tloc['2020-07-23':'2020-07-24'] # get dataset items from timestamp range
        dataset.tloc['2020-07-23':] # get all dataset items starting from specified timestamp
        """
        return TimeIndexer(self)

    @property
    def sploc(self) -> LocIndexer:
        """
        Location-based indexing for items selection by lat and lon
        Usage:
        dataset.sploc[55.850951, 37.348591] # get dataset item with specified location
        dataset.sploc[55.3:55.8, :] # get dataset items with locations in specified ranges
        """
        return LocIndexer(self)

    def random_sensors(self, n: int, random_seed=42) -> Dataset:
        """
        Select random sds_sensors id
        """
<<<<<<< HEAD
        np.random.seed(random_seed)
        all_ids = self.data.sds_sensor.unique()
        if len(all_ids) <= n:
            return self
        selected = np.random.choice(all_ids, n, replace=False)
        self.data = self.data[self.data['sds_sensor'].isin(selected)]
        return self
=======
        pass

    def plot_series(self,  column: str):
        series = [(i, x)
                  for i, x in self.data[self.default_columns+[column]].groupby(self.data['sds_sensor'])]
        _, ax = plt.subplots()
        for i, x in series:
            x.plot(x='timestamp', y=column, ax=ax, label=i)
        ax.set_xlabel('timestamp')
        ax.set_ylabel(column)
        plt.show()

    def plot_locations(self, ax=None):
        data = self.data.groupby(self.data['sds_sensor']).last()
        gdata = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data.lon, data.lat))
        gdata['geometry'] = gdata.geometry.set_crs(epsg=4326)
        gdata.plot(ax=ax, color='black')
        plt.show()
>>>>>>> 796b2ab (add plots)


if __name__ == '__main__':
    ds = Dataset('DATA/processed/dataset.csv', ['surface_alt'], 'P1')
<<<<<<< HEAD
    # print(ds.tloc['2020-07-23':].x.head())
    print(ds.random_sensors(10).x.head())
=======
    ds = ds.tloc['2020-07-1':'2020-07-20']
    ds = ds.sploc[55.6: 55.8, 37.2:37.4]
    # ds.plot_series('P1')
    ds.plot_locations()
>>>>>>> 796b2ab (add plots)
