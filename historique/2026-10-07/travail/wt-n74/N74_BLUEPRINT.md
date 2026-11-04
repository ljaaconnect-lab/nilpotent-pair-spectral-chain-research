# n74: five AND obligations for the actual suffix quotient

Artifact version n74-atomic-suffix-blueprint-v1. The two candidates are
fixed by n74-protocol.json. The user changed the method to elementary
subproblems; direct global search stopped before any experiment. No Lean
invocation or numerical/SymPy evaluation was executed in n74. All new
identities below are informal, not kernel-verified declarations.

The inherited n69 materials were read only. Its exact sectors, first-row
fusion and resolvent identities are informal supporting derivations. The
coordinator reports an independently verified all-n subset transfer in
n73, of dimension 2^n; this is a closed reference rather than a compact
construction. No n73 test or artifact was regenerated in this leaf.

## Fixed target and notation

Let q_j be commuting even square-zero elements and let
L(q_J)=(-1)^|J|. Define the actual rows and prefixes by

    ell_r(q) = -sum_j b_(r,j) q_j,
    P_0=1,   P_(i+1)=ell_i P_i.

Then L(P_n)=per(B), by expansion over injective assignments. The source
substitution b_ij=(1+a_ij^2)z^(2^(i*n+j)) is preserved. Every rational A
and every n remain in scope. The central-coefficient bridge remains the
original one; changing a sufficient helper does not weaken that target.
For n=1 the terminal scalar is already h_0=b_00. The second-fusion
response below is required only when a second row exists.

For a Gaussian cross covariance M define its paired moment polynomial

    R_M(t)=det(I+diag(t)M).

For the ACTUAL remaining rows of this B, put

    Lambda_i^B(F)
      = [product_(r=i..n-1)(-D_(b_r)) F(t)]_(t=0),
    D_b = sum_j b_j partial_(t_j).

This notation specifies an exact linear functional. It is not a
derivative gate or a scalar implementation. It reads only the real
suffix, not every arbitrary future polynomial f(q).

The five obligations form an AND chain. A supporting identity may be
elementary while its charged scalar construction remains open.

## O1. Explicit initialization

Construct m_0=1 and M_0=-I from constants 0,-1,1. Then
R_(M_0)=product_j(1-t_j), which gives precisely the initial L(q_J).
No target response is an input. The original marked B can be compiled
with shared powers z,z^2,z^4,...: n^2-1 squarings and n^2 products with
the prescribed p_ij=1+a_ij^2 leaves, for 2n^2-1 scalar gates.

The first genuinely calculable scalar is

    h_0=sum_j b_(0,j).

It costs n-1 additions with those input entries supplied. The first
projective covariance can also be constructed immediately:

    h_0 M_1 = -h_0 I + b_0 1^T.

Compute -h_0 once, then its n diagonal sums; the off-diagonal entries
reuse b_(0,j). Including the h_0 sum, this costs exactly 2n arithmetic
gates in this no-fold recipe. All marked entries plus the projective
first-prefix data therefore cost 2n^2-1+2n gates. These are analytical
recipe counts, not measured DAG counts or Lean cost theorems.

Status: explicit elementary construction. A first-row symbolic API or
its equations must still receive the separate formal verification planned
by the coordinator; no n74 compiler success is asserted.

## O2. Exact insertion of one column

For an occupied set S, define G_S(q_J)=(-1)^|J| if J is disjoint from S,
and zero otherwise. Then for every paired polynomial f(q),

    G_S(-q_j f)=G_(S union {j})(f),  j notin S,
    G_S(-q_j f)=0,                  j in S.

The identity follows from q_j^2=0 and the displayed moment signs. A
branch coefficient multiplied by b_(i,j) uses one scalar multiplication;
merging it into an existing coefficient uses one addition. Neither the
functional nor exterior multiplication is declared a free scalar gate.

Status: elementary sector identity, inherited from n69. It accounts for
initialization and signs, but enumerating all sectors is not a compact
n74 candidate and is not rerun here.

## O3. Charged reading of the actual suffix

For a paired Gaussian state, expansion gives exactly

    G_M(product_(r=i..n-1) ell_r)=Lambda_i^B(R_M).

This is an elementary semantic translation. Its general scalar reading
algorithm is the first open construction. Candidate 1 below needs an
adjugate response, not the terminal target supplied as a leaf:

    K_i(M)=Lambda_(i+1)^B(adj(I+T M) T),   T=diag(t).

Lambda is applied entrywise. This matrix depends only on the actual
remaining rows and the proposed current M. A compact polynomial source
for adj(I+TM) does not itself evaluate these directional coefficients.
Neither K_i nor its contractions may be initialized by an oracle.

Status: reader semantics elementary; polynomial scalar initialization
and evaluation of the needed response K_i are NOT constructed.

## O4. Fusion preserving only that suffix

Candidate 1: context-specific projective Schur/covariance update. Its
proposed state is mass m_i and an n-by-n cross covariance M_i. It needs
only the invariant

    m_i Lambda_i^B(R_(M_i)) = L(P_n),

not equality on every polynomial f(q). Initialization O1 satisfies this
semantic equality by the original assignment expansion, without having
to compute its right side as an input.

The first fusion is already established informally in n69. On h_0!=0,

    u_j=b_(0,j)/h_0,   M_1=-I+u 1^T,
    h_0 det(M_1[J,J])=(-1)^|J|(h_0-sum_(j in J)b_(0,j)).

This matches the actual first-prefix moments for every paired context,
and in particular for the actual suffix. It is an elementary determinant
lemma calculation. It does not establish later fusion.

For a next row b, put tau=Tr(diag(b)M), h=-tau. If h is admissibly
invertible, a rank-one update Delta=x y^T gives an exact candidate

    m'=m h,   M'=M+Delta.

Jacobi's identity and the rank-one determinant lemma reduce its ACTUAL
suffix condition to one scalar equation:

    tau*y^T K_i(M) x + Tr(K_i(M) M diag(b) M)=0.          (F)

Indeed the whole polynomial discrepancy is
Tr(adj(I+TM) T (Delta+M diag(b)M/tau)); applying the one actual suffix
reader gives (F). No full-context annihilator equality is required.

Given M and b, tau and h use 2n arithmetic gates in a no-fold sum/negate
recipe. The missing data are K_i(M), or an explicit identity yielding
x,y without reading that response, followed by a certified charged
choice of x,y satisfying (F) at every step. Fusion is OPEN, not obvious.
Projective equality at a zero pivot does not construct a normalized
scalar update.

Candidate 2: charged adjugate response restricted to actual suffix rows.
Its construction target is exactly K_i(M). At the first fused frame
M_1=-I+u1^T with sum u=1, put p=product_j(1-t_j) and
lambda_j=t_j/(1-t_j). The adjugate response has division-free entries

    (adj(I+TM_1)T)_(j,j)
      = t_j product_(a!=j)(1-t_a)
        +sum_(k!=j)u_k t_j t_k product_(a!=j,k)(1-t_a),
    (adj(I+TM_1)T)_(j,k)
      = -u_j t_j t_k product_(a!=j,k)(1-t_a), j!=k.

Thus the first response required for the SECOND row is determined by

    eta_j = Lambda_2^B(t_j product_(a!=j)(1-t_a)),
    eta_jk = Lambda_2^B(t_j t_k product_(a!=j,k)(1-t_a)),
    K_jj=eta_j+sum_(k!=j)u_k eta_jk,
    K_jk=-u_j eta_jk.

These eta values are the first non-initialized quantities in this
attempt. They use only rows 2,...,n-1 of this B, not arbitrary f(q).
They are not accepted as input leaves. In injective-assignment language,
eta_j is the negative total weight of the actual suffix assignments
whose image contains j, and eta_jk is the positive total weight whose
image contains both j and k. This identifies the requested value without
providing a polynomial scalar algorithm for it.

Some genuinely calculable short readers are explicit. With no suffix,
all eta values are zero. With one remaining row c, eta_j=-c_j and
eta_jk=0. With two remaining rows c,d,

    eta_j=-c_j sum_(a!=j)d_a-d_j sum_(a!=j)c_a,
    eta_jk=c_j d_k+c_k d_j,  j!=k.

These are finite scalar formulas, not executed experiments or evidence
of closure for arbitrary suffix length n-2. General eta initialization
requires a new charged construction, not an unnamed coefficient gate.

Status: first fusion and reduction to (F) are elementary informal
identities. General actual-suffix response initialization and subsequent
fusion are the exact unsolved constructions.

## O5. Normalization, scalar cost and terminal boundary

The first projective data from O1 avoid variable division. To use the
normalized M_1 in a scalar circuit, one admissible compiler mechanism
is B(epsilon)=ones+epsilon(B-ones). Then h_0 has known constant term n.
Its reciprocal coefficients can be formed using only + and * and the
known constant 1/n. For a general proved safe pivot h with constant h_c,

    v_0=1/h_c,
    v_k=-(1/h_c) sum_(r=1..k) h_r v_(k-r).

Through degree n, this uses n(n+1) gates in the inherited padded recipe;
one scalar array multiplication costs (n+1)^2 gates. Constants 1/n have
O(log n) bit length. Original marker inputs are compiled as in O1.
No reciprocal of a variable is a primitive gate.

Only the first normalized pivot is known here. True prefix masses at
ones have explicit falling-factorial values, but a suffix-only fused
representation need not have those true prefix masses. Their later
pivots cannot be assigned those values by assumption. Each actual
fusion must provide its own safe constant pivots and bit/cost bounds.

If O1--O4 were fully constructed and normalized with these certificates,
the terminal reader is Lambda_n^B(F)=F(0), R_M(0)=1, and the output is
m_n. This charges the scalar terminal rather than inserting per(B).
Recovering the exact degree-n target from its epsilon arrays would use
n additions at epsilon=1, after a complete identity is proved. This is
a compiler ingredient, not a proof of the missing fusion.

Status: first pivot and the scalar reciprocal mechanism are elementary.
Later pivot certificates, full polynomial gate/literal/bit-time bounds
and the global uniform construction remain required.

## Frozen result and next atomic obligation

The AND chain is initialization -> column insertion -> actual suffix
reader -> fusion -> normalization/terminal. Semantic identities in these
steps are distinguishable from charged algorithms. The first response
not initialized is K_1(M_1), concretely its eta_j and eta_jk above for
the arbitrary actual suffix of length n-2. A next atomic task can prove
the first-fusion identities and their initialization; it must not call
the general suffix fusion solved. No new strategy, compiler window,
held-out read or identity-only replacement test is opened by this leaf.

Strict development score: null. No initialized, closed, polynomial
scalar candidate is isolated. The objective of Conjecture 1.5 remains
open; this records exact constructive subproblems, not impossibility.
