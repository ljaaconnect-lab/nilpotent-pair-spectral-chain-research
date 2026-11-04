# n68: contextual row-incidence reduction

Artifact version: n68-contextual-closure-search-v1. Status: **informal**.
No declaration in this document was submitted to Lean. No new symbolic or
numerical experiment is claimed. This reduction supports the fixed n68
hypothesis; it does not construct the original coefficient extractor.

## Exact port conventions

Let B=(b_ij) be generic formal entries over a commutative Q-algebra. Nothing
specializes or erases the original marked substitution
b_ij=(1+a_ij^2) z^(2^(i*n+j)). Write m=n^2. The real edge ports are
a_e,b_e, interleaved in row-major edge order. The dummy pair g_a,g_b follows
all real ports. Let J_n be the skew matrix with upper entries +1. Set

    R_(i,e) = [row(e)=i],   C_(j,e) = [col(e)=j],
    A0 = [[0,B],[-B^T,0]],
    T_(u_i,a_e) = [row(e)=i] b_e,
    T_(v_j,b_e) = [col(e)=j],
    Z = [[A0,T],[-T^T,0]].

For a real-port subset Q in inherited order, define

    F_Q = Pf Z[core,Q],
    G_Q = Pf K[dummy,Q],
    D_a = diag(-1 on real a ports, +1 elsewhere),
    Ktilde = D_a K D_a,
    Gtilde_Q = Pf Ktilde[dummy,Q].

The convention Pf of an odd-size skew matrix is zero. The ordering of
dummy relative to Q is inherited from n66; moving an entire pair past Q
has even shuffle parity. The target interface inherited from n64/n66 is

    P(B) = gamma_n sum_(Q=union of complete edge pairs) F_Q Gtilde_Q,
    gamma_n = (-1)^(n(n-1)/2).

That target interface and its orientation are prior informal blueprint
dependencies, rather than new Lean-certified theorems in n68.

## New pointwise replacement

Define Krow to agree with Ktilde in every block except the real a,a block:

    Krow_aa = R^T J_n R,       Ktilde_aa = J_(row-major edges),
    Krow_bb = Ktilde_bb = -C^T J_n C,
    Krow_(a_e,b_f) = [e=f],
    Krow_(a_e,g_a) = -1,       Krow_(b_e,g_b) = -1,
    Krow_(g_a,g_b) = +1.

All unspecified a,b cross entries and dummy couplings are zero; skew
symmetry supplies the lower entries. Define Grow_Q=Pf Krow[dummy,Q].

The proposed universal lemma is

    for every Q,  F_Q * (Gtilde_Q - Grow_Q) = 0.             (CQ)

There is a direct termwise derivation, without an inverse of B or b_e:

1. If Q contains a_e and a_f with row(e)=row(f), both selected ports have
   their only potentially nonzero Z neighbors at the same core vertex u_i.
   The real-port block of Z is zero. A perfect matching term of the
   Pfaffian cannot pair two vertices to the same vertex. Every term is
   zero, hence F_Q=0. This also follows from proportional T columns, but
   the incidence argument avoids division by either b_e or b_f.
2. Otherwise the selected a ports have distinct row labels. Row-major edge
   order agrees with row order between every such pair. Consequently the
   J_(row-major edges) restriction and the R^T J_n R restriction agree
   entrywise on Q. Every other block was preserved. The two restricted
   skew matrices are equal, hence Gtilde_Q=Grow_Q.

The same first-family incidence reasoning gives F_Q=0 when two selected
b ports have the same column. That additional support fact is retained;
the b,b block already has the column factorization everywhere.

## Every diagonal synchronization context is preserved

For arbitrary commuting weights omega(Q), (CQ) gives

    sum_Q omega(Q) F_Q Gtilde_Q = sum_Q omega(Q) F_Q Grow_Q.

The weights may include every remaining synchronization indicator, every
already imposed edge-pair indicator, and any prefix of such diagonal
constraints. Thus the replacement preserves the entire future product
of constraints at this coefficient interface. It applies to unpaired Q
as well as paired Q. It does not replace the future context by a Gaussian
tail, and it does not infer Gaussianity after a synchronization step.

This argument is stronger than an equality only for the final paired sum,
but it remains **informal**, with no new development pass fraction.

## Explicit low-rank update representation

Use temporary block order [all a, all b, g_a, g_b]. Let Dpair have the
real a,b identity cross block, its negative transpose, and zeros otherwise.
Define P=diag(R,C,I_2), with the natural rectangular incidence blocks, and

    H = [[ J_n,    0,     -1_n,     0   ],
         [  0,   -J_n,      0,   -1_n  ],
         [ 1_n^T,  0,       0,     1   ],
         [  0,   1_n^T,    -1,     0   ]].

Then entrywise Krow = Dpair + P^T H P. H has order 2n+2. This is a
constructive constant-incidence factorization of the reduced kernel.
Changing to interleaved real ports uses one fixed permutation; its sign
must accompany any Pfaffian computation. The two diagonal sectors have
rank at most n over a field. These rank statements do not by themselves
bound the dimension of a synchronized mixed-moment module.

An explicit entry-by-entry constructor needs O(n^4) integer indexing work
to emit its O(n^4) matrix entries. Its only scalar constants are 0,+1,-1,
with bounded binary length. It emits data, not the target, and no derivative,
projection, or full contraction is counted as a scalar gate.

## Required stability beyond diagonal contexts

(CQ) is a pointwise identity of coefficient families. It does not certify
that an ideal imposing duplicate-row a monomials is stable under arbitrary
Grassmann differentiation: differentiating a product can remove the very
duplicate that made it vanish. A Ward update can also differentiate the
future factors. A valid reduced state therefore needs an actual
intertwining theorem for its updates and its complete remaining context.

The exact constructive obligation is a polynomial-size state Psi_t and
scalar transition U_t, cheaply initialized from generic B, such that for
every synchronization prefix t and every subsequent target contraction,

    Psi_(t+1)(actual synchronized context) = U_t(Psi_t(actual context)),

with a charged scalar boundary computing the final paired contraction.
No such closed state is provided here. Rank reduction and (CQ) are
supporting positive constructions, not a proof of Conjecture 1.5.
