import pickle
from typing import List

import matplotlib.pyplot as plt
import pandas as pd

from src.features.preproc_anom import prepare_sensors_data, prepare_meteo_data
from src.model.anom_clustering import Model, num_clusters, sensor_columns, meteo_columns

# ------ constants --------------------------------------------------------------------------------------
data_file = 'DATA/processed/dataset.csv'
dim_red_file = 'models/anomalies/dim_red.obj'
clustering_file = 'models/anomalies/clustering.obj'
map_file = 'models/anomalies/cluster_map.obj'
anomalies_file = 'DATA/processed/anomalies.csv'
image_file = 'src/web/client/application/static/images/clusters_distribution.png'


# ------ constants --------------------------------------------------------------------------------------


def plot_distribution(anomalies):
    colors = {0: 'g', 1: 'r', 2: 'b'}
    n_clast = num_clusters
    f, axs = plt.subplots(1, 4, figsize=(30, 15))
    for i in range(n_clast):
        anomalies[anomalies.cluster == i].hum_max.hist(ax=axs[0], alpha=0.6, label=f'cluster {i}',
                                                       density=True, color=colors[i])
    axs[0].set_title('Влажность')
    axs[0].legend(loc='best')

    for i in range(n_clast):
        anomalies[anomalies.cluster == i].wind_speed.hist(ax=axs[1], alpha=0.6, label=f'cluster {i}',
                                                          density=True, color=colors[i])
    axs[1].set_title('Изменение скорости ветра')
    axs[1].legend(loc='best')

    for i in range(n_clast):
        anomalies[anomalies.cluster == i].P1.hist(ax=axs[2], alpha=0.6, label=f'cluster {i}',
                                                  density=True, color=colors[i])
    axs[2].set_title('PM2.5')
    axs[2].legend(loc='best')

    for i in range(n_clast):
        anomalies[anomalies.cluster == i].resid_max.hist(ax=axs[3], alpha=0.6, label=f'cluster {i}',
                                                         density=True, color=colors[i])
    axs[3].set_title('residual')
    axs[3].legend(loc='best')

    print('plot distribution has been saved:', image_file)
    plt.savefig(image_file, bbox_inches='tight')


def extract_anom(data: pd.DataFrame, model: Model) -> (pd.DataFrame, List[pd.DataFrame]):
    weeks = [g for n, g in data.groupby(pd.Grouper(freq='7D'))]  # split dataset by 7 days series
    results = []
    anom_data = []
    for week in weeks[:-2]:
        clusters, anomalies = model.predict(week)
        results.append(clusters)
        anom_data.append(anomalies)
    result = pd.concat(results, axis=0)
    anom_data = pd.concat(anom_data, axis=0)
    return result, anom_data


def main():
    data = pd.read_csv(data_file, parse_dates=['date'])
    data = data.set_index('date')
    data = prepare_sensors_data(data, sensor_columns)
    data = prepare_meteo_data(data, meteo_columns)
    with open(dim_red_file, 'rb') as pca_file, open(clustering_file, 'rb') as km_file, open(map_file, 'rb') as m_file:
        pca = pickle.load(pca_file)
        kmean = pickle.load(km_file)
        cluster_map = pickle.load(m_file)
        model = Model(pca, kmean, cluster_map)
    anomalies, anom_data = extract_anom(data, model)
    anomalies.to_csv(anomalies_file, index=False)
    plot_distribution(anom_data)


if __name__ == '__main__':
    main()
