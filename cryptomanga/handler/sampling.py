import numpy as np


def bernoulli(p: float) -> int:
    return np.random.binomial(1, p=p)


def normal(mu: float, sigma: float) -> float:
    return np.random.normal(mu, sigma)


def normal_batch(mu: float, sigma: float, samples: int):
    return np.random.normal(mu, sigma, samples)


def bernoulli_batch(p: float, samples: int):
    return np.random.binomial(samples, p=p)
