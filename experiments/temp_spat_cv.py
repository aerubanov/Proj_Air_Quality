import pandas as pd
import numpy as np
from sklearn.preprocessing import QuantileTransformer
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import gpflow
import tensorflow as tf

from src.gp.models.osgpr import OSGPR
from src.gp.trainer.osgpr_trainer import OSGPRTrainer
from src.gp.transform.basic import GPTransform


pd.options.mode.chained_assignment = None  # default='warn'

data_file = 'DATA/processed/dataset.csv'
x_col = ['timestamp', 'lon', 'lat']
y_col = 'P1'

spat_cov = gpflow.kernels.Matern32(
        variance=1,
        lengthscales=0.05,
        active_dims=[1, 2],
        )

mt = gpflow.kernels.Matern32(variance=1, lengthscales=24, active_dims=[0])
pk = gpflow.kernels.Periodic(
        gpflow.kernels.SquaredExponential(
            lengthscales=24*1.5,
            active_dims=[0],
            ),
        period=24,
        )
time_cov = mt * pk
kernel = spat_cov * time_cov


def time_cv(data: pd.DataFrame, step=24):
    curr_t = data['timestamp'].min()
    next_t = curr_t + pd.Timedelta(step, unit='hours')
    while curr_t < data['timestamp'].max():
        item = data[
                (data['timestamp'] >= curr_t) & (data['timestamp'] < next_t)
                ]
        if len(item) > 0:
            yield item
        curr_t = next_t
        next_t += pd.Timedelta(step, unit='hours')


def plot_time(model: gpflow.models.GPModel, train_data, test_data):
    x_train = train_data[x_col].values
    x_test = test_data[x_col].values

    _, (ax1, ax2) = plt.subplots(1, 2,
                                 figsize=(15, 5),
                                 gridspec_kw={'width_ratios': [3, 1]})

    mu, var = model.predict_f(x_test)
    test_data.loc[:, 'prediction'] = mu[:, 0]
    df = test_data.groupby('timestamp').median().reset_index()
    df.plot(y=['P1', 'prediction'], ax=ax2)

    mu, _ = model.predict_f(x_train)
    train_data.loc[:, 'prediction'] = mu[:, 0]
    df = train_data.groupby('timestamp').median().reset_index()
    df.plot(y=['P1', 'prediction'], ax=ax1)

    plt.show()


def plot_spatial(model: gpflow.models.GPModel, data, timestamp=None):
    if timestamp is None:
        timestamp = train_data['timestamp'].max()
    df = data[train_data['timestamp'] == timestamp]
    x = df[x_col].values
    y = df[y_col].values

    lon_min, lon_max = x[:, 1].min(), x[:, 1].max()
    lat_min, lat_max = x[:, 2].min(), x[:, 2].max()

    new_lon, new_lat = np.mgrid[lon_min:lon_max:0.025, lat_min:lat_max:0.0125]
    xx = np.vstack((x[0, 0] * np.ones(new_lon.flatten().shape[0]),
                    new_lon.flatten(),
                    new_lat.flatten())).T
    mx, var = model.predict_f(xx)

    f, (ax3, ax4) = plt.subplots(1, 2, figsize=(16, 8))
    plot1 = ax3.hexbin(xx[:, 1], xx[:, 2], mx,
                       gridsize=30, cmap='rainbow', alpha=0.7)
    ax3.scatter(x[:, 1], x[:, 2],
                c=y,
                s=300, cmap='rainbow')
    plot2 = ax4.hexbin(xx[:, 1], xx[:, 2], np.sqrt(var),
                       gridsize=30, cmap='rainbow', alpha=0.7)
    plt.colorbar(plot1, ax=ax3)
    plt.colorbar(plot2, ax=ax4)
    plt.show()


if __name__ == '__main__':
    np.random.seed(0)
    tf.random.set_seed(0)

    data = pd.read_csv(data_file, parse_dates=['timestamp'])
    data = data[
            (data['timestamp'] >= '2021-01-01')
            & (data['timestamp'] < '2021-04-01')]
    data = data.dropna(subset=['P1'])

    init_data = data[data['timestamp'] < '2021-01-15']

    transf = GPTransform()
    transf.fit(data)

    init_data = transf.transform(init_data)

    trainer = OSGPRTrainer(kernel=kernel)
    trainer.build_model(
            init_data[x_col].values,
            init_data[y_col].values[:, None],
            max_iter=100,
            )

    results = []
    cv = time_cv(data[data['timestamp'] >= '2021-01-16'])
    test_data = next(cv)
    test_data = transf.transform(test_data)
    for i, item in enumerate(cv):
        train_data = test_data
        test_data = item
        y_test = test_data[y_col].values
        test_data = transf.transform(test_data)
        trainer.update_model(
                train_data[x_col].values,
                train_data[y_col].values[:, None],
                max_iter=100,
                iprint=0,
                )
        mu, var = trainer.model.predict_f(test_data[x_col].values)
        pred = np.hstack((mu, mu + 2*np.sqrt(var), mu - 2 * np.sqrt(var)))
        pred = transf.inverse_transform(pred)
        mse = mean_squared_error(y_test, pred[:, 0])
        print(f'step {i} RMSE: {np.sqrt(mse)}')
        results.append(mse)
    print(np.mean(np.sqrt(results)), np.std(np.sqrt(results)))
    # _, ax = plt.subplots(figsize=(15, 5))
    # ax.plot([i for i in range(len(results))], np.sqrt(results))
    # ax.set_xlabel('iteration')
    # ax.set_ylabel('RMSE')
    # plt.show()
    # plot_spatial(model, train_data)
