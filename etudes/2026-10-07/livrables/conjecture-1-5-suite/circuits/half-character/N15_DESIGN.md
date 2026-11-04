# n15: Gray-shared half-character contraction

Artifact version: n15-gray-half-character-v1. Hypothesis, initial data and gate
count below were specified before positive validation. This is a lawful
factorization alternative to the subset transfer, with dimension 2^(n-1).
The intended bound is O(n 2^n) scalar gates. A polynomial bound is not claimed.
General statements are UNVERIFIED until a separate Lean kernel check succeeds.

The polarization identity used here is associated with [Glynn's 2010 paper,
The permanent of a square matrix](https://doi.org/10.1016/j.ejc.2010.01.010).
The following gate accounting and proposed bridge obligations describe this
implementation. They are not a claim of a new permanent formula.

## Concrete initial data and factors

Retain the original entries b_ij=(1+a_ij^2) z^(2^(i*n+j)), with A an arbitrary
rational matrix and zero-based indices. Let Delta be the sign vectors
delta in {+1,-1}^n with delta_0=1, so r=|Delta|=2^(n-1). Define

    D_i[delta,delta] = sum_j delta_j b_ij,
    u[delta] = product_j delta_j / r,
    v[delta] = 1.

Every off-diagonal D_i entry is structurally zero. No target coefficient,
permanent, unspecified initial value or oracle is an input. All data comes
from the b_ij and constants +/-1 and 1/r. The candidate contraction is

    u D_0 D_1 ... D_(n-1) v
      = (1/r) sum_delta (product_j delta_j) product_i(sum_j delta_j b_ij).

This pairs sign vectors delta and -delta from the full character average:
the weight and degree-n row product both change by (-1)^n, so their product
is invariant. Choosing delta_0=1 is a genuine factor-of-two dimension
compression. It does not create polynomial dimension.

## Exact scalar gate derivation

Implement all gates explicitly as binary addition or multiplication, including
subtraction as multiplication by -1 then addition. Allowed p_ij=1+a_ij^2
constants are input leaves. Markers and marked entries use 2n^2-1 gates.

Enumerate Delta in reflected binary Gray order on columns 1,...,n-1. When one
sign flips, update each row sum by adding +2b_ij or -2b_ij. The highest Gray
bit flips exactly once from + to -, and every lower bit flips in both
directions. Precompute only the needed signed updates and share each one.

- Markers and entries: 2n^2-1 gates.
- Signed updates: n(n-2) for +2b and n(n-1) for -2b, totaling 2n^2-3n.
- Initial all-positive row sums: n(n-1) additions.
- Subsequent Gray row updates: n(r-1) additions.
- Product of the n row sums at each of r signs: (n-1)r multiplications.
- Two parity buckets: r-2 additions.
- Negate the negative bucket, add the buckets, normalize by 1/r: 3 gates.

Adding these quantities gives exactly

    G(n) = 5n(n-1) + n 2^n.

The additional scalar constants +/-2 have bounded length, and 1/r has O(n)
binary length. The integer loop bounds, Gray masks and addresses are generated
uniformly. The graph has G(n) gates and O(n^2) constant leaves; its binary
encoding has O(G(n) log G(n) + L + n^2) bits, where the input amplitude lengths
are bounded as in the original p_ij leaf convention. This construction gives
initial-data costs explicitly. It still has exponential construction size.

At n=2,3,4,5 the formula predicts 18,54,124,260 scalar gates. These are
predictions from the concrete counting formula, not a fitted polynomial curve.
The actual DAG is implemented in `half_character.py`.

## Exact Hilbert bridge obligation

Let n>=2, let s:Fin n -> Fin n, and let delta range over sign vectors with
delta_0=1. Work in Q. Prove

    sum_delta (product_j delta_j) (product_i delta_(s(i)))
      = if Function.Bijective s then 2^(n-1) else 0.

Informal blueprint: let m_j be the cardinality of the j-th fiber of s. The
summand equals product_j delta_j^(m_j+1). Independent summation over each
delta_j, j>=1, gives the product of 1+(-1)^(m_j+1). It vanishes unless each
m_j is odd. Since sum_j m_j=n, those n-1 positive odd counts must all be 1,
and m_0 must also be 1. Conversely a bijection has every count 1, making every
summand equal 1. Expand the n row sums and apply the identity assignment by
assignment to leave exactly the permutation products with coefficient one.

Required formal sublemmas are: regroup finite products by fibers; factor
finite sums over independent Boolean choices; parity evaluation of the two
sign powers; the fiber-count total; and the degree-budget inference that odd
fiber counts force bijectivity. None is silently assumed as kernel-verified.
The finite development projector checks verify this obligation at n=2..5.

## Remaining polynomial obligation

To resolve the requested root target, one would still need a uniformly
constructible polynomial-size scalar circuit for the displayed half-character
contraction, or a further representation whose factors, scalar u/v data and
terminal contraction all have polynomial construction costs. This obligation
is absent from the current exponential graph and is not implied by its small
local factor description. A low-dimensional model with P_A placed in u, v or
an initial state would not discharge it.

The new hypothesis does not rerun the previous subset-transfer baseline,
generate counterexamples, or replace arbitrary A by a structured family.
Positive SymPy validation uses fully independent x_ij for n=2..5. A second
check evaluates the actual marked DAG exactly in Q[z] at explicitly specified
rational A while leaving z formal; that finite input check supplements the
generic symbolic identities rather than replacing them.
