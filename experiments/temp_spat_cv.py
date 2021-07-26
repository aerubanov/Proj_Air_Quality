import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
import gpflow
import tensorflow as tf
import matplotlib.pyplot as plt

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




if __name__ == '__main__':
    np.random.seed(0)
    tf.random.set_seed(0)

    start_date = '2021-01-01'
    end_date = '2021-02-01'
    val_split = '2021-01-23'

    data = pd.read_csv(data_file, parse_dates=['timestamp'])
    data = data[
            (data['timestamp'] >= start_date)
            & (data['timestamp'] < end_date)]
    data = data.dropna(subset=['P1'])

    init_data = data[data['timestamp'] < val_split]

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
    cv = time_cv(data[data['timestamp'] >= val_split])
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
    _, ax = plt.subplots(figsize=(15, 5))
    ax.plot([i for i in range(len(results))], np.sqrt(results))
    ax.set_xlabel('iteration')
    ax.set_ylabel('RMSE')
    plt.show()
    # plot_spatial(model, train_data)
