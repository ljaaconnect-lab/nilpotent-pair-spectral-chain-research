# n5 — Principal-minor coordinates for permanent flags

Status: the proposed common n-by-n matrix does not exist in general,
already on allowed inputs at n=4. This has an exact algebraic certificate.
There are useful positive representations for individual layers 2 and 3,
but no polynomial fusion/readout for all layers was obtained.

Let

    f_S(B) = per(B_[|S|],S),   f_empty = 1.

Here rows [|S|] mean the initial |S| rows, and S is a column subset.
The experiments are entirely symbolic and concern original row factors.
They do not assume that high-order f_S are free inputs to a compiler.

## 1. The dimension coincidence is genuine

The flag image has dimension n(n-1)+1. Its upper bound follows because
the first n-1 input rows have n(n-1) entries, and the last row enters
only the single coordinate f_[n]. At B=J, the Jacobian block of the
coordinates |S|=i with respect to row i is

    (i-1)! * (1_{j in S})_(S,j).

For 1<=i<n, this incidence matrix has rank n. One explicit independent
selection consists of S0={1,...,i}, the n-i sets S0\{i} union {j}, j>i,
and the i-1 sets S0\{j} union {i+1}, j<i. Differences span the subspace
of coordinate sum zero, while S0 has nonzero coordinate sum i. Choose
these n outputs at each layer, and the one output at the final layer.
Their Jacobian in the first n-1 rows plus one last-row variable is block
triangular, with invertible diagonal blocks. Thus its rank reaches the
upper bound at J.

The general principal-minor image also has dimension n^2-n+1. The
diagonal-conjugation gauge accounts for n-1 parameters. Conversely,
after normalizing m_1j=1, the diagonals, all opposite-edge products, and
all triples containing 1 generically recover every remaining edge from
a quadratic equation. Their count is

    n + binom(n,2) + binom(n-1,2) = n^2-n+1,

and the reconstruction is generically finite. Equal dimension, however,
does not imply inclusion. The following allowed-input examples disprove it.

## 2. Exhaustive certificate at B=J4

If all f_S are principal minors of M, its diagonal entries are 1 and

    m_ij m_ji = f_i f_j - f_ij = -1.

Hence no off-diagonal entry vanishes and diagonal conjugation always
normalizes m_1j=1, m_j1=-1. Put x=m_23, y=m_24, z=m_34. Each triple
containing 1 must have determinant 6, which gives

    -x+1/x=2,   x^2+2x-1=0,

and the same equation for y,z. There are exactly eight choices in C,
using roots -1+sqrt(2), -1-sqrt(2). The reverse edges are respectively
-x-2, -y-2, -z-2, so the complete normalized matrix is

    [[ 1,  1,     1,     1],
     [-1,  1,     x,     y],
     [-1, -x-2,   1,     z],
     [-1, -y-2,  -z-2,   1]].

For all eight branches its determinant is 20. Six branches give the
remaining triple determinant 6, and two give -10. Therefore none gives
the required f_[4]=24. This is an impossibility over C, not merely over Q.
The gauge exhausts all possible matrices. At n>4, restricting any proposed
matrix for J_n to four indices yields the same contradiction.

This input is within the contract: a_ij=0, p_ij=1, z=1.

## 3. Even a common representation of the proper layers can fail

One possible repair was to represent all proper f_S by a common M, then
read the final row using its principal cofactors. That repair also fails
at n=4, without involving the unknown full permanent.

Take the first two input rows to be (1,1,1,1), and the third row to be
(2,1,1,1). All entries are again allowed p=1+a^2 at z=1. Then

    f_i=1, f_ij=2,
    f_123=f_124=f_134=8,   f_234=6.

The same exhaustive gauge gives x^2+4x-1=0 for each of x,y,z, with
roots -2+sqrt(5), -2-sqrt(5). The eight possibilities give triple 234
equal to 8 in six cases and -72 in two cases. None gives 6. No fourth
input row or full-permanent value is needed for this obstruction.

Both branch lists, with exact radicals simplified symbolically, are in
`principal_minors_results.json`; `principal_minors_experiments.py`
reproduces them and checks every branch.

## 4. Constant auxiliary blocks and rank-one variables do not repair it

Suppose the full generating polynomial were represented as

    F_B(x) = det(H + U diag(x) V),

where H is an arbitrary-size invertible constant block and each x_j
enters through one rank-one update. Since F_B(0)=f_empty=1, det H=1.
The determinant lemma gives

    F_B(x)=det(I_n + diag(x) V H^(-1) U).

Its coefficients are therefore principal minors of the single n-by-n
matrix V H^(-1) U. The two certificates above still apply regardless
of the number of constant auxiliary indices. A common mandatory
invertible principal block reduces in the same way by Schur complement.

This argument does not exclude variables of rank at least two with
cancellations, sums of determinants, singular cores with a separate
readout, or a different matrix for each degree layer.

The primary source [Lin and Sturmfels, Polynomial relations among
principal minors of a 4x4-matrix](https://arxiv.org/abs/0812.0601)
also proves that the general principal-minor image is closed. Thus
allowing a rational matrix with poles cannot evade the counterexample
by claiming only a generic parametrization whose coefficient limits
approach the forbidden point. The proof above itself uses exhaustive
quadratic reconstruction, not a black-box membership algorithm.
[Lin's earlier exposition](https://shaoweilin.github.io/public/pminors.pdf)
describes the diagonal gauge and cycle-product reconstruction.

## 5. A different matrix for each layer: genuine positive formulas

The common-matrix counterexamples do not reject M_i depending on i.
For two input rows a,b, define the n-by-n matrix

    M2 = diag(a) + 1 (b-a/2)^T.

Every principal pair minor is

    det(M2[{j,k}]) = a_j b_k + a_k b_j.

Its entries use O(n) shared scalar operations after the input leaves;
it has unrestricted matrix rank and is division-free. This representation
is verified symbolically in the experiment.

For three rows a,b,c, temporarily assume the a_j are invertible and put
r_j=b_j/a_j, s_j=c_j/a_j. Define row vectors

    U_j=(1,r_j),   V_j=(-1/2,2s_j),
    M3=diag(a)(I+U V^T).

For a subset S of size k, the 2x2 determinant lemma gives

    det(M3[S])/product_(j in S) a_j
      = det([[1-k/2, -(sum r)/2],
             [2 sum s, 1+2 sum rs]])
      = 1-k/2 + (2-k)sum rs + (sum r)(sum s).

At k=3, therefore,

    f_(3,S) = det(M3[S]) + (1/2)det(diag(a)[S]).          (1)

This is a two-determinant representation for the complete third layer.
It uses only the original three rows. It does not use any third-layer
permanent to initialize an entry. The experiment checks the identity
symbolically with nine independent input variables.

The entries of M3 are

    (M3)_jk = a_j delta_jk - a_j/2 + 2 b_j c_k/a_k.

These rational entries are not asserted to be legal final scalar gates.
For each fixed-layer identity, use independent matrix-entry variables
first, deform a_j=1+t(a_j-1) (and the other entries along an affine path),
and replace each inverse by its geometric expansion through total degree
3. Since the final identity is a polynomial of degree 3 in independent
input entries, summing its t-coefficients recovers the exact result.
All operations are additions and multiplications with polynomial overhead.
At a hypothetical layer i, degree-i truncation costs O(i^2) per arithmetic
gate with schoolbook series multiplication. Marked z powers are substituted
only afterward, so their exponential degree causes no additional truncation.
This removes divisions from the fixed identities, but does not provide
the missing polynomial family of layer representations.

## 6. The rank-i product-of-Plucker variant fails already at layer two

If M2 had a rank-two factorization U V with U n-by-2 and V 2-by-n, then
its principal pair minors would be

    f_jk=det(U_{j,k}) det(V_{j,k}).

The two skew-symmetric arrays P_jk=det(U_{j,k}) and Q_jk=det(V_{j,k})
each have rank at most 2. Their Hadamard product F has rank at most 4:
expanding each skew rank-two form gives four rank-one outer products.
But for the allowed input a=b=1, the symmetric array with zero diagonal
and entries f_jk is 2(J-I), which has rank n in characteristic zero.
Thus this rank-i/Plucker-product repair is impossible at i=2 for n>=5.
This is consistent with M2 above, whose full rank is essential.

## 7. Honest continuation and its current cost

For any fixed matrix M and next row d,

    [t] det(M[S]+t diag(d_S))
       = sum_(j in S) d_j det(M[S\{j}]).                (2)

Thus a sum of determinant representations for layer i can be fused
correctly to layer i+1 by an explicit first jet. It cannot be counted as
a free derivative. A degree i+1 polynomial can be differentiated at zero
using its values at 0,...,i+1, with rational weights

    lambda_0=-H_(i+1),
    lambda_k=(-1)^(k+1) binom(i+1,k)/k, 1<=k<=i+1.

Their bit lengths are polynomial. This yields at most i+2 new determinant
components per old component. Starting from the two components at layer3,
the literal construction has at most (i+1)!/12 components at layer i>=3.
It is an exact but nonpolynomial fusion bound, not a claimed lower bound.

The special diag-plus-rank-two structure in (1) gives a shorter description
of the fourth-layer jet. Normalize the four rows by a and call the three
remaining ratios r,s,q. With R=sum r, S=sum s, Q=sum q and
M_T=sum_j product_(v in T) v_j, the answer divided by product a is

    R S Q - Q M_rs - R M_sq - S M_rq + 2 M_rsq.           (3)

The experiment verifies (3) against the sum over distinct column choices.
It uses all seven nonempty moments of three ratios. Continuing this
particular moment closure gives 2^(i-1)-1 possible moments at layer i;
the general combination is the inclusion-exclusion sum over partitions
of the remaining row indices. This is the cumulant/Bell closure already
encountered in collision filtering, not a new polynomial compression.
No continued enumeration of this equivalent state was performed.

## Outcome

The equal-dimension common principal-minor hypothesis is false, even with
arbitrary nonlinear dependence of the proposed entries on the original
factors. Exact allowed-input certificates also reject the proper-layer
common-matrix repair and the rank-i Plucker-product repair. Distinct
full-rank matrices or sums of matrices for separate layers remain possible;
layers 2 and 3 have the explicit constructions above. Their demonstrated
fusion has exponential/factorial descriptions, and no polynomial scalar
compiler for all layers has been constructed.

No new `candidate.py` is supplied for n5. The candidate inherited on this
branch is the earlier n2 exponential jet witness, not a principal-minor
compiler. Consequently n5 has no new development score.
