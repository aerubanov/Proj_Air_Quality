import gpflow
import numpy as np
import matplotlib.pyplot as plt
import tensorflow_probability as tfp

from experiments.pymc_gp_time import get_data


data_file = 'DATA/processed/dataset.csv'


def plot_result(model, ax, cur_x, cur_y,  x_star, y_star, xx):
    mx, vx = model.predict_f(xx)
    samples = model.predict_f_samples(xx, 10)
    Zopt = model.inducing_variable.Z
    mu, Su = model.predict_f(Zopt, full_cov=True)
    if len(Su.shape) == 3:
        Su = Su[0, :, :]
        vx = vx[:, 0]
    ax.plot(cur_x, cur_y, 'kx', mew=1, alpha=0.8)
    ax.plot(x_star, y_star, 'rx', mew=1, alpha=0.8)
    ax.plot(xx, mx, 'b', lw=2)
    ax.fill_between(
        xx[:, 0],
        mx[:, 0] - 2 * np.sqrt(vx),
        mx[:, 0] + 2 * np.sqrt(vx),
        color='b', alpha=0.3)
    ax.plot(Zopt.numpy(), mu.numpy(), 'ro', mew=1)
    plt.plot(xx, samples[:, :, 0].numpy().T, "C0", linewidth=0.5)


def main(M=30):
    X, y, x_star, y_star = get_data(data_file)
    y = y[:, None]
    X = X.astype(np.float64)
    x_star = x_star.astype(np.float64)
    y_star = y_star[:, None]
    print(X.shape, y.shape)
    print(X.dtype, y.dtype)

    Z = X[np.random.permutation(X.shape[0])[0:M], :]
    # Z = np.vstack((Z, x_star[np.random.permutation(x_star.shape[0])[0:round(0.25 * M)], :]))

    periods = [6.7, 8.4, 9.5, 14]
    mt = gpflow.kernels.Matern32(variance=1, lengthscales=24)
    # cov = mt + sum([mt * gpflow.kernels.Periodic(gpflow.kernels.SquaredExponential(lengthscales=i*1.5), period=i)
    #                 for i in periods])
    pk = gpflow.kernels.Periodic(gpflow.kernels.SquaredExponential(lengthscales=24*1.5), period=12)
    cov = mt * pk
    model = gpflow.models.sgpr.SGPR((X, y), cov, Z)
    # model.kernel.kernels[1].period.prior = tfp.distributions.Normal(24., 1.)
    # gpflow.set_trainable(model.kernel, False)
    gpflow.utilities.print_summary(model)
    # print(model.kernel.kernels[1].trainable_variables)
    optimizer = gpflow.optimizers.Scipy()

    optimizer.minimize(model.training_loss, model.trainable_variables)

    gpflow.utilities.print_summary(model)

    _, axs = plt.subplots(figsize=(12, 5))
    xx = np.linspace(X.min(), x_star.max(), 200)[:, None]
    plot_result(model, axs, X, y, x_star, y_star, xx)
    plt.savefig("experiments/plots/SGPR_time.png")
    plt.show()


if __name__ == '__main__':
    main(100)
