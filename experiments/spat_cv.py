import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

from experiments.temp_spat_cv import data_file, x_col, y_col, kernel, time_cv
from src.gp.trainer.osgpr_trainer import OSGPRTrainer
from src.gp.transform.basic import GPTransform

pd.options.mode.chained_assignment = None  # default='warn'


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
    n_sensors = round(len(val_data['sds_sensor'].unique()) * 0.25)
    for i, item in enumerate(time_cv(val_data)):
        test_data = item.spat.random_sensors(n_sensors)
        train_data = item[~item['sds_sensor'].isin(
            test_data['sds_sensor'].unique())]
        y_test = test_data.spat.y.values

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
    val_data = data[data['timestamp'] >= val_split]
    main(init_data, val_data)
