# n68: two exact transition interfaces, closure still required

The root-frozen n68-protocol.json is authoritative. There are two analytical
candidate attempts, zero executed experiments, and zero Lean invocations.
Neither attempt is an eligible complete scalar compiler. The strict
development score is null. Source marker variables remain generic in all
formulas; no unknown target coefficient is an initialization leaf.

The new contextual kernel replacement is recorded separately in
N68_CONTEXTUAL_QUOTIENT.md. It preserves F_Q G_Q entrywise under arbitrary
diagonal synchronization contexts and reduces the second family's two
sectors to row and column incidence factors. It is explicitly informal.

## Candidate 1: contextual moments through degree four

Fix an ordered exterior algebra with odd coordinates theta_1,...,theta_d.
Let L_A(Q) be a fixed Berezin integral against an explicit initial Gaussian
kernel. A genuine Gaussian initial chart must be supplied if normalized
covariances or inverses are used; no globally safe future chart is assumed.
Let the actual remaining factors be

    F_e = 1 + (a_e-U_e)(b_e-V_e),
    U_e = u_e wedge v_e,       V_e = s_e wedge t_e,
    h_e = 1 + a_e b_e,
    Q_future = product_(all remaining e) F_e.

U_e,V_e are even quadratic expressions. They commute. The local
division-free identity inherited from n66 is

    h_e F_e - (h_e-b_e U_e)(h_e-a_e V_e) = U_e V_e.

Any transport from the original port contraction to a sequence of these
local charts needs its ordering, denominators, and semantics proved. This
blueprint does not infer that every future synchronized state is Gaussian.

For the processed product P_t, define exact unnormalized moments

    M_t(I) = L_A(theta_I P_t),
    M_t(I;W) = L_A(theta_I W P_t).

Applying the next factor gives an exact linear expression in moment values:

    M_(t+1)(I)
      = h_e M_t(I) - b_e M_t(I;U_e) - a_e M_t(I;V_e)
        + M_t(I;U_e V_e).                                  (M)

This specifies actual scalar additions and multiplications once all
referenced moments and coefficients are available. It does not treat the
functional L_A or an exterior derivative as a scalar gate.

For an explicit coefficient version write

    U_e = sum_(p<q) U_(pq) theta_p theta_q,
    V_e = sum_(r<s) V_(rs) theta_r theta_s.

Replace M_t(I;U_e) by sum U_(pq) epsilon(I,p,q) M_t(sort(I,p,q)),
where epsilon is zero for a repeated index and otherwise the sign of the
sorting permutation. The V expression is identical with V coefficients.
The UV expression uses U_(pq)V_(rs) epsilon(I,p,q,r,s) and moments indexed
by the sorted union. Thus all multiplication and ordering signs are
explicit. If H=binom(d,2), a direct scalar transition of one moment has
at most 4H^2+6H+10 gates, including coefficient products, sign multipliers,
the two outer scalar weights and h_e. For H>=1, the padded no-fold count
is 4H^2+6H+7: each quadratic sum costs 3H-1 (coefficient times moment,
sorting sign, binary sum), the quartic sum costs 4H^2-1 (coefficient
product, moment product, sorting sign, binary sum), and the four outer
terms plus h_e cost 10. For H=0 the bound 10 still suffices. These are
source-derived counts of the displayed expression, not measured DAG data
or a Lean theorem. This is a conditional upper bound
for THIS expression with its moment inputs supplied, not a compiler cost
for those inputs. Constants are only the displayed input scalars and
0,+1,-1. The general chart-construction cost remains a separate obligation.

An initial Gaussian would supply M_0(I) as its charged small Pfaffians for
small |I|. Defining instead M_0(I)=L_A(theta_I Q_future) would already
contain the unsolved full contextual contraction, and is not a lawful
cheap initialization. In the forward definition above M_t becomes a
contextual moment after the first processed factor; bare Gaussian Wick
formulas no longer automatically apply to it.

The proposed degree-0/2/4 state fails to be a demonstrated closed state:
(M) asks for degrees 6 and 8 at its degree-four boundary. The exact missing
positive lemma is a polynomial scalar formula for those contextual moments
from the retained state, valid with every future factor and its derivatives
present. This is a missing lemma, not an impossibility statement.

In integration by parts, for every odd coordinate theta_i one must retain

    partial_i Q_future
      = sum_e (partial_i F_e) product_(f != e) F_f,
    partial_i F_e
      = -b_e partial_i U_e - a_e partial_i V_e
        + (partial_i U_e) V_e + U_e (partial_i V_e).

The exact Ward relation is

    L_A(partial_i Q + (sum_j A_ij theta_j) Q) = 0.

All terms of the displayed derivative of Q_future must be charged or
represented by an actually closed state. Dropping them changes the target.
The new contextual row reduction does not prove their closure.

## Candidate 2: row and column paired square-zero occupation states

This candidate considers a precisely specified reduced algebra. Its
generators xi_i and eta_j are **PAIRS OF ODD GENERATORS**, for example

    xi_i = alpha_i wedge beta_i,    eta_j = rho_j wedge sigma_j,

in a fixed ordered exterior algebra with independent underlying modes.
They have even degree, commute with each other, and satisfy xi_i^2=0 and
eta_j^2=0. Equivalently the prototype algebra is

    Q[xi_1,...,xi_n,eta_1,...,eta_n] / (xi_i^2, eta_j^2).

There is no unaccounted Grassmann ordering sign in the following update,
because these named generators are commuting EVEN pairs. Arbitrary signs
needed to identify them with original ports have not been discarded;
they belong to the missing transport theorem below.

For explicit weights w_e consider the structured prototype product

    W_t = product_(processed e=(i,j)) (1+w_e xi_i eta_j)
        = sum_(I,J) q_t(I,J) xi_I eta_J.

Initialize q_0(empty,empty)=1 and every other coefficient to zero. Retain
the entire processed product and the entire future factor list. Multiplying
the next factor gives the exact scalar transition

    q_(t+1)(I,J) = q_t(I,J) + w_e q_t(I\{i},J\{j})
                  if i in I and j in J,
    q_(t+1)(I,J) = q_t(I,J) otherwise.                       (O)

Each changed coefficient costs one multiplication and one addition. No
unknown target appears in its initialization. Only |I|=|J| coordinates
are needed for this prototype. Keeping all such coordinates requires

    sum_k binom(n,k)^2 = binom(2n,n)

scalar state values; a straightforward no-fold update of a single edge
costs 2 binom(2n-2,n-1) gates. These are exact costs of this reference
state, not lower bounds on another representation. No reference state is
executed here, and no n18 occupation validation is repeated as n68 evidence.

For n=2,3,4,5 the derived state sizes are 6,20,70,252 and the derived
per-edge update counts are 4,12,40,140; executing every one of n^2
factors without folding would give 16,108,640,3500 gates. These formulas
are analytical reference counts, without an executed DAG or formal audit.

This gives a real conditional scalar interface, but it is not the promised
polynomial-dimensional closure. Three separate obligations remain:

1. Prove an actual target-preserving transport from the original two
   bordered Pfaffian families and all synchronization factors to the
   paired commuting algebra, using the reduced row/column incidences.
2. Prove all orientation signs and any chart data costs for that transport.
3. Construct a polynomial-size aggregation of (O), with a charged boundary
   computing the required top occupation coefficient or equivalent
   contraction. The coefficient extraction itself is not a gate.

It is insufficient to use the large occupation state as an unnamed input,
to call its terminal top coefficient already known, or to assert that
rank n makes all mixed moments costless.

## Compact generators retain the same missing diagonal contraction

On a generic invertible B chart write Y=B^-1. For edges e,f, the direct
bordered determinant update uses

    Ldirect_(e,f) = b_f Y_(col(e),row(f)).

The row-weighted version L_(e,f)=b_e Y_(col(e),row(f)) has the same
principal minors: both determinant expressions have the common factor
product_(e in S) b_e. No division by a marked b_e is needed to transfer
these weights in a principal determinant. With

    Q_S = (-1)^(sum I+sum J) sign(tau_S) b_S det B[I^c,J^c],

the chart identity is det(B) det(L[S,S])=Q_S for compatible S. Thus
det(B) det(I-diag(x)L) has coefficient (-1)^|S| Q_S.
The F family coefficient is gamma_n times this expression. Inverse and
determinant construction costs, and extension off the chart, must be charged.

The same generator is division-free: det(B-B circ X), where
(B circ X)_ij=b_ij*x_ij, equals det(B)det(I-diag(x)L) on the chart and
extends the polynomial to every B, including singular B. A polynomial
scalar DAG for this auxiliary-variable determinant can use the inherited
constant-division determinant recurrence; the final coefficient-wise
contraction with G is still uncompiled in Q[z].

For the G family, put x_e on the diagonal at a_e and 1 at b_e and the
dummy ports, calling that diagonal matrix D_x. Let J_e be the local
standard skew block on the adjacent real pair a_e,b_e. Then the informal
principal-Pfaffian generator identity is

    [x_S] Pf(D_x Krow D_x + sum_e J_e) = Grow_(ports(S)).

Selecting J_e removes the entire complementary adjacent pair. Its shuffle
sign is even, while each selected a port contributes one x_e by the
congruence. For compatible S the contextual quotient identifies this
coefficient with (-1)^|S| c(S). The dummy pair is always retained. The
fixed port order is necessary to this coefficient statement.

Both families consequently have compact determinants or Pfaffians at each
requested x, but the target remains their **coefficient-wise contraction**,
not their ordinary product or evaluation at x=1. The singular block order,
orientation and scalar costs cannot be hidden in that contraction. These
generator identities are informal supporting reductions, not scored new
experiments or a polynomial extractor.

## Frozen outcome

Two analytical candidates were considered. Neither supplies all initial
data, a polynomial-dimensional closed transition, and the target boundary.
The development score is null; no complete root obligation is discharged.
No SymPy checks, numerical samples, Lean compiler invocation, B_test read,
counterexample search, or lower-bound experiment was executed in n68.
No new formal allocation is requested in this window. The contextual
quotient, full-context moment equations and paired occupation interface
are retained as explicit constructive obligations for a later node.
