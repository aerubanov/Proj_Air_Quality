import pandas as pd


class TimeIndexer:
    def __init__(self, dataset):
        self._dataset = dataset

    def __getitem__(self, key):
        if isinstance(key, slice):
            if key.start is not None:
                self._dataset.data = self._dataset.data[self._dataset.data['timestamp'] >= key.start]
            if key.stop is not None:
                self._dataset.data = self._dataset.data[self._dataset.data['timestamp'] < key.stop]
        else:
            self._dataset.data = self._dataset.data[self._dataset.data['timestamp'] == key]
        return self._dataset


class LocIndexer:
    def __init__(self, dataset):
        self._dataset = dataset

    def __getitem__(self, keys):
        key1, key2 = keys
        for key, col in zip((key1, key2), ('lat', 'lon')):
            if isinstance(key, slice):
                if key.start is not None:
                    self._dataset.data = self._dataset.data[self._dataset.data[col] >= key.start]
                if key.stop is not None:
                    self._dataset.data = self._dataset.data[self._dataset.data[col] < key.stop]
            else:
                self._dataset.data = self._dataset.data[self._dataset.data[col] == key]
        return self._dataset
