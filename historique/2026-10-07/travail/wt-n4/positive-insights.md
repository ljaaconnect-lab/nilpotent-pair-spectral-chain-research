# Arbor n4: positive transfer constructions

All general proof arguments below are informal and **UNVERIFIED by Lean** in
this node. Exact formal-z development computations succeeded; this is neither
a formal proof nor a solution to Conjecture 1.5. This node performs positive
construction tests and does not generate counterexamples.

## Fixed hypothesis and frozen boundary

The n4 hypothesis is constructive: subset transfer matrices with a terminal
self-loop realize the target marked permanent as `(M^K)[empty,full]` whenever
K>=n, and row/tensor structure may permit useful simplification. The committed
`candidate.py` and `evaluate.py` are unchanged. New files are `recurrence.py`,
`evaluate_recurrence.py`, `dev-recurrence.json`, this report, and the evaluator
freeze record. Only the coordinator accesses held-out cases.

The positive-dev evaluator was written and its SHA-256 frozen before execution:
`bff57a9e99156a5795ecda3ef346ae9103e127d35055db2a08a02d4edfa90456`.
It compares four constructions with an independent permutation-expansion oracle
on identity/cyclic/Vandermonde A for n=2,3,4,5. The metric is exact formal-z
identity pass fraction: **48/48=1.0**. Neither sampling z nor estimating proof
confidence contributes to this score. Sparse polynomials store each integer
z exponent and exact Fraction coefficient. No full Hhat expansion is performed
for n=5. Additional exponent-n stabilization checks on the four identity cases
are recorded as diagnostics outside the frozen score.

## Explicit transfer-matrix construction

Write `b_ij=(1+a_ij^2) z^(2^(i*n+j))` with zero-based indices. States are subsets
S of the n columns, encoded by bit masks. In row-oriented matrix notation set

`M[S,S union {j}]=b_(|S|),j` for j outside S, and `M[full,full]=1`.

Every other entry is zero. The dimension is `r=2^n` and the number of nonzero
entries is `n*2^(n-1)+1`. A path from empty to full makes exactly n raising
transitions, selects each column once, and uses row i at its ith transition.
Thus its non-loop weight is one permutation product, including its full marked
z address. For any K>=n it then takes exactly K-n terminal loops of weight one.
Conversely each permutation yields exactly one such path. Therefore

`(M^K)[empty,full]=P_A(z)` for every K>=n.

This includes K=n^n-1 for the tested n and all n>=2. It constructs a recurrence
representation valid at the required target index, while using exponential
dimension. Its initial matrix entries are explicitly and cheaply describable.

`build_matrix_power` constructs an actual scalar +/* DAG for sparse matrix
binary powering. Structural zeros are omitted; every surviving scalar multiply
and add is counted, including multiplication by one. Rational p_ij are allowed
leaves, and all z markers are constructed by squaring. The source amplitudes
are preserved exactly.

## Measured dimensions and gate counts

The counts are the same across the three tested A families because all p_ij
are positive and the constructor uses structural support.

- n=2: K=3, dimension 4, M^K DAG 17 gates, exponent-n DAG 13 gates,
  row-chain/subset-DP DAG 12 gates, peak active row states 2.
- n=3: K=26, dimension 8, M^K DAG 83 gates, exponent-n DAG 51 gates,
  row-chain/subset-DP DAG 34 gates, peak active row states 3.
- n=4: K=255, dimension 16, M^K DAG 357 gates, exponent-n DAG 150 gates,
  row-chain/subset-DP DAG 80 gates, peak active row states 6.
- n=5: K=3124, dimension 32, M^K DAG 975 gates, exponent-n DAG 511 gates,
  row-chain/subset-DP DAG 178 gates, peak active row states 10.

Each formal-z output contains respectively 2,6,24,120 distinct marked
permutation terms. These term counts describe expanded output representations;
they are not arithmetic-circuit lower bounds.

For exponent K>=1 let

`J(K)=floor(log_2 K)+popcount(K)-1 <= 2 floor(log_2 K)`.

Binary powering uses J(K) matrix products. A dense r-by-r product using ordinary
scalar multiplication requires `r^3` multiplication and `r^2*(r-1)` addition
gates, totaling `2r^3-r^2`. Marker/entry construction uses `s0=2n^2-1` gates.
Because the desired output is a fixed matrix entry, no additional contraction
gates are needed here. Thus a valid generic bound is

`s0 + J(K)*(2r^3-r^2) <= s0+2 floor(log_2 K)*(2r^3-r^2)`.

The first bound at n=2,3,4,5 is respectively 231,5777,111135,967729 gates;
the second is 231,7697,111135,1419313. Our sparse counts above are much smaller
than these dense upper bounds, but retain exponential state dependence.
For arbitrary circuit-specified u,v rather than coordinate vectors, add the
appropriate u,v construction and at most `2r^2` final contraction gates, as
in source Remark 14.11(ii).

## Row-chain simplification and exact circuit formula

The chronological row-chain construction propagates only cardinality-i subsets
after i rows. For every source S it sends its current scalar polynomial along
each missing-column edge weighted b_ij. This equals multiplication by the row
operator T_i followed by retaining the reachable cardinality i+1 layer.
The committed subset DP builds the same polynomials in predecessor order.

There are `n*2^(n-1)` transitions. Across all destinations there are
`n*2^(n-1)-(2^n-1)` addition gates. Including marker/entry construction gives

`G_DP(n)=2n^2-1 + n*2^n-(2^n-1)=2n^2+(n-1)*2^n`.

This is an exact gate count for these actual DAGs, not merely a big-O bound.
Restricting to one reachable layer changes peak vector storage to
`binomial(n,floor(n/2))` active scalar coordinates. It preserves every marked
z exponent and gives the finite peaks above. Neither this layer restriction
nor the gate formula establishes polynomial asymptotic scalar complexity.

## Lawful terminal stabilization

Order nonterminal subsets by cardinality and place the full subset last. Then

`M = [[N,b],[0,1]]`.

N raises nonterminal cardinality strictly at every transition, hence `N^n=0`.
For k>=1 an induction on k gives the exact block formula

`M^k = [[N^k, sum_(i=0)^(k-1) N^i b],[0,1]]`.

When k>=n all terms with i>=n vanish, so

`M^k=M^n` and `M^n(M-I)=0`.

This is a constructive reduction of the huge exponent K to n, valid for the
whole matrix, with initialization supplied explicitly by N and b. It explains
the additional positive stabilization diagnostics. It also yields the scalar
sequence, for u=empty and v=full,

`a_k=u^T M^k v = 0` for k<n, and `a_k=P_A(z)` for k>=n,

and consequently `a_(k+n+1)=a_(k+n)` for k>=0. This low-order recurrence is
valid, but its initialization includes `a_n=P_A(z)`. Building a small companion
matrix from those scalar initial values would assume the desired extraction.
It must not be counted as a cheaply constructible polynomial-dimensional
solution. The explicit subset-space M avoids that circular initialization but
still has dimension 2^n.

These generic block-operator facts give clean Hilbert sublemmas: prove the power
formula by induction, show that a cardinality-raising operator is nilpotent,
and deduce stabilization and the annihilating polynomial. Verifying those facts
would validate this construction without by itself resolving the root bound.

## Product/tensor factorization preserves the marked output

Let `R=[[0,1],[0,0]]` in row-oriented convention, and let R_j act by R on the
jth two-dimensional occupancy factor and by identity on the other factors.
Then `R_j^2=0` and the R_j commute. The row operator has a compact expression

`T_i=sum_j b_ij R_j`, and `P_A=(T_0 ... T_(n-1))[empty,full]`.

Equivalently, multiply the n linear row forms `sum_j b_ij x_j` in the commutative
algebra `Q[z][x_0,...,x_(n-1)]/(x_j^2)` and take the coefficient of the top
occupancy monomial. Repeated columns vanish locally; each valid product retains
its correct amplitude and marked z address. `tensor_product_polynomial`
checks this product without numerical z specialization and matches every
development oracle exactly.

The compact expression shares n elementary raising operators across n row
forms and has n^2 weighted terms. It is a useful structured description of
the operators. Its ambient tensor dimension is still `2^n`; a tensor/operator
algebra multiplication is not one scalar arithmetic gate. Scalar compilation
through the reachable subset coordinates has the explicit DP cost above.

There is also a compact cardinality-projector description of M. With local
occupation operators `Q_j=diag(0,1)` on factor j, set `D=sum_j Q_j` and
`Pi_i=product_(ell!=i)(D-ell I)/(i-ell)` for i=0,...,n. Lagrange evaluation on
the integer eigenvalues 0,...,n makes Pi_i the cardinality-i projector. Then,
in row-oriented convention,

`M=sum_(i=0)^(n-1) Pi_i T_i + Pi_n`.

The literals here have polynomial bit length and the expression has polynomial
operator-algebra description size. This is a positive structural factorization;
the displayed projector identity is informal and was not scored in the frozen
development evaluator. A scalar evaluation of its terminal entry still needs
an independently justified, cheap contraction/compression method.

Current result: terminal stabilization, reachable-layer restriction, and shared
local raising factors are lawful simplifications. **No polynomial scalar gate
bound for arbitrary n was obtained.** The implemented general construction
remains exponential; this is not a disproof. The next positive search should
seek a compression whose initial scalar data and final marked contraction are
both efficiently constructible, preserving all marked exponents.
