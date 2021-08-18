from typing import List
import gpflow
from gpflow.kernels.base import Kernel
import numpy as np
from src.gp.models.osgpr import OSGPR
from sklearn.base import TransformerMixin
import pandas as pd


class OSGPRTrainer:
    """
    Build, update and evaluate OSGPR model
    """

    def __init__(
            self,
            kernel: Kernel,
            transform: TransformerMixin,
            x_col: List[str],
            y_col: str,
            ):
        self.kernel = kernel
        self.transform = transform
        self.x_col = x_col
        self.y_col = y_col
        self.model = None

    def build_model(
            self,
            data: pd.DataFrame,
            M: int = 200,
            max_iter: int = 1000,
            iprint: int = 50,
            ):
        """
        data: training data
        M: number of inducing points
        max_iter: maximum number of iterations for optimazer
        iprint: optimazer output frequncy
        """
        data = self.transform.transform(data)
        X = data[self.x_col].values
        y = data[self.y_col].values[:, None]
        Z = X[np.random.permutation(X.shape[0])[0:M], :]

        model = gpflow.models.sgpr.SGPR((X, y), self.kernel, Z)
        # gpflow.set_trainable(model.kernel, False)
        optimizer = gpflow.optimizers.Scipy()
        optimizer.minimize(
                model.training_loss,
                model.trainable_variables,
                options={'iprint': iprint, 'maxiter': max_iter},
                )
        self.model = model

    def _init_Z(self, cur_Z, new_X):
        M = cur_Z.shape[0]
        M_old = int(0.7 * M)
        M_new = M - M_old
        old_Z = cur_Z[np.random.permutation(M)[0:M_old], :]
        new_Z = new_X[np.random.permutation(new_X.shape[0])[0:M_new], :]
        Z = np.vstack((old_Z, new_Z))
        return Z

    def update_model(
            self,
            data: pd.DataFrame,
            new_m: int = 20,
            max_iter: int = 1000,
            iprint: int = 50,
            ):
        """
        data, max_iter, iprint: see build_model()
        new_M: number of inducing point to be added with new data
        """
        if self.model is None:
            raise ValueError("You need to run build_model()"
                             "before update_model()")
        data = self.transform.transform(data)
        X = data[self.x_col].values
        y = data[self.y_col].values[:, None]
        Z_opt = self.model.inducing_variable.Z
        mu, Su = self.model.predict_f(Z_opt, full_cov=True)
        if len(Su.shape) == 3:
            Su = Su[0, :, :]
        Kaa1 = self.model.kernel.K(self.model.inducing_variable.Z)

        Zinit = self._init_Z(Z_opt.numpy(), X)

        new_model = OSGPR(
                (X, y),
                self.kernel,
                mu,
                Su,
                Kaa1,
                Z_opt,
                Zinit,
                )
        new_model.likelihood.variance.assign(self.model.likelihood.variance)
        for i, item in enumerate(self.model.kernel.trainable_variables):
            new_model.kernel.trainable_variables[i].assign(item)
        # gpflow.set_trainable(new_model.kernel, False)
        optimizer = gpflow.optimizers.Scipy()
        optimizer.minimize(
                new_model.training_loss,
                new_model.trainable_variables,
                options={'iprint': iprint, 'maxiter': max_iter},
                )
        self.model = new_model

    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """
        Return ndarray with model prediction in 3 columns:
        [mean, conficence interval low bound, conficence in upper bound]
        """
        data = self.transform.transform(data)
        X = data[self.x_col].values
        mu, var = self.model.predict_f(X)
        pred = np.hstack((mu, var))
        pred = self.transform.inverse_transform(pred)
        return pred
