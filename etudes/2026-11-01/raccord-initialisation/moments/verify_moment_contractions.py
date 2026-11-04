"""Verify collision contractions; not a polynomial general-chain compiler."""

from argparse import ArgumentParser
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
from random import Random


def prod(xs, q):
    answer = 1
    for x in xs:
        answer = answer * x % q
    return answer


def assignment_histogram(x, q):
    n = len(x)
    h = n * (n - 1) // 2
    hist = [0] * (h + 1)
    for js in product(range(n), repeat=n):
        kappa = sum(js[a] == js[b] for a in range(n) for b in range(a + 1, n))
        hist[kappa] = (hist[kappa] + prod((x[i][js[i]] for i in range(n)), q)) % q
    return hist


def graph_contractions(x, q, max_edges):
    n = len(x)
    edges = list(combinations(range(n), 2))
    cache = {}

    def w(block):
        key = tuple(block)
        if key not in cache:
            cache[key] = sum(prod((x[i][j] for i in key), q) for j in range(n)) % q
        return cache[key]

    coefficients = []
    for e in range(min(max_edges, len(edges)) + 1):
        total = 0
        for chosen in combinations(edges, e):
            parent = list(range(n))

            def find(a):
                while parent[a] != a:
                    a = parent[a]
                return a

            for a, b in chosen:
                parent[find(a)] = find(b)
            blocks = {}
            for i in range(n):
                blocks.setdefault(find(i), []).append(i)
            total += prod((w(block) for block in blocks.values()), q)
        coefficients.append(total % q)
    return coefficients


def explicit_low_moments(x, q):
    n = len(x)
    universe = set(range(n))
    ell = [sum(row) % q for row in x]

    def term(blocks):
        used = set().union(*map(set, blocks)) if blocks else set()
        factors = [sum(prod((x[i][j] for i in block), q) for j in range(n)) % q
                   for block in blocks]
        factors.extend(ell[i] for i in universe - used)
        return prod(factors, q)

    def single(size):
        return sum(term([s]) for s in combinations(range(n), size)) % q

    a3, a4 = single(3), single(4)
    m22 = 0
    for a, b, c, d in combinations(range(n), 4):
        m22 += term([(a, b), (c, d)]) + term([(a, c), (b, d)]) + term([(a, d), (b, c)])
    m32 = sum(term([triple, pair]) for triple in combinations(range(n), 3)
              for pair in combinations(sorted(universe - set(triple)), 2))

    def pairings(items):
        if not items:
            yield []
        else:
            first, *rest = items
            for index, other in enumerate(rest):
                for tail in pairings(rest[:index] + rest[index + 1:]):
                    yield [(first, other)] + tail

    m222 = sum(term(pairs) for six in combinations(range(n), 6) for pairs in pairings(list(six)))
    mu0, mu1 = term([]), single(2)
    return [mu0, mu1, (mu1 + 6 * a3 + 2 * m22) % q,
            (mu1 + 24 * a3 + 6 * m22 + 96 * a4 + 18 * m32 + 6 * m222) % q]


def stirling_factorial(rmax):
    table = [[0] * (rmax + 1) for _ in range(rmax + 1)]
    table[0][0] = 1
    for r in range(1, rmax + 1):
        for e in range(1, r + 1):
            table[r][e] = e * (table[r - 1][e] + table[r - 1][e - 1])
    return table


def main(write_report):
    source = Path(__file__).resolve()
    before = sha256(source.read_bytes()).hexdigest()
    rng = Random(20261101)
    cases = []
    for q in [17, 97, 998244353]:
        for n in range(1, 7):
            h = n * (n - 1) // 2
            all_orders = n <= 5
            depth = h if all_orders else 3
            for sample in range(2):
                x = [[rng.randrange(q) for _ in range(n)] for _ in range(n)]
                hist = assignment_histogram(x, q)
                cs = graph_contractions(x, q, depth)
                transform = stirling_factorial(depth)
                for r in range(depth + 1):
                    lhs = sum(pow(k, r, q) * hist[k] for k in range(h + 1)) % q
                    rhs = sum(transform[r][e] * cs[e] for e in range(r + 1)) % q
                    assert lhs == rhs, (q, n, sample, r, lhs, rhs)
                expected = [sum(pow(k, r, q) * hist[k] for k in range(h + 1)) % q
                            for r in range(4)]
                assert explicit_low_moments(x, q) == expected
                if all_orders:
                    assert sum((-1) ** e * cs[e] for e in range(h + 1)) % q == hist[0]
                cases.append({"prime": q, "n": n, "sample": sample,
                              "max_moment": depth, "all_orders_and_readout": all_orders})
    assert sha256(source.read_bytes()).hexdigest() == before
    report = {"status": "passed", "source_sha256": before, "cases": cases,
              "case_count": len(cases), "general_polynomial_closure": False,
              "scope": "Exact all-order identities on n<=5; fixed orders 0..3 on n=6. Enumeration belongs to verifier only."}
    if write_report:
        source.with_name("moment-contractions-validation.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "cases"}, ensure_ascii=False))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--write-report", action="store_true")
    main(parser.parse_args().write_report)
