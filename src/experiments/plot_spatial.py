import arviz
import matplotlib.pyplot as plt

from src.experiments.gp_spatial import get_data

if __name__ == '__main__':
    data_file = 'DATA/processed/dataset.csv'
    x, y, x_new = get_data(data_file)
    trace = arviz.from_netcdf('src/experiments/results/gp_spatial_trace')

    f, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    ax1.hexbin(x_new[:, 0], x_new[:, 1], C=trace.posterior['f_star'][0, :, :].mean(axis=0),
               gridsize=30, cmap='rainbow', alpha=0.7)
    plot = ax1.scatter(x[:, 0], x[:, 1], c=y, s=300, cmap='rainbow')
    ax2.scatter(x[:, 0], x[:, 1], c=y, s=300, cmap='rainbow')
    ax1.set_title("Data + Posterior")
    ax2.set_title("Data")
    plt.colorbar(plot)
    plt.show()
