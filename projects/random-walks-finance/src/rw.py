from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Optional

import numpy as np


def simulate_steps(*, n: int, p: float, paths: int, rng: Optional[np.random.Generator] = None) -> np.ndarray:
    """
    Simula incrementos i.i.d. xi ∈ {-1,+1} con P(+1)=p.
    Retorna array shape=(paths, n) con valores -1/+1.
    """
    if not (0.0 <= p <= 1.0):
        raise ValueError("p debe estar en [0,1].")
    if n < 0 or paths <= 0:
        raise ValueError("n debe ser >=0 y paths > 0.")

    rng = rng or np.random.default_rng()
    return rng.choice(np.array([-1, 1], dtype=np.int8), size=(paths, n), p=[1 - p, p])


def simulate_X(*, n: int, p: float, paths: int, x0: int = 0, seed: Optional[int] = None) -> np.ndarray:
    """
    Simula trayectorias de X_t y retorna X_n final por trayectoria.
    """
    rng = np.random.default_rng(seed)
    steps = simulate_steps(n=n, p=p, paths=paths, rng=rng)
    return x0 + steps.sum(axis=1)


def pmf_Xn(*, x: int, n: int, p: float) -> float:
    """
    P(X_n = x | X_0=0) para caminata simple en Z.
    Usa: X_n = 2R_n - n, con R_n ~ Bin(n,p).
    """
    if abs(x) > n:
        return 0.0
    if (n - x) % 2 != 0:
        return 0.0
    r = (n + x) // 2
    q = 1.0 - p
    return comb(n, r) * (p**r) * (q ** (n - r))


@dataclass(frozen=True)
class MCResult:
    estimate: float
    se: float
    ci_low: float
    ci_high: float


def mc_bernoulli_ci(*, hits: int, n: int, z: float = 1.96) -> MCResult:
    """
    IC para una proporción Bernoulli usando Wilson score (más estable que normal simple).
    Útil para checks rápidos de Monte Carlo, especialmente cerca de 0/1.
    """
    if n <= 0:
        raise ValueError("n debe ser > 0.")
    if not (0 <= hits <= n):
        raise ValueError("hits debe estar en [0,n].")
    phat = hits / n
    # Wilson score interval
    z2 = z * z
    denom = 1.0 + z2 / n
    center = (phat + z2 / (2.0 * n)) / denom
    half = (z / denom) * ((phat * (1.0 - phat) / n + z2 / (4.0 * n * n)) ** 0.5)
    ci_low = max(0.0, center - half)
    ci_high = min(1.0, center + half)
    # Error estándar (para referencia) usando normal approx:
    se = (phat * (1.0 - phat) / n) ** 0.5
    return MCResult(estimate=phat, se=se, ci_low=ci_low, ci_high=ci_high)

