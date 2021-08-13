import gpflow

spat_cov = gpflow.kernels.Matern32(
        variance=1,
        lengthscales=0.05,
        active_dims=[1, 2],
        )

mt = gpflow.kernels.Matern32(variance=1, lengthscales=5, active_dims=[0])
pk1 = gpflow.kernels.Periodic(
        gpflow.kernels.SquaredExponential(
            lengthscales=12,
            active_dims=[0],
            ),
        period=24,
        )
pk2 = gpflow.kernels.Periodic(
        gpflow.kernels.SquaredExponential(
            lengthscales=12,
            active_dims=[0],
            ),
        period=72,
        )
time_cov = mt * (pk1 + pk2)


def get_kernel(kernel_name: str):
    return {'time_cov': time_cov,
            'basic': time_cov * spat_cov,
            }[kernel_name]
