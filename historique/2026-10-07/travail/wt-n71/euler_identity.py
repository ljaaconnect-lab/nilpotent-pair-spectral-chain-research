"""Exact SymPy validation of Euler phases; not a scalar compiler."""
from itertools import permutations
from math import prod
import sympy as sp


def inversion_sign(sigma):
    return (-1)**sum(sigma[i] > sigma[l] for i in range(len(sigma)) for l in range(i+1, len(sigma)))


def edge_pairs(n):
    return [(i*n+j, l*n+m) for i in range(n) for l in range(i+1, n)
            for j in range(n) for m in range(j)]


def row_pairs(n):
    return [(i,l) for i in range(n) for l in range(i+1,n)]


def permutation_polys(n):
    x = sp.symbols(f'x0:{n*n}')
    signed, unsigned = 0, 0
    for sigma in permutations(range(n)):
        term = prod(x[i*n+sigma[i]] for i in range(n))
        signed += inversion_sign(sigma)*term
        unsigned += term
    return x, sp.Poly(signed, *x), sp.Poly(unsigned, *x)


def check_identities(n):
    x, determinant, permanent = permutation_polys(n)
    current = determinant
    for e, f in edge_pairs(n):
        # Exact algebra only. Differentiation is not credited as circuit gates.
        projected = current.diff(x[e]).diff(x[f])*sp.Poly(x[e]*x[f], *x)
        current = current - 2*projected
    grouped = determinant
    for i,l in row_pairs(n):
        projected = sp.Poly(0, *x)
        for j in range(n):
            for m in range(j):
                e, f = i*n+j, l*n+m
                projected += grouped.diff(x[e]).diff(x[f])*sp.Poly(x[e]*x[f], *x)
        grouped -= 2*projected
    return {"n": n, "inversion_pairs": len(edge_pairs(n)),
            "row_pairs": len(row_pairs(n)),
            "euler_diagonal_identity": current == permanent,
            "grouped_row_identity": grouped == permanent == current,
            "permutation_terms": len(permanent.terms()),
            "scope": "SymPy exact identity only; no differentiation counted as a scalar gate"}
