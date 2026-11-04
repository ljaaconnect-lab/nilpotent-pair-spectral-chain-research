# Euler pair phases and counted complementary cofactors

The frozen protocol is `n61-protocol.json`, SHA256
`f599b50a2a6e94fe6c2a2b2a5dd45b1b57cad74d4780e0a3f317373da4e16061`.
Three precise variants are allowed; the selected candidate is the third.
No held-out data, shared Arbor state, or existing branch files are modified.

For a multilinear polynomial, put E_e=x_e d/dx_e. Then

    E_e E_f F = F - F[e=0] - F[f=0] + F[e=f=0].
    T_ef F = -F + 2F[e=0] + 2F[f=0] - 2F[e=f=0].

Every inversion (i,l,j,m), i<l and j>m, contributes one phase. On a
permutation monomial their product has sign (-1)^inv(sigma), so applying
all phases to det(X) yields the unsigned permutation sum. This paragraph
is an informal general proof; finite SymPy checks and the separate Lean
bridge have their own provenance. Differentiation is never a scalar gate.

On assignment monomials, projectors for distinct column pairs at fixed
rows i,l are orthogonal. Hence the row group is

    1 - 2 sum_{j>m} E_(i,j) E_(l,m).

Variant 1 copies four scalar circuits per inversion, retaining all gates.
The unchanged determinant seed recurrence has

    S0(n)=2n^4-n^3+2n^2-n,
    q=n(n-1)/2, h=q^2,
    G_h=4^h S0(n)+7(4^h-1)/3.

The seven additional gates are four scalar multiplications by rational
constants and three scalar additions. Only n=2 is materialized; the
larger exact counts are derived from this explicit construction, not a
lower bound for other constructions. Marking adds 2n^2-1 shared gates.

Variant 2 groups by rows and shares zero specializations. It memoizes
(node, zero mask), intersects masks with syntactic support, hash-conses
identical add/mul gates, and simplifies only known zero/one operations.
This requires no expanded polynomial or corrected target input. Its
resource cap is 200000 nodes or 45 construction seconds. A capped run
does not establish impossibility or invalidate the cofactor variant.

Variant 3 expands the row-group projector product into

    sum_F alpha_F P_F,  P_F=product_{e in F} E_e,

where F is a compatible partial matching. Incompatible products annihilate
det(X); repeated edges are idempotent. The integers alpha_F depend only
on n and the inversion list. Their preprocessing additions/multiplications,
state counts and bit lengths are explicitly reported. They are not computed
from the corrected determinant value.

For selected rows I and columns J and the matching bijection tau:I->J,
the exact local cofactor identity is

    P_F det(X) = (-1)^(sum I+sum J) sign(tau)
                  (product_{e in F} x_e) det(X[I^c,J^c]).

The compiler shares complementary minors keyed by (I,J) and recursive edge
products keyed by F. Every minor uses the actual scalar determinant
recurrence, with all live binary additions/multiplications serialized.
Known rational inverses 1/k are constant leaves; no division gate occurs.
Unreachable arithmetic is removed by a purely structural liveness pass.

Before measurements, a constructive general bound is available:

    M_n=sum_{k=0}^n binom(n,k)^2 k!,
    D_n=sum_{k=0}^{n-1} binom(n,k)^2 S0(n-k),
    generic gates <= D_n + 4 M_n - 2,
    marked gates <= D_n + 4 M_n - 2 + 2n^2 - 1.

There are at most binom(2n,n) distinct complementary minors, at most M_n-1
edge-product multiplication gates, at most 2 M_n projection/coefficient
multiplications, and at most M_n-1 final additions. This is a conservative
upper bound on this construction. It does not assert polynomial growth.
Each row stage examines at most q M_n column-pair transitions, so integer
preprocessing examines at most q^2 M_n transitions. Coefficient absolute
l1 norm is at most (1+2q)^q; its bit length is bounded accordingly. Counted
preprocessing gates are reported separately from the target scalar circuit.

The marked compiler retains b_ij=(1+a_ij^2)z^(2^(in+j)) and never evaluates
z numerically. The p_ij rational constant leaves follow the source model.
They require exact rational preprocessing, whose bit costs are not a
polynomial-time coefficient-extraction proof. The new circuit computes
P_A(z) directly, equivalent to the desired corrected expression through
the separately established pairing identity; it does not offer a generic
coefficient-extraction primitive.

Six checks per n=2,3,4,5 form the fixed 24-check development metric. Generic
and marked scalar-DAG evaluations execute the actual serialized gates;
permutation expansion is used only as an independent validation oracle.
The finite check is not a kernel proof of this compiler's general semantics.
The remaining constructive obligation is a uniformly cheap sharing scheme
for these projectors/cofactors (or another exact representation), preserving
arbitrary entries and formal markers, with a polynomial bound including
initialization and admissible literal provenance. No such bound is assumed.
