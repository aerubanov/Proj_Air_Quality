import typing
import copy
if typing.TYPE_CHECKING:
    from src.dataset.dataset import Dataset


class TimeIndexer:
    def __init__(self, dataset: 'Dataset'):
        self._dataset = copy.deepcopy(dataset)

    def __getitem__(self, key) -> 'Dataset':
        if isinstance(key, slice):
            if key.start is not None:
                self._dataset.data = self._dataset.data[self._dataset.data['timestamp'] >= key.start]
            if key.stop is not None:
                self._dataset.data = self._dataset.data[self._dataset.data['timestamp'] < key.stop]
        else:
            self._dataset.data = self._dataset.data[self._dataset.data['timestamp'] == key]
        return self._dataset


class LocIndexer:
    def __init__(self, dataset: 'Dataset'):
        self._dataset = copy.deepcopy(dataset)

    def __getitem__(self, keys) -> 'Dataset':
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
