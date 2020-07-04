import pickle
import pandas as pd
import matplotlib.pyplot as plt
from typing import List

from src.model.anom_clustering import Model, num_clusters, sensor_columns, meteo_columns
from src.features.preproc_anom import prepare_sensors_data, prepare_meteo_data


# ------ constants --------------------------------------------------------------------------------------
data_file = 'DATA/processed/dataset.csv'
dim_red_file = 'models/anomalies/dim_red.obj'
clustering_file = 'models/anomalies/clustering.obj'
map_file = 'models/anomalies/cluster_map.obj'
anomalies_file = 'DATA/processed/anomalies.csv'
# ------ constants --------------------------------------------------------------------------------------


def plot_distribution(anomalies):
    n_clast = num_clusters
    f, axs = plt.subplots(2, 5, figsize=(30, 15))
    for i in range(n_clast):
        anomalies[anomalies.cluster == i].P1_filtr_mean.hist(ax=axs[0, 0], alpha=0.6, label=f'cluster {i}',
                                                             density=True)
    axs[0, 0].set_title('PM2.5')
    axs[0, 0].legend(loc='best')

    for i in range(n_clast):
        anomalies[anomalies.cluster == i].P2_filtr_mean.hist(ax=axs[0, 1], alpha=0.6, label=f'cluster {i}',
                                                             density=True)
    axs[0, 1].set_title('PM10')
    axs[0, 1].legend(loc='best')

    for i in range(n_clast):
        anomalies[anomalies.cluster == i].humidity_filtr_mean.hist(ax=axs[0, 2], alpha=0.6, label=f'cluster {i}',
                                                                   density=True)
    axs[0, 2].set_title('Влажность')
    axs[0, 2].legend(loc='best')

    for i in range(n_clast):
        anomalies[anomalies.cluster == i].temperature_filtr_mean.hist(ax=axs[0, 3], alpha=0.6, label=f'cluster {i}',
                                                                      density=True)
    axs[0, 3].set_title('Температура')
    axs[0, 3].legend(loc='best')

    for i in range(n_clast):
        anomalies[anomalies.cluster == i].wind_speed.hist(ax=axs[0, 4], bins=10, alpha=0.6, label=f'cluster {i}',
                                                          density=True)
    axs[0, 4].set_title('Скорость ветра')
    axs[0, 4].legend(loc='best')

    for i in range(n_clast):
        anomalies[anomalies.cluster == i].prec_amount.hist(ax=axs[1, 0], bins=20, alpha=0.6, label=f'cluster {i}',
                                                           density=True)
    axs[1, 0].set_title('Количество осадков')
    axs[1, 0].set_xlim([0, 1])
    axs[1, 0].legend(loc='best')

    for i in range(n_clast):
        anomalies[anomalies.cluster == i].dew_point_temp.hist(ax=axs[1, 1], alpha=0.6, label=f'cluster {i}',
                                                              density=True)
    axs[1, 1].set_title('Температура точки росы')
    axs[1, 1].legend(loc='best')

    for i in range(n_clast):
        anomalies[anomalies.cluster == i].dew_point_diff.hist(ax=axs[1, 2], alpha=0.6, label=f'cluster {i}',
                                                              density=True)
    axs[1, 2].set_title('Разность температуры и точки росы')
    axs[1, 2].legend(loc='best')

    for i in range(n_clast):
        anomalies[anomalies.cluster == i].resid.hist(ax=axs[1, 3], alpha=0.6, label=f'cluster {i}', density=True)
    axs[1, 3].set_title('Отклонение')
    axs[1, 3].legend(loc='best')

    for i in range(n_clast):
        anomalies[anomalies.cluster == i].wind_direction.hist(ax=axs[1, 4], alpha=0.6, label=f'cluster {i}',
                                                              density=True)
    axs[1, 4].set_title('Направление ветра')
    axs[1, 4].legend(loc='best')
    plt.savefig('src/web/client/application/static/images/clusters_distribution.png',
                clear=True, bbox_inches='tight')


def extract_anom(data: pd.DataFrame, model: Model) -> (pd.DataFrame, List[pd.DataFrame]):
    weeks = [g for n, g in data.groupby(pd.Grouper(freq='7D'))]  # split dataset by 7 days series
    results = []
    anom_data = []
    for week in weeks[:-2]:
        clusters, anomalies = model.predict(week)
        results.append(clusters)
        anom_data += anomalies
    result = pd.concat(results, axis=0)
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
    for i in range(len(anomalies)):
        anom_data[i]['cluster'] = anomalies.iloc[i]['cluster']
    anom_data = pd.concat(anom_data, axis=0)
    plot_distribution(anom_data)


if __name__ == '__main__':
    main()
