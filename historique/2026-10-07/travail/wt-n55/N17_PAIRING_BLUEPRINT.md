# N17: general coefficient pairing, kernel verified

The two independently compiled files prove a general finite-list pairing
identity. `GeneralPairing.lean` uses rational coefficients;
`GeneralPairingRing.lean` uses an arbitrary coefficient type R with
`Lean.Grind.CommRing R`. No determinant identity or circuit-complexity result
is assumed. The nine declarations in each file are separately audited.

For a finite list L of natural labels, arbitrary weight and sign functions,
define the sparse polynomial data

F = [(r, sign(r)*weight(r)) : r in L],
G = [(K-r, sign(r)) : r in L].

A sparse monomial is a pair (degree, coefficient). Its coefficient at degree k
is the sum of coefficients of all pairs with that degree. Sparse multiplication
explicitly lists every pair of monomials, adds their natural degrees, and
multiplies their coefficients. It does not assume a coefficient extractor.

The accepted theorem `central_product_coefficient` states, for every K and L:

If L has no duplicates, every r in L satisfies r<=K, and each sign(r) is 1 or
-1, then the coefficient at degree K of the actual sparse product F*G equals
the sum of weight(r) over r in L.

The assumptions are preserved in the generic-ring theorem. The label bound
is essential because K-r uses natural-number subtraction. Duplicate labels
would introduce off-diagonal products, so the no-duplicate condition is not
optional. The weight function is arbitrary; it can take values in a
polynomial coefficient ring once that ring's `Lean.Grind.CommRing` instance
is supplied. That application requires a separate checked specialization.

The dependency order is acyclic:

1. `sign_square`: a sign in {1,-1} has square 1.
2. `selectSum_nodup`: filtering a duplicate-free label list picks one value.
3. `central_label_iff`: r+(K-s)=K iff r=s, assuming s<=K.
4. `central_row_select`: the central-degree condition equals label filtering.
5. `central_row`: the diagonal signed contribution equals its unsigned weight.
6. `central_pairing`: summing the rows proves the explicit double convolution.
7. `coefficient_append`: coefficient sums respect sparse concatenation.
8. `coefficient_multiply`: the explicit convolution is the actual coefficient
   of sparse multiplication.
9. `central_product_coefficient`: combines 6 and 8.

The generic file has two local additive-law instances derived directly from
the existing ring fields. They introduce no additional hypotheses or axioms.
Its `coefficient_append` and `coefficient_multiply` depend only on propext;
the remaining declarations use only the disclosed standard Lean trust base
propext, Classical.choice, Quot.sound. No final declaration uses sorryAx.

All eighteen actual compiler rounds are saved individually. Rat's final
acceptance is round 15; the generic-ring final acceptance is round 18. Earlier
unsolved goals, the deprecated if_pos spelling, and the generic instance
binding errors are preserved in the logs and corrected in the final files.
The strict audit matches current source byte hashes to these compiler logs,
requires exit 0, rejects placeholders, and audits all eighteen declarations.
It does not rerun a compiler or reinterpret failed rounds as proof evidence.

This advances Step B: general diagonal pairing is now formally established
for explicit sparse polynomial data. To apply it to the paper's H_A, the next
formal work must identify the determinant's Leibniz expansion and the reverse
Vandermonde factor with F and G, then specialize the base-n labels and the
permutation signs. The earlier recursive digit-list injectivity is useful,
but the indexed power-sum representation still needs a checked connection.

Step C remains the original constructive obligation: compile the desired
central coefficient into a polynomial-size scalar +/* circuit over Q with
the specified short literals and polynomial-time uniform constructor. This
proof evaluates an explicitly expanded sparse product; it does not bound
that expansion by a polynomial or give coefficient extraction a free gate.
Conjecture 1.5 has not been claimed proved or disproved.
