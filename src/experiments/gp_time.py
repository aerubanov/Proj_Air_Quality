import pandas as pd
import pymc3 as pm
import numpy as np
import matplotlib.pyplot as plt

import src.dataset.accessor


if __name__ == '__main__':
    data = pd.read_csv('DATA/processed/dataset.csv')
    data = data.spat.tloc['2021-01-01':'2021-01-31']
    data = data[data.sds_sensor == 56073]
    data.spat.set_y_col('P1')
    x = np.arange(len(data))[:, None]
    y = data.spat.y

    with pm.Model():
        mt = pm.gp.cov.Matern32(1, ls=5)
        pr = pm.gp.cov.Periodic(1, period=24, ls=20)
        pr2 = pm.gp.cov.Periodic(1, period=64, ls=70)
        pr3 = pm.gp.cov.Periodic(1, period=100, ls=120)
        cov = mt + mt * (pr + pr2 + pr3)
        f = pm.gp.Latent(mean_func=pm.gp.mean.Constant(y.values.mean()), cov_func=cov)
        pr = f.prior('pr', X=x)
        check = pm.sample_prior_predictive(samples=1)

    print(x.flatten(), y.values)

    plt.plot(x.flatten(), y.values, label="data")
    plt.plot(x.flatten(), check['pr'][0], label="prior")
    plt.legend()
    plt.show()




