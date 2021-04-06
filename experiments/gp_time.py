import pandas as pd
import pymc3 as pm
import numpy as np

import src.dataset.accessor


if __name__ == '__main__':
    data = pd.read_csv('DATA/processed/dataset.csv')
    data = data.spat.tloc['2021-01-01':'2021-03-31']
    data = data[data.sds_sensor == 56073]
    data.spat.set_y_col('P1')
    x = np.arange(len(data))
    y = data.spat.y

    with pm.Model():
        mt = pm.gp.cov.Matern32(0, 20)
        pr = pm.gp.cov.Periodic(0, 24, 48)
        cov = mt + mt * pr


