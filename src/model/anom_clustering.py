import pandas as pd
import pickle
import json
import statsmodels.api as sm
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import typing
import warnings

from src.features.preproc_anom import prepare_features

pd.options.mode.chained_assignment = None  # prevent false positives SettingWithCopyWarning
warnings.simplefilter(action='ignore', category=FutureWarning)  # prevent "FutureWarning: elementwise comparison failed;
# returning scalar instead, but in the future will perform elementwise comparison"
# from line 44: anomaly['gap'] = (anomaly.index.to_series().diff()) > pd.Timedelta(10, 'm')

sel_columns = ['mean_hum', 'prec_amount',
               'max_w_speed', 'min_w_speed', 'change_hum', 'max_resid', 'min_resid', 'prec_time']


def anom_detector(time_series: pd.DataFrame, freq=round(60 * 25 / 5), quant=0.85) -> typing.List[pd.DataFrame]:
    """
    Anomaly detection by time-series decomposition.
    :param time_series: to series for anomaly search
    :param freq: frequency of decomposition
    :param quant: al moment with decomposition residual above this quantile is anomaly
    :return: list of anomaly series
    """
    time_series['P1'] = time_series.P1.interpolate()
    time_series['P1'] = time_series.P1.rolling(4, min_periods=1).mean()
    decomp = sm.tsa.seasonal_decompose(time_series.P1, model='additive', freq=freq, extrapolate_trend='freq')
    q = decomp.resid.quantile(quant)

    # find anomaly
    time_series['trend'] = decomp.trend
    time_series['seasonal'] = decomp.seasonal
    time_series['resid'] = decomp.resid
    time_series['anomaly'] = abs(time_series.resid) > q
    anomaly = time_series[time_series['anomaly']]

    # split anomaly on separate dataframe
    anomaly['gap'] = (anomaly.index.to_series().diff()) > pd.Timedelta(10, 'm')
    l_mod = pd.to_datetime(anomaly[anomaly.gap].index)
    l_mod = l_mod.insert(0, anomaly.index[0])
    l_mod = l_mod.insert(len(l_mod), anomaly.index[-1])
    ls = [anomaly[l_mod[n]:l_mod[n + 1]] for n in range(0, len(l_mod) - 1, 1)]
    ls = [i[:-1] for i in ls]
    ls = [i for i in ls if len(i) > 12]
    return ls


def detect_anomalies(data: pd.DataFrame) -> typing.List[pd.DataFrame]:
    """
    Anomaly detection by time series decomposition
    :param data: preprocessed data (see src/features/prerpoc_anom.py)
    :return: list of anomalies
    """
    weeks = [g for n, g in data.groupby(pd.Grouper(freq='7D'))]  # split dataset by 7 days series
    anom_list = []
    # for each series detect anomalies separately
    for w in weeks[:-2]:
        # decomposition
        ls = anom_detector(w)
        anom_list = anom_list + ls
    return anom_list


def get_anomaly_features(anom_list: typing.List[pd.DataFrame]) -> pd.DataFrame:
    anomdata = pd.DataFrame(index=[i for i in range(len(anom_list))])
    anomdata['max_P1'] = [i.P1.max() for i in anom_list]
    anomdata['min_P1'] = [i.P1.min() for i in anom_list]
    anomdata['min_P2'] = [i.P2.min() for i in anom_list]
    anomdata['max_P2'] = [i.P2.max() for i in anom_list]
    anomdata['mean_hum'] = [i.humidity.mean() for i in anom_list]
    anomdata['change_hum'] = [i.humidity.max() - i.humidity.min() for i in anom_list]
    anomdata['change_temp'] = [i.temperature.max() - i.temperature.min() for i in anom_list]
    anomdata['prec_amount'] = [i.prec_amount.mean() for i in anom_list]
    anomdata['max_w_speed'] = [i.wind_speed.max() for i in anom_list]
    anomdata['min_w_speed'] = [i.wind_speed.min() for i in anom_list]
    anomdata['w_dir_sin_max'] = [np.max(np.sin(i.wind_direction)) for i in anom_list]
    anomdata['w_dir_sin_mix'] = [np.min(np.sin(i.wind_direction)) for i in anom_list]
    anomdata['w_dir_cos_max'] = [np.max(np.cos(i.wind_direction)) for i in anom_list]
    anomdata['w_dir_cos_min'] = [np.min(np.cos(i.wind_direction)) for i in anom_list]
    anomdata['max_resid'] = [np.max(i.resid) for i in anom_list]
    anomdata['min_resid'] = [np.min(i.resid) for i in anom_list]
    anomdata['prec_time'] = [np.max(i.prec_time) for i in anom_list]
    return anomdata


def dimension_reduction(anomdata: pd.DataFrame, sel_col=None) -> (PCA, np.array, float):
    if sel_col is None:
        sel_col = sel_columns
    pca = PCA(n_components=3)
    pca.fit(anomdata[sel_col])
    x = pca.transform(anomdata[sel_col])
    score = 1 - pca.explained_variance_ratio_[-1]
    return pca, x, score


def clustering(x: np.array, n_clusters=4, random_state=42) -> (KMeans, float, float):
    km = KMeans(n_clusters=n_clusters, random_state=random_state)
    km.fit(x)
    score = km.inertia_
    silh_score = silhouette_score(x, km.labels_, random_state=42)
    return km, score, silh_score


class AnomalyCluster:
    """ Anomaly selection and cluster label prediction on test data"""

    def __init__(self, kmean: KMeans, pca: PCA):
        self.kmean = kmean
        self.pca = pca
        self.prepare_feture = prepare_features
        self.anom_detector = anom_detector
        self.get_anomaly_features = get_anomaly_features

    def get_anomaly(self, data: pd.DataFrame) -> typing.List[pd.DataFrame]:
        """Get time series (7-day length preferable, as used in train) and return list of anomaly dataframes"""
        data = self.prepare_feture(data)
        anomaly = self.anom_detector(data)
        return anomaly

    def get_clusters(self, anomlies: typing.List[pd.DataFrame]) -> typing.List[int]:
        """Det list of anomaly dataframes and return list of cluster labels"""
        anom_fetures = self.get_anomaly_features(anomlies)
        x = self.pca.transform(anom_fetures[sel_columns])
        clusters = self.kmean.predict(x)
        return clusters


def main(dataset_file: str, kmean_file: str, pca_file: str, metric_file: str):
    data = pd.read_csv(dataset_file, parse_dates=['date'])
    data = data.set_index('date')
    data = prepare_features(data)
    anomalies_list = detect_anomalies(data)
    anomalies = get_anomaly_features(anomalies_list)
    pca, red_data, pca_score = dimension_reduction(anomalies)
    km, score, silh_score = clustering(red_data)
    print(f'PCA score: {pca_score}')
    print(f'KMean score: {score}')
    print(f'KMean silhouette_score: {silh_score}')
    with open(kmean_file, 'wb') as f:
        pickle.dump(km, f)
    with open(pca_file, 'wb') as f:
        pickle.dump(pca, f)
    with open(metric_file, "w") as f:
        json.dump({'pca_score': pca_score, 'clustering_score': score, 'silhouette_score': silh_score}, f)
    return pca, km


if __name__ == '__main__':
    data_file = 'DATA/processed/dataset.csv'
    model = "models/anom_model.obj"
    metric = 'DATA/metrics/clustering_metric.json'
    kmean = 'models/kmean.obj'
    pca = 'models/pca.obj'
    main(data_file, kmean, pca, metric)
