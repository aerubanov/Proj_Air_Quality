import pandas as pd
import typing


class Dataset:
    def __init__(self, datafile: str, x_columns: typing.List[str], y_column: str):
        data = pd.read_csv(datafile, parse_dates=["timestamp"]).set_index('timestamp')
        self.x_columns = x_columns
        self.y_column = y_column
        self._data = data[x_columns + [y_column]]

    @property
    def x(self) -> pd.Dataframe:
        return self._data[self.x_columns]

    @property
    def y(self) -> pd.DataFrame:
        return self._data[[self.y_column]]

