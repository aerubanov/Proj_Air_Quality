import gpflow
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
import tensorflow as tf
import yaml
import json
import matplotlib.pyplot as plt

from src.gp.trainer.osgpr_trainer import OSGPRTrainer
from src.gp.transform.basic import GPTransform
from src.gp.models.kernel import get_kernel


with open('params.yaml', 'r') as fd:
    params = yaml.safe_load(fd)

pd.options.mode.chained_assignment = None  # default='warn'
data_file = params['data']['paths']['dataset_file']
kernel = get_kernel(params['model']['kernel'])
x_col = ['timestamp', 'lon', 'lat', 'wind_speed', 'hum_meteo',
        'temp_meteo', 'pres_meteo']
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
            max_iter=params['model']['max_iter'],
            M=params['model']['num_induc'],
            )

    results = []
    cv = time_cv(val_data)
    predictions = []
    for i, item in enumerate(cv):
        y_test = item[y_col].to_numpy(copy=True)
        train_data = item.copy()
        pred = trainer.predict(item.copy())
        item['pred'], item['var'] = \
            pred[:, 0], pred[:, 1]
        predictions.append(item)
        mse = mean_squared_error(y_test, pred[:, 0])
        print(f'step {i} RMSE: {np.sqrt(mse)}')
        results.append(mse)
        trainer.update_model(
                train_data,
                max_iter=params['model']['max_iter'],
                new_m=params['model']['num_induc_upd'],
                iprint=-1,
                )
    gpflow.utilities.print_summary(trainer.model)
    print(np.mean(np.sqrt(results)), np.std(np.sqrt(results)))

    with open(params['model']['temp_cv']['result_file'], 'w') as fd:
        json.dump({
            'mean RMSE': np.mean(np.sqrt(results)),
            'RMSE std': np.std(np.sqrt(results)),
            }, fd)

    plot_data = np.sqrt(results)
    plot_data = [{'step': i, 'RMSE': plot_data[i]}
                 for i in range(len(plot_data))]
    with open(params['model']['temp_cv']['plot_file'], 'w') as fd:
        json.dump({'temp_cv': plot_data}, fd)

    predictions = pd.concat(predictions, ignore_index=True)
    predictions.to_csv(params['model']['temp_cv']['prediction'])
    return predictions


def plot_pred(predictions: pd.DataFrame):
    fig, axs = plt.subplots(2, 1, sharex=True, figsize=(15, 5))
    predictions = predictions.reset_index()
    predictions = predictions.groupby(['timestamp'], as_index=False).mean()
    predictions['sds_sensor'] = 1
    predictions[['P1', 'pred']].plot(ax=axs[0])
    predictions[['var']].plot(ax=axs[1])
    plt.show()


if __name__ == '__main__':
    np.random.seed(0)
    tf.random.set_seed(0)

    start_date = params['model']['start_date']
    end_date = params['model']['end_date']
    val_split = params['model']['val_split']

    data = pd.read_csv(data_file, parse_dates=['timestamp'])
    data = data[
            (data['timestamp'] >= start_date)
            & (data['timestamp'] < end_date)]
    data = data.dropna(subset=['P1'])
    data = data[x_col + [y_col, 'sds_sensor']]
    data['hum_meteo'] = data['hum_meteo'].fillna(method='bfill')
    data['temp_meteo'] = data['temp_meteo'].fillna(method='bfill')
    data['pres_meteo'] = data['pres_meteo'].fillna(method='bfill')
    data.info()

    # data['hum_meteo'] = (data['hum_meteo'] - data['hum_meteo'].mean()) / data['hum_meteo'].std()
    # data['wind_speed'] = (data['wind_speed'] - data['wind_speed'].mean()) / data['wind_speed'].std()

    data.loc[data.P1 <= 1, 'P1'] = 1

    init_data = data[data['timestamp'] < val_split]
    val_data = data[data['timestamp'] >= val_split]

    pred = main(init_data, val_data)
    plot_pred(pred)
