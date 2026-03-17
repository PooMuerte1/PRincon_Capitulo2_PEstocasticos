from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from .rw import MCResult, mc_bernoulli_ci


def ruin_probability_closed_form(*, k: int, N: int, p: float) -> float:
    """
    u_k = P(absorción en 0 | X0=k) para caminata absorbente en {0,...,N}.
    """
    if not (0 <= k <= N):
        raise ValueError("Requiere 0 <= k <= N.")
    if not (0.0 <= p <= 1.0):
        raise ValueError("p debe estar en [0,1].")
    if N <= 0:
        raise ValueError("N debe ser > 0.")

    if k == 0:
        return 1.0
    if k == N:
        return 0.0

    q = 1.0 - p
    if abs(p - 0.5) < 1e-12:
        return (N - k) / N
    if p == 0.0:
        return 1.0
    if p == 1.0:
        return 0.0

    r = q / p
    return (r**k - r**N) / (1.0 - r**N)


def expected_duration_closed_form(*, k: int, N: int, p: float) -> float:
    """
    m_k = E[tau | X0=k], tau = tiempo a absorción en {0,N}.
    """
    if not (0 <= k <= N):
        raise ValueError("Requiere 0 <= k <= N.")
    if not (0.0 <= p <= 1.0):
        raise ValueError("p debe estar en [0,1].")
    if N <= 0:
        raise ValueError("N debe ser > 0.")

    if k in (0, N):
        return 0.0
    if p == 0.0 or p == 1.0:
        # Absorción determinística: si p=1, sube 1 cada paso hasta N; si p=0, baja hasta 0.
        # Desde k interior, duración = min(k, N-k) pero en realidad:
        # - p=1: siempre sube => tau = N-k
        # - p=0: siempre baja => tau = k
        return float((N - k) if p == 1.0 else k)

    q = 1.0 - p
    if abs(p - 0.5) < 1e-12:
        return float(k * (N - k))

    if abs(q - p) < 1e-15:
        return float(k * (N - k))

    r = q / p
    return (1.0 / (q - p)) * (k - N * (1.0 - r**k) / (1.0 - r**N))


@dataclass(frozen=True)
class RuinSimResult:
    ruin: MCResult
    avg_tau: float
    tau_se: float


def simulate_ruin_absorption(
    *,
    k: int,
    N: int,
    p: float,
    paths: int,
    seed: Optional[int] = None,
    max_steps: int = 10_000_000,
) -> RuinSimResult:
    """
    Simula tau y evento {absorbe en 0} para el juego absorbente.
    max_steps evita loops infinitos por bugs; en teoría tau es a.s. finito para N finito.
    """
    if not (0 < k < N):
        raise ValueError("Requiere 0 < k < N para simular absorción no trivial.")
    if paths <= 0:
        raise ValueError("paths debe ser > 0.")

    rng = np.random.default_rng(seed)
    x = np.full(paths, k, dtype=np.int32)
    tau = np.zeros(paths, dtype=np.int32)
    alive = (x > 0) & (x < N)

    steps = 0
    while alive.any():
        if steps >= max_steps:
            raise RuntimeError("Se alcanzó max_steps; revisa parámetros o implementación.")

        u = rng.random(alive.sum())
        move = np.where(u < p, 1, -1).astype(np.int32)
        x_alive_idx = np.flatnonzero(alive)
        x[x_alive_idx] += move
        tau[x_alive_idx] += 1

        alive = (x > 0) & (x < N)
        steps += 1

    ruined = (x == 0)
    ruin_ci = mc_bernoulli_ci(hits=int(ruined.sum()), n=paths)

    avg_tau = float(tau.mean())
    tau_se = float(tau.std(ddof=1) / (paths**0.5))
    return RuinSimResult(ruin=ruin_ci, avg_tau=avg_tau, tau_se=tau_se)

