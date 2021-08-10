import gpflow

spat_cov = gpflow.kernels.Matern32(
        variance=1,
        lengthscales=0.05,
        active_dims=[1, 2],
        )

mt = gpflow.kernels.Matern32(variance=1, lengthscales=3, active_dims=[0])
mt1 = gpflow.kernels.Matern32(variance=1, lengthscales=3, active_dims=[0])
pk1 = gpflow.kernels.Periodic(
        gpflow.kernels.SquaredExponential(
            lengthscales=48*3,
            active_dims=[0],
            ),
        period=48,
        )
pk2 = gpflow.kernels.Periodic(
        gpflow.kernels.SquaredExponential(
            lengthscales=32*3,
            active_dims=[0],
            ),
        period=32,
        )
pk3 = gpflow.kernels.Periodic(
        gpflow.kernels.SquaredExponential(
            lengthscales=24*5,
            active_dims=[0],
            ),
        period=24,
        )
pk4 = gpflow.kernels.Periodic(
        gpflow.kernels.SquaredExponential(
            lengthscales=12*5,
            active_dims=[0],
            ),
        period=12,
        )
time_cov = mt1 + mt * (pk3 + pk4)


def get_kernel(kernel_name: str):
    return {'time_cov': time_cov,
            'basic': time_cov * spat_cov,
            }[kernel_name]
