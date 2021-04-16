import arviz
import matplotlib.pyplot as plt
from pymc3.gp.util import plot_gp_dist

from src.experiments.gp_time import get_data
from src.experiments.data_gen import genetate_data

trace = "src/experiments/results/gp_time_trace"
data_file = 'DATA/processed/dataset.csv'


def plot_trace(trace, X, X_star, y=None, y_star=None):
    fig = plt.figure(figsize=(12, 5))
    ax = fig.gca()

    ad = arviz.from_netcdf(trace)
    plot_gp_dist(ax, ad.posterior["pr"][0, :, :], X)
    plot_gp_dist(ax, ad.posterior["f_star"][0, :, :], X_star)
    if y is not None:
        plt.plot(X, y, "bo", lw=3, label="Observed values")
    if y_star is not None:
        plt.plot(X_star, y_star, "bo", lw=3, label="Observed values")

    plt.xlabel("X")
    plt.ylabel("Y (normalized)")
    plt.legend()
    plt.show()


if __name__ == '__main__':
    # X, y, x_star, y_star = genetate_data(100)
    X, y, x_star, y_star = get_data(data_file)
    plot_trace(trace, X, x_star, y=y, y_star=y_star)
