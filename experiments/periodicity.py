import yaml
from statsmodels.tsa.stattools import acovf
import matplotlib.pyplot as plt
import pandas as pd
from scipy.signal import periodogram

from src.gp.transform.basic import GPTransform


with open('params.yaml', 'r') as fd:
    params = yaml.safe_load(fd)
data_file = params['data']['paths']['dataset_file']


def caf_plot(data):
    transf = GPTransform()
    data = transf.fit_transform(data)
    y = data.P1
    acf = acovf(y)
    _, pxx = periodogram(acf)
    fig, ax = plt.subplots(1, 2, figsize=(15, 7))
    ax[0].plot(acf)
    ax[1].plot(pxx)
    ax[1].set_xlim(0, 72)
    ax[1].set_title("Power spectral density")
    ax[0].set_title("Auto-covariance function")
    plt.show()


if __name__ == '__main__':
    start_date = params['model']['start_date']
    end_date = params['model']['end_date']
    data = pd.read_csv(data_file, parse_dates=['timestamp'])
    data = data[
            (data['timestamp'] >= start_date)
            & (data['timestamp'] < end_date)]
    data = data.groupby(data['timestamp']).mean()
    data = data.reset_index()
    data.loc[data.P1 <= 1, 'P1'] = 1
    caf_plot(data)
