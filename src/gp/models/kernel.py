import gpflow

spat_cov = gpflow.kernels.Matern32(
        variance=1,
        lengthscales=0.05,
        active_dims=[1, 2],
        )

mt = gpflow.kernels.Matern32(variance=1, lengthscales=5, active_dims=[0])
mt1 = gpflow.kernels.Matern32(variance=1, lengthscales=5, active_dims=[0])

pk1 = gpflow.kernels.Periodic(
        gpflow.kernels.SquaredExponential(
            lengthscales=12,
            active_dims=[0],
            ),
        period=8,
        )
pk2 = gpflow.kernels.Periodic(
        gpflow.kernels.SquaredExponential(
            lengthscales=12,
            active_dims=[0],
            ),
        period=10,
        )
pk3 = gpflow.kernels.Periodic(
        gpflow.kernels.SquaredExponential(
            lengthscales=12,
            active_dims=[0],
            ),
        period=30,
        )
pk4 = gpflow.kernels.Periodic(
        gpflow.kernels.SquaredExponential(
            lengthscales=12,
            active_dims=[0],
            ),
        period=2,
        )

# time_cov = mt + mt1 * (pk1 + pk2 + pk3 + pk4)
time_cov = mt + mt1 * (pk1 + pk2 + pk3)


def get_kernel(kernel_name: str):
    return {'time_cov': time_cov,
            'basic': time_cov * spat_cov,
            }[kernel_name]
