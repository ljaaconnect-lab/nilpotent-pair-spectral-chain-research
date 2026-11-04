# n70 candidate 2: explicit moving frames, exact new response required

This is a refinement of candidate 2 in n70-candidates.json, not a fourth
candidate. Every claim below is informal and unverified by Lean. No
experiment or root theorem is claimed. The coefficients of B and every
future factor remain symbolic and present.

## Exact moving-frame construction

For the row residuals in N70_BLUEPRINT.md write

    D_r = diag(d_r) + p_r q_r^T,
    d_r = h_r w_r,  p_r = -(w_r elementwise b_r),  q_r=a_r.

Each w_r is the complete row of diagonal weights. Suppose its entries
are invertible in a chart and put H_i=diag(w_i). The normalized data in
frame i are

    A_(i,r) = H_i^(-1) D_r
            = diag(d_(i,r)) + p_(i,r) q_r^T,
    d_(i,r) = w_i^(-1) elementwise d_r,
    p_(i,r) = w_i^(-1) elementwise p_r.

Define the actual transport matrix and its diagonal vector

    T_i=H_(i+1)^(-1) H_i=diag(tau_i),
    tau_(i,j)=w_(i,j)/w_(i+1,j).

Then the scalar data updates for EVERY residual r are exactly

    d_(i+1,r)=tau_i elementwise d_(i,r),
    p_(i+1,r)=tau_i elementwise p_(i,r),
    q_r unchanged.                                         (FT)

Given tau_i, transporting n residuals uses 2n^2 multiplications. This
closes their matrix-data class, including every future residual. It is
not a closed evaluator for the contraction. No unknown evaluated scalar
is placed in those data.

The basis operation is a left change between the source and target
column spaces of the bilinear matrices. It is not an uncharged similarity
claim. In a bilinear expression v^T A t, use v_(i+1)=T_i^(-T)v_i;
then A_(i+1)=T_i^T A_i=T_i A_i as T_i is diagonal. All other data must
be transported along with it.

For example, if an exterior Gaussian tail has coefficient matrix Gamma
and the first n coordinates are v, put Q_i=diag(T_i,I). Its actual data
update is Gamma_(i+1)=Q_i^T Gamma_i Q_i. Upper skew entries need at most
n(d-1) multiplications when Gamma has order d: two for each internal
v,v pair and one for each v,other pair. Each remaining odd covector
ell transforms to Q_i^T ell, costing n multiplications per covector.
Thus a retained future factor list with M covectors is transported with
nM further multiplications. Keeping that list does not evaluate it.

The determinant/Pfaffian normalization also changes. For the auxiliary
matrix pencil, C_i=[t_1...t_n]det(sum_r t_r A_(i,r)) satisfies

    C_(i+1)=det(T_i) C_i,     original C=det(H_i) C_i.

For exterior Gaussian integrals the corresponding Berezin Jacobian is
det(Q_i)^(-1). These are exact orientation and normalization factors to
charge, not arbitrary omissions. Using C_i itself as an initial scalar
state would assume the unknown contraction and is forbidden.

## Ratios are not arithmetic gates

The chart ratios in (FT) require a scalar compilation. One concrete
division-free formal-series compilation is available for their DATA.
Write w_(r,j)(epsilon)=w0_(r,j)+epsilon*Delta_(r,j), where each known
rational w0 is nonzero. At truncation degree q set

    c_0=1/w0,
    c_k=(-Delta/w0)c_(k-1),    1<=k<=q.

These are the inverse coefficients modulo epsilon^(q+1), using only
addition and multiplication and the known rational constant 1/w0.
Delta construction costs one addition, (-Delta/w0) one multiplication,
and the q remaining coefficients q multiplications: q+2 gates per
denominator. Multiplying that inverse by the next linear numerator
requires one product for degree zero and two products plus one addition
at each positive degree, for 3q+1 gates, plus one numerator Delta addition.
A conservative fresh construction of all n ratios costs n(4q+4) gates.
Cached Delta and inverse data can improve this bound but are not needed.

Every transported scalar can be an array of length q+1; one product of
arrays costs (q+1)^2 gates by explicit truncated convolution. Thus the
matrix/covector updates above cost at most

    (2n^2+n(d-1)+nM)(q+1)^2 + n(4q+4)

with their input arrays supplied. Determinant normalization factors need
their own charged product operations. A known Hilbert input chart has
w0_(r,j)=1/(r+j+1), zero-based, so its constants and reciprocal constants
have O(log n) bit length. This is a data transport construction, not
evidence of safe unspecified future charts or an evaluated root circuit.

Taking q=n would recover a degree-n target only after a complete target
identity and all nonzero chart constant terms were proved. Neither is
assumed here. No inverse of a variable is treated as one scalar gate.

There is also a projective polynomial data identity. Let

    delta_i=det(H_i),  P_(i,r)=adj(H_i)D_r,
    Tproj_i=adj(H_(i+1))H_i.

Then

    delta_i P_(i+1,r)=Tproj_i P_(i,r).                    (PFT)

All diagonal adjugates are prefix/suffix products of the supplied w_i
entries, constructible in at most 3n multiplications; the n diagonal
entries of Tproj need n further multiplications. This statement is
polynomial and remains true at singular w. Reading P_(i+1,r) from (PFT)
would still require division by delta_i; alternatively it can be rebuilt
directly from original D_r with charged scalar operations. (PFT) alone
does not give a division-free evaluated transfer or terminal boundary.

## The first new object required by varying frames

The common-base identity (CB) closed because the diagonal coefficients
of row r were alpha_r, independent of column. In a moving frame the
exact diagonal-plus-rank-one expansion instead requires the following
contextual diagonal response, for equally sized row and column sets S,I:

    P_(S,I) = [product_(r notin S) t_r]
      product_(j notin I) (sum_(r notin S) d_(i,r,j) t_r).    (DR)

It is a precisely defined object, not a proposed free coefficient gate.
Let Pmat have columns p_(i,r), Qmat columns q_r. The fully multilinear
determinant coefficient is exactly

    sum_(S,I, |S|=|I|)
      det(Pmat[I,S]) det(Qmat[I,S]) P_(S,I).              (EXP)

This follows by selecting the diagonal columns in the determinant,
then applying Cauchy-Binet to the remaining rank-one sum. It identifies
the exact response an evaluator must produce; no large response family
is initialized with unknown values or executed in this leaf.

With a common scalar diagonal, (DR) reduces to
(n-|S|)! product_(r notin S) alpha_r. This is what allowed the single
univariate determinant and factorial weighting in (CB). The transported
weights d_(i,r,j) retain their column index and this simplification has
not been established. The underlying product of linear forms is cheap
as a circuit IN t; its requested fully multilinear scalar value remains
to be compiled. Total degree <= n does not make that operation a gate.

The moving frame has exact response transport

    P'_(S,I) = product_(j notin I) tau_(i,j) * P_(S,I).

The Pmat minor acquires product_(j in I) tau_(i,j), so each whole term
in (EXP) acquires det(T_i), agreeing with the global normalization.
This proves informally that the data transport is coherent with the
required functional. It does not supply the INITIAL responses (DR).
Using those initial responses as leaves would reintroduce unknown
coefficients. An actual scalar initialization/aggregation of (DR), or
a different closed response with the same context semantics, is the
first still-unsupplied operation in this candidate.

Therefore the variable bases have an explicit charged transport, and
the larger diagonal-plus-rank-one DATA class is closed. The target
scalar transfer is not closed. This is the exact current frontier,
without a counterexample, a lower-bound claim, or a fourth candidate.
