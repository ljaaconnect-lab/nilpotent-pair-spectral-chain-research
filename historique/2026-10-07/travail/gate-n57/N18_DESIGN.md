# n18: Cauchy-Binet Gram factor and occupation encoding

Artifact version: n18-occupation-gram-v1. The independent 36-check development
evaluator and checklist were frozen before this variant was coded. The local
freeze record is `n18-freeze.json`; earlier n15 validation is not this node's
evidence. General claims here are UNVERIFIED unless separately kernel checked.

## Explicit cheap Gram factors

Retain b_ij=(1+a_ij^2) z^(2^(i*n+j)), with arbitrary rational A. Index n^2
edges by e=(i,j) in row-major order. Define the n by n^2 incidence matrix
X by X[k,(i,j)]=1 if k=j and 0 otherwise. Let W be diagonal with
W[(i,j),(i,j)]=b_ij y_i. These matrices need no unknown coefficient or target
polynomial as data. Their sparse descriptions have n^2 incidence entries and
n^2 edge weights, with polynomial description length.

Their product is explicitly diagonal:

    X W X^T = diag_j(sum_i b_ij y_i).

Its determinant is the product of its n diagonal entries. The actual scalar
circuit compiles that product with n-1 multiplications; it calls no determinant
black box and gives no free scalar credit for matrix multiplication.

## Local sign neutralization through Cauchy-Binet

The informal Cauchy-Binet expansion is

    det(X W X^T) = sum_(E, |E|=n) det(X_E)^2 product_((i,j) in E) b_ij y_i.

If E misses a column label, X_E has a zero row; if it repeats one, it has
duplicate columns. Otherwise it selects one edge for every column label, and
X_E is a permutation matrix, whose determinant square is one. Thus both minor
orientations cancel locally, leaving exactly the n^n column assignments with
positive amplitudes. The evaluator checks the supported minor-square sum and
computes the incidence determinants explicitly, caching repeated incidence
patterns. Omitted zero-minor classification remains a stated formal lemma;
the implementation does not silently assert kernel verification.

Taking coefficient y_0 ... y_(n-1) then selects exactly those assignments that
also use every row once. Hence the coefficient is the unsigned marked
permanent P_A. This supplies a positive alternative to the determinant-pair
encoding in source Proposition 14.2. It encodes the same desired coefficient;
it is a different full polynomial from H_A and does not compute H_A's complete
coefficient list.

## Univariate occupation encoding and scalar count

Set q=n+1, y_i=s^(q^i), and T=sum_i q^i=((n+1)^n-1)/n. Then

    F_A(s,z)=product_j(sum_i b_ij s^(q^i)),
    [s^T] F_A = P_A.

For a column assignment let m_i be row occupancy. Every m_i is at most n and
sum_i m_i=n. The auxiliary exponent is sum_i m_i q^i. All m_i are valid base-q
digits, so matching T's all-one digits forces m_i=1 for every i. This is an
explicit injective occupation code, with no carry ambiguity. The connection
to the original central coefficient is

    [t^K] H_A(t,z) = P_A(z) = [s^T] F_A(s,z).

The identity by itself gives no scalar coefficient-extraction algorithm.

The actual +/* graph has the following exact costs. The original z markers
and marked entries cost 2n^2-1 gates. Starting with u_0=s, build
u_(i+1)=u_i^q by binary powering. If

    g(q)=floor(log2 q)+popcount(q)-1,

those n-1 markers cost (n-1)g(q) gates. The n^2 products b_ij u_i cost n^2;
the n column sums cost n(n-1); the diagonal product costs n-1. Total:

    G_F(n)=4n^2-2+(n-1)g(n+1)=O(n^2+n log n).

This is a circuit bound for the full encoding polynomial. There is no free
division, determinant or contraction. Its constants are the prescribed p_ij;
only z and the new auxiliary are variable leaves. The implementation uses the
existing evaluator's name t for the auxiliary axis; it is mathematically s
in this design. The encoded exponent and target T have O(n log n) bit length
and are generated without unary-sized exponentiation chains.

Predicted values, derived before validation, are:

- n=2: q=3, T=4, degree 6, G_F=16 gates.
- n=3: q=4, T=21, degree 48, G_F=38 gates.
- n=4: q=5, T=156, degree 500, G_F=71 gates.
- n=5: q=6, T=1555, degree 6480, G_F=110 gates.

## Exact constructive obligations for Hilbert

The finite checks do not replace these general kernel obligations:

1. Prove X W X^T has the stated diagonal entries over a commutative ring.
2. Apply Cauchy-Binet with diagonal W and prove the incidence-minor square
   classification, including zero minors from missing/repeated column labels.
3. Expand the diagonal product and show the squarefree occupation coefficient
   is the permutation sum, preserving every original marked z exponent.
4. For m:Fin n -> Nat, with m_i<=n, prove
   sum_i m_i(n+1)^i=sum_i(n+1)^i implies every m_i=1. The degree-budget
   condition sum_i m_i=n follows from this product construction. The existing
   recursive digit-injectivity theorem can help once its indexed-sum form is
   proved.

The remaining polynomial obligation is separate: construct a uniformly
polynomial scalar circuit that contracts the squarefree occupation coefficient,
or equivalently this univariate target channel, from the cheap factors above.
The diagonal determinant and local minor-sign cancellation do not discharge
that obligation. This node supplies an exact successful partial factorization
and improved small circuit for the encoding, not a root-conjecture proof.
