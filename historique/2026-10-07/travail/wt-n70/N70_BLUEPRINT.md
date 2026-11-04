# n70: simultaneous row blocks and a conditional aggregation circuit

Artifact version n70-row-block-transfer-v1. All new identities in this
document are informal; zero Lean invocations are allocated or performed.
Three analytical candidates are fixed in n70-candidates.json. No complete
executable root compiler was isolated. No symbolic or numerical experiment
was executed, and the root development score is null.

The formal entries B=(b_ij) remain generic. The source marking
b_ij=(1+a_ij^2)z^(2^(i*n+j)) is retained as a later exact substitution.
The inherited n68 contextual quotient gives, informally, F_Q=0 when two
selected a ports have the same row, or two selected b ports the same
column. Replacing the a,a kernel by R^T J_n R preserves F_Q G_Q for every
Q; the b,b kernel is -C^T J_n C. This is an inherited support statement,
not a new n70 proof or development test.

## 1. A row-anchored residual, with its complete context

At a Gaussian local chart, removing an entire row of ports restricts the
first family's support to either the empty selection or one selected
edge pair. For each column j let its two-family local selected coefficients
be a_j-U_j and b_j-V_j. The simultaneous row factor is

    F = 1 + sum_j (a_j-U_j)(b_j-V_j)
      = h - A - Bq + W,
    h = 1 + sum_j a_j b_j,
    A = sum_j b_j U_j,   Bq = sum_j a_j V_j,
    W = sum_j U_j V_j.                                  (R1)

All symbols a_j,b_j here are local chart data, NOT the matrix entries
b_ij. U_j,V_j are even quadratic forms and commute. An actual transport
from the original kernels must prove this chart representation, port
orientation and chart data costs. Row-support alone does not certify a
Gaussian chart after preceding synchronizations.

The following polynomial identity is division-free:

    h F - (h-A)(h-Bq) = h W - A Bq.                     (R2)

Suppose the incidence structure at this chart supplies common odd row
anchors u,s and common-column covectors v_j,t_j, with

    U_j = w_j u wedge v_j,   V_j = s wedge t_j.

Then A^2=Bq^2=0 and exterior sorting gives

    h W - A Bq
      = -u s sum_(j,k) D_(j,k) v_j t_k,
    D = diag(w) (h I - b a^T).                         (R3)

The minus sign is the single swap of v_j past s. For h invertible,
(h I-b a^T)^(-1)=(I+b a^T)/h, because h-a^T b=1. No inverse of a
marked w_j is used or supplied. The identity is a local data compression:
one row pair u s anchors the entire quartic remainder. It does not yet
evaluate that remainder in the actual remaining context.

Conservatively, constructing D from explicit scalar a,b,w costs exactly
2n^2+5n gates in this padded recipe: h costs 2n; w*b costs n; all outer
products cost n^2; all their negations cost n^2; h*w on the diagonal
costs n; adding it to the negative outer diagonal costs n. These are
analytical construction counts, not measured or formally certified counts.
They omit the separately required construction of chart covectors and
all contextual moments. Only integer constants and the explicit chart
data are inputs; no unknown contraction is an input.

If Q_future is the product of all remaining row factors or constraints,
the actual residual obligation is

    L(E_tail Q_future u s sum_(j,k) D_(j,k) v_j t_k).

Q_future remains present. A Ward identity differentiates it. A small matrix
D or a shared anchor pair does not authorize replacing this functional
by a bare-Gaussian Wick evaluation. The missing closure theorem must
intertwine every subsequent row block on a polynomial state initialized
from B, with an explicit scalar boundary.

## 2. A polynomial scalar aggregation for a precise common-base class

There is a genuinely charged aggregation for the following conditional
class. In ONE common n-dimensional column basis suppose all row matrices
have the form

    D_i = alpha_i I + u_i v_i^T,   i=1,...,n.

Let U,V have those column vectors and G=V^T U. Define

    f(x)=det(diag(alpha)+x G),   degree f <= n.

An exact informal determinant expansion gives

    [t_1 ... t_n] det(sum_i t_i D_i)
      = sum_(k=0..n) (n-k)! [x^k] f(x).                 (CB)

To derive this, put z=sum_i alpha_i t_i. The rank-one determinant
expansion is sum_S z^(n-|S|) t_S det(G[S,S]). Its fully multilinear
coefficient is sum_S (n-|S|)! det(G[S,S]) product_(i outside S) alpha_i.
The degree-k coefficient of f is the same principal-minor sum without
the factorial. This works when some alpha_i are zero, without dividing
by them. It is a new conditional aggregation identity, not a target
transport theorem or a replacement development check.

No coefficient extraction is free in the proposed scalar implementation:

1. Construct G by n^2 dot products, costing 2n^3-n^2 scalar gates.
2. Run the inherited division-by-constant determinant recurrence on
   coefficient arrays of length n+1 in Q[x]/(x^(n+1)). A scalar addition
   becomes n+1 scalar additions. A truncated scalar multiplication uses
   (n+1)(n+2)/2 products and n(n+1)/2 sums, hence (n+1)^2 gates.
   Degree <= n makes truncation exact for the output determinant.
3. Build the factorials from 1,...,n by n-1 multiplications and sum the
   n+1 weighted coefficients using n+1 multiplications and n additions.

If the supplied data construction costs S, the analytical bound is

    S + (2n^3-n^2) + S0(n)(n+1)^2 + 3n,
    S0(n)=2n^4-n^3+2n^2-n,

using the actual inherited scalar determinant seed. Constants 1/k in
that seed have O(log n) bit length. The factorials have O(n log n) bit
length, and their construction has been charged. This describes scalar
transitions and array costs, but is not an executed DAG or a Lean theorem.

The important unsupplied hypothesis is the global transport. The actual
weighted row residual (R3) has a row-dependent diagonal diag(w_i), not
an established common scalar multiple of I. Absorbing w_i into v_j for
one row changes that row's column basis; it does not establish one common
basis for ALL rows and ALL future contractions. In addition, identifying
the original Pfaffian contraction with the left side of (CB), including
orientation and initialization, remains unproved. No polynomial circuit
for the root is inferred from (CB) alone.

The requested moving-frame refinement is explicit in
N70_FRAME_TRANSPORT.md: T_i=H_(i+1)^(-1)H_i, with scalar updates for all
diagonals, rank-one vectors, the Gaussian kernel and future covectors;
the ratios have a charged truncated-series compilation and a projective
division-free identity. The DATA class closes. Its first still-needed
scalar object is the diagonal response (DR), whose initial evaluation
is not supplied. The refinement remains inside this second candidate.

## 3. A division-free coherent Gaussian row mixture

Under the shared-anchor assumptions above, U_j^2=V_j^2=0 and
(U_j+V_j)^3=0. Thus

    exp(U_j+V_j)+exp(-U_j-V_j)=2+2 U_j V_j,
    exp(A)=1+A,   exp(Bq)=1+Bq.

Substitution into (R1) gives the division-free identity

    F = (h-n+2) exp(0) - exp(A) - exp(Bq)
        + (1/2) sum_j [exp(U_j+V_j)+exp(-U_j-V_j)].     (GM)

It uses 2n+3 Gaussian quadratic exponentials. The only division is the
constant 1/2. Each summand must carry its coefficient, orientation and
scalar construction cost. An exponential here is a compact exterior
Gaussian description, NOT a scalar arithmetic gate.

There is a smaller division-free identity within the same candidate.
Put Uall=sum_j U_j and Vall=sum_j V_j. Then

    F = sum_j exp(U_j+V_j) + (h-n+2) exp(0)
        -exp(A+Uall)-exp(Bq+Vall).                      (GM2)

Each correction still squares to zero, because it has one common odd
anchor. This uses n+3 exponentials, with no division at all. This
reduces the local mixture description; it does not close the whole sum.

Every future factor is retained in the exact functional version:

    L(E_tail Q_future F)
      = (h-n+2)L(E_tail Q_future)
        -L(E_tail exp(A) Q_future)-L(E_tail exp(Bq) Q_future)
        +(1/2)sum_j L(E_tail exp( +/- (U_j+V_j)) Q_future).

In each branch only the quadratic Gaussian part is shifted; Q_future is
unchanged. No branch is evaluated by Wick unless its remaining context
is actually accounted for. No individual derivative is treated as free.

The new positive closure candidate is a coherent polynomial-size span of
these branch kernels, stable under every later row contraction. Such a
span would need a scalar data map, an explicit initialization, and exact
transition matrices. Merely identifying identical-looking ranks does
not provide it. If the local representation continued at every stage,
the literal no-sharing expansion would have at most (2n+3)^n leaves and
sum_(r=0..n)(2n+3)^r nodes. These are conditional costs of this explicit
construction, not a lower bound and not a measured target algorithm.
Terminal Pfaffians must use a charged scalar compiler, such as the
inherited n64 trace recurrence; they are not contraction primitives.

Even singular constant-term charts have a homogeneous Gaussian
description with n+1 local components. The exact row expression is
F=1+sum_j (a_j-U_j)(b_j-V_j). Introduce four ordered private odd modes
x,y,zeta,eta and write U_j=u_j v_j, V_j=s_j t_j. The bordered Gaussian

    exp(a_j x y + x u_j + y v_j
        + b_j zeta eta + zeta s_j + eta t_j)

has top private-mode coefficient (a_j-U_j)(b_j-V_j). The single swap
in x u_j y v_j gives -U_j, and the second pair gives -V_j. This
notation denotes a real Gaussian auxiliary boundary, not a free
coefficient gate: after all actual context operations its scalar value
is a Pfaffian of the explicitly bordered kernel, and that Pfaffian
must be compiled. Its auxiliary block is diag(a_j J_2,b_j J_2), and
the four coupling rows are u_j,v_j,s_j,t_j. No inverse of a_j or b_j
appears. The vacuum component can use two uncoupled unit J_2 blocks
with zero couplings, fixing a common padded dimension.

With all future factors present, the auxiliary integration leaves them
unchanged. If a compatible transport of every original row block to
these Gaussian components is supplied, choosing one of n+1 components
per row gives at most (n+1)^n fixed-dimension bordered kernels of order
d+4n. Each component uses explicit data; no unknown scalar is an input.
The missing operation is a polynomial coherent aggregation of this
sum for every future context. The branch count is a conditional bound
for this particular description, without an executed compiler or a
lower-bound claim. No repeated n61 matching validation is scored as
new evidence here.

## Remaining exact global criterion

Provide a polynomial-dimensional state Phi_i of the ACTUAL original
marked two-family contraction after row blocks 1,...,i, with scalar
construction from generic B, transition T_i satisfying

    Phi_(i+1)(synchronized context)=T_i(Phi_i(actual context)),

for every future block product, and a scalar boundary equal to P(B).
The transition must preserve the contextual quotient and all graded
orientations. Every chart, literal bit length, initialization gate,
uniform preprocessing step and final operation must be charged.

Neither the row-anchored residual, the conditional common-base aggregator,
nor the local Gaussian mixture supplies this global intertwining. The
two auxiliary generators det(B-B circ X) and Pf(D_x Krow D_x+sum J_e)
remain compact; their coefficient-wise contraction remains uncompiled.
No identity-only tests are substituted for the fixed root metric. The
absence of a completed candidate here is not an impossibility claim.
