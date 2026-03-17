from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from .rw import MCResult, mc_bernoulli_ci, simulate_steps


@dataclass(frozen=True)
class HitResult:
    hit_by_T: MCResult


def simulate_hit_upper(
    *,
    p: float,
    delta: float,
    y0: float,
    H: float,
    T: int,
    paths: int,
    seed: Optional[int] = None,
) -> HitResult:
    """
    Estima P(tau_H <= T) para Y_n = y0 + delta * X_n con pasos +/-1.
    tau_H = min{n>=0 : Y_n >= H}.
    """
    if T < 0 or paths <= 0:
        raise ValueError("T debe ser >= 0 y paths > 0.")
    if delta <= 0:
        raise ValueError("delta debe ser > 0.")
    if H <= y0:
        return HitResult(hit_by_T=MCResult(estimate=1.0, se=0.0, ci_low=1.0, ci_high=1.0))

    rng = np.random.default_rng(seed)
    steps = simulate_steps(n=T, p=p, paths=paths, rng=rng).astype(np.int16)
    x = steps.cumsum(axis=1)
    y = y0 + delta * x
    hit = (y >= H).any(axis=1)
    return HitResult(hit_by_T=mc_bernoulli_ci(hits=int(hit.sum()), n=paths))

