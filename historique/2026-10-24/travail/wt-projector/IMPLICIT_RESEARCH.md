# Implicit-series research n4: Schur self-energies and the exact Good Jacobian

Branch research/implicit, based on e59cbe84958d5d3968f45f5097a8b9150b910dd2.
This is a separate hypothesis from PROJECTOR_RESEARCH.md. The scalar candidate
in candidate.py remains the verified exponential source, score 1912 at n=8.
The new polynomial-size scalar proposed here is not the permanent in general.
No evaluator file was modified, and no held-out protocol was read or run.

The constructive result is an exact input-dependent normalization that removes
every occupation with exactly one repeated index, at all degrees. Explicit
polynomial corrections then remove the remaining errors through degree five.
They do not provide an all-degree polynomial closure. All identities below are
proved algebraically; no new Lean certification is claimed.

## 1. General Good change of variables and an exact determinant cancellation

Set X=diag(x), Q_B(x)=det(I-XB), and F_B(x)=1/Q_B(x). The squarefree coefficient
of F_B is per(B), as proved by the cycle expansion in PROJECTOR_RESEARCH.md.

For a formal invertible map x_i=w_i/phi_i(w), with phi_i(0)=1, the logarithmic
Jacobian is

    J_log(w)=det(delta_ij - w_j partial_j phi_i(w)/phi_i(w)).

Formal residue change of variables gives

    per(B)=[w_1...w_n] F_B(x(w)) product_i phi_i(w) J_log(w).

This follows directly by substituting into
Res F_B(x) product_i dx_i/x_i^2. It is an n-dimensional residue identity;
substituting all w_i=t is an additional operation and changes the coefficient
functional unless unwanted total-degree-n monomials have been eliminated.

For phi_i(w)=1+sum_j B_ij w_j, Sylvester's determinant identity gives

    J_log=det(I-diag(w/phi)B)=Q_B(x(w)).

The determinant cancels exactly, leaving product_i(1+sum_j B_ij w_j). The
implicit equations w_i=x_i phi_i(w), specialized at x_i=t, are solved by

    w=t(I-tB)^(-1) 1.

Thus n polynomially computable adaptive series and an exact Jacobian do exist
in this example. The resulting squarefree extraction is the original row
product. At common w=t the degree-n coefficient is product_i sum_j B_ij,
which already differs from the permanent for J_2 (4 instead of 2).

## 2. Full Schur self-energy normalization

Let

    R(x)=(I-XB)^(-1),
    g_i(x)=R_ii(x)=Q_{B without i}(x_without i)/Q_B(x).

The ratio is the diagonal cofactor identity. Denote the numerator by A_i.
Since Q_B is affine in x_i, it has the exact Schur form

    Q_B=A_i(1-x_i c_i(x_without i)),
    g_i=1/(1-x_i c_i),
    c_i=b_ii+B_{i,-i}(I-X_{-i}B_{-i,-i})^(-1)X_{-i}B_{-i,i}.

Define n adaptive variables by

    w_i=x_i g_i(x),
    equivalently x_i=w_i/(1+w_i c_i(x_without i)).

Each coordinate is the exact one-variable Mobius normalization of every
return path through vertex i; this uses the full cavity resolvent, not a
low-order truncation. All g_i have constant term 1, so the simultaneous map
has a unique formal inverse x(w) with linear part w.

Let J=partial w/partial x be its ordinary Jacobian. Differentiating the matrix
inverse gives an explicit polynomial-size expression in matrix series:

    J_ij=delta_ij g_i + x_i R_ij (B R)_ji.

The exact Good-transformed density is

    G_B(w)=F_B(x(w)) product_i (w_i/x_i(w))^2 / det J(x(w)).

The exponent two comes from the dx_i/x_i^2 residue form. In particular

    per(B)=[w_1...w_n]G_B(w).

The proposed ordinary scalar readout is [t^n]G_B(t,...,t). Its computation is
polynomial; its equality to the target is the property investigated below.

## 3. A polynomial scalar compiler for the proposed readout

Specialize w_i=t and retain jets through degree n. Solve the inverse map by

    x_i^(0)=t,
    x_i^(r+1)=t/g_i(x^(r)).

The factor t makes this iteration t-adically contractive: each iteration fixes
one more coefficient. After n iterations all x_i are correct through degree n.
Only inverses of series with constant term 1 are used. Such an inverse is
compiled by

    u_0=1,
    u_m=-sum_{k=1}^m a_k u_{m-k}.

Thus no division by an input scalar, coefficient oracle, or algebraic-root
operation is required. All coefficients are actual scalar +,-,* circuits.
For R=(I-XB)^(-1), write x_i=sum_m x_{i,m}t^m and use

    R_0=I,
    R_m=sum_{a=1}^m diag(x_{1,a},...,x_{n,a}) B R_{m-a}.

There are O(n^2) pairs (m,a), each costing O(n^3) scalar operations. One
iteration costs O(n^5) gates and n iterations cost O(n^6). Constructing J uses
matrix and scalar jet products with at most O(n^5) additional gates.

Both I-XB and J have constant matrix I. Formal Gaussian elimination therefore
has pivots with constant term 1. Compile every pivot inverse with the explicit
unit-series recurrence above. O(n^3) jet operations at O(n^2) gates each give
O(n^5) gates per determinant, with no exceptional-input branch. Finally compute

    G_B(t1)= product_i g_i(t)^2 / (det(I-X(t)B) det J(t))

by the same jet arithmetic. This yields a uniform O(n^6) scalar compiler for
all coefficients of the proposed readout, including input preparation. The
required literal constants have polynomial bit length (in fact the jet update
can use only 0, 1 and -1). This is a cost proof for the displayed scalar, not a
cost proof for the permanent.

## 4. Exact coefficients by occupation; all unary repetitions vanish

The transformation can be analyzed without expanding its implicit inverse.
For every multiindex m>=0, the same residue calculation yields

    [w^m]G_B(w) = [x^m] F_B(x) product_i g_i(x)^(1-m_i).             (1)

Indeed G_B(w) dw/product w_i^2 = F_B(x) dx/product x_i^2; multiply by
product w_i^(1-m_i), then use w_i=x_i g_i. This proves (1) directly.

Let S=support(m), k=|S|, and Q_S=det(I-X_S B[S,S]). Setting x outside S to zero
makes g_i=1 there. On S, write A_i=Q_{S without i}. Formula (1) becomes

    [w^m]G_B = [x^m] Q_S^(|m|-k-1) product_{i in S} A_i^(1-m_i).    (2)

If every positive m_i equals one, (2) is the original permanent coefficient of
B[S,S]. Therefore all desired squarefree coefficients are preserved.

Suppose exactly one index i repeats, m_i=r>=2, and all other positive entries
are one. Formula (2) is Q_S^(r-2)/A_i^(r-1). Its denominator is independent of
x_i and its numerator has x_i-degree at most r-2, since Q_S is affine in x_i.
Its coefficient of x_i^r is zero. This proves, at every degree:

    Every occupation with exactly one repeated index is annihilated.

This is stronger than agreement on a few scalar examples. It leaves the
occupations with two or more repeated indices to be contracted or corrected.

## 5. Generic degree-four error, proved by every occupation type

Write d_i=b_ii, a_ij=b_ij b_ji for i!=j, and a_ii=0. For total degree four:

* (4), (3,1), and (2,1,1) vanish by the preceding theorem.
* (1,1,1,1) gives the permanent of the corresponding principal 4x4 matrix.
* For (2,2) on indices i,j, Q=(1-d_i x_i)(1-d_j x_j)-a_ij x_i x_j.
  Formula (2) is Q/((1-d_i x_i)(1-d_j x_j)). Its coefficient of x_i^2 x_j^2 is
  exactly -a_ij d_i d_j.

Consequently the complete generic identity is

    [t^4]G_B(t1)=sum_{|S|=4}per(B[S,S])-c4,
    c4=sum_{i<j} a_ij d_i d_j.

The multivariate error is exactly
-sum_{i<j} a_ij d_i d_j w_i^2 w_j^2; all other nonsquarefree degree-four types
are zero. The correction c4 is polynomial in the actual entries and needs
O(n^2) scalar gates. It is not calibrated to a symmetric matrix.

For example, the legal asymmetric matrix

    [[2,1,5,5], [2,5,5,2], [2,5,5,5], [5,5,5,5]]

has per(B)=5520, c4=1870, and [t^4]G_B=3650. Each entry is 1+a^2 for rational
(in fact integer) a, and z=1 is allowed. This is an exact finite counterexample
to the uncorrected all-size readout within the requested input family.

## 6. Degree-five correction by occupation and matrix formulas

Let c_ijk=b_ij b_jk b_ki+b_ik b_kj b_ji, the two directed triangle weights.
Only the following nonsquarefree types survive at degree five:

    [w_i^3 w_j^2]G_B = a_ij^2 d_i,

    [w_i^2 w_j^2 w_k]G_B
      =-a_ij d_i d_j d_k - c_ijk d_i d_j
       -a_ij a_jk d_i -a_ij a_ik d_j.                           (3)

Every other nonsquarefree degree-five type has a single repeated index.
For (3,2), (2) gives Q^2/(A_i^2 A_j); expanding Q=A_i A_j-a_ij x_i x_j shows
that only the a_ij^2 x_i^2 x_j^2/(A_i^2 A_j) term reaches x_i^3 x_j^2, giving
a_ij^2 d_i. For (2,2,1), (2) gives Q/(A_i A_j). Expand to first order in x_k;
the four terms in (3) follow. This proves the listed errors symbolically.

Let A=(a_ij), r=A1, D=diag(d), C=B-D, and

    S2=sum_{i,j} d_i a_ij^2,
    c5=d^T A r - 2 S2
       -sum_{i<j} a_ij d_i d_j(d_i+d_j)
       +tr(D C D C^2).

Summing (3) and the (3,2) terms gives the exact degree-five error

    [t^5]G_B(t1)-sum_{|S|=5}per(B[S,S]) = -c4 tr(B)-c5.

Hence the genuinely polynomial corrected scalar series

    G_B(t1) (1+c4 t^4+c5 t^5)

agrees with perm(I+tB) through degree five for every B and every matrix size.
Computing c4 and c5 uses O(n^3) scalar gates by the displayed matrix formulas,
on top of the counted O(n^6) implicit-jet construction. These corrections give
an actual exact permanent algorithm for dimensions at most five, but do not
yet imply a uniform algorithm for unbounded dimensions.

For clarity, no unproved degree-six recurrence is inferred from these formulas.
The next occupations include (4,2),(3,3),(3,2,1),(2,2,2),(2,2,1,1). Formula (2)
still handles each separately, but their sum has not been compiled by a closed
polynomial scalar update for all degrees.

## 7. Independent all-ones closed form and the failure at degree six

For B=J_n, symmetry gives x_i=x and Q=1-nx. Set rho=x/Q. Then

    g_i=1+rho,
    t=w_i=rho(1+rho)/(1+n rho).

The ordinary Jacobian has the form
(1+2rho)I+rho^2 11^T, so its determinant is
(1+2rho)^(n-1)(1+2rho+n rho^2). The exact diagonal Good series is therefore

    G_{J_n}(t1)
      =(1+n rho)(1+rho)^(2n)
        /((1+2rho)^(n-1)(1+2rho+n rho^2)),
    rho=t(1+n rho)/(1+rho).

Univariate Lagrange inversion or direct formal substitution computes every
coefficient exactly. The coefficient of degree n for n=1,...,8 is

    1, 2, 6, 18, -10, -1270, -18088, -27454.

The corresponding permanents are n!, so the first failure is n=4. For n=6,
c4=15 and c5=180; the corrected degree-six coefficient is

    -1270 + 15*30 + 180*6 = 260,

whereas per(J_6)=720. This is an admissible A=0, z=1 instance. Thus the
finite-order corrected rule also fails as an all-size compiler. It supplies
no basis for silently declaring the unknown higher correction coefficients
free or assuming that their scalar recurrence has closed.

## 8. Verification and result boundary

verify_implicit.py implements the complete implicit fixed point, its analytic
Jacobian, and the exact Good readout with rational truncated series. It tests
15 legal matrices with independently drawn entries, three in each dimension 1 through 5. It checks
the uncorrected identities through degree three, the generic c4 error, and the
c4/c5 corrected readout. It also checks degree four against the sum of principal
4x4 permanents in every tested dimension. Small-case determinant and permanent
evaluation deliberately use permutation enumeration as an independent checker;
the O(n^6) circuit construction above uses unit-series elimination instead.

The separate all-ones closed form is checked against the generic implicit
implementation through dimension four, then evaluated through dimension eight.
implicit_verification.json records the results and the 260-versus-720 failure.
The earlier candidate and its frozen development result are unchanged.

The present mechanism achieves a polynomial-size implicit normalization and
correctly removes a broad infinite family of collisions. It also admits exact
polynomial corrections through degree five. The missing step is a uniform
polynomial construction of all remaining multiple-repeat corrections. The
formal ratio perm(I+tB)/G_B(t1) would merely rename those unknown coefficients,
and its degree-n coefficient cannot be supplied as an oracle. Nothing here
proves a lower bound against other adaptive representations, or resolves the
requested general polynomial scalar-source construction.
