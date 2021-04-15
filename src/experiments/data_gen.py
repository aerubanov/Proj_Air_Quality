import numpy as np
import pymc3 as pm


def genetate_data(size, train_part=0.7):
    x = np.arange(size)[:, None]

    with pm.Model():
        mt = pm.gp.cov.Matern32(1, ls=10)
        pk = pm.gp.cov.Periodic(1, period=5, ls=15)
        cov = mt * pk

        gp = pm.gp.Latent(cov_func=cov)
        pr = gp.prior('pr', X=x)

        check = pm.sample_prior_predictive(1, random_seed=42)

    y = check['pr'][0]
    # y += 0.2 * np.random.randn(*y.shape)

    idx = round(size * train_part)
    x, y, x_star, y_star = x[:idx], y[:idx], x[idx:], y[idx:]
    return x, y, x_star, y_star


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    x, y, x_star, y_star = genetate_data(100)
    fig = plt.figure(figsize=(12, 5))
    plt.plot(x, y)
    plt.plot(x_star, y_star)
    plt.show()
