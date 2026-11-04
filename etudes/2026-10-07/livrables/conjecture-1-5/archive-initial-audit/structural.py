"""Exact development tools for Arbor n2; no polynomial algorithm is claimed.

All infinite-domain mathematical arguments in constraints.md remain Lean-unverified.
The default P_A(1) evaluator explicitly enumerates n! permutations.
"""
from fractions import Fraction
from itertools import permutations
from math import factorial, prod, isqrt


def square_matrix(A):
    A = tuple(tuple(Fraction(v) for v in row) for row in A)
    if not A or any(len(row) != len(A) for row in A):
        raise ValueError("Expected a nonempty square matrix")
    return A


def permanent(A):
    A = square_matrix(A)
    n = len(A)
    return sum((prod(A[i][sigma[i]] for i in range(n))
                for sigma in permutations(range(n))), Fraction(0))


def specialize_pa(A):
    """Compute P_A(1) = per(1 + A**2), with entrywise squaring."""
    A = square_matrix(A)
    return permanent([[1 + a*a for a in row] for row in A])


def interpolation_weights(n):
    """Top coefficient weights at the n+1 distinct nodes x_r=r**2."""
    if not isinstance(n, int) or n < 1:
        raise ValueError("n must be positive")
    nodes = [r*r for r in range(n+1)]
    return tuple(Fraction(1, prod(nodes[r]-nodes[s]
                                 for s in range(n+1) if s != r))
                 for r in range(n+1))


def closed_form_weights(n):
    return (Fraction((-1)**n, factorial(n)**2),) + tuple(
        Fraction(2*(-1)**(n-r), factorial(n-r)*factorial(n+r))
        for r in range(1, n+1))


def recover_boolean(B, oracle=None):
    """Recover per(B) from n+1 calls to a P_A(1) evaluator.

    oracle(A) must return the exact P_A(1). The default oracle is factorial;
    this finite check verifies the reduction, not the conjecture.
    """
    B = square_matrix(B)
    if any(v not in (0, 1) for row in B for v in row):
        raise ValueError("B must be Boolean")
    n = len(B)
    oracle = specialize_pa if oracle is None else oracle
    samples = [Fraction(oracle([[r*v for v in row] for row in B]))
               for r in range(n+1)]
    return sum((w*y for w, y in zip(interpolation_weights(n), samples)),
               Fraction(0))


def interpolation_symbolic_check(n):
    """SymPy check of the linear functional for arbitrary degree <=n f."""
    import sympy as sp
    a = sp.symbols(f"a0:{n+1}")
    nodes = [r*r for r in range(n+1)]
    weights = interpolation_weights(n)
    extracted = sp.expand(sum(sp.Rational(w.numerator, w.denominator)
                              * sum(a[j]*x**j for j in range(n+1))
                              for w, x in zip(weights, nodes)))
    return {"identity": str(extracted),
            "expected": str(a[n]),
            "exact": sp.expand(extracted-a[n]) == 0,
            "closed_form_exact": weights == closed_form_weights(n),
            "nodes": nodes,
            "weights": [str(w) for w in weights]}


def evaluate_modular(nodes, prime):
    """Evaluate a division-free rational +/* circuit modulo a good prime.

    Each node is ('const', numerator, denominator), ('add', i, j), or
    ('mul', i, j), with operation references pointing to earlier nodes.
    A bad prime dividing a leaf denominator is rejected. Intermediate
    rational values are never constructed.
    """
    values = []
    for tag, left, right in nodes:
        if tag == "const":
            if right % prime == 0:
                raise ValueError("Prime divides a rational leaf denominator")
            value = left*pow(right, -1, prime)
        elif tag in ("add", "mul"):
            if not (0 <= left < len(values) and 0 <= right < len(values)):
                raise ValueError("Invalid circuit reference")
            value = (values[left]+values[right] if tag == "add"
                     else values[left]*values[right])
        else:
            raise ValueError("Unsupported gate")
        values.append(value % prime)
    if not values:
        raise ValueError("Empty circuit")
    return values[-1]


def sieve_primes(limit):
    marks = bytearray(b"\x01")*(limit+1)
    if limit >= 0:
        marks[0] = 0
    if limit >= 1:
        marks[1] = 0
    for p in range(2, isqrt(limit)+1):
        if marks[p]:
            marks[p*p:limit+1:p] = b"\x00"*((limit-p*p)//p+1)
    return [p for p in range(2, limit+1) if marks[p]]


def reconstruct_integer(nodes, bound):
    """CRT reconstruction of an integer circuit output in [-bound,bound].

    The caller supplies the output bound; this routine does not estimate
    enormous intermediate integers. A polynomial-size sieve is used in
    the sum of leaf denominator bits and output-bound bits. This is a
    general evaluator, not a constructor for conjectured P_A circuits.
    """
    if bound < 0:
        raise ValueError("bound must be nonnegative")
    denominators = [abs(den) for tag, _, den in nodes if tag == "const"]
    if any(den == 0 for den in denominators):
        raise ValueError("Zero denominator")
    bad_prime_bound = sum(den.bit_length() for den in denominators)
    needed = (2*bound+1).bit_length()
    count = max(6, bad_prime_bound+needed)
    # p_count < count*(log(count)+log(log(count))) < 4*count**2
    # for count>=6 (Rosser--Schoenfeld); deliberately loose sieve range.
    primes = sieve_primes(4*count*count)
    residue, modulus, used = 0, 1, []
    for p in primes:
        if any(den % p == 0 for den in denominators):
            continue
        y = evaluate_modular(nodes, p)
        correction = ((y-residue)*pow(modulus, -1, p)) % p
        residue += modulus*correction
        modulus *= p
        used.append(p)
        if modulus > 2*bound:
            output = residue if residue <= modulus//2 else residue-modulus
            if abs(output) > bound:
                raise ValueError("Output does not satisfy supplied integer bound")
            return {"integer": output, "modulus": modulus, "primes": used}
    raise ArithmeticError("Sieve failed to provide enough good primes")


def integer_circuit(A):
    """Factorial-size permanent circuit for modular evaluator checks only."""
    A = square_matrix(A)
    nodes = []
    leaves = {}
    for i, row in enumerate(A):
        for j, value in enumerate(row):
            leaves[i, j] = len(nodes)
            nodes.append(("const", value.numerator, value.denominator))
    terms = []
    for sigma in permutations(range(len(A))):
        term = leaves[0, sigma[0]]
        for i in range(1, len(A)):
            nodes.append(("mul", term, leaves[i, sigma[i]]))
            term = len(nodes)-1
        terms.append(term)
    output = terms[0]
    for term in terms[1:]:
        nodes.append(("add", output, term))
        output = len(nodes)-1
    # Ensure even the 1x1 case has the desired leaf as final output.
    if output != len(nodes)-1:
        nodes.append(("const", 0, 1))
        nodes.append(("add", output, len(nodes)-1))
    return nodes
