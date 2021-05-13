import gpflow
import numpy as np
import matplotlib.pyplot as plt

from src.models.osgpr import OSGPR


def test_data(n=100):
    np.random.seed(1)
    x = np.linspace(0, 5, n)
    y = np.sin(x) + np.random.normal(loc=0, scale=0.2, size=n)
    # plt.plot(x, y)
    # plt.show()
    return x, y


def test_hyperparams():
    x, y = test_data()