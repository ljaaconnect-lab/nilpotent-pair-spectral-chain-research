# Joint Schur–Good normalization, phases, and cycle interactions

## Result and executable status

This node studies the whole chain from the original `p`, `z`, and supplied
root of unity to **every** inverse-transform slot. It imposes no interface
that would require a permanent amplitude before the spectral computation.

There is an exact new polynomial correction for every disjoint union of
directed cycles, and a further exact closure for arbitrary bouquets and
forests of cycle blocks. There is also a universal, explicitly contracted
degree-six interaction correction for matrices with zero diagonal. These
are constructive identities with ordinary scalar implementations.
They do **not** yet give a uniform polynomial compiler for dense matrices.
The direct extension of the block messages to cyclic incidence fails.

The executable `candidate.py` is consequently an exact exponential reference,
with the redundant spectral tail folded by character orthogonality. The
frozen development evaluator reports **1912 scalar gates at n=8**, after 84
numeric and 8 formal marked-polynomial full-table checks. This score is not
evidence of a polynomial bound for the normalization hypothesis.

No held-out protocol was read or run. `dag.py` and `evaluate_dev.py` are
unchanged. The earlier worktree was only read; `schur_jet_helper.py` is a
local copy of its independent rational-jet verifier.

## 1. Formal change of variables and scalar implementation

Put X=diag(x), Q=det(I-XB), F=Q^(-1), R=(I-XB)^(-1), and

    g_i=R_ii=Q_[n]\{i}/Q,          w_i=x_i g_i(x).

The formal inverse x(w) exists because the linear part is the identity.
The ordinary Jacobian is

    J_ij=delta_ij g_i+x_i R_ij (BR)_ji.

Define the transformed density, including its exact Jacobian,

    G_B(w)=F_B(x(w)) prod_i g_i(x(w))^2 / det J(x(w)).             (1)

Formal substitution in the coefficient residue proves, for every
occupation vector m, the invariant

    [w^m]G_B = [x^m] F_B prod_i g_i^(1-m_i).                     (2)

For support S of size k, write Q_S=det(I-X_S B_SS). Setting all other
variables to zero in (2) gives

    [w^m]G_B = [x^m] Q_S^(|m|-k-1)
                         prod_(i in S) Q_(S\{i})^(1-m_i).       (3)

Thus all squarefree coefficients are their principal permanents. If only
one positive coordinate, i, repeats, with m_i=r>=2, the expression is
Q_S^(r-2)/Q_(S\{i})^(r-1); its degree in x_i is at most r-2. Every such
collision is exactly zero, in every degree and for every matrix.

Equation (1) is not left as a coefficient oracle. For w_i=t xi_i, truncate
all series modulo t^(n+1). Start x_i=t xi_i and repeat
x_i <- t xi_i/g_i(x) n times. Each iteration fixes one more coefficient.
The required resolvent is computed by the scalar recurrence

    R_0=I,
    R_m=sum_(a=1..m) diag(x_a) B R_(m-a).

A unit-series inverse uses v_0=1 and v_m=-sum_(j=1..m)u_j v_(m-j).
Both determinant matrices have identity constant coefficient, so ordinary
series Gaussian elimination has unit pivots. No inverse of a data value
is used. Naive jet convolutions give O(n^6) scalar gates for one reading,
including the fixed-point iterations, Jacobian and terminal coefficient.
All required constants are rational of polynomial bit length.

This is a polynomial compiler for **G's proposed reading**; (3) determines
precisely which extra terms keep it from being the desired output.

## 2. Spectral covariance concerns the whole chain

For diagonal Xi=diag(xi_i), Sylvester's identity and the diagonal cofactors
give Q_(B Xi)(x)=Q_B(Xi x) and g_(B Xi),i(x)=g_B,i(Xi x). Hence

    G_(B Xi)(w)=G_B(Xi w).                                      (4)

The proof first works for invertible Xi and then extends as a polynomial
identity to zero phases. It also follows directly by conjugating the
Jacobian. Therefore the coupled frequency reading

    Y_f=[t^n] G_B(t omega^(f d_1),...,t omega^(f d_n))

assigns phase omega^(f d.m) to occupation m. Its inverse transform selects
the congruence class d.m modulo N. This is a derivation of the actual
joint program, not an assumption that an amplitude precedes the transform.

Preparing B_ij=p_ij z^(2^(in+j)) takes O(n^2) scalar gates by repeated
squaring. Preparing all N=O(n) phase readings and evaluating (1) has an
O(n^7) bound, plus the ordinary O(N log N) transform. This bound only
becomes a solution if the collision corrections are complete.

Two elementary spectral tests show why labels alone do not complete (1).
The Sidon set [0,1,4,10,12,17] has distinct unordered pair sums, yet the
triples {0,10,12} and {1,4,17} have the same sum 22. A doubled directed
triangle on the first triple survives (3), with coefficient 1, and aliases
the desired all-ones occupation. Similarly {0,3,5,6} and {1,2,4,7} have
equal cardinality, sums and sums of squares; a doubled four-cycle survives
with coefficient 3. More generally the parity partition of
0,...,2^(s+1)-1 equalizes moments 0 through s. For s>=2 the relevant doubled
cycle coefficient is nonzero. These examples concern these label models,
not arbitrary frequency-dependent implicit changes.

## 3. Exact isolated-cycle correction using Hadamard traces

Suppose B is a directed cycle of length h and edge product c. Write
s=prod_i w_i. Its density has the scalar parametrization

    r=c s (1-r)^h,
    G_h=1/((1+(h-1)r)(1-r)^h).

More directly, (3) proves the exact coefficient formula

    [s^l]G_h = c^l (-1)^l binom(h(l-1)-1,l).                    (5)

In particular the doubled cycle has coefficient (h-1)(h-2)c^2/2.
Thus removing diagonal entries or merely subdividing cycles does not
annihilate all repeated occupancies.

Define universal rational numbers, for h*r<=n and r>=2,

    g_(h,l)=(-1)^l binom(h(l-1)-1,l),
    L_(h,r)=[s^r] log((1+s)/(sum_(l>=0) g_(h,l) s^l)),
    beta_(h,r)=L_(h,r)/h
       -sum_(d|r, d>1, r/d>=2) beta_(h*d,r/d).                  (6)

The recursion is ordered by increasing r. Its right-hand indices have
smaller second coordinate, so (6) is an actual finite scalar compilation
of constants, not an implicit coefficient specification. Logarithms of
unit series can be computed by

    ell_m=f_m-(1/m)sum_(j=1..m-1) j ell_j f_(m-j).

Set, retaining all multidegrees,

    K_B(w)=sum_(h*r<=n, r>=2)
           beta_(h,r) tr((diag(w_i^r) B^(Hadamard r))^h).       (7)

On a cycle of length k, the trace vanishes unless k divides h; when it
does not vanish it equals k*c^(h*r/k)*(prod w_i)^(h*r/k).
Consequently the coefficient of s^l in (7) is
k*sum_(d|l,l/d>=2)beta_(k*d,l/d), exactly L_(k,l) by (6). It follows that

    G_B(w) exp K_B(w) = 1+c prod_i w_i  modulo degree n+1       (8)

for every directed cycle. Block factorization and trace additivity prove
(8), with the corresponding product on the right, for any disjoint union
of cycles. Edges between such strongly connected components cannot occur
in a closed walk or a cycle cover, so they do not change this conclusion.

The trace construction is an ordinary scalar computation. Reuse entrywise
powers; for each r multiply the n-by-n matrix successively through power
floor(n/r). The resulting trace cost is O(n^4 log n); scalar series
exponentiation adds O(n^2). The constants in (6) have polynomial bit
length: binomial numerators have O(n log n) bits, log coefficients can be
formed with denominator dividing n! and O(n^2 log n) numerator bits, and
the divisor recursion increases this by at most a polynomial factor.
An O(n^3 log n) bound on literal bit lengths is more than sufficient.
The construction commutes with (4), since each closed-walk monomial
contains its original vertex phases with its full multiplicities.

The first nonzero correction is

    K_6= -tr(B^(Hadamard 6))/6
          +tr((B^(Hadamard 3))^2)/2
          -tr((B^(Hadamard 2))^3)/3.                           (9)

The verifier checks 54 isolated-cycle examples through degree 18 and a
mixed disjoint union. This correction changes lower-degree interactions
and therefore lies outside the restricted linear-reading bound in §7.

## 4. First overlap interaction: a universal matrix contraction

Assume only in this section that B has zero diagonal. Put

    A_ij=B_ij B_ji,   r=A*1,   s_i=sum_j A_ij^2.

All coefficients of G_B(t*1) below degree six already equal those of
per(I+tB). At degree six, the residual after the pure-cycle correction
(9) is exactly

    R_6 = 2 sum_i r_i s_i - (3/2)sum_(i,j) A_ij^3
          +tr(A^3) -(1/2)r^T A r.                            (10)

Thus replacing K_6 by K_6-R_6 corrects this degree for every matrix size,
with O(n^3) scalar work. It is not a fit to all-ones matrices.
For arbitrary vertex weights apply (10) to B'=diag(xi)B; every monomial
has exactly its proper phase and mixed occupation degree.

Here is a proof by the complete list of nonzero collision types. Single
repetitions vanish by (3). Let a_ij=B_ij B_ji and
d_ijk=B_ij B_jk B_ki+B_ik B_kj B_ji. Formula (3) gives:

| Occupation on its support | Coefficient |
| --- | --- |
| (3,3) on i,j | -a_ij^3 |
| (4,2) on i,j | 0 |
| (3,2,1) on i,j,k | a_ij^2 a_ik |
| (2,2,2) on i,j,k | d_ijk^2+a_ij a_ik a_jk |
| (2,2,1,1), repeats i,j | -a_ij(a_ik a_jl+a_il a_jk) |

These identities are independently verified symbolically in
`verify_residue6.py`, with generic cycle coefficients and no numerical
specialization. Since the product of the two directed triangle weights
is a_ij a_ik a_jk, (9) removes the pure squares in d_ijk^2 and all isolated
(3,3) terms. The remaining sum is

    sum_(i;j!=k) a_ij^2 a_ik
      +3 sum_(i<j<k) a_ij a_ik a_jk
      -sum_(i<j;k<l outside i,j) a_ij(a_ik a_jl+a_il a_jk).

Expanding r^T A r turns this expression into (10). In particular a
bidirected two-edge star with cycle weights a,b has G's degree-six
coefficient -a^3-b^3+a^2 b+a b^2. Correcting isolated cycles leaves
a^2 b+a b^2, equal to 30 at a=2,b=3. A fully bidirected triangle with unit
weights leaves 9. These are genuine overlapping-cycle interactions.

Zero diagonal is a structural assumption, not an allowed simplification
of arbitrary legal inputs. Generic diagonal corrections from the prior
node, c4 and c5, do not close this gap: on the legal dense matrix J6,
the coefficient after exp(c4 t^4+c5 t^5+K_6 t^6) is **205**, versus 720.
With zero labels, this is directly a wrong full inverse-transform table.

## 5. Exact all-order closure for bouquets

Let the simple directed cycles C_i share a common vertex and otherwise
have disjoint vertices. They may have arbitrary lengths h_i and arbitrary
marked activities

    s_i=(prod_(e in C_i) B_e)(prod_(v in C_i)w_v).

A loop at the common vertex is allowed. Write u_i for the corresponding
x-activity, Q=1-sum_i u_i, and r_i=u_i/Q. Then the Schur change of
variables has the **decoupled** scalar equations

    s_i=r_i(1+r_i)^(h_i-1).                                   (11)

At the common vertex g=1+sum r_i; at every other vertex in C_i, g=1+r_i.
Changing logarithmic coordinates to the common vertex and the u_i shows
that the logarithmic Jacobian determinant is

    (1+sum r_i) prod_i (1+h_i r_i)/(1+r_i).

Inserting it in (1) proves

    G_B(w)=(1+sum r_i) prod_i (1+r_i)^h_i/(1+h_i r_i).          (12)

Consequently the exact correction is

    C_B(w)=(1+sum s_i)/(1+sum r_i)
              prod_i (1+h_i r_i)/(1+r_i)^h_i,                 (13)
    G_B C_B=1+sum s_i=per(I+diag(w)B).

Equations (11)-(13) are closed scalar recurrences at every degree. They
preserve mixed terms, including interactions between cycles of unequal
length and phase. For univariate degree-n jets, n fixed-point steps in
(11), unit-series inverses and products cost O(n^4) by naive convolution;
all h_i sum to O(n). No coefficient of a multivariate diagonal is read.

Tests compare (12) to the full independent Jacobian construction on a
weighted 2+2 bouquet, a 2+3 bouquet, and a loop+2+2 bouquet through degree
eight, including nonconstant vertex phases. In the 2+3 example, G has
terms 217 t^6+60 t^7+1430 t^8, all removed correctly by (13).

## 6. Closure for forests of cycle blocks, and the next obstruction

The bouquet rule extends to a fixed support graph whose incidence graph
of vertices and all simple directed cycles is a forest. Every cycle
activity s_C retains all B entries, t degrees and phases. Root this
bipartite forest at a vertex. For vertex v, let F_v be the partition
series with v available to its parent cycle and G_v the unrestricted
series. For a child cycle C, with its other vertices u, set

    A_C=prod_u G_u,                 B_C=s_C prod_u F_u,
    F_v=prod_C A_C,
    G_v=F_v+sum_C B_C prod_(D!=C) A_D.                         (14)

Leaves have F_v=G_v=1. A cycle is selected or unselected, and at most one
selected child cycle uses v. This proves (14) and the terminal invariant
G_root=per(I+diag(w)B). Prefix/suffix products evaluate every sum without
division. Such a forest has O(n) incidence edges, so truncated scalar
evaluation costs O(n^3). If one specifically wants a normalized Schur
program, multiply (1) by G_root/G_B, a unit-series ratio; the total cost
is still polynomial. This structural result is stronger than disjoint
cycles or one bouquet, but it assumes a known fixed support pattern.
It does not branch on whether an arbitrary input entry is zero.

The natural attempt at a general closure is to use the same messages on
a cyclic incidence graph. With m_(v->C) an availability ratio and
u_(C->v) the selected-cycle ratio, its fixed-point equations are

    u_(C->v)=s_C prod_(w in C\{v})m_(w->C),
    m_(v->C)=1/(1+sum_(D contains v,D!=C)u_(D->v)).             (15)

All inverses are unit series; degree-n jets stabilize after n+1 rounds.
The usual product assembled from these local factors is

    Z_messages = prod_v(1+sum_C u_(C->v))
                 prod_C(1+s_C prod_v m_(v->C))
                 /prod_(v in C)(1+u_(C->v)m_(v->C)).          (16)

It agrees with (14) on forests. It does not extend the invariant to all
graphs: on the unit bidirected triangle, list its three two-cycles and
two directed three-cycles. Equation (16) gives

    1+3t^2+2t^3-6t^5-t^6+24t^7+27t^8+O(t^9),

whereas the exact result is 1+3t^2+2t^3. This counterexample includes every
simple cycle, so it is not caused by omitting an isolated-cycle activity.

There is a complete exact continuation in terms of connected clusters of
overlapping cycles, but the explicit continuation has no polynomial cost
bound. To make the gap precise, let H be the incompatibility graph on
simple directed cycles, with an edge for a shared vertex. Then

    Z=sum_(independent sets I in H) prod_(C in I)s_C,
    Z(T)=Z(T\{C})+s_C Z(T\({C} union N(C))).                  (17)

The logarithm is the connected-cluster expansion: for each ordered tuple
of cycles, sum (-1)^(number of edges) over connected spanning subgraphs
of its incompatibility graph, divide by the tuple-length factorial, and
multiply its activities. Thus log Z-log G is an exact full correction.
Equation (7) resums repeated isolated cycles; (13) resums all cliques
arising from one common vertex; (14) resums incidence forests. The first
additional local terms include (10). However explicitly forming all
simple cycles is already factorial on a dense directed graph, and (17)
adds subset states. For a fixed degree d, motif contraction gives bounds
such as n^d; the exponent grows with the requested terminal degree. These
facts describe the cost of this explicit continuation. They are not an
impossibility theorem for a different compact representation.

## 7. Precisely scoped bound for a narrower family of adaptive readings

This section does not bound the trace or block corrections above. It
identifies a restriction that a broader successful correction must evade.

Consider q readings of the form [t^n]G_(B,alpha_f)(t xi_f), where the
change is w_i=x_i g_i^(alpha_(i,f)), with the corresponding exact Good
Jacobian, followed by a linear combination with weights beta_f. The
parameters may depend polynomially on the input entries, provided they
are independent of t. More generally the argument works for parameters
regular at B=0, when their Taylor expansions exist. They may depend on
labels, omega and z in the coefficient field. No nonlinear mixing of
different t-degrees, t-dependent parameters, singular parameter maps,
extra implicit equations, or data-dependent branching is covered.

For a cycle on U, let A_f(U)=sum_(i in U)alpha_(i,f). The doubled-cycle
coefficient is p(A_f(U)) with p(a)=(a-1)(a-2)/2. This follows from (2),
now with g_i^(alpha_i(1-m_i)). In particular p(0)=1.

Let r=floor(n/2), and index rows and columns by r-subsets S,T. On a
monomial consisting of a directed cycle on S\T traversed twice and
diagonal loops on the complement of S triangle T, the occupation is
1+1_S-1_T and total input degree is n. Its target permanent coefficient
is zero when S!=T. When S=T, use all diagonal loops; its coefficient is
one. Hence any exact member of this restricted family must satisfy

    I_(S,T)=sum_f beta_f
             (prod_(i in S)xi_(i,f)) (prod_(i not in T)xi_(i,f))
             p(sum_i alpha_(i,f) 1_S(i)(1-1_T(i))).             (18)

This formula needs no inverse phase, so zero phase values are allowed.
If the parameters depend regularly on B, first take homogeneous input
degree n. Every [t^n] reading already has input degree at least n; thus
only degree-zero Taylor terms of the parameters contribute to (18).
Higher parameter coefficients cannot repair (18). This is the exact
scope of the input-dependence argument; it does not freeze parameters
inside a more general degree-mixing program.

For u_i=1_S(i)(1-1_T(i)), expand

    p(sum alpha_i u_i)=1+sum_i (alpha_i^2-3alpha_i)u_i/2
                         +sum_(i<j)alpha_i alpha_j u_i u_j.

Each term, including its phase factor, separates into a row factor and
a column factor. The matrix for one reading has rank at most
D_n=1+n+binom(n,2). Therefore

    q >= binom(n,floor(n/2))/D_n.                              (19)

The field characteristic is zero, or sufficiently large for the stated
identities. A finite-field experiment checks the feature decomposition
on all 70 subsets at n=8; its sample rank is 28, below D_8=37. Equation
(19) is exponential asymptotically. It rejects polynomially many such
powered readings with linear fusion, including data-polynomial phase
and power choices, but **not** the broader hypothesis of this node.
In particular (7) and (13) mix degrees multiplicatively and are outside
the assumptions. Their constructive success on cycles and bouquets is
consistent with (19).

## 8. Exact reference and reproducibility

The committed exact candidate prepares all marked B entries, then uses

    D[empty]=1,
    D[S]=sum_(j in S) B_(|S|-1,j) D[S\{j}].                   (20)

Its invariant is the sum of all bijections from the first |S| rows to S,
with every original marker. For singleton S it reuses the B wire.
Character orthogonality folds the complete spectral tail: output wire
D[[n]] at slot sum(labels) modulo N, and literal zero at every other
slot. This is an exact global rewrite, permitted without reading omega
at runtime once its primitive-root precondition is known.

Its scalar gate count, including marker preparation, is

    (n-1)2^n+2n^2-n.

The compiler is exponential; there is no claim that (20) resolves the
subset bottleneck. It is retained so the worktree contains a fully valid
whole-table candidate while the broader normalization remains incomplete.

Run the frozen check and the independent research checks with:

    python evaluate_dev.py
    python verify_joint.py
    python verify_trace_correction.py
    python verify_residue6.py

The last script uses SymPy 1.14 for symbolic proof checks. All other
scripts and the candidate use the Python standard library. Saved exact
outputs are `development.json`, `joint_verification.json`,
`trace_verification.json`, and `residue6_verification.json`.

The reusable positive result is the passage from isolated-cycle traces
to the bouquet and incidence-forest closures, with the explicit degree-six
overlap contraction. The unresolved step is a scalar recurrence for the
connected overlapping-cycle corrections on arbitrary dense supports whose
total size has a fixed polynomial bound in n.
