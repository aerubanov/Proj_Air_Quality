import pandas as pd
import numpy as np
import scipy.fftpack
import matplotlib.pyplot as plt


if __name__ == '__main__':
    data = pd.read_csv('DATA/processed/dataset.csv')
    data = data.spat.tloc['2021-01-01':'2021-03-31']
    data = data[data.sds_sensor == 56073]
    data.spat.set_y_col('P1')
    y = data.spat.y

    fft = abs(scipy.fft(y.values))
    freqs = scipy.fftpack.fftfreq(y.values.size)

    plt.subplot(211)
    plt.plot(y.values)
    ax = plt.subplot(212)
    plt.plot(1/freqs, 20*scipy.log10(fft), 'x')
    ax.set_xlim(0, 30)
    ax.set_xticks(np.arange(30))
    plt.show()
