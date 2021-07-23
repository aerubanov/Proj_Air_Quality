from sklearn.base import TransformerMixin
from sklearn.preprocessing import QuantileTransformer
import pandas as pd
import numpy as np

import src.gp.dataset.accessor  # noqa: F401


class GPTransform(TransformerMixin):
    def __init__(
            self,
            random_state: int = 42,
            n_quantiles: int = 100,
    ):
        self.target_transform = QuantileTransformer(
                output_distribution='normal',
                random_state=random_state,
                n_quantiles=n_quantiles,
            )
        self.start_date = None
        super().__init__()

    def fit(self, X, **fit_params):
        self.target_transform.fit(X.spat.y, fit_params)
        self.start_date = X['timestamp'].min()

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X[['timestamp', 'lat', 'lon', 'P1', 'sds_sensor']]
        X.spat.y = self.target_transform.transform(X.spat.y.values).flatten()
        X.spat.x = self._convert_time(X)
        return X

    def _convert_time(self, data) -> pd.DataFrame:
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data['timestamp'] = (
                data['timestamp'] - self.start_date
                )/pd.Timedelta(hours=1)
        return data

    def inverse_transform(self, X: np.ndarray) -> pd.DataFrame:
        for i in range(X.shape[1]):
            X[:, i] = self.target_transform.inverse_transform(
                    X[:, i].reshape(-1, 1)).flatten()
        return X
