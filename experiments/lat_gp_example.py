import arviz as az
import matplotlib.pyplot as plt
import numpy as np
import pymc3 as pm


RANDOM_SEED = 8927
np.random.seed(RANDOM_SEED)
az.style.use("arviz-darkgrid")

if __name__ == '__main__':
    n = 200  # The number of data points
    X = np.linspace(0, 10, n)[:, None]  # The inputs to the GP must be arranged as a column vector

    # Define the true covariance function and its parameters
    ℓ_true = 1.0
    η_true = 3.0
    cov_func = η_true ** 2 * pm.gp.cov.Matern52(1, ℓ_true)

    # A mean function that is zero everywhere
    mean_func = pm.gp.mean.Zero()

    # The latent function values are one sample from a multivariate normal
    # Note that we have to call `eval()` because PyMC3 built on top of Theano
    f_true = np.random.multivariate_normal(
        mean_func(X).eval(), cov_func(X).eval() + 1e-8 * np.eye(n), 1
    ).flatten()

    # The observed data is the latent function plus a small amount of T distributed noise
    # The standard deviation of the noise is `sigma`, and the degrees of freedom is `nu`
    σ_true = 2.0
    ν_true = 3.0
    y = f_true + σ_true * np.random.standard_t(ν_true, size=n)

    # Plot the data and the unobserved latent function
    fig = plt.figure(figsize=(12, 5))
    ax = fig.gca()
    ax.plot(X, f_true, "dodgerblue", lw=3, label="True generating function 'f'")
    ax.plot(X, y, "ok", ms=3, label="Observed data")
    ax.set_xlabel("X")
    ax.set_ylabel("y")
    plt.legend()
    plt.show()

    with pm.Model() as model:
        l_ = pm.Gamma("l", alpha=2, beta=1)
        eta = pm.HalfCauchy("eta", beta=1)

        cov = eta ** 2 * pm.gp.cov.Matern52(1, l_)
        gp = pm.gp.Latent(cov_func=cov)

        f = gp.prior("f", X=X)

        sigma = pm.HalfCauchy("sigma", beta=5)
        nu = pm.Gamma("nu", alpha=2, beta=0.1)
        y_ = pm.StudentT("y", mu=f, lam=1.0 / sigma, nu=nu, observed=y)

        trace = pm.sample(200, n_init=100, tune=100, chains=2, cores=2, return_inferencedata=True)
        az.to_netcdf(trace, 'src/experiments/results/lat_gp_trace')

    # check Rhat, values above 1 may indicate convergence issues
    n_nonconverged = int(np.sum(az.rhat(trace)[["eta", "l", "f_rotated_"]].to_array() > 1.03).values)
    print("%i variables MCMC chains appear not to have converged." % n_nonconverged)

    # plot the results
    fig = plt.figure(figsize=(12, 5))
    ax = fig.gca()

    # plot the samples from the gp posterior with samples and shading
    from pymc3.gp.util import plot_gp_dist

    plot_gp_dist(ax, trace.posterior["f"][0, :, :], X)

    # plot the data and the true latent function
    ax.plot(X, f_true, "dodgerblue", lw=3, label="True generating function 'f'")
    ax.plot(X, y, "ok", ms=3, label="Observed data")

    # axis labels and title
    plt.xlabel("X")
    plt.ylabel("True f(x)")
    plt.title("Posterior distribution over $f(x)$ at the observed values")
    plt.legend()
    plt.show()
