# Hard-core spectral compression with every parameter charged

Arbor cycle 2, node n7. This result contains a complete polynomial scalar
compiler for a structurally banded class and an exact, all-order Schur
proposal for general inputs. The latter has no polynomial parameter closure
proved here. The banded class does not equal the contract's dense legal
family p_ij=1+a_ij^2: entries outside its band are structural zeros. Within
the band the binary z markers and all original column phases are preserved.
There is no general development candidate and dev_score=null.

The starting point is the spin operator and generalized-nullspace elimination
in Alase, Doty, Feder, [The matrix permanent and determinant from a spin
system](https://arxiv.org/pdf/2307.04681), Sections III and V. The constructions
and scalar-cost accounting below are derived explicitly rather than using
the count of distinct eigenvalues as a computational primitive.

## 1. The operator with the original spectral register

Use zero-based rows and columns. Work over
R=Q[p_ij,z][Z/N], N=2^bit_length(n), and write

    M_ij = p_ij z^(2^(in+j)) e_(d_j mod N).

The basis of T consists of all proper column subsets S. If |S|=k<n-1,
the edge S -> S union {j} has weight M_kj for j not in S. From a subset
of size n-1 the corresponding edge returns to the empty subset. Therefore
T^n applied to the empty state has only its empty coordinate nonzero,
equal to

    Y = sum_sigma product_i M_i,sigma(i)
      = (sum_sigma product_i p_i,sigma(i) z^E(sigma)) e_(sum_j d_j mod N).

The exclusion of an occupied column implements q_j^2=0, while the positive
transition signs implement the commuting double-orientation markers. The
global orientation factor is already normalized as in the task contract.
The spectral register accompanies every transition; Y is an output of the
construction, never an input coefficient.

Every directed cycle passes through the empty state and has length n.
Thus a cycle cover contributing to det(lambda I-T) contains at most one
nontrivial cycle. Its sign, including the minus signs from lambda I-T, is
negative. For D basis states this proves directly over R that

    det(lambda I-T) = lambda^(D-n) (lambda^n-Y).

This identity is valid even when a specialization makes Y=0. It does not
require roots, nonzero eigenvalues, or input-dependent inverses.

## 2. What the natural Krylov normalization asks for

Let v_k=T^k e_empty for 0<=k<n and w_k=e_empty^T T^(n-k). Layer supports
are disjoint, and the full-cycle contraction gives

    w_i v_j = delta_ij Y.

This particular biorthogonal frame would normalize by Y. Keeping its
vectors in factored operator notation does not implement that contraction
or division in scalar gates. The code verifies this Gram identity through
n=5; it is a diagnosis of this frame, not an obstruction to other frames.

## 3. A normalization that uses only rational constants

For layer k let r_k be the all-ones vector on its binom(n,k) subsets and
let ell_k be their average. Set

    P = sum_(k=0)^(n-1) r_k ell_k,  Q=I-P.

Then ell_k r_k=1, using only the legal constant 1/binom(n,k). No target
amplitude occurs in these projectors. Q has no empty-layer component.
Consequently Q T Q raises the layer until it is killed, so for n>=2 it is
nilpotent of index at most n-1 for every B, not only at a chosen baseline.
For n=1 the eliminated space is empty.

For a formal spectral parameter lambda, the Schur complement on im(P) is

    T_eff(lambda) = PTP + PTQ (lambda I-QTQ)^(-1) QTP.

Its inverse expands into a finite series of at most n-1 powers. This is an
identity of formal Laurent-polynomial operator matrices. The proposed scalar
construction must evaluate the coefficients of that series; treating the
inverse or an operator product as one scalar gate is not allowed.

### 3.1 Every excursion coefficient, not only order two

Temporarily distinguish the full subset as layer n, to be identified with
the empty state when closing a cycle. Let U_k denote the upward transition
from layer k, and define, for 0<=a<b<=n,

    m_ab = ell_b U_(b-1) ... U_a r_a,
    kappa_ab = ell_b U_(b-1) Q_(b-1) ... Q_(a+1) U_a r_a.

There is no Q at either endpoint. Put m_aa=1. If l=b-a and

    J_[a,b) = sum_(j_a,...,j_(b-1) distinct) product_(i=a)^(b-1) M_i,j_i,

then counting the a occupied starting columns avoiding the l new ones gives

    m_ab = binom(n-l,a)/binom(n,b) * J_[a,b)
         = (b!/a!)/(n)_l * J_[a,b),

where (n)_l=n(n-1)...(n-l+1). Expanding every Q=I-P gives the full formula

    kappa_ab = sum_(a=t0<t1<...<tr=b) (-1)^(r-1)
                           product_(s=1)^r m_(t_(s-1),t_s)

or, equivalently,

    kappa_ab = (b!/a!) sum_(consecutive block partitions pi of [a,b))
                         (-1)^(|pi|-1) product_(I in pi) J_I/(n)_(|I|).

These are formulas in the spectral group algebra R, so overlapping column
choices introduced by coarse projection retain their original phases and
are cancelled by the complete excursion sum.

The 2^(l-1)-term displayed expansion can be shared by the genuinely scalar
interval recurrence

    kappa_ab = m_ab - sum_(a<c<b) kappa_ac m_cb.

If the m_ab are already computed, all kappa_ab cost O(n^3) ring operations.
Similarly, with F_0=1,

    F_b = sum_(a=0)^(b-1) F_a kappa_ab

recovers F_n=Y in O(n^2) ring operations. Explicit cyclic convolution in R
costs O(N^2) scalar operations per product. All rational normalization
literals have polynomial bit lengths (binomial constants have O(n) bits).

The effective Schur edge from coarse layer a to b (with b=n returning to
zero) has weight lambda^(1-(b-a)) kappa_ab. No uncharged lambda inverse is
needed for the recurrence for F above; lambda only describes the spectral
pencil.

### 3.2 The exact closure condition still missing in the dense case

There are only n(n+1)/2 interval parameters, but that fact alone does not
compute them. In particular J_[0,n)=Y. Supplying the entire interval family
as inputs would supply the target. The general audit code computes J by
explicit injective-column dynamic programming and charges no claim of
polynomial size to that calculation.

The direct extension rule exposes the missing states. If J_I(F) forbids
the columns in F, adding a row i requires

    J_(I union {i})(F) = sum_(j notin F) M_ij J_I(F union {j}).

The no-forbidden-column interval family does not close under this rule.
The straightforward implementation carries forbidden-column subsets. A
general solution of this Schur proposal would need a uniform polynomial
scalar procedure that computes all required kappa_ab (or their total
contraction) from the original marked cells, shares these conditional
quantities without that subset list, and accounts for its terminal reader.
No such rule is obtained here. This does not require an intermediate scalar
permanent before the spectral stage: all these quantities live in R.

For clarity, the low-order formulas actually obtained are

    kappa_(k,k+1) = (k+1)/n * S_k,

    kappa_(k,k+2) = (k+1)(k+2)/(n(n-1))
                       * (S_k S_(k+1)/n - C_(k,k+1)),

where S_i=sum_j M_ij and C_il=sum_j M_ij M_lj. Higher excursions do not
reduce universally to these row sums and pairwise inner products. At z=1
and zero original column labels (equivalently, after the zero-frequency
character), the two dense legal input matrices

    B = [[ 1,17,10,26],      C = [[10,26, 1,17],
         [ 1, 1,37,37],           [37,37, 1, 1],
         [26,17, 1,10],           [10, 1,17,26],
         [ 1,10,17,26]]           [17,26, 1,10]]

have equal row sums and equal complete row Gram matrices, yet weights
1,145,322 and 811,368. Every entry is 1+a^2 for an integer a. Indeed C=BH
with H=I-vv^T/2, v=(1,1,-1,-1)^T, so H is orthogonal and fixes the all-ones
vector. All excursions of lengths one and two coincide; length three
already differs. This rules out that specific pair-statistic closure,
not a larger family of scalar intermediates. No further diagnostic family
is substituted for the missing all-order construction.

## 4. A support-adapted compression that does close

Assume now M_ij=0 whenever |i-j|>w, for a fixed half-bandwidth w. Every
remaining marked cell is arbitrary, including its original binary address
and column phase. At layer k, a subset on a complete cycle must contain
every column less than k-w: these columns cannot be chosen by a later row.
It also cannot yet contain any column at least k+w.

Only the at most 2w columns in [k-w,k+w) need be tracked. In an interior
layer precisely w of them are occupied, giving at most binom(2w,w) states.
The boundary counts are no larger. Forward reachability plus this expired-
column condition is exact: any retained partial matching can be completed
by assigning the unused columns in increasing order. If the first unused
column is at least k-w, the j-th unused column is between k-w+j and k+j,
so that completion obeys the band restriction.

Delete the other states. Each deleted state is outside the strongly
connected component containing the empty state. Since every cycle passes
through that state, the deleted diagonal blocks are acyclic and nilpotent.
This is an explicit elimination of generalized-zero components based only
on the support. It does not introduce an amplitude into the reduced matrix.
The reduced operator has at most

    V <= n binom(2w,w),   E <= (2w+1)V

vertices and edges, all still weighted by original M_ij. It need not remove
every remaining zero eigenvalue: obtaining a polynomial-sized operator is
already enough to compile its action without a hidden large representation.

`build_banded` implements that action in ordinary scalar gates. For each
occupied-column state S it stores one scalar coefficient and the known
phase sum_(j in S) d_j mod N. Paths merging at S have exactly that common
phase. Each transition multiplies by its original marked cell and updates
the phase index; each merge emits an addition. At the end every output slot
is produced, with the full state located at sum_j d_j mod N.

No algebra-valued gate, input-dependent normalization, or coefficient oracle
is used. The supplied omega is unnecessary because the cyclic spectral
grading is carried symbolically through the fused computation.

### 4.1 Exact scalar accounting

Let m_band be the number of allowed cells and r0=min(n,w+1) the first-row
branch count. The shared binary marking uses n^2-1 squarings and m_band
multiplications. The first row forwards its cell values, so transition
products cost E-r0 gates. The number of merge additions is E-V. Thus

    gates = n^2-1 + m_band + 2E-V-r0.

For fixed w this is O(n^2+n w binom(2w,w)). Every literal is 0 or 1. State
masks have n bits; compiler time is polynomial in n and the bit lengths of
the labels for fixed w. No numerical values of p or z are inspected by the
compiler.

For w=1 the surviving states at each interior layer k are exactly

    S_k={0,...,k-1},   S'_k={0,...,k-2,k}.

Hence V=2n-1 and E=3n-2. The main/pending-state update gives the familiar
but here fully marked recurrence

    F_0=1, F_1=B_00,
    F_k=B_(k-1,k-1)F_(k-1)
           +B_(k-1,k-2)B_(k-2,k-1)F_(k-2).

The implementation maintains the two original phase indices, rather than
using F_n as a supplied spectral amplitude. The exact count is 1 for n=1,
and n^2+7n-8 for n>=2. An equivalent sign-corrected determinant negates
the subdiagonal: every allowed permutation consists of disjoint adjacent
swaps, and each swap then receives its second minus sign. Thus sign
correction also remains explicit throughout this infinite class.

For w=2 and n>=4, the layer counts are 1,3,6,...,6,3, yielding V=6n-11.
The edge counts are 3,9,12,...,12,9,3, yielding E=12n-24. Since
m_band=5n-6 and r0=3, the exact scalar count is n^2+23n-47. This class
already includes nontrivial three-cycles and is handled by the hard-core
state action, not by assuming one scalar signing works on all its cells.

At n=8 the actual counts are 112 gates for w=1 and 201 gates for w=2.
These are class-specific counts, not development scores for the dense task.

## 5. Verification and scope

Run `python verify_spectral_hardcore.py`. The frozen evaluator is not used.

* 192 numerical full output tables and 48 formal-z full output tables pass
  through n=8, for the specialized tridiagonal and general frontier builders.
  Inputs include z=0,1,-1 and random values, and negative/random labels.
* Raw and reduced characteristic polynomials agree with
  lambda^(D-n)(lambda^n-P omega^(f sum d)) for n<=6, widths 1 and 2,
  and three frequencies (two distinct frequencies when n=1).
* The uniform-projector excursion recurrence, its full consecutive-partition
  expansion, and direct Q-operator action agree at every order through n=6.
* Krylov Gram identities and the dense legal pair-statistic counterexample
  are checked exactly with integer/rational arithmetic.

The banded compilers prove that polynomial elimination can retain all
addresses and original phases without preloading the cycle weight. They
do not supply the dense positive family with a bounded support width.
For that family the all-order uniform Schur formula is exact and its
normalizations are legal, but its conditional-column parameter closure
remains unconstructed. `candidate.py`, `dag.py`, and `evaluate_dev.py` stay
unchanged, and no coordinator held-out data was accessed.
