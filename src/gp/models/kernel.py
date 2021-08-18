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
        period=6,
        )
pk2 = gpflow.kernels.Periodic(
        gpflow.kernels.SquaredExponential(
            lengthscales=12,
            active_dims=[0],
            ),
        period=12,
        )
pk3 = gpflow.kernels.Periodic(
        gpflow.kernels.SquaredExponential(
            lengthscales=12,
            active_dims=[0],
            ),
        period=24,
        )
pk4 = gpflow.kernels.Periodic(
        gpflow.kernels.SquaredExponential(
            lengthscales=12,
            active_dims=[0],
            ),
        period=48,
        )
pk5 = gpflow.kernels.Periodic(
        gpflow.kernels.SquaredExponential(
            lengthscales=12,
            active_dims=[0],
            ),
        period=72,
        )
pk6 = gpflow.kernels.Periodic(
        gpflow.kernels.SquaredExponential(
            lengthscales=12,
            active_dims=[0],
            ),
        period=96,
        )
pk7 = gpflow.kernels.Periodic(
        gpflow.kernels.SquaredExponential(
            lengthscales=12,
            active_dims=[0],
            ),
        period=120,
        )
time_cov = mt + mt1 * (pk1 + pk2 + pk3 + pk4 + pk5 + pk6 + pk7)


def get_kernel(kernel_name: str):
    return {'time_cov': time_cov,
            'basic': time_cov * spat_cov,
            }[kernel_name]
