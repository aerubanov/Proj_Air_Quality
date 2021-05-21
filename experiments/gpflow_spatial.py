import gpflow
import numpy as np
import matplotlib.pyplot as plt

from .gp_spatial import get_data

data_file = 'DATA/processed/dataset.csv'


def plot_result(model, cur_x, cur_y, xx):
    mx, _ = model.predict_f(xx)

    f, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    ax1.hexbin(xx[:, 0], xx[:, 1], mx,
               gridsize=30, cmap='rainbow', alpha=0.7)
    plot = ax1.scatter(cur_x[:, 0], cur_x[:, 1], c=cur_y[:, 0], s=300, cmap='rainbow')
    ax2.scatter(cur_x[:, 0], cur_x[:, 1], c=cur_y[:, 0], s=300, cmap='rainbow')
    ax1.set_title("Data + Posterior")
    ax2.set_title("Data")
    plt.colorbar(plot)
    plt.savefig('experiments/plots/gpflow_spatial.png')
    plt.show()


def main(M=100):
    x, y, x_new = get_data(data_file)
    y = y[:, None]



    z = x[np.random.permutation(x.shape[0])[0:M], :]

    print(x.shape, y.shape, z.shape)
    print(x)
    print(y)
    model = gpflow.models.sgpr.SGPR((x, y), gpflow.kernels.Matern32(variance=1, lengthscales=0.1), z)
    gpflow.set_trainable(model.kernel, False)
    gpflow.utilities.print_summary(model)

    optimizer = gpflow.optimizers.Scipy()
    optimizer.minimize(model.training_loss, model.trainable_variables)

    gpflow.utilities.print_summary(model)
    plot_result(model, x, y, x_new)


if __name__ == '__main__':
    main()
