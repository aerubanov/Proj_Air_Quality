from pandas.core.frame import DataFrame
from sklearn.base import TransformerMixin
from sklearn.preprocessing import QuantileTransformer
import pandas as pd


def GPTransform(TransformerMixin):
    def __init__(
            random_state: int = 42,
            n_quantiles: int = 100,
    ):
        self.target_transform = QuantileTransformer(
                output_distribution='normal',
                random_state=random_state,
                n_quantiles=n_quantiles,
            )

        def fit(self, X, **fit_params):
       self.target_transform.fit(X.spat.y, fit_params)

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.dropna(subset=['P1'])
        X = X[['timestamp', 'lat', 'lon', 'P1', 'sds_sensor']
        X.spat.y = self.target_transform.transform(X.spat.y.values).flatten()
        X.spat.x = self._convert-time(X)
        return X

    def _convert_time(data) -> pd.DataFrame:
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data['timestamp'] = (
                data['timestamp'] - pd.to_datetime('2021-01-01', utc=True)
                )/pd.Timedelta(hours=1)
        return data
    
    def inverse_transform(X: pd.DataFrame) -> pd.DataFrame:
        X.spat.y = self.target_transform.inverse_transform(X.spat.y.values).flatten()
        X['up_bound'] = self.target_transform.inverse_transform(X['up_bound']).flatten()
        X['low_bound'] = self.target_transform.inverse_transform(X['low_bound']).flatten()
        return X
