"""Scalar NTT x sign-transform compiler for the complete oriented chain.

The coefficient to be computed is never an input.  Every arithmetic gate
is add/mul over a fixed prime field; z remains a genuine input.  The sign
channels are streamed in Gray order.  This removes subset-state storage,
but the gate count of this construction is still exponential.
"""
from fractions import Fraction
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[3]
REFERENCE = ROOT / 'etudes/2026-10-24/chaine-complete/reference/dag.py'
spec = importlib.util.spec_from_file_location('reference_scalar_dag', REFERENCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
DAG = module.DAG


def transform_length(n):
    if n < 1:
        raise ValueError('n must be positive')
    return 1 << n.bit_length()


def spectral_constants(n, prime, generator):
    N = transform_length(n)
    if prime == 2 or (prime - 1) % N:
        raise ValueError('Need an odd prime Q with N dividing Q-1')
    # Q primality is part of the declared field specification.
    omega = pow(generator, (prime - 1) // N, prime)
    if pow(omega, N, prime) != 1 or pow(omega, N // 2, prime) == 1:
        raise ValueError('The supplied generator does not give order N')
    return N, omega


def build(n, labels, prime=998244353, generator=3, from_a=False):
    """Return a charged scalar DAG and every output slot of Z modulo Q.

    All sign channels and all spectral slots are compiled together. No
    subset DP, coefficient oracle, or amplitude input is used here.
    """
    if len(labels) != n:
        raise ValueError('one label per column is required')
    N, omega = spectral_constants(n, prime, generator)
    dag = DAG()
    one = dag.const(1)
    if from_a:
        a = [[dag.inp(('a', i, j)) for j in range(n)] for i in range(n)]
        p = [[dag.add(one, dag.mul(a[i][j], a[i][j]))
              for j in range(n)] for i in range(n)]
    else:
        p = [[dag.inp(('p', i, j)) for j in range(n)] for i in range(n)]

    powers = [dag.inp('z')]
    for _ in range(n * n - 1):
        powers.append(dag.mul(powers[-1], powers[-1]))
    b = [[dag.mul(p[i][j], powers[i * n + j])
          for j in range(n)] for i in range(n)]

    # The phase and Gray-update constants are data-independent.
    phase = [[pow(omega, f * labels[j], prime) for j in range(n)]
             for f in range(N)]
    terms = [[[dag.mul(b[i][j], dag.const(phase[f][j]))
               for j in range(n)] for i in range(n)] for f in range(N)]
    plus2 = [[[dag.mul(dag.const(2), terms[f][i][j]) for j in range(n)]
              for i in range(n)] for f in range(N)]
    minus2 = [[[dag.mul(dag.const(-2), terms[f][i][j]) for j in range(n)]
               for i in range(n)] for f in range(N)]

    def total(xs):
        out = xs[0]
        for x in xs[1:]:
            out = dag.add(out, x)
        return out

    def product(xs):
        out = xs[0]
        for x in xs[1:]:
            out = dag.mul(out, x)
        return out

    # Fix epsilon_n=+1, using homogeneity to pair epsilon and -epsilon.
    sums = [[total(terms[f][i]) for i in range(n)] for f in range(N)]
    accum = [product(sums[f]) for f in range(N)]
    previous = 0
    M = 1 << (n - 1)
    for index in range(1, M):
        gray = index ^ (index >> 1)
        changed = gray ^ previous
        column = changed.bit_length() - 1
        update = minus2 if (gray >> column) & 1 else plus2
        for f in range(N):
            for i in range(n):
                sums[f][i] = dag.add(sums[f][i], update[f][i][column])
            value = product(sums[f])
            accum[f] = (dag.sub(accum[f], value) if index & 1
                        else dag.add(accum[f], value))
        previous = gray
    frequency = [dag.mul(dag.const(Fraction(1, M)), x) for x in accum]

    # An actual inverse NTT: no assumption about the location of its peak.
    def inverse(values):
        size = len(values)
        if size == 1:
            return values
        even = inverse(values[::2])
        odd = inverse(values[1::2])
        lo, hi = [], []
        for j in range(size // 2):
            twiddle = pow(omega, (-j * (N // size)) % N, prime)
            t = dag.mul(dag.const(twiddle), odd[j])
            lo.append(dag.add(even[j], t))
            hi.append(dag.sub(even[j], t))
        return lo + hi

    outputs = [dag.mul(dag.const(Fraction(1, N)), x)
               for x in inverse(frequency)]
    return dag, outputs, {'n': n, 'N': N, 'Q': prime, 'omega': omega,
                          'sign_channels': M, 'gates': dag.gates,
                          'from_a': from_a}


def evaluate_streamed(p, z, labels, prime=998244353, generator=3):
    """Numerical version with polynomial working memory, same sign sum.

    This implementation explicitly computes the final inverse DFT; the
    charged DAG above uses FFT butterflies instead.
    """
    n = len(p)
    N, omega = spectral_constants(n, prime, generator)
    b = [[p[i][j] * pow(z, 1 << (i * n + j), prime) % prime
          for j in range(n)] for i in range(n)]
    terms = [[[b[i][j] * pow(omega, f * labels[j], prime) % prime
               for j in range(n)] for i in range(n)] for f in range(N)]
    sums = [[sum(terms[f][i]) % prime for i in range(n)] for f in range(N)]
    accum = [0] * N
    previous = 0
    M = 1 << (n - 1)
    for index in range(M):
        gray = index ^ (index >> 1)
        if index:
            column = (gray ^ previous).bit_length() - 1
            factor = -2 if (gray >> column) & 1 else 2
            for f in range(N):
                for i in range(n):
                    sums[f][i] = (sums[f][i] + factor * terms[f][i][column]) % prime
        for f in range(N):
            value = 1
            for x in sums[f]:
                value = value * x % prime
            accum[f] = (accum[f] + (-value if index & 1 else value)) % prime
        previous = gray
    invM, invN = pow(M, -1, prime), pow(N, -1, prime)
    frequency = [x * invM % prime for x in accum]
    return [sum(frequency[f] * pow(omega, (-f * k) % N, prime)
                for f in range(N)) * invN % prime for k in range(N)]


def gate_formula(n, from_a=False):
    """Exact add/mul count of build(), including unused prepared updates."""
    N = transform_length(n)
    M = 1 << (n - 1)
    return ((4 if from_a else 2) * n * n - 1
            + 3 * N * n * n + N * (n * n - 1)
            + (M - 1) * N * (2 * n)
            + N * (M // 2)  # negative products in the Gray sum
            + 2 * N + 2 * N * (N.bit_length() - 1))
