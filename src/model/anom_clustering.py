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

from src.features.preproc_anom import prepare_meteo_data, prepare_sensors_data, add_features

pd.options.mode.chained_assignment = None  # prevent false positives SettingWithCopyWarning
warnings.simplefilter(action='ignore', category=FutureWarning)  # prevent "FutureWarning: elementwise comparison failed;
# returning scalar instead, but in the future will perform elementwise comparison"

data_file = 'DATA/processed/dataset.csv'
dim_red_file = 'models/anomalies/dim_red.obj'
clustering_file = 'models/anomalies/clustering.obj'
map_file = 'models/anomalies/cluster_map.obj'
metrics_file = 'DATA/metrics/clustering_metric.json'

sensor_columns = ['P1_filtr_mean', 'P2_filtr_mean', 'temperature_filtr_mean',
                  'humidity_filtr_mean', 'pressure_filtr_mean']
meteo_columns = ['temp_meteo', 'pres_meteo', 'hum_meteo', 'wind_direction', 'wind_speed',
                 'precipitation', 'prec_amount', 'prec_time', 'visibility',
                 'dew_point_temp']
sel_columns = ['P1_filtr_mean', 'P2_filtr_mean',
               'temperature_filtr_mean', 'humidity_filtr_mean', 'temp_meteo', 'pres_meteo', 'hum_meteo', 'wind_speed',
               'prec_amount', 'dew_point_temp', 'dew_point_diff', 'prec_time', 'wind_sin', 'wind_cos', 'wind_direction']

PCA_n_components = 3
num_clusters = 4


def anom_detector(time_series: pd.DataFrame, freq=round(60 * 25 / 5), quant=0.85) -> typing.List[pd.DataFrame]:
    """
    Anomaly detection by time-series decomposition.
    :param time_series: to series for anomaly search
    :param freq: frequency of decomposition
    :param quant: al moment with decomposition residual above this quantile is anomaly
    :return: list of anomaly series
    """
    time_series['P1_filtr_mean'] = time_series.P1_filtr_mean.interpolate()
    time_series['P1_filtr_mean'] = time_series.P1_filtr_mean.rolling(4, min_periods=1).mean()
    decomp = sm.tsa.seasonal_decompose(time_series.P1_filtr_mean, model='additive', freq=freq, extrapolate_trend='freq')
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
    anomdata['resid_change'] = [i.loc[i.resid.abs().idxmax()].resid -
                                i.loc[i.resid.abs().idxmin()].resid for i in anom_list]

    anomdata['hum'] = [i.loc[i.resid.abs().idxmax()].hum_meteo -
                       i.loc[i.resid.abs().idxmin()].hum_meteo for i in anom_list]

    anomdata['temp'] = [i.loc[i.resid.abs().idxmax()].temp_meteo -
                        i.loc[i.resid.abs().idxmin()].temp_meteo for i in anom_list]

    anomdata['prec'] = [i.loc[i.resid.abs().idxmax()].prec_amount -
                        i.loc[i.resid.abs().idxmin()].prec_amount for i in anom_list]

    anomdata['wind_speed'] = [i.loc[i.resid.abs().idxmax()].wind_speed -
                              i.loc[i.resid.abs().idxmin()].wind_speed for i in anom_list]

    anomdata['wind_sin'] = [i.loc[i.resid.abs().idxmax()].wind_sin -
                            i.loc[i.resid.abs().idxmin()].wind_sin for i in anom_list]
    anomdata['wind_cos'] = [i.loc[i.resid.abs().idxmax()].wind_cos -
                            i.loc[i.resid.abs().idxmin()].wind_cos for i in anom_list]
    return anomdata


def dimension_reduction(anomdata: pd.DataFrame, sel_col=None) -> (PCA, np.array, float):
    """fit and transform data with PCA"""
    if sel_col is None:
        sel_col = sel_columns
    pca = PCA(n_components=PCA_n_components)
    pca.fit(anomdata[sel_col])
    x = pca.transform(anomdata[sel_col])
    score = 1 - pca.explained_variance_ratio_[-1]
    return pca, x, score


def clustering(x: np.array, n_clusters=num_clusters, random_state=42) -> (KMeans, float, float):
    """k-means clustering"""
    km = KMeans(n_clusters=n_clusters, random_state=random_state)
    km.fit(x)
    score = km.inertia_
    silh_score = silhouette_score(x, km.labels_, random_state=42)
    return km, score, silh_score


class Model:

    def __init__(self, reduction: PCA, clustering: KMeans, cluster_map=None):
        self.reduction = reduction
        self.clustering = clustering
        self.cluster_map = cluster_map

    def train(self, train_data: pd.DataFrame) -> (float, float, float):
        train_data = self._prepare_data(train_data)
        anomalies_list = detect_anomalies(train_data)
        anom_features = get_anomaly_features(anomalies_list)

        self.reduction.fit(anom_features)
        x = self.reduction.transform(anom_features)
        pca_score = 1 - self.reduction.explained_variance_ratio_[-1]

        self.clustering.fit(x)
        km_score = self.clustering.inertia_
        silh_score = silhouette_score(x, self.clustering.labels_, random_state=42)
        anom_features['cluster'] = self.clustering.labels_
        clust_prop = anom_features.groupby(['cluster']).mean().sort_values('resid_change').reset_index()
        self.cluster_map = {}
        for i in range(len(clust_prop)):
            self.cluster_map[int(clust_prop.iloc[i].cluster)] = i
        return pca_score, km_score, silh_score

    @staticmethod
    def _prepare_data(data: pd.DataFrame) -> pd.DataFrame:
        data = prepare_sensors_data(data, sensor_columns)
        data = prepare_meteo_data(data, meteo_columns)
        data = add_features(data)
        return data[sel_columns]

    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        data = self._prepare_data(data)
        anomalies = anom_detector(data)
        anom_fetures = get_anomaly_features(anomalies)
        x = self.reduction.transform(anom_fetures)
        clusters = self.clustering.predict(x)
        start_dates = [anomalies[i].index[0].to_pydatetime() for i in range(len(anomalies))]
        end_dates = [anomalies[i].index[-1].to_pydatetime() for i in range(len(anomalies))]
        result = pd.DataFrame(data={'start_date': start_dates, 'end_date': end_dates, 'cluster': clusters})
        result['cluster'] = result.cluster.map(self.cluster_map)
        return result


def main():
    data = pd.read_csv(data_file, parse_dates=['date'])
    data = data.set_index('date')
    kmean = KMeans(n_clusters=num_clusters, random_state=42)
    pca = PCA(n_components=PCA_n_components)
    model = Model(pca, kmean)
    pca_score, km_score, silh_score = model.train(data)
    with open(dim_red_file, 'wb') as pca_file, open(clustering_file, 'wb') as km_file, open(map_file, 'wb') as m_file:
        pickle.dump(model.reduction, pca_file)
        pickle.dump(model.clustering, km_file)
        pickle.dump(model.cluster_map, m_file)
    with open(metrics_file, 'w') as file:
        json.dump({'pca_score': pca_score, 'clustering_score': km_score, 'silhouette_score': silh_score}, file)
    print(f'pca_score: {pca_score}, clustering_score: {km_score}, silhouette_score: {silh_score}')


if __name__ == '__main__':
    main()
