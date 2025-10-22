import math
import random
import numpy as np

class RandomGenerators:
    @staticmethod
    def uniform(a=0.0, b=1.0, size=1):
        u = np.random.random(size)
        return a + (b - a) * u

    @staticmethod
    def exponential(lam=1.0, size=1):
        u = np.random.random(size)
        return -np.log(1 - u) / lam

    @staticmethod
    def erlang(k=1, lam=1.0, size=1):
        if k <= 0:
            raise ValueError('k debe ser entero positivo')
        u = np.random.random((size, k))
        exps = -np.log(1 - u) / lam
        return np.sum(exps, axis=1)

    @staticmethod
    def gamma(shape, scale=1.0, size=1):
        size = int(size)
        a = shape
        if a <= 0:
            raise ValueError('shape must be > 0')
        out = np.zeros(size)
        for i in range(size):
            if a < 1:
                g = RandomGenerators.gamma(a + 1, scale=1.0, size=1)[0]
                u = np.random.random()
                out[i] = g * (u ** (1.0 / a))
            else:
                d = a - 1.0/3.0
                c = 1.0 / math.sqrt(9.0 * d)
                while True:
                    x = np.random.normal()
                    v = 1.0 + c * x
                    if v <= 0:
                        continue
                    v = v**3
                    u = np.random.random()
                    if u < 1 - 0.0331 * (x**4):
                        out[i] = d * v
                        break
                    if math.log(u) < 0.5 * x**2 + d * (1 - v + math.log(v)):
                        out[i] = d * v
                        break
        return out * scale

    @staticmethod
    def normal(mu=0.0, sigma=1.0, size=1):
        size = int(size)
        out = np.zeros(size)
        i = 0
        while i < size:
            u1 = random.random()
            u2 = random.random()
            z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2 * math.pi * u2)
            z1 = math.sqrt(-2.0 * math.log(u1)) * math.sin(2 * math.pi * u2)
            out[i] = mu + sigma * z0
            i += 1
            if i < size:
                out[i] = mu + sigma * z1
                i += 1
        return out

    @staticmethod
    def weibull(k=1.0, lam=1.0, size=1):
        u = np.random.random(int(size))
        return lam * ((-np.log(1 - u)) ** (1.0 / k))

    @staticmethod
    def bernoulli(p=0.5, size=1):
        u = np.random.random(int(size))
        return (u < p).astype(int)

    @staticmethod
    def binomial(n=1, p=0.5, size=1):
        size = int(size)
        out = np.zeros(size, dtype=int)
        for i in range(n):
            out += RandomGenerators.bernoulli(p, size=size)
        return out

    @staticmethod
    def poisson(lam=1.0, size=1):
        size = int(size)
        out = np.zeros(size, dtype=int)
        for i in range(size):
            L = math.exp(-lam)
            k = 0
            p = 1.0
            while p > L:
                k += 1
                p *= random.random()
            out[i] = k - 1
        return out