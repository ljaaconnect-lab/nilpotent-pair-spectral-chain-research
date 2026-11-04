"""Exploratory rational invariant, with spectral residue classes retained."""
from hashlib import sha256
from itertools import permutations
from math import prod
from pathlib import Path
import json

Q = 97


def multiply(a, b, q=Q):
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i + j] = (result[i + j] + x * y) % q
    return result


def compositions(total, parts):
    if parts == 1:
        yield (total,)
    else:
        for a in range(total + 1):
            for rest in compositions(total - a, parts - 1):
                yield (a,) + rest


def common_numerator(m, tags):
    n = len(m)
    answer = [1]
    for j, count in enumerate(m):
        for _ in range(n - count):
            answer = multiply(answer, [-tags[j] % Q, 1])
    return answer


def reduce_vector(vector, basis):
    vector = vector[:]
    for pivot, row in sorted(basis.items()):
        if vector[pivot]:
            scale = vector[pivot]
            vector = [(a - scale * b) % Q for a, b in zip(vector, row)]
    return vector


def check_spectral_linear_reader(n, quadratic_tags=False):
    length = 1
    while length <= n:
        length *= 2
    residue = n * (n - 1) // 2 % length
    tags = [(j + 1) ** 2 % Q for j in range(n)] if quadratic_tags else list(range(n))
    target = common_numerator((1,) * n, tags)
    basis = {}
    count = 0
    for m in compositions(n, n):
        if m == (1,) * n or sum(j * k for j, k in enumerate(m)) % length != residue:
            continue
        count += 1
        vector = reduce_vector(common_numerator(m, tags), basis)
        pivot = next((i for i, value in enumerate(vector) if value), None)
        if pivot is not None:
            inverse = pow(vector[pivot], -1, Q)
            basis[pivot] = [value * inverse % Q for value in vector]
    outside = any(reduce_vector(target, basis))
    return {"n": n, "N": length, "target_slot": residue, "pole_tags": tags,
            "collision_occupancies_in_slot": count,
            "polynomial_coordinates": len(target), "collision_rank": len(basis),
            "linear_reader_exists_for_this_rational_invariant": outside}


def dense_refactorization(n):
    tags = list(range(n))
    roots = list(range(n + 1, n + 1 + n * (n - 1)))
    groups_a = [roots[i * (n - 1):(i + 1) * (n - 1)] for i in range(n)]
    groups_b = [roots[i::n] for i in range(n)]

    def matrix(groups):
        return [[prod(t - r for r in group) *
                 pow(prod(t - s for s in tags if s != t), -1, Q) % Q
                 for t in tags] for group in groups]

    def readout(x):
        return sum(prod(x[i][p[i]] for i in range(n)) for p in permutations(range(n))) % Q

    a, b = matrix(groups_a), matrix(groups_b)
    assert all(value for row in a + b for value in row)
    assert sorted(sum(groups_a, [])) == sorted(sum(groups_b, []))
    ra, rb = readout(a), readout(b)
    assert ra != rb
    return {"n": n, "matrix_a": a, "matrix_b": b,
            "readout_a": ra, "readout_b": rb,
            "rational_products_equal_by_root_multiset": True,
            "scope": "one frequency only; cross-frequency data can distinguish these matrices"}


def original_source_at_frequency_zero():
    q = 17
    first = [[0, 4, 4], [4, 0, 4], [4, 4, 0]]
    second = [[4, 0, 4], [4, 0, 4], [5, 4, 5]]
    basis = []
    for j in range(3):
        polynomial = [1]
        for k in range(3):
            if j != k:
                polynomial = multiply(polynomial, [-k % q, 1], q)
        basis.append(polynomial)

    def prepare(a):
        b = [[(1 + value * value) % q for value in row] for row in a]
        polynomial = [1]
        for row in b:
            factor = [sum(row[j] * basis[j][degree] for j in range(3)) % q
                      for degree in range(3)]
            polynomial = multiply(polynomial, factor, q)
        readout = sum(prod(b[i][p[i]] for i in range(3))
                      for p in permutations(range(3))) % q
        return polynomial, readout

    p, x = prepare(first)
    r, y = prepare(second)
    assert p == r and (x, y) == (1, 0)
    return {"prime": q, "z": 1, "frequency": 0, "A_first": first,
            "A_second": second, "common_numerator": p,
            "readouts": [x, y], "scope": "one-frequency invariant only"}


if __name__ == "__main__":
    source = Path(__file__).resolve()
    digest = sha256(source.read_bytes()).hexdigest()
    report = {"status": "passed", "prime": Q, "candidate": "R_B(u)=product_i sum_j x_ij/(u-lambda_j)",
              "original_source_example": original_source_at_frequency_zero(),
              "dense_counterexamples": [dense_refactorization(n) for n in (3, 4)],
              "spectral_rank_tests": [check_spectral_linear_reader(n, quadratic)
                                      for quadratic in (False, True) for n in range(2, 8)],
              "general_polynomial_closure": False, "source_sha256": digest}
    assert all(case["linear_reader_exists_for_this_rational_invariant"] == (case["n"] <= 4)
               for case in report["spectral_rank_tests"])
    assert sha256(source.read_bytes()).hexdigest() == digest
    source.with_name("rational-contractions-validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
