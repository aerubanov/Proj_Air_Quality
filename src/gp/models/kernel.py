import gpflow

spat_cov = gpflow.kernels.Matern32(
        variance=1,
        lengthscales=0.05,
        active_dims=[1, 2],
        )

mt = gpflow.kernels.Matern32(variance=1, lengthscales=24, active_dims=[0])
pk = gpflow.kernels.Periodic(
        gpflow.kernels.SquaredExponential(
            lengthscales=24*1.5,
            active_dims=[0],
            ),
        period=24,
        )
time_cov = mt * pk
basic_kernel = spat_cov * time_cov
