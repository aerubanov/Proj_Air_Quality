import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def plot_spat_cor(df: pd.DataFrame):
    spat_features = [
            'sealevel_alt',
            'surface_alt',
            'nearest_park',
            'nearest_road',
            'nearest_indust',
            ]
    y_col = 'P1'

    fig, ax = plt.subplots(figsize=(7, 7))
    corr = df[spat_features+[y_col]].corr()
    ax.matshow(corr)
    for (i, j), z in np.ndenumerate(corr):
        ax.text(j, i, '{:0.4f}'.format(z), ha='center', va='center')
    plt.xticks(range(len(corr.columns)), corr.columns)
    plt.yticks(range(len(corr.columns)), corr.columns)


def plot_spat_scatter(df: pd.DataFrame):
    spat_features = [
            'sealevel_alt',
            'surface_alt',
            'nearest_park',
            'nearest_road',
            'nearest_indust',
            ]
    y_col = 'P1'
    fig, ax = plt.subplots(1, len(spat_features), figsize=(15, 5))
    for i, feat in enumerate(spat_features):
        ax[i].scatter(df[feat], df[y_col])
        ax[i].set_xlabel(feat)
        ax[i].set_ylabel(y_col)


if __name__ == '__main__':
    data = pd.read_csv('DATA/processed/dataset.csv')
    plot_spat_cor(data)
    plot_spat_scatter(data)
    plt.show()
