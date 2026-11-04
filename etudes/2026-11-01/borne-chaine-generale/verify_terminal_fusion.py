"""Replay the independent checks of FUSION_TOUT_ORDRE.md.

This is a numerical identity verifier, not a scalar gate compiler.
The test body preserves the previously executed tests and RNG seed.
"""

import argparse
import hashlib
import json
from itertools import combinations, permutations, product
from math import comb
from pathlib import Path
from random import Random

Q = 97


def partitions(n, low=1):
    if n == 0:
        yield ()
    for b in range(low, n + 1):
        for p in partitions(n - b, b):
            yield (b,) + p


def red(r):
    return [p for s in range(r + 1) for p in partitions(s, 2)]


def kap(p):
    return sum(comb(b, 2) for b in p)


def bm(beta, lam):
    out = 0
    for inds in permutations(range(len(lam)), len(beta)):
        term = 1
        for b, j in zip(beta, inds):
            term *= comb(lam[j], b) if lam[j] >= b else 0
        out += term
    return out % Q


def basis(r, w):
    coeff = {}
    for lam in red(r):
        diagonal = bm(lam, lam)
        remainder = (
            w(kap(lam)) - sum(coeff[b] * bm(b, lam) for b in coeff)
        ) % Q
        coeff[lam] = remainder * pow(diagonal, -1, Q) % Q
    return coeff


def coeff_moment(B, j, ks, beta, r):
    n = len(B)
    zero = (0,) * (1 + len(beta))
    dp = {zero: 1}
    for i in range(n):
        nxt = {}
        tail = sum(B[i][k] for k in range(n) if k != j) % Q
        options = [(zero, B[i][j]), ((1,) + (0,) * len(beta), tail)]
        for index, k in enumerate(ks):
            degree = [0] * (1 + len(beta))
            degree[0] = 1
            degree[index + 1] = 1
            options.append((tuple(degree), B[i][k]))
        for u, a in dp.items():
            for v, b in options:
                uv = tuple(c + d for c, d in zip(u, v))
                if uv[0] <= r and all(
                    uv[index + 1] <= beta[index] for index in range(len(beta))
                ):
                    nxt[uv] = (nxt.get(uv, 0) + a * b) % Q
        dp = nxt
    return dp.get((r,) + beta, 0)


def evaluate_moment_expansion(B, r, w):
    n = len(B)
    coeff = basis(r, w)
    answer = 0
    for beta, a in coeff.items():
        if not a:
            continue
        for j in range(n):
            for ks in permutations([k for k in range(n) if k != j], len(beta)):
                answer += a * coeff_moment(B, j, ks, beta, r)
    return answer % Q


def direct_tail(B, r, w):
    n = len(B)
    answer = 0
    for j in range(n):
        others = [k for k in range(n) if k != j]
        for rows in combinations(range(n), r):
            outside = set(rows)
            dominant = 1
            for i in range(n):
                if i not in outside:
                    dominant = dominant * B[i][j] % Q
            for cols in product(others, repeat=r):
                amplitude = dominant
                occupation = [0] * n
                for i, k in zip(rows, cols):
                    amplitude = amplitude * B[i][k] % Q
                    occupation[k] += 1
                answer += amplitude * w(kap(occupation))
    return answer % Q


def run():
    rng = Random(41)
    checks = 0
    for r in range(10):
        weights = [rng.randrange(Q) for _ in range(comb(r, 2) + 1)]
        coeff = basis(r, lambda k: weights[k])
        for lam in red(r):
            assert sum(a * bm(b, lam) for b, a in coeff.items()) % Q == weights[kap(lam)]
            checks += 1

    cases = 0
    for n in (5, 6, 7):
        for sample_type in range(3):
            B = [[rng.randrange(Q) for _ in range(n)] for _ in range(n)]
            if sample_type == 1:
                B[1] = [0] * n
            if sample_type == 2:
                B[1][-1] = -sum(B[1][:-1]) % Q
            for r in range(min(3, (n - 1) // 2) + 1):
                weights = [rng.randrange(Q) for _ in range(comb(r, 2) + 1)]
                a = evaluate_moment_expansion(B, r, lambda k: weights[k])
                b = direct_tail(B, r, lambda k: weights[k])
                assert a == b, (n, sample_type, r, a, b)
                cases += 1

    full = 0
    for n in (3, 4, 5, 6):
        K = {kap(p) for p in partitions(n)}
        B = [[rng.randrange(Q) for _ in range(n)] for _ in range(n)]
        amplitudes = {}
        for cols in product(range(n), repeat=n):
            amplitude = 1
            occupation = [0] * n
            for i, j in enumerate(cols):
                amplitude = amplitude * B[i][j] % Q
                occupation[j] += 1
            collision = kap(occupation)
            amplitudes[collision] = (amplitudes.get(collision, 0) + amplitude) % Q
        target = amplitudes.get(0, 0)
        for R in range((n - 1) // 2 + 1):
            bound = n - R - 1
            quotient, remainder = divmod(n, bound)
            tau = quotient * comb(bound, 2) + comb(remainder, 2)
            denominators = sorted(k for k in K if 0 < k <= tau)

            def c(k):
                value = 1
                for denominator in denominators:
                    value = value * (1 - k * pow(denominator, -1, Q)) % Q
                return value

            prefix = sum(a * c(k) for k, a in amplitudes.items()) % Q
            correction = sum(
                evaluate_moment_expansion(
                    B, r, lambda value, r=r: c(comb(n - r, 2) + value)
                )
                for r in range(R + 1)
            ) % Q
            assert (prefix - correction) % Q == target, (
                n, R, prefix, correction, target
            )
            full += 1

    assert (checks, cases, full) == (97, 30, 10)
    here = Path(__file__).resolve().parent
    sources = {}
    for name in (Path(__file__).name, "FUSION_TOUT_ORDRE.md"):
        sources[name] = hashlib.sha256((here / name).read_bytes()).hexdigest()
    report = {
        "status": "passed",
        "Q": Q,
        "rng_seed": 41,
        "binomial_basis_profiles": checks,
        "weighted_tail_instances": cases,
        "whole_chain_raccords": full,
        "scope": {
            "general_polynomial_closure": False,
            "general_quasipolynomial_closure": False,
            "scalar_gate_compiler": False,
            "lean_verified": False,
            "claim": "Exact terminal identities only; the prefix cost remains unbounded polynomially.",
        },
        "source_sha256": sources,
    }
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    result = run()
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.write_report:
        Path(__file__).with_name("terminal-fusion-validation.json").write_text(
            rendered, encoding="utf-8"
        )
    print(rendered, end="")
