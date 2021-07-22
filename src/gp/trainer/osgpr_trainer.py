import gpflow
from gpflow.kernels.base import Kernel
import numpy as np
from src.models import OSGPR


class OSGPRTrainer:

    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.model = None

    def build_model(
            self,
            X: np.ndarray,
            y: np.ndarray,
            M: int,
            max_iter: int = 1000,
            iprint: int = 50,
            ):
        """
        X: training samples array of shape (num_samples, num_features)
        y: target variables array of shape (num_samples, 1)
        M: number of inducing points
        max_iter: maximum number of iterations for optimazer
        iprint: optimazer output frequncy
        """
        Z = X[np.random.permutation(X.shape[0])[0:M], :]
        model = gpflow.models.sgpr.SGPR((X, y), self.kernel, Z)
        gpflow.set_trainable(model.kernel, False)

        optimizer = gpflow.optimizers.Scipy()
        optimizer.minimize(
                model.training_loss,
                model.trainable_variables,
                options={'iprint': iprint, 'maxiter': max_iter},
                )
        self.model = model

    def update_model(
            self,
            X: np.ndarray,
            y: np.ndarray,
            new_m: int = 20,
            max_iter: int = 1000,
            iprint: int = 50,
            ):
        """
        X, y, max_iter, iprint: see build_model()
        new_M: number of inducing point to be added with new data
        """
        if self.model is None:
            raise ValueError("You need to run build_model()"
                             "before update_model()")
        Z_opt = self.model.inducing_variable.Z
        mu, Su = self.model.predict_f(Z_opt, full_cov=True)
        if len(Su.shape) == 3:
            Su = Su[0, :, :]
        Kaa1 = self.model.kernel.K(self.model.inducing_variable.Z)

        Zinit = X[np.random.permutation(X.shape[0])[0:new_m], :]
        Zinit = np.vstack((Z_opt.numpy(), Zinit))

        new_model = OSGPR(
                (X, y),
                self.kernel,
                mu[new_m:, :],
                Su[new_m:, new_m:],
                Kaa1[new_m:, new_m:],
                Z_opt[new_m:, :],
                Zinit,
                )
        new_model.likelihood.variance.assign(self.model.likelihood.variance)
        for i, item in enumerate(self.model.kernel.trainable_variables):
            new_model.kernel.trainable_variables[i].assign(item)
        gpflow.set_trainable(new_model.kernel, False)
        optimizer = gpflow.optimizers.Scipy()
        optimizer.minimize(
                new_model.training_loss,
                new_model.trainable_variables,
                options={'iprint': iprint, 'maxiter': max_iter},
                )
        self.model = new_model
