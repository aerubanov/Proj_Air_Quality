import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import QuantileTransformer
import pymc3 as pm
import arviz


def get_data(file):
    df = pd.read_csv(file)
    qt = QuantileTransformer(output_distribution='normal', random_state=42, n_quantiles=100)
    qt.fit(df.spat.y)

    df = df[df.timestamp == '2021-03-31 15:00:00+00:00']
    x = df[['lon', 'lat']].values
    y = qt.transform(df.spat.y.values).flatten()

    lon_min, lon_max = x[:, 0].min(), x[:, 0].max()
    lat_min, lat_max = x[:, 1].min(), x[:, 1].max()

    new_lon, new_lat = np.mgrid[lon_min:lon_max:0.025, lat_min:lat_max:0.0125]
    x_new = np.vstack((new_lon.flatten(), new_lat.flatten())).T
    return x, y, x_new


if __name__ == '__main__':
    data_file = 'DATA/processed/dataset.csv'
    x, y, x_new = get_data(data_file)

    with pm.Model() as model:
        mt = pm.gp.cov.Matern32(2, ls=0.1)

        gp = pm.gp.Latent(cov_func=mt)
        pr = gp.prior('pr', X=x)
        sigma = pm.HalfNormal('sigma', sigma=2)
        f_star = gp.conditional("f_star", x_new)

    with model:
        check = pm.sample_prior_predictive(samples=1)

    with model:
        y_ = pm.Normal("y", mu=pr, sigma=sigma, observed=y)

    with model:
        trace = pm.sample(200, n_init=100, tune=100, chains=2, cores=2, return_inferencedata=True)
        arviz.to_netcdf(trace, 'src/experiments/results/gp_spatial_trace')

    f, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    ax1.hexbin(x_new[:, 0], x_new[:, 1], C=trace.posterior['f_star'][0, :, :].mean(axis=0),
               gridsize=30, cmap='rainbow')
    plot = ax1.scatter(x[:, 0], x[:, 1], c=y, s=300, cmap='rainbow')
    ax2.scatter(x[:, 0], x[:, 1], c=check['pr'], s=300, cmap='rainbow')
    ax1.set_title("Data + Posterior")
    ax2.set_title("Prior")
    plt.colorbar(plot)
    plt.show()
