"""Exact, finite research checks for the subset bottleneck (Python standard library).

This is an exponential reference verifier, not a proposed polynomial algorithm.
Run: python verify_subset_representations.py --output verification.json
All computations use integers/Fraction; there is no floating-point tolerance.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, permutations, product
from math import factorial, prod
from pathlib import Path
import json
import random


def permanent(b):
    n = len(b)
    return sum(prod(b[i][p[i]] for i in range(n)) for p in permutations(range(n)))


def prefix_states(rows, n):
    f = {0: 1}
    for row in rows:
        nxt = defaultdict(int)
        for mask, c in f.items():
            for j, weight in enumerate(row):
                if not (mask >> j) & 1:
                    nxt[mask | (1 << j)] += c * weight
        f = dict(nxt)
    return f


def poly_add(a, b):
    c = dict(a)
    for k, v in b.items():
        c[k] = c.get(k, 0) + v
        if c[k] == 0:
            del c[k]
    return c


def poly_mul(a, b):
    c = defaultdict(int)
    for i, x in a.items():
        for j, y in b.items():
            c[i + j] += x * y
    return {k: v for k, v in c.items() if v}


def root_code(mask, n):
    q = {0: 1}
    for j in range(n):
        if (mask >> j) & 1:
            q = poly_mul(q, {1: 1, 0: -(j + 1)})
    return q


def averaged_root_code(states, n):
    out = {}
    for mask, c in states.items():
        out = poly_add(out, {e: c * v for e, v in root_code(mask, n).items()})
    return out


def perm_sign(p):
    return (-1) ** sum(p[i] > p[j] for i in range(len(p)) for j in range(i+1, len(p)))


def address(p):
    n = len(p)
    return sum(1 << (i * n + j) for i, j in enumerate(p))


def marked_permanent(p):
    n = len(p)
    return {address(s): prod(p[i][s[i]] for i in range(n))
            for s in permutations(range(n))}


def sign_samples(n):
    for tail in product((-1, 1), repeat=n-1):
        yield (1,) + tail


def sample_block(rows, signs):
    return prod(sum(b * e for b, e in zip(row, signs)) for row in rows)


def sampled_permanent(b):
    n = len(b)
    return Fraction(sum(prod(e) * sample_block(b, e) for e in sign_samples(n)), 2 ** (n-1))


def sampled_marked_permanent(p):
    n = len(p)
    result = {}
    for eps in sign_samples(n):
        term = {0: prod(eps)}
        for i, row in enumerate(p):
            term = poly_mul(term, {1 << (i*n+j): row[j]*eps[j] for j in range(n)})
        result = poly_add(result, term)
    return {e: Fraction(c, 2 ** (n-1)) for e, c in result.items() if c}


def compositions(n, k):
    if k == 1:
        yield (n,)
    else:
        for j in range(n+1):
            for tail in compositions(n-j, k-1):
                yield (j,) + tail


def rational_rank(matrix):
    a = [[Fraction(v) for v in row] for row in matrix]
    r = 0
    for j in range(len(a[0])):
        pivot = next((i for i in range(r, len(a)) if a[i][j]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        d = a[r][j]
        a[r] = [v / d for v in a[r]]
        for i in range(r+1, len(a)):
            d = a[i][j]
            if d:
                a[i] = [v-d*w for v, w in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def root_checks():
    count = 0
    for n in range(1, 7):
        codes = [root_code(mask, n) for mask in range(1 << n)]
        assert len({tuple(sorted(q.items())) for q in codes}) == 1 << n
        for s in range(1 << n):
            for t in range(1 << n):
                if s & t == 0:
                    assert poly_mul(codes[s], codes[t]) == codes[s | t]
                    count += 1
    b1 = [[1, 10, 1], [2, 1, 1], [2, 1, 1]]
    b2 = [[5, 2, 5], [2, 1, 1], [2, 1, 1]]
    a1 = [[0, 3, 0], [1, 0, 0], [1, 0, 0]]
    a2 = [[2, 1, 2], [1, 0, 0], [1, 0, 0]]
    for aa, bb in [(a1,b1),(a2,b2)]:
        assert [[1+x*x for x in row] for row in aa] == bb
    q1 = averaged_root_code(prefix_states(b1[:1],3),3)
    q2 = averaged_root_code(prefix_states(b2[:1],3),3)
    assert q1 == q2 == {1:12,0:-24}
    assert permanent(b1) == 46 and permanent(b2) == 38
    # A second counterexample after two prefix rows.
    c1 = [[1]*4,[1,17,5,5],[2,1,1,1],[2,1,1,1]]
    c2 = [[1]*4,[5,5,17,1],[2,1,1,1],[2,1,1,1]]
    r1 = averaged_root_code(prefix_states(c1[:2],4),4)
    r2 = averaged_root_code(prefix_states(c2[:2],4),4)
    assert r1 == r2 == {2:84,1:-420,0:506}
    assert permanent(c1) == 276 and permanent(c2) == 260
    return {"disjoint_union_checks":count,
            "single_subset_codes_injective_through_n":6,
            "legal_counterexample":{"A1":a1,"A2":a2,"B1_at_z1":b1,"B2_at_z1":b2,
                "identical_prefix_summary":"12 X - 24","PA1_at_z1":46,"PA2_at_z1":38},
            "depth2_counterexample":{"B1_at_z1":c1,"B2_at_z1":c2,
                "identical_prefix_summary":"84 X^2 - 420 X + 506",
                "PA1_at_z1":276,"PA2_at_z1":260}}


def sampling_checks():
    rng = random.Random(20261024)
    numeric = symbolic = fusions = basis = 0
    for n in range(1, 8):
        for case in range(12):
            a = [[rng.randint(-3,3) for _ in range(n)] for _ in range(n)]
            b = [[1+x*x for x in row] for row in a]
            assert sampled_permanent(b) == permanent(b)
            numeric += 1
            for cut in range(n+1):
                for eps in sign_samples(n):
                    assert sample_block(b[:cut],eps)*sample_block(b[cut:],eps) == sample_block(b,eps)
                    fusions += 1
        for exps in compositions(n,n):
            value = Fraction(sum(prod(eps)*prod(e**m for e,m in zip(eps,exps))
                                 for eps in sign_samples(n)), 2**(n-1))
            assert value == (1 if exps == (1,)*n else 0)
            basis += 1
        if n <= 4:
            for case in range(4):
                a = [[rng.randint(-2,2) for _ in range(n)] for _ in range(n)]
                p = [[1+x*x for x in row] for row in a]
                assert sampled_marked_permanent(p) == marked_permanent(p)
                symbolic += 1
    return {"numeric_legal_matrices":numeric,"whole_marked_polynomials":symbolic,
            "pointwise_block_fusion_checks":fusions,"homogeneous_monomial_checks":basis,
            "seed":20261024,"sample_count":"2^(n-1)",
            "polynomial_algorithm":False}


def spectral_checks():
    records = []
    for n in range(1,7):
        perms = list(permutations(range(n)))
        es = [address(p) for p in perms]
        signs = [perm_sign(p) for p in perms]
        assert len(set(es)) == factorial(n)
        # For A=0, verify every T<n! fails on the complete marked polynomial.
        for modulus in range(1,factorial(n)):
            sums = defaultdict(int)
            for e, s in zip(es,signs):
                sums[e % modulus] += s
            output = [s*sums[e % modulus] for e,s in zip(es,signs)]
            assert any(c != 1 for c in output)
        record = {"n":n,"permutation_count":len(es),"all_T_below_factorial_rejected_for_A0":True}
        if n <= 5:
            found = next((m for m in range(factorial(n),10001)
                          if len({e % m for e in es}) == len(es)),None)
            record["minimum_injective_modulus_up_to_10000"] = found
        if n <= 4:
            h = [[2**sum(a == b for a,b in zip(s,t)) for t in perms] for s in perms]
            rank = rational_rank(h)
            assert rank == len(perms)
            record["legal_permutation_input_coefficient_rank"] = rank
        records.append(record)
    perms = list(permutations(range(3)))
    es = [address(p) for p in perms]
    signs = [perm_sign(p) for p in perms]
    sums = defaultdict(int)
    for e,s in zip(es,signs): sums[e%5] += s
    example = [{"exponent":e,"correct":1,"T5_output":s*sums[e%5]} for e,s in sorted(zip(es,signs))]
    return {"records":records,"n3_A0_T5_counterexample":example,
            "theorem_scope":"Fixed scalar sample nodes independent of A and z; linear reconstruction independent of A.",
            "sample_lower_bound":"n!","general_circuit_lower_bound":False}


def paper_checks():
    # Proposition B.26: polynomial in the collision counter on every monomial.
    count = 0
    for n in range(1,8):
        hn = n*(n-1)//2
        for exps in compositions(n,n):
            kappa = sum(m*(m-1)//2 for m in exps)
            projection = prod(Fraction(r-kappa,r) for r in range(1,hn+1))
            assert projection == (1 if exps == (1,)*n else 0)
            count += 1
    # B.18 at Q=13, N=4, omega=5; arbitrary amplitude 6, target slot 3.
    q, N, omega, amplitude, slot = 13,4,5,6,3
    spectrum = [amplitude*pow(omega,f*slot,q)%q for f in range(N)]
    restored = [sum(spectrum[f]*pow(omega,(-f*k)%N,q) for f in range(N))*pow(N,-1,q)%q
                for k in range(N)]
    assert restored == [0,0,0,6]
    return {"B26_monomial_checks":count,"B18_exact_example_spectrum":spectrum,
            "B18_exact_example_output":restored,
            "spectral_overhead_preserved":"2 N log2(N) + 3 N - 3 for N a power of two >=2"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=Path('verification.json'))
    parser.add_argument('--paper',type=Path)
    args = parser.parse_args()
    results = {"date":"2026-10-24","status":"General polynomial scalar source remains unconstructed",
               "exact_arithmetic":True,"formal_proof_status":"Written arguments; no new Lean certification",
               "verification_kind":"Finite development checks, not an asymptotic proof or held-out benchmark",
               "root_polynomial":root_checks(),"sign_evaluations":sampling_checks(),
               "B27_fixed_sampling":spectral_checks(),"paper_bridge":paper_checks()}
    if args.paper:
        results['source_pdf'] = {'name':args.paper.name,'sha256':sha256(args.paper.read_bytes()).hexdigest()}
    results['verifier_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(results,indent=2,ensure_ascii=False))


if __name__ == '__main__':
    main()
