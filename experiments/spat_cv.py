import json
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.metrics import mean_squared_error
import yaml
import matplotlib.pyplot as plt
import gpflow

from experiments.temp_cv import x_col, y_col, time_cv
from src.gp.trainer.osgpr_trainer import OSGPRTrainer
from src.gp.transform.basic import GPTransform
from src.gp.models.kernel import get_kernel

with open('params.yaml', 'r') as fd:
    params = yaml.safe_load(fd)

pd.options.mode.chained_assignment = None  # default='warn'

data_file = params['data']['paths']['dataset_file']
kernel = get_kernel(params['model']['kernel'])


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
    predictions = []
    n_sensors = round(len(val_data['sds_sensor'].unique()) * 0.25)
    for i, item in enumerate(time_cv(val_data)):
        test_data = item.spat.random_sensors(n_sensors)
        train_data = item[~item['sds_sensor'].isin(
            test_data['sds_sensor'].unique())]
        y_test = test_data.spat.y.values

        trainer.update_model(
                train_data.copy(),
                max_iter=params['model']['max_iter'],
                new_m=params['model']['num_induc_upd'],
                iprint=-1,
                )
        pred = trainer.predict(test_data.copy())
        test_data['pred'], test_data['var'] = \
            pred[:, 0], pred[:, 1]
        predictions.append(test_data)
        mse = mean_squared_error(y_test, pred[:, 0])
        print(f'step {i} RMSE: {np.sqrt(mse)}')
        results.append(mse)
    print(np.mean(np.sqrt(results)), np.std(np.sqrt(results)))
    gpflow.utilities.print_summary(trainer.model)
    plot_spatial(trainer, train_data)

    with open(params['model']['spat_cv']['result_file'], 'w') as fd:
        json.dump({
            'mean RMSE': np.mean(np.sqrt(results)),
            'RMSE std': np.std(np.sqrt(results)),
            }, fd)

    plot_data = np.sqrt(results)
    plot_data = [{'step': i, 'RMSE': plot_data[i]}
                 for i in range(len(plot_data))]
    with open(params['model']['spat_cv']['plot_file'], 'w') as fd:
        json.dump({'spat_cv': plot_data}, fd)

    predictions = pd.concat(predictions, ignore_index=True)
    predictions.to_csv(params['model']['spat_cv']['prediction'])


def plot_spatial(trainer, data: pd.DataFrame):
    timestamp = data['timestamp'].max()
    df = data[data['timestamp'] == timestamp]
    x = df[x_col].values
    y = df[y_col].values

    lon_min, lon_max = x[:, 1].min(), x[:, 1].max()
    lat_min, lat_max = x[:, 2].min(), x[:, 2].max()

    new_lon, new_lat = np.mgrid[
            lon_min:lon_max:0.025,
            lat_min:lat_max:0.0125,
            ]
    xx = pd.DataFrame(
            data={
                'timestamp': [timestamp for i in range(
                    new_lon.flatten().shape[0])],
                'lon': new_lon.flatten(),
                'lat': new_lat.flatten(),
            }
    )
    xx['sds_sensor'] = 1
    xx['P1'] = 1
    pred = trainer.predict(xx)
    mx, var = pred[:, 0], pred[:, 1]
    f, (ax3, ax4) = plt.subplots(1, 2, figsize=(16, 8))
    plot1 = ax3.hexbin(xx.lon, xx.lat, mx,
                       gridsize=30, cmap='rainbow', alpha=0.7)
    ax3.scatter(x[:, 1], x[:, 2],
                c=y,
                s=300, cmap='rainbow')
    plot2 = ax4.hexbin(xx.lon, xx.lat, var,
                       gridsize=30, cmap='rainbow', alpha=0.7)
    plt.colorbar(plot1, ax=ax3)
    plt.colorbar(plot2, ax=ax4)
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

    data.loc[data.P1 <= 1, 'P1'] = 1

    init_data = data[data['timestamp'] < val_split]
    val_data = data[data['timestamp'] >= val_split]
    main(init_data, val_data)
