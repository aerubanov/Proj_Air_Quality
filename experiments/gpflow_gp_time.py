import gpflow
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from sklearn.metrics import mean_squared_error

from experiments.pymc_gp_time import get_data

data_file = 'DATA/processed/dataset.csv'


def plot_result(model, cur_x, cur_y,  x_star, y_star):
    _, ax = plt.subplots(figsize=(15, 5))
    xx = np.linspace(cur_x.min(), x_star.max(), 200)[:, None]
    samples = model.predict_f_samples(xx, 50)
    var = samples[:, :, 0].numpy().T.var(axis=1)
    mn = samples[:, :, 0].numpy().T.mean(axis=1)
    Zopt = model.inducing_variable.Z
    mu, Su = model.predict_f(Zopt, full_cov=True)
    if len(Su.shape) == 3:
        Su = Su[0, :, :]
    ax.plot(cur_x, cur_y, 'kx', mew=1, alpha=0.8)
    ax.plot(x_star, y_star, 'kx', mew=1, alpha=0.8)
    ax.plot(xx, mn, 'b', lw=2)
    ax.fill_between(
        xx[:, 0],
        mn - 2 * np.sqrt(var),
        mn + 2 * np.sqrt(var),
        color='b', alpha=0.3)
    ax.plot(Zopt.numpy(), mu.numpy(), 'ro', mew=1)
    y_pr = model.predict_f_samples(x_star, 100)[:, :, 0].numpy().T.mean(axis=1)
    rmse = mean_squared_error(y_star, y_pr)
    print(rmse)
    extra = Rectangle((0, 0), 1, 1, fc="w", fill=False,
                      edgecolor='none', linewidth=0)
    ax.legend([extra], (f"RMSE: {rmse}",))
    plt.savefig("experiments/plots/SGPR_time.png")
    plt.show()
    return mu, Su, Zopt, rmse


def train_model(M=30):
    X, y, x_star, y_star = get_data(data_file)
    print(len(X))
    y = y[:, None]
    X = X.astype(np.float64)
    x_star = x_star.astype(np.float64)
    y_star = y_star[:, None]
    print(X.shape, y.shape)
    print(X.dtype, y.dtype)
    print(np.isnan(X).any())
    print(np.isnan(y).any())


    Z = X[np.random.permutation(X.shape[0])[0:M], :]

    mt = gpflow.kernels.Matern32(variance=1, lengthscales=24)
    pk = gpflow.kernels.Periodic(
            gpflow.kernels.SquaredExponential(lengthscales=24*1.5),
            period=24,
            )
    cov = mt * pk
    model = gpflow.models.sgpr.SGPR((X, y), cov, Z)
    
    # gpflow.utilities.print_summary(model)

    optimizer = gpflow.optimizers.Scipy()
    optimizer.minimize(model.training_loss, model.trainable_variables)

    # gpflow.utilities.print_summary(model)

    _, _, _, rmse = plot_result(model, X, y, x_star, y_star)
    return rmse


if __name__ == '__main__':
    np.random.seed(0)
    tf.random.set_seed(0)
    num_ind = [10, 30, 100, 200, 300, 400, 600]
    errors = [train_model(i) for i in num_ind]
    plt.plot(num_ind, errors)
    plt.xlabel('Num. inducing pounts')
    plt.ylabel('RMSE')
    plt.savefig("experiments/plots/SGPR_num_ind.png")
    plt.show()
