import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import List


spat_features = [
        'sealevel_alt',
        'surface_alt',
        'nearest_park',
        'nearest_road',
        'nearest_indust',
        ]
meteo_features = [
        'temp_meteo',
        'pres_meteo',
        'hum_meteo',
        'wind_speed',
        ]
y_col = 'P1'


def plot_spat_cor(df: pd.DataFrame, features: List[str]):
    fig, ax = plt.subplots(figsize=(7, 7))
    corr = df[features+[y_col]].corr()
    ax.matshow(corr)
    for (i, j), z in np.ndenumerate(corr):
        ax.text(j, i, '{:0.4f}'.format(z), ha='center', va='center')
    plt.xticks(range(len(corr.columns)), corr.columns)
    plt.yticks(range(len(corr.columns)), corr.columns)


def plot_spat_scatter(df: pd.DataFrame, features: List[str]):
    fig, ax = plt.subplots(1, len(features), figsize=(15, 5))
    for i, feat in enumerate(features):
        ax[i].scatter(df[feat], df[y_col])
        ax[i].set_xlabel(feat)
        ax[i].set_ylabel(y_col)


if __name__ == '__main__':
    data = pd.read_csv('DATA/processed/dataset.csv')
    data[y_col] = np.log(data[y_col])
    plot_spat_cor(data, meteo_features)
    plot_spat_cor(data, spat_features)
    plot_spat_scatter(data, meteo_features)
    plot_spat_scatter(data, spat_features)
    plt.show()
