import pandas as pd
import typing


class Dataset:
    def __init__(self, datafile: str, x_columns: typing.List[str], y_column: str):
        data = pd.read_csv(datafile, parse_dates=["timestamp"])
        self.default_columns = ['timestamp', 'lat', 'lon']  # need to get data by time and location
        self.x_columns = x_columns
        self.y_column = y_column
        print(x_columns + [y_column])
        self._data = data[x_columns + [y_column] + self.default_columns]
        print(self._data.columns)

    @property
    def x(self) -> pd.DataFrame:
        return self._data[self.x_columns]

    @property
    def y(self) -> pd.DataFrame:
        return self._data[[self.y_column]]

    def tloc(self, key):
        if isinstance(key, slice):
            self._data = self._data[self._data['timestamp'] >= key.start & self._data['timestamp'] < key.stop]
            return self
        else:
            self._data = self._data[self._data['timestamp'] == key]
            return self


if __name__ == '__main__':
    ds = Dataset('DATA/processed/dataset.csv', ['lat', 'lon'], 'P1')
    print(ds.tloc['2020-07-23':'2020-07-24'].y.head())
