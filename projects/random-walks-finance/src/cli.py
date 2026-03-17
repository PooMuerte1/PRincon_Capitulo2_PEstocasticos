from __future__ import annotations

import argparse
from dataclasses import asdict

from .barriers import simulate_hit_upper
from .gambler_ruin import (
    expected_duration_closed_form,
    ruin_probability_closed_form,
    simulate_ruin_absorption,
)
from .rw import pmf_Xn, simulate_X, mc_bernoulli_ci


def cmd_pmf(args: argparse.Namespace) -> int:
    xN = simulate_X(n=args.n, p=args.p, paths=args.paths, seed=args.seed)
    hits = int((xN == args.x).sum())
    mc = mc_bernoulli_ci(hits=hits, n=args.paths)
    exact = pmf_Xn(x=args.x, n=args.n, p=args.p)

    print("### P(X_n = x)")
    print(f"n={args.n} x={args.x} p={args.p} paths={args.paths}")
    print(f"exact={exact:.8g}")
    print(f"mc={mc.estimate:.8g}  (95% CI [{mc.ci_low:.8g}, {mc.ci_high:.8g}], se={mc.se:.3g})")
    print(f"abs_error={abs(mc.estimate - exact):.3g}")
    return 0


def cmd_ruin(args: argparse.Namespace) -> int:
    closed = ruin_probability_closed_form(k=args.k, N=args.N, p=args.p)
    sim = simulate_ruin_absorption(k=args.k, N=args.N, p=args.p, paths=args.paths, seed=args.seed)

    print("### Ruina del jugador: u_k = P(absorción en 0)")
    print(f"N={args.N} k={args.k} p={args.p} paths={args.paths}")
    print(f"closed_form={closed:.8g}")
    print(
        f"mc={sim.ruin.estimate:.8g}  (95% CI [{sim.ruin.ci_low:.8g}, {sim.ruin.ci_high:.8g}], se={sim.ruin.se:.3g})"
    )
    print(f"abs_error={abs(sim.ruin.estimate - closed):.3g}")
    return 0


def cmd_duration(args: argparse.Namespace) -> int:
    closed = expected_duration_closed_form(k=args.k, N=args.N, p=args.p)
    sim = simulate_ruin_absorption(k=args.k, N=args.N, p=args.p, paths=args.paths, seed=args.seed)

    print("### Duración: m_k = E[tau]")
    print(f"N={args.N} k={args.k} p={args.p} paths={args.paths}")
    print(f"closed_form={closed:.8g}")
    print(f"mc_avg_tau={sim.avg_tau:.8g} (se={sim.tau_se:.3g})")
    print(f"abs_error={abs(sim.avg_tau - closed):.3g}")
    return 0


def cmd_hit(args: argparse.Namespace) -> int:
    res = simulate_hit_upper(
        p=args.p,
        delta=args.delta,
        y0=args.y0,
        H=args.H,
        T=args.T,
        paths=args.paths,
        seed=args.seed,
    )
    print("### Hitting: P(tau_H <= T)")
    print(f"p={args.p} delta={args.delta} y0={args.y0} H={args.H} T={args.T} paths={args.paths}")
    print(
        f"mc={res.hit_by_T.estimate:.8g}  (95% CI [{res.hit_by_T.ci_low:.8g}, {res.hit_by_T.ci_high:.8g}], se={res.hit_by_T.se:.3g})"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="random-walks-finance")
    sub = p.add_subparsers(dest="cmd", required=True)

    pmf = sub.add_parser("pmf", help="Validar P(X_n=x) exacta vs Monte Carlo")
    pmf.add_argument("--n", type=int, required=True)
    pmf.add_argument("--x", type=int, required=True)
    pmf.add_argument("--p", type=float, required=True)
    pmf.add_argument("--paths", type=int, default=200_000)
    pmf.add_argument("--seed", type=int, default=123)
    pmf.set_defaults(fn=cmd_pmf)

    ruin = sub.add_parser("ruin", help="Ruina: u_k cerrada vs simulación")
    ruin.add_argument("--N", type=int, required=True)
    ruin.add_argument("--k", type=int, required=True)
    ruin.add_argument("--p", type=float, required=True)
    ruin.add_argument("--paths", type=int, default=200_000)
    ruin.add_argument("--seed", type=int, default=123)
    ruin.set_defaults(fn=cmd_ruin)

    dur = sub.add_parser("duration", help="Duración: m_k cerrada vs simulación")
    dur.add_argument("--N", type=int, required=True)
    dur.add_argument("--k", type=int, required=True)
    dur.add_argument("--p", type=float, required=True)
    dur.add_argument("--paths", type=int, default=200_000)
    dur.add_argument("--seed", type=int, default=123)
    dur.set_defaults(fn=cmd_duration)

    hit = sub.add_parser("hit", help="Hitting: P(tau_H<=T) por Monte Carlo")
    hit.add_argument("--p", type=float, required=True)
    hit.add_argument("--delta", type=float, required=True)
    hit.add_argument("--y0", type=float, default=0.0)
    hit.add_argument("--H", type=float, required=True)
    hit.add_argument("--T", type=int, required=True)
    hit.add_argument("--paths", type=int, default=200_000)
    hit.add_argument("--seed", type=int, default=123)
    hit.set_defaults(fn=cmd_hit)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.fn(args))


if __name__ == "__main__":
    raise SystemExit(main())

