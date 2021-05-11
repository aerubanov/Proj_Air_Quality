from gpflow.models import GPModel
from gpflow.models.training_mixins import RegressionData, InputData
from gpflow.kernels import Kernel
from gpflow.mean_functions import Zero
from gpflow.likelihoods import Gaussian
from gpflow.types import MeanAndVariance
from gpflow.inducing_variables import InducingPoints
import gpflow
import tensorflow as tf
from typing import Optional, Union
import numpy as np


float_type = gpflow.config.default_float()
print(float_type)

class OSGPR(GPModel, gpflow.models.InternalDataTrainingLossMixin):
    """
    Online Sparse Variational GP regression.

    Streaming Gaussian process approximations
    Thang D. Bui, Cuong V. Nguyen, Richard E. Turner
    NIPS 2017
    """
    def __init__(self,
                 data: RegressionData,
                 kernel: Kernel,
                 mu_old: Optional[tf.Tensor],
                 Su_old: Optional[tf.Tensor],
                 Kaa_old: Optional[tf.Tensor],
                 Z_old: Optional[tf.Tensor],
                 inducing_variable: Union[InducingPoints, np.ndarray],
                 mean_function=Zero()):
        """
        Z is a matrix of pseudo inputs, size M x D
        kern, mean_function are appropriate gpflow objects
        mu_old, Su_old are mean and covariance of old q(u)
        Z_old is the old inducing inputs
        This method only works with a Gaussian likelihood.
        """
        X, Y = data
        self.X = X
        self.Y = Y
        likelihood = Gaussian()
        self.inducing_variable = gpflow.models.util.inducingpoint_wrapper(inducing_variable)

        GPModel.__init__(self, kernel, likelihood, mean_function, inducing_variable.size)

        self.num_data = X.shape[0]
        self.num_latent = Y.shape[1]

        self.mu_old = gpflow.Parameter(mu_old, trainable=False)
        self.M_old = Z_old.shape[0]
        self.Su_old = gpflow.Parameter(Su_old, trainable=False)
        self.Kaa_old = gpflow.Parameter(Kaa_old, trainable=False)
        self.Z_old = gpflow.Parameter(Z_old,  trainable=False)

    def _build_common_terms(self):
        Mb = tf.shape(self.inducing_variable.Z)[0]
        Ma = self.M_old
        # jitter = settings.numerics.jitter_level
        jitter = 1e-3
        sigma2 = self.likelihood.variance
        sigma = tf.sqrt(sigma2)

        Saa = self.Su_old
        ma = self.mu_old

        # a is old inducing points, b is new
        # f is training points
        # s is test points
        Kbf = self.kernel.K(self.inducing_variable.Z, self.X)
        Kbb = self.kernel.K(self.inducing_variable.Z) + tf.eye(Mb, dtype=float_type) * jitter
        Kba = self.kernel.K(self.inducing_variable.Z, self.Z_old)
        Kaa_cur = self.kernel.K(self.Z_old) + tf.eye(Ma, dtype=float_type) * jitter
        Kaa = self.Kaa_old + tf.eye(Ma, dtype=float_type) * jitter

        err = self.Y - self.mean_function(self.X)

        Sainv_ma = tf.linalg.solve(Saa, ma)
        Sinv_y = self.Y / sigma2
        c1 = tf.matmul(Kbf, Sinv_y)
        c2 = tf.matmul(Kba, Sainv_ma)
        c = c1 + c2

        Lb = tf.linalg.cholesky(Kbb)
        Lbinv_c = tf.linalg.triangular_solve(Lb, c, lower=True)
        Lbinv_Kba = tf.linalg.triangular_solve(Lb, Kba, lower=True)
        Lbinv_Kbf = tf.linalg.triangular_solve(Lb, Kbf, lower=True) / sigma
        d1 = tf.matmul(Lbinv_Kbf, tf.transpose(Lbinv_Kbf))

        LSa = tf.linalg.cholesky(Saa)
        Kab_Lbinv = tf.transpose(Lbinv_Kba)
        LSainv_Kab_Lbinv = tf.linalg.triangular_solve(
            LSa, Kab_Lbinv, lower=True)
        d2 = tf.matmul(tf.transpose(LSainv_Kab_Lbinv), LSainv_Kab_Lbinv)

        La = tf.linalg.cholesky(Kaa)
        Lainv_Kab_Lbinv = tf.linalg.triangular_solve(
            La, Kab_Lbinv, lower=True)
        d3 = tf.matmul(tf.transpose(Lainv_Kab_Lbinv), Lainv_Kab_Lbinv)

        D = tf.eye(Mb, dtype=float_type) + d1 + d2 - d3
        D = D + tf.eye(Mb, dtype=float_type) * jitter
        LD = tf.linalg.cholesky(D)

        LDinv_Lbinv_c = tf.linalg.triangular_solve(LD, Lbinv_c, lower=True)

        return (Kbf, Kba, Kaa, Kaa_cur, La, Kbb, Lb, D, LD,
                Lbinv_Kba, LDinv_Lbinv_c, err, d1)

    def maximum_log_likelihood_objective(self) -> tf.Tensor:
        """
        Construct a tensorflow function to compute the bound on the marginal
        likelihood.
        """

        # Mb = tf.shape(self.inducing_variable)[0]
        # Ma = self.M_old
        # jitter = gpflow.config.default_jitter()
        # jitter = 1e-4
        sigma2 = self.likelihood.variance
        # sigma = tf.sqrt(sigma2)
        N = self.num_data

        Saa = self.Su_old
        ma = self.mu_old

        # a is old inducing points, b is new
        # f is training points
        Kfdiag = self.kernel(self.X, full_cov=False)
        (Kbf, Kba, Kaa, Kaa_cur, La, Kbb, Lb, D, LD,
        Lbinv_Kba, LDinv_Lbinv_c, err, Qff) = self._build_common_terms()

        LSa = tf.linalg.cholesky(Saa)
        Lainv_ma = tf.linalg.triangular_solve(LSa, ma, lower=True)

        bound = 0
        # constant term
        bound = -0.5 * N * np.log(2 * np.pi)
        # quadratic term
        bound += -0.5 * tf.reduce_sum(tf.square(err)) / sigma2
        # bound += -0.5 * tf.reduce_sum(ma * Sainv_ma)
        bound += -0.5 * tf.reduce_sum(tf.square(Lainv_ma))
        bound += 0.5 * tf.reduce_sum(tf.square(LDinv_Lbinv_c))
        # log det term
        bound += -0.5 * N * tf.reduce_sum(tf.math.log(sigma2))
        bound += - tf.reduce_sum(tf.math.log(tf.linalg.diag_part(LD)))

        # delta 1: trace term
        bound += -0.5 * tf.reduce_sum(Kfdiag) / sigma2
        bound += 0.5 * tf.reduce_sum(tf.linalg.diag_part(Qff))

        # delta 2: a and b difference
        bound += tf.reduce_sum(tf.math.log(tf.linalg.diag_part(La)))
        bound += - tf.reduce_sum(tf.math.log(tf.linalg.diag_part(LSa)))

        Kaadiff = Kaa_cur - tf.matmul(tf.transpose(Lbinv_Kba), Lbinv_Kba)
        Sainv_Kaadiff = tf.linalg.solve(Saa, Kaadiff)
        Kainv_Kaadiff = tf.linalg.solve(Kaa, Kaadiff)

        bound += -0.5 * tf.reduce_sum(
            tf.linalg.diag_part(Sainv_Kaadiff) - tf.linalg.diag_part(Kainv_Kaadiff))
        print(bound)

        return bound

    def predict_f(self, Xnew: InputData, full_cov: bool = False, **kwargs) -> MeanAndVariance:
        """
        Compute the mean and variance of the latent function at some new points
        Xnew.
        """

        # jitter = settings.numerics.jitter_level
        jitter = 1e-3

        # a is old inducing points, b is new
        # f is training points
        # s is test points
        Kbs = self.kernel.K(self.inducing_variable.Z, Xnew)
        (Kbf, Kba, Kaa, Kaa_cur, La, Kbb, Lb, D, LD,
            Lbinv_Kba, LDinv_Lbinv_c, err, Qff) = self._build_common_terms()

        Lbinv_Kbs = tf.linalg.triangular_solve(Lb, Kbs, lower=True)
        LDinv_Lbinv_Kbs = tf.linalg.triangular_solve(LD, Lbinv_Kbs, lower=True)
        mean = tf.matmul(tf.transpose(LDinv_Lbinv_Kbs), LDinv_Lbinv_c)

        if full_cov:
            Kss = self.kernel.K(Xnew) + jitter * tf.eye(tf.shape(Xnew)[0], dtype=float_type)
            var1 = Kss
            var2 = - tf.matmul(tf.transpose(Lbinv_Kbs), Lbinv_Kbs)
            var3 = tf.matmul(tf.transpose(LDinv_Lbinv_Kbs), LDinv_Lbinv_Kbs)
            var = var1 + var2 + var3
        else:
            var1 = self.kernel(Xnew, full_cov=False)
            var2 = -tf.reduce_sum(tf.square(Lbinv_Kbs), 0)
            var3 = tf.reduce_sum(tf.square(LDinv_Lbinv_Kbs), 0)
            var = var1 + var2 + var3

        return mean + self.mean_function(Xnew), var
