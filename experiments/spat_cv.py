import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.metrics import mean_squared_error

from experiments.temp_spat_cv import data_file, x_col, y_col, kernel, time_cv
from src.gp.trainer.osgpr_trainer import OSGPRTrainer
from src.gp.transform.basic import GPTransform

pd.options.mode.chained_assignment = None  # default='warn'

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
    n_sensors = round(len(val_data['sds_sensor'].unique()) * 0.25)
    for i, item in enumerate(time_cv(val_data)):
        test_data = item.spat.random_sensors(n_sensors)
        train_data = item[~item['sds_sensor'].isin(test_data['sds_sensor'].unique())]
        y_test = test_data.spat.y.values

        train_data = transf.transform(train_data)
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


