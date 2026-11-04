# Bounded inversion spectrum and the initialization it still needs

Artifact version: n65-inversion-jet-audit-v1. The root-supplied
n65-protocol.json is preserved unchanged. No experiment, held-out access,
negative search, or Lean compiler round is performed by this leaf. The
reason is specific: a complete polynomial scalar state family has not been
isolated, so running an identity-only test would not evaluate that hypothesis.

All new universal mathematics below is an informal derivation. It is not
presented as a kernel-verified theorem or as a proof of Conjecture 1.5.

## Exact operator identity

For e=(i,j), put E_e=x_e partial_e and

    N=sum_(i<l,j>m) E_(i,j) E_(l,m),
    D=n(n-1)/2.

On each permutation monomial, N acts by the integer inv(sigma) in [0,D].
The explicit polynomial

    p_D(T)=sum_(k=0..D) (-2)^k binom(T,k)

has p_D(r)=(-1)^r for each such integer r, by the binomial theorem. Hence
p_D(N)det(X) is exactly the unsigned permutation sum. Constructing p_D's
rational coefficients is cheap relative to n, and its literals have a
polynomial bit bound. Applying N is a second-order differential operation;
it is not one scalar arithmetic gate.

Let R_D(T)=product_(r=0..D)(T-r)=T^(D+1)+sum_(j=0..D) r_j T^j.
The bounded spectrum gives R_D(N)det(X)=0. Thus the jets J_k=N^k det(X)
satisfy the constant scalar recurrence

    J_(k+D+1)=-sum_(j=0..D) r_j J_(k+j).

Its companion transition is cheap. It still requires all of
J0,J1,...,JD as actual initial polynomials. Supplying these jets as input
leaves would insert the unknown difficult computation into initialization.
The coefficient spectrum and the recurrence do not themselves construct them.

## First two jets have explicit scalar data

The exact complementary-minor formula is

    J0=det(X),
    J1=-sum_(i<l,m<j) (-1)^(i+l+j+m)
          x_ij x_lm det X[{i,l}^c,{m,j}^c].

There are D^2 terms. The scalar source initial_jets.py implements this
formula through the unchanged determinant recurrence, with all binary
addition/multiplication gates explicit. It supplies ONLY J0 and J1. In
particular it does not initialize a D+1-state companion for n>=3.

Writing S0(r)=2r^4-r^3+2r^2-r and S0(0)=0, its directly derived gate count is

    S0(n)+D^2 S0(n-2)+4D^2-1,

and all original marked entries add 2n^2-1 shared scalar multiplications.
The generic formula values n2..5 are 33,203,1699,16569; marked values are
40,220,1730,16618. These are derived counts of the written constructor,
NOT measured executions or positive root-target scores. The source has
not been run here. It uses only formal entries or the source-model prescribed
p_ij=1+a_ij^2 and rational constants. No target coefficient is an input.

## Inverse identities give an exact transition, but no cheap closed basis

On the generic invertible locus, let Y=X^-1. For e=(i,j), define the
derivation delta_e on the coordinate algebra by

    delta_e x_ab = [a=i,b=j],
    delta_e Y_ab = -Y_ai Y_jb,
    r_e=Y_ji.

Write J_k=det(X) F_k, with F0=1. Then F_(k+1)=L F_k, where

    L F=sum_(e=(i,j),f=(l,m), i<l,j>m) x_e x_f *
       (delta_e delta_f F + r_e delta_f F + r_f delta_e F
        +(r_e r_f-Y_mi Y_jl)F).

This follows by differentiating det(X)F twice and the inverse matrix once.
It explicitly identifies the first-jet quantity and every derivative that
the next jet would require. It does not certify a cheap scalar update:
delta_e and delta_e delta_f are still differential operations. Repeated
application introduces higher mixed cofactor data. The complementary-minor
and Pluecker identities supply lawful relations among them; this leaf has
not derived a polynomial-size invariant list with scalar transition entries.

The exact missing constructive sublemma is now precise. Supply an explicitly
constructed state map Psi_X of polynomial dimension r on the reachable
function family, a scalar transition matrix M(X), and boundary row u(X), such
that

    Psi_X(L F)=M(X) Psi_X(F) for every reachable F,
    Psi_X(1) and u(X) are cheap scalar initial/boundary data,
    F(X)=u(X) Psi_X(F).

Every matrix entry and datum must have a uniform polynomial scalar constructor;
no unknown jet/target coefficient is an input. A jet-based state map must prove
this actual differential intertwining, including derivatives of its variable
coefficients. Merely proving L g_a=sum_b M_ab(X)g_b for a list of functions is
insufficient for powering: L also differentiates the M_ab(X) at the next step.
A basis closed over Q with CONSTANT transition coefficients is a sufficient
alternative, provided its evaluation and initial coordinates are cheap. This
distinction is an explicit path-adjustment constraint, not a negative search.
Boundary multiplication by det(X) and linear evaluation of p_D need their
complete scalar costs. A Neumann expansion of X_eps=I+eps(X-I) modulo
eps^(n+1) can remove variable inverses if such a closure is supplied, but is
conditional on that closure.

## Falling jets expose the unchanged cofactor frontier

Put H_k=binom(N,k)det(X). For each row pair, the inversion projectors are
orthogonal on permutation monomials, so Q_(i,l)=sum_(j>m)E_ij E_lm is an
idempotent there. The exact generating operator is

    product_(i<l)(1+s Q_(i,l))det(X)
      =sum_(k=0..D) H_k s^k.

Evaluation at s=-2 gives the n61 Euler phase product. Expanding the factors
introduces exactly the compatible partial-matching projector states of
n61. The bounded degree D reduces the count coordinate, but has not reduced
the number of distinct cofactor states or supplied cheap initial jets.
This is retained as a positive identity preserving the construction gap,
not rerun as new evidence and not used for a lower-bound claim.

## Strict outcome

1. Complete explicit scalar data and transition: unclosed. Only J0,J1 and
   a companion transition conditional on J0..JD are constructed.
2. Polynomial total gate/literal/initialization certificate: unclosed.
   The partial initializer has a derived polynomial count; full initialization
   and a closed scalar jet update do not have such a certificate.
3. Exact root-target identity: informally derived through bounded spectrum,
   but neither a root-target scalar compiler nor a full Lean chain is supplied.

The strict development score is null (no eligible complete candidate was
executed), not 1.0 for an operator identity alone. The next positive search
must construct the invariant jet/cofactor basis and its initialization before
requesting Hilbert verification. Shared formal-round budget consumed: zero.
