import copy
import pandas as pd


class TimeIndexer:
    def __init__(self, data: pd.DataFrame):
        self._dataset = copy.deepcopy(data)

    def __getitem__(self, key) -> pd.DataFrame:
        if isinstance(key, slice):
            if key.start is not None:
                self._dataset = self._dataset[self._dataset['timestamp'] >= key.start]
            if key.stop is not None:
                self._dataset = self._dataset[self._dataset['timestamp'] < key.stop]
        else:
            self._dataset = self._dataset[self._dataset['timestamp'] == key]

        return self._dataset


class LocIndexer:
    def __init__(self, data: pd.DataFrame):
        self._dataset = copy.deepcopy(data)

    def __getitem__(self, keys) -> pd.DataFrame:
        key1, key2 = keys
        for key, col in zip((key1, key2), ('lat', 'lon')):
            if isinstance(key, slice):
                if key.start is not None:
                    self._dataset = self._dataset[self._dataset[col] >= key.start]
                if key.stop is not None:
                    self._dataset = self._dataset[self._dataset[col] < key.stop]
            else:
                self._dataset = self._dataset[self._dataset[col] == key]
        return self._dataset
