import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
import tensorflow as tf
import matplotlib.pyplot as plt

from src.gp.trainer.osgpr_trainer import OSGPRTrainer
from src.gp.transform.basic import GPTransform
from src.gp.models.kernel import basic_kernel as kernel


pd.options.mode.chained_assignment = None  # default='warn'

data_file = 'DATA/processed/dataset.csv'
x_col = ['timestamp', 'lon', 'lat']
y_col = 'P1'


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


def main(init_data: pd.DataFrame, val_data: pd.DataFrame):
    transf = GPTransform()
    transf.fit(data)

    trainer = OSGPRTrainer(
            kernel=kernel,
            transform=transf,
            x_col=x_col,
            y_col=y_col,
            )
    trainer.build_model(
            init_data,
            max_iter=100,
            )

    results = []
    cv = time_cv(val_data)
    test_data = next(cv)
    for i, item in enumerate(cv):
        train_data = test_data
        test_data = item
        y_test = test_data[y_col].values
        trainer.update_model(
                train_data,
                max_iter=100,
                iprint=0,
                )
        pred = trainer.predict(test_data)
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


if __name__ == '__main__':
    np.random.seed(0)
    tf.random.set_seed(0)

    start_date = '2021-05-01'
    end_date = '2021-07-01'
    val_split = '2021-06-10'

    data = pd.read_csv(data_file, parse_dates=['timestamp'])
    data = data[
            (data['timestamp'] >= start_date)
            & (data['timestamp'] < end_date)]
    data = data.dropna(subset=['P1'])

    init_data = data[data['timestamp'] < val_split]
    val_data = data[data['timestamp'] >= val_split]

    main(init_data, val_data)
