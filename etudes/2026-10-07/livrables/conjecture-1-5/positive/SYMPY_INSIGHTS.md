# Arbor leaf n5: positive symbolic tensor and transfer verification

Artifact version: n5-sympy-positive-v1. This is the final planned positive
construction cycle. It introduces no counterexample search and claims no
original-target theorem. General statements below remain **UNVERIFIED by Lean
in this leaf**. Exact symbolic verification covers only n=2,3,4,5.

## Frozen protocol and result

The checklist and script were written before the first execution. Their hashes
and the pre-execution timestamp are in `sympy-freeze.json`. The checklist hash
is `e10a48b1cd35353f63ac7197a94638f6ba13f3c52b578ed40681853c5a36f2a4`.
The script hash is
`f632b00c0efc021042178f33eeb8d39c5d460f41dd1521a181ef1c5b5d7ee933`.

The command `python sympy_invariants.py --output sympy-report.json` exited 0
using Python 3.12 and SymPy 1.14.0. Frozen boundary
B_dev-positive-symbolic score: **112/112 = 1.0**. Each declared assertion has
equal weight; failures or infrastructure errors would count as failed checks.
The score reports finite exact assertion success, not formal proof confidence.
Existing frozen evaluators and recurrence implementations were not edited.

The fixed families comprise 14 square-zero identities, 20 pairwise commutation
identities, 14 tensor/subset operator comparisons, four tensor-product terminal
permanent identities, four transfer-terminal permanent identities, four
whole-matrix stabilization identities, four nonterminal nilpotence identities,
14 scalar early-zero checks, four scalar initialization identities, 18 scalar
tail-recurrence checks, and 12 marked scalar-cost checks. All individual results
are recorded in `sympy-report.json`. No held-out test boundary was accessed.

## Verified finite symbolic construction

Use row-oriented subset basis vectors e_S, where the matrix row is the source
subset and the column is the destination. For absent j, R_j sends e_S to
e_(S union {j}); for present j it sends e_S to zero. Actual SymPy sparse matrices
of dimensions 4,8,16,32 verify R_j^2=0 and R_i R_j=R_j R_i. Explicit Kronecker
products agree with these subset matrices: the local occupancy factor is
[[0,1],[0,0]], and the factor order runs from the highest mask bit to the lowest.

Let x_ij be independent commuting symbolic row weights and
T_i=sum_j x_ij R_j. Structured sparse SymPy multiplication and exact polynomial
expansion verify

    (T_0 ... T_(n-1))[empty,full] = sum_sigma product_i x_(i,sigma(i)).

The right-hand side is constructed independently by permutation enumeration.
The resulting polynomials contain 2,6,24,120 terms for n=2,3,4,5. The identity
uses generic indeterminates, so the informal polynomial-substitution argument
specializes x_ij to the original
b_ij=(1+a_ij^2) z^(2^(i*n+j)) without numerical z evaluation or altered marking.
That general substitution argument is not a Lean theorem in this leaf.

The transfer matrix M has weighted edges from S to S union {j}, with row
weight x_(|S|),j, plus a terminal self-loop of weight 1. Exact full symbolic
matrix comparisons verify M^(n+1)=M^n. Removing the terminal row and column
gives N, whose n-th power is exactly zero in each tested dimension. No numeric
sampling or matrix-spectrum heuristic contributes to these identities.

## Exact positive scalar recurrence and its initialization

For a_k=(M^k)[empty,full], the tested early values are zero for 0<=k<n and
a_n is the generic permanent. The whole-matrix stabilization identity supplies
the following informal all-k deduction for each tested fixed dimension:
right-multiply M^(n+1)=M^n by M^k and use associativity. Thus

    a_k = 0 for k<n;
    a_k = P_A(z) for k>=n after the original marked substitution;
    a_(k+n+1) = a_(k+n) for k>=0.

The script also checks the displayed tail recurrence directly at k=0,...,n
using explicitly multiplied symbolic matrices through exponent 2n+1.

The recurrence's initialization includes a_n=P_A(z), the target polynomial.
Its value remains unknown to a recurrence-only extraction procedure until the
marked permanent is computed. Supplying a_n as a cheap scalar initial value
would assume the required solution. The explicit subset matrix avoids that
circular initialization but has dimension 2^n. Neither its stabilization nor
the order n+1 scalar recurrence establishes a polynomial scalar extractor.

## Actual marked scalar costs

Cost records use the existing `recurrence.py` builders and count their actual
scalar addition/multiplication nodes. SymPy matrix arithmetic and tensor
operators are verification machinery and are not assigned free scalar gates.
All marked DAGs preserve p_ij=1+a_ij^2 and the original z squaring chain.
Marker and entry preparation uses 2n^2-1 gates, with prescribed p_ij constants
as allowed leaves.

- n=2: dimension 4, K=3; row chain 12 gates, M^n 13 gates, M^K 17 gates.
- n=3: dimension 8, K=26; row chain 34 gates, M^n 51 gates, M^K 83 gates.
- n=4: dimension 16, K=255; row chain 80 gates, M^n 150 gates, M^K 357 gates.
- n=5: dimension 32, K=3124; row chain 178 gates, M^n 511 gates, M^K 975 gates.

The row-chain formula is exactly 2n^2+(n-1)2^n for these builders, not a
polynomial bound. The report records every sparse matrix-product gate count,
the actual powering schedule and dense upper bounds. It does not re-evaluate
marked polynomials or sample z; that positive exact formal-z evaluation belongs
to the unchanged n4 boundary.

Measured symbolic times at n=5 were 0.094 seconds for raising/tensor-factor
identities, 0.170 seconds for the row-operator product and 0.248 seconds for
transfer powers, nilpotence and scalar recurrence checks. Total n5 elapsed time
including costs was approximately 0.593 seconds. These are observations on
this host, not asymptotic performance guarantees.

## Distilled insight and path constraint

Commuting square-zero local factors correctly remove repeated columns and
retain positive permutation products. Terminal stabilization lawfully reduces
the large exponent K to n in the explicit transfer representation. These facts
give concrete Hilbert bridge obligations: the raising relations, finite-path
terminal coefficient identity and nilpotent block stabilization.

The resulting marked scalar computation still uses exponential subset space.
The missing ingredient is efficient construction of the initial terminal
coefficient, or an independently justified compression with cheap initial and
terminal scalar data. Do not count operator-description compactness, a small
recurrence order, or successful finite symbolic identities as resolving that
ingredient. This node does not establish or refute Conjecture 1.5.

Reproduce only this frozen positive development run with:

    python sympy_invariants.py --output sympy-report.json
