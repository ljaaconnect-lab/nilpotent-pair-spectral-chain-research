# Cycle 2 / n6: edge messages, nonbacktracking determinants, and Good

## Status

Two concrete scalar-jet formulas were constructed and tested. Both retain
the original edge amplitudes and phases, use polynomially many series
states, and avoid listing simple cycles. Neither is a general exact
compiler of the required table, so this node has **no development score**.
The previously verified exponential `candidate.py` is unchanged; its 1912
gate score is not assigned to these partial constructions.

The positive results are:

* an exact Bass/Schur factorization on arbitrary matrices, including every
  Gaussian loop, with O(n^2) cavity states;
* a determinant formula exact on every graph whose underlying undirected
  components are trees or unicyclic graphs, including arbitrary directed
  weights, diagonal entries, attachments and spectral phases;
* an implementable exact degree-six repair for the two proposed readings
  when the diagonal is zero, using the previously proved occupation
  identities, with no permanent oracle.

The missing invariant is identified by explicit overlapping-cycle terms.
There is no inference here that another edge-state closure is impossible.

## 1. Conventions and the weighted Bass determinant

At frequency f, replace B_ij by B_ij xi_j, where
B_ij=p_ij z^(2^(in+j)) and xi_j=omega^(f d_j). All statements below are
formal polynomial identities in these entries. Truncate in t at the
requested terminal degree. The final coefficient is taken from the
explicitly computed scalar jet; there is no free coefficient reader.

For directed edge weights u_ij with zero constant coefficient, let
T(u)_(i,j),(j,k)=u_jk for k!=i, and zero otherwise. The n(n-1) states are
present even when an input entry happens to vanish. Define

    D(u)=det(I-T(u)),
    P_ij=u_ij u_ji,
    L_ii=1+sum_(j!=i) P_ij/(1-P_ij),
    L_ij=-u_ij/(1-P_ij).

Weighted Ihara–Bass gives

    D(u)=prod_(i<j)(1-P_ij) det L.                            (1)

One can obtain (1) by writing the edge transition as the incidence
product minus edge reversal, eliminating the independent two-by-two
reversal blocks, and applying det(I-AB)=det(I-BA). This is a reduction to
an n-by-n matrix, not a determinant of an exponentially large operator.
The implementation checks it against the full edge-state determinant on
an asymmetric three-vertex example.

For context, the weighted Bass reduction and its relation to Gaussian
or Bethe loop determinants are established in
[Watanabe–Fukumizu, Graph Zeta Function in the Bethe Free Energy and Loopy
Belief Propagation](https://proceedings.neurips.cc/paper_files/paper/2009/file/b6f0479ae87d244975439c6124592772-Paper.pdf).
The separate exact permanent loop-series identity in
[Watanabe–Chertkov, Belief propagation and loop calculus for the permanent](https://arxiv.org/pdf/0911.1419)
uses an **average** of nonbacktracking determinants. A single determinant
is not asserted there to remove the paired-edge projection. We do not
use that average as an uncharged operation. The formulas and tests below
are explicit alternative constructions, not an invocation of that oracle.

All divisions in (1) are unit-series inversions. With degree K, the
coefficient recurrence v_0=1,
v_m=-sum_(j=1..m)a_j v_(m-j) uses ordinary scalar gates. Determinants use
unit-pivot series Gaussian elimination. A square root below always means
the unit root obtained by

    s_0=1, s_m=(a_m-sum_(j=1..m-1)s_j s_(m-j))/2.              (2)

It introduces no square root or inverse of an input scalar.

## 2. Formula one: matching messages and two determinant corrections

Let d_i=1+t B_ii and a_ij=t^2 B_ij B_ji. Compute the formal cavity messages

    h_(i->j)=1/(d_i+sum_(k!=i,j)a_ik h_(k->i)),
    Z_M=prod_i(d_i+sum_(j!=i)a_ij h_(j->i))
             /prod_(i<j)(1+a_ij h_(i->j)h_(j->i)),
    q_ij=a_ij h_(i->j)h_(j->i),
    u_ij=t B_ij h_(j->i).                                    (3)

These messages have constant coefficient one. K+1 parallel iterations
from one fix all coefficients through degree K. For edge arrays, define

    Psi(u)=D(u^(Hadamard 2))/D(u).

The concrete proposed output series is

    H_1=Z_M [Psi(u)-sqrt(Psi(q))+sqrt(Psi(-q))].               (4)

The subtraction and final square-root term are essential. The first
quotient counts both orientations of a long cycle, while the other terms
replace their joint contribution by the correct matching-loop parity.
This is a new determinant correction to edge messages, not the previously
refuted cycle-incidence BP formula.

### Exact invariant on trees and unicyclic supports

On a tree the nonbacktracking matrices have no closed walks, so all D and
Psi factors are one. Equation (4) reduces to Z_M, the exact matching
partition, which is per(I+tB) on that support.

For a single undirected cycle of length h>=3, let c_+ and c_- be its two
directed activities (each includes t^h), and let A=prod_edges a_ij=c_+c_-.
Let lambda be the formal unit eigenvalue of the two-by-two matching
transfer product. The cavity equations give

    Z_M=lambda,
    prod_cycle h_(i->previous)=1/lambda

in either direction. The transfer trace is the exact matching partition
Z_match, and its determinant is (-1)^h A. Thus

    Z_match=lambda+(-1)^h A/lambda.

The only primitive nonbacktracking cycles are the two orientations. Their
weights in u are c_+/lambda and c_-/lambda. The q-cycle weight is
A/lambda^2. Substitution into (4) yields exactly

    H_1=lambda+c_++c_-+(-1)^h A/lambda
       =Z_match+c_++c_-=per(I+tB).                            (5)

Arbitrary diagonal entries are already included in the monomer factors
d_i. Trees attached to the cycle can be eliminated using their unit
monomer messages. This multiplies the partition by their local factors
and changes the cycle's monomer weights; the same proof then applies.
Disconnected components factor independently. No cycles need to be
enumerated by the evaluation algorithm for this theorem to hold.

The tests cover asymmetric triangles, a bidirected square with diagonal
entries, a weighted tree, and a directed 2+3 bouquet. The last support is
unicyclic as an undirected graph, so (5) explains its exactness. Mixed
column phases [-2,3,5] are checked independently.

### Overlap terms and the degree-six correction

For a directed bouquet of cycles of lengths at least three with no reverse
edges, the matching messages are one. Let s_C be the individual cycle
activities and S=sum_C s_C. Since at most one such cycle can be selected,

    Q_B=1-S,    Q_(B Hadamard 2)=1-sum_C s_C^2,
    H_1=(1-sum_C s_C^2)/(1-S)
       =1+S+2 sum_(C<D)s_C s_D/(1-S).                        (6)

The desired output is 1+S. Thus the nonbacktracking determinant has an
explicit unwanted interaction, even though no immediate backtracking
exists. Two triangles of weights c=10 and d=21 give 420 t^6.

For zero diagonal, the full first error is a matrix contraction. Put
A_ij=B_ij B_ji and e_ij=B_ij(B^2)_ji. Then

    E_6^(1)=sum_i ((B^3)_ii)^2 -sum_(i,j)e_ij^2
              -2sum_(i,j)e_ij e_ji +tr(A^3).                 (7)

One way to derive (7) is to classify the balanced edge multisets of total
degree at most six. Single cycles, unions of dimers, and a dimer with a
long cycle are accounted for by (5), factorization, or the two triangles
sharing an antiparallel chord. The surviving errors are pairs of directed
triangles that share one vertex or a common edge in the same direction;
each has coefficient 2. Identical cycles and reverse pairs do not survive.
The first term of (7) counts ordered pairs by shared vertices. The next
two terms correct same-direction and opposite-direction shared edges;
tr(A^3) restores the over-subtracted reverse triangle pairs. This gives
exactly the stated surviving cases.

Consequently H_1 exp(-E_6^(1)t^6) is exact through degree six on loopless
matrices of every size. This agrees with the prior universal R6 invariant;
it does not discard mixed occupations or phases. Generic positive
asymmetric matrices of sizes 3, 4 and 5 verify the contraction.

For an implementation that does not rely on the simplified expression
(7), `repair_degree_six` computes the exact sixth coefficient from the
previously proved identity

    P_6=[t^6]G_B+K_6-R_6,

then multiplies by exp((P_6-[t^6]H)t^6). All three terms are computed by
explicit scalar jets or matrix products; P_6 here denotes the derived
degree-six expression, not an input or oracle. This repair is fixed-degree
and does not claim a uniform all-degree recurrence.

An all-order repair of (6) alone is the scalar ratio
(1-S^2)/(1-sum s_C^2), giving 1+S. On a support known to have no two
vertex-disjoint cycles, this can also be written using 2-Q_B, without
listing cycles. Applying the same replacement to a general determinant
changes the signs of disjoint-cycle configurations. It therefore does
not supply a general dense-matrix invariant.

## 3. An exact Gaussian Bass/Schur identity on every graph

This identity is fully general, including diagonal terms. Let

    d_i=1-x_i B_ii,
    v_ij=x_i x_j B_ij B_ji,
    h_(i->j)=1/(d_i-sum_(k!=i,j)v_ik h_(k->i)),
    g_i=1/(d_i-sum_(k!=i)v_ik h_(k->i)),
    q_ij=v_ij h_(i->j)h_(j->i),
    u_ij=x_i B_ij h_(j->i),
    Q_Bethe=1/(prod_i g_i prod_(i<j)(1-q_ij)).                (8)

Then the exact formal identity is

    det(I-XB)=Q_Bethe D(u).                                  (9)

For completeness, the cavity equations imply
h_(i->j)=(1-q_ij)g_i. In the reduced Bass matrix of (1), therefore,

    L_ij=-x_i B_ij g_j,
    L_ii=1+sum_j q_ij/(1-q_ij)=d_i g_i.

Thus L=(I-XB)diag(g), and substitution into (1) proves (9) directly.
The proof charges every inverse, message and determinant. It does not
use a sum over cycles. Four exact jet tests include dense asymmetric
matrices, diagonals and mixed vertex phases.

Equation (9) resums all Gaussian loops, not only the first correction.
It also states why applying it alone cannot change the original Good
occupation invariant: fully correcting the Gaussian determinant and its
derivatives recovers the same Q_B and diagonal resolvent used in Good.
The missing step is an additional, non-Gaussian cancellation of repeated
vertex occupancies, not a missing implementation of the Bass determinant.

## 4. Formula two: Good with a cavity-density replacement

A second explicit formula tries to combine the useful parts of these
representations. From (8), use w_i=x_i g_i, but retain Q_Bethe rather than
the fully loop-corrected Q. Let J be its exact ordinary Jacobian, including
the derivatives of the cavity messages. Define

    G_GB(w)=Q_Bethe(x(w))^(-1) prod_i g_i(x(w))^2/det J.

The derivatives are computed by an affine fixed-point recurrence. For
example,

    d h_(i->j)/d x_l = h_(i->j)^2 [delta_il B_ii
       +sum_(k!=i,j)B_ik B_ki ((delta_il x_k+x_i delta_kl)h_(k->i)
                                +x_i x_k d h_(k->i)/d x_l)].

There are O(n^3) derivative series. All feedback coefficients have positive
t-order, so a finite number of iterations computes the truncated jet.

Use the universal beta constants of the previous node, but replace
ordinary closed walks by nonbacktracking walks:

    K_NB(t)=sum_(h*r<=n,r>=2) beta_(h,r)
                          tr(T(B^(Hadamard r))^h) t^(h*r).

The traces themselves are evaluated with Bass, using
tr(T^h)=-h[t^h]log D(t), so no n^2-by-n^2 dense matrix is needed.
The second concrete reading is

    H_2=G_B (Z_M/G_GB) exp K_NB.                              (10)

It is exact on every bidirected forest, including diagonals: the Gaussian
cavity determinant and its Good density are then exact, so G_B/G_GB=1,
all nonbacktracking traces vanish, and Z_M is exact. On an isolated
directed cycle with no reciprocal edges, the ratio is one and the prior
trace normalization gives the exact cycle polynomial.

However, the new coupling does not give the general invariant. On the
asymmetric triangle with rows (0,2,3), (5,0,7), (11,13,0), the target is
1+134t^2+349t^3, while (10) has an additional 240240t^6. Its first error
on the 2+3 bouquet is 60t^7. On a 3+3 directed bouquet with cycle weights
c,d, the first mixed error is 2cd(c+d)t^9; at c=10,d=21 it is 13020t^9.
For example this last identity follows by expanding the prior exact
bouquet formula: G=1+c+d+c^2+d^2-10(c^3+d^3)+3cd(c+d)+...;
the isolated-cycle exponent removes the pure terms and leaves 2cd(c+d).

On loopless dense test matrices the sixth residual simplifies to
(4/3)tr(A^3). This simplification is checked in the saved experiments;
the implementation's exact repair uses the already proved P6 expression
above, so it does not depend on promoting these finite checks into an
all-order theorem. The repaired formula still has the degree-seven and
degree-nine witnesses just given.

## 5. Scalar costs, full-chain interpretation, and verification

For terminal degree n, every series has n+1 scalar coefficients. Equation
(4) uses O(n^2) message and matrix series; its direct implementation costs
O(n^6) scalar gates with naive convolutions and message summation.
Sharing the vertex sums lowers the message portion, but is not needed
for the stated bound. Bass determinants cost O(n^5) each. Equations
(8)-(10) use O(n^3) series, dominated by the Jacobian derivative messages,
and the implemented recurrences admit an O(n^7) scalar bound.
The ordinary Good determinant is evaluated by unit-pivot elimination in
`scalar_schur_good`; the factorial determinant in the old helper is used
only as a small independent verifier.

Preparing the marked entries costs O(n^2) gates. Running N=O(n) phase
readings therefore gives bounds O(n^7) and O(n^8), respectively, plus
the charged inverse transform. Rational constants are small integers,
the unit-root factor 1/2, and the polynomial-bit beta constants already
constructed by recurrence. All terminal reading work is included.
These are bounds for the proposed readings, not bounds for a correct
general compiler.

Replacing B by B diag(xi) throughout each recurrence attaches exactly
the original column phase to each edge occurrence. Reciprocal products,
Hadamard powers, derivatives and determinant terms retain the resulting
occupation phases. There is no amplitude input or unmarked substitution.
The legal dense specialization B=J6, z=1, labels all zero gives H_1's
terminal coefficient **1800**, versus **720**. Thus its complete inverse
spectral table is wrong, independently of any sparse witness. Formula
two also fails on dense legal input: its terminal coefficient on J5 is
**60**, versus **120**. These specializations test the actual final degree.

Run `python nonbacktracking_research.py` for the saved exact report
`nonbacktracking_verification.json`. It checks the two explicit formulas,
the independent Bass determinant reduction, the exact Gaussian identity,
generic degree-six repairs, asymmetric unicyclic cases, and phases.
The frozen evaluator was not modified or used to score an incorrect
partial formula. No held-out protocol was accessed.

The remaining closure must cancel interactions such as (6) and the mixed
terms of (10), while preserving disjoint-cycle products, using a fixed
polynomial number of scalar states. The exact Bass identity supplies
this closure for Gaussian walks; neither of the two constructed
determinant corrections supplies it for the oriented terminal reading.
