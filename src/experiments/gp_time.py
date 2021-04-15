import pandas as pd
import pymc3 as pm
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import QuantileTransformer
import arviz

from  src.experiments.data_gen import genetate_data


def get_data(file_path: str):
    data = pd.read_csv(file_path)
    data.spat.set_y_col('P1')
    data = data[data.sds_sensor == 56073]
    qt = QuantileTransformer(output_distribution='normal', random_state=42, n_quantiles=100)
    # qt = PowerTransformer()
    qt.fit(data.spat.y)

    data = data.spat.tloc['2021-01-20':'2021-01-30']

    x = np.arange(len(data))[:, None]
    y = data.spat.y.values
    y = qt.transform(y)
    idx = round(len(data)*0.7)
    x, y, x_star, y_star = x[:idx], y[:idx], x[idx:], y[idx:]
    return x, y, x_star, y_star


if __name__ == '__main__':
    data_file = 'DATA/processed/dataset.csv'
    # x, y, x_star, _ = get_data(data_file)
    x, y, x_star, _ = genetate_data(100)

    with pm.Model() as model:
        # p = pm.Uniform('p', lower=5, upper=10)
        # l = pm.Uniform('l', lower=2, upper=7)
        p = pm.Normal('p', mu=5, sigma=1)
        l = pm.Normal('l', mu=5, sigma=1)
        lm = pm.Normal('lm', mu=15, sigma=1)
        mt = pm.gp.cov.Matern32(1, ls=lm)
        pk = pm.gp.cov.Periodic(1, period=p, ls=l)
        cov = mt * pk

        gp = pm.gp.Latent(mean_func=pm.gp.mean.Constant(y.mean()), cov_func=cov)
        pr = gp.prior('pr', X=x)

    with model:
        check = pm.sample_prior_predictive(samples=3)

    plt.plot(x.flatten(), y, label="data", color='red')
    for i in range(check['pr'].shape[0]):
        plt.plot(x.flatten(), check['pr'][i], alpha=0.3)
    plt.legend()
    plt.show()

    with model:
        f_star = gp.conditional("f_star", x_star)

    with model:
        trace = pm.sample(1000, chains=2, cores=2, return_inferencedata=True)
        arviz.to_netcdf(trace, 'src/experiments/results/gp_time_trace')
