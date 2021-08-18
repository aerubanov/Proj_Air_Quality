from sklearn.base import TransformerMixin
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

import src.gp.dataset.accessor  # noqa: F401


class GPTransform(TransformerMixin):
    """
    Data transformation for gaussian process
    """

    def __init__(
            self,
            random_state: int = 42,
            n_quantiles: int = 100,
    ):
        # self.target_transform = QuantileTransformer(
        #         output_distribution='normal',
        #         random_state=random_state,
        #         n_quantiles=n_quantiles,
        #     )
        self.target_transform = StandardScaler()
        self.start_date = None
        super().__init__()

    def fit(self, X, **fit_params):
        self.target_transform.fit(np.log(X.spat.y), fit_params)
        # self.lat_transform.fit(X['lat'])
        # self.lon_transform.fit(X['lon'])
        self.start_date = X['timestamp'].min()
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X.spat.y = self.target_transform.transform(np.log(X.spat.y.values)).flatten()
        X.spat.x = self._convert_time(X)
        return X

    def _convert_time(self, data) -> pd.DataFrame:
        data['timestamp'] = pd.to_datetime(data['timestamp'], utc=True)
        data['timestamp'] = (
                data['timestamp'] - self.start_date
                )/pd.Timedelta(hours=1)
        return data

    def inverse_transform(self, X: np.ndarray) -> pd.DataFrame:
        for i in range(X.shape[1]):
            X[:, i] = self.target_transform.inverse_transform(
                    X[:, i].reshape(-1, 1)).flatten()
            X[:, i] = np.exp(X[:, i])
        return X
