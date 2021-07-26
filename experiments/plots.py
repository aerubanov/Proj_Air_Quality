import gpflow
import matplotlib.pyplot as plt

from .temp_spat_cv import x_col, y_col


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
