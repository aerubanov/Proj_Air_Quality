import arviz
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from pymc3.gp.util import plot_gp_dist
from sklearn.metrics import mean_squared_error

from experiments.pymc_gp_time import get_data


trace = "experiments/results/gp_time_trace"
data_file = 'DATA/processed/dataset.csv'


def plot_trace(trace, X, X_star, y=None, y_star=None):
    fig = plt.figure(figsize=(12, 5))
    ax = fig.gca()

    ad = arviz.from_netcdf(trace)
    rmse = mean_squared_error(
        y_true=y_star,
        y_pred=ad.posterior['f_star'][0, :, :].mean(axis=0),
        )
    print(rmse)

    plot_gp_dist(ax, ad.posterior["pr"][0, :, :], X)
    plot_gp_dist(ax, ad.posterior["f_star"][0, :, :], X_star)
    if y is not None:
        plt.plot(X, y, "kx", lw=3)
    if y_star is not None:
        plt.plot(X_star, y_star, "kx", lw=3)

    plt.xlabel("X")
    plt.ylabel("Y (normalized)")
    extra = Rectangle((0, 0), 1, 1, fc="w", fill=False,
                      edgecolor='none', linewidth=0)
    ax.legend([extra], (f"RMSE: {rmse}",))
    plt.savefig("experiments/plots/" + trace.split('/')[-1] + '.png')
    plt.show()


if __name__ == '__main__':
    # X, y, x_star, y_star = genetate_data(100)
    X, y, x_star, y_star = get_data(data_file)
    plot_trace(trace, X, x_star, y=y, y_star=y_star)
