# Fixed edge ports and the precise synchronized contraction

This leaf replaces the matching-dependent rank matrix for one coefficient
by principal submatrices of a single fixed matrix. It does not claim a global
polynomial extractor. The development protocol was extended before tests.

## Möbius identity from the actual n61 recurrence

In the idempotent projector algebra, with incompatible matching products
annihilating determinant-supported monomials, the n61 recurrence multiplies

    Q=product_(i<l) (1-2 sum_(j>m) e_ij e_lm)=sum_S c(S)e_S.

For every matching U, evaluation at its Boolean indicator gives

    sum_(S subset U)c(S)=(-1)^inv(U).

Boolean Möbius inversion gives the exact candidate coefficient formula

    c(S)=sum_(T subset S)(-1)^(|S|-|T|+inv(T)).

This also supplies |c(S)|<=2^|S|<=2^n and at most n+1 magnitude bits.
These are informal general derivations until the parent closes their Lean
dependency chain. Finite tests compare against the unchanged n61 recurrence.

## Matching-dependent local Pfaffian

Sort the k selected edges by row. Set A_ab=sgn(col_b-col_a). Its even
principal Pfaffians are the permutation signs of the selected column orders:
after sorting columns they become the skew matrix with upper entries one,
whose even principal Pfaffian is one. Choose even order h=k+1 for odd k and
h=k+2 for even k, append dummy d=k with Atilde_(a,d)=-1, and for even k append
one inert final index. Let J have upper entries one and D_aa=(-1)^a. Then

    c(S)=(-1)^k Pf(J-D Atilde D).

The dummy contributes the negative odd-subset sum; the inert index contributes
no nonempty principal Pfaffian. The Pfaffian addition expansion cancels its
shuffle signs against the D signs. This is the original local formula.

## One fixed matrix with paired ports

Order the n^2 real edges lexicographically, then append a dummy edge g with
column larger than every real column. For every edge e give two ports a_e,b_e,
and interleave them. Construct a fixed skew matrix K of order 2n^2+2:

    K(a_e,b_e)=-1 for real e; K(a_g,b_g)=+1;
    K(a_e,a_f)=+1 for e<f;
    K(b_e,b_f)=-sgn(col_f-col_e) for e<f;
    K(a_e,b_f)=0 for e!=f;
    K(a_e,a_g)=+1; K(b_e,b_g)=-1.

Then for every compatible matching S,

    c(S)=Pf K[ports(S) union ports(g)].

An internal a_e/b_e pairing removes both ports. Every remaining real subset
T therefore appears in both the row block and column block. For even T the
two block Pfaffians and their interleaving sign produce sign(T); the remaining
internal weights produce (-1)^(|S|-|T|). For odd T, the dummy enters both
blocks, its column-largest order preserves sign(T), and the same internal
weight formula holds. Each subset T occurs once. This is a constructive
informal proof of the fixed-matrix identity, not a claim that all resulting
principal submatrices have been summed by one cheap scalar circuit.

## Charged scalar Pfaffian compiler

For any skew A of even order d=2m, let J be the standard block-diagonal skew
matrix with J_(2r,2r+1)=1, Pf(J)=1, and put B=-JA. Compute shared powers B^i
and traces, then

    q0=1,
    qk=(1/(2k))*sum_(i=1..k) (-1)^(i-1)tr(B^i)q_(k-i).

The coefficient sequence is derived informally from
det(I+tB)=Pf(J+tA)^2; the terminal q_m is Pf(A). The compiler directly
constructs q_m by this explicit recurrence, so extraction is not an operation.
Upper skew entries are leaves; lower entries cost d(d-1)/2 negation gates.
Forming B costs d^2/2 negations, with its other rows reused by pointers.
Dense powers cost (m-1)(2d^3-d^2), traces m(d-1), shared negative traces
floor(m/2), and q recurrence m(m+1) gates. Total:

    G(d)=d(d-1)/2+d^2/2+(m-1)(2d^3-d^2)
          +m(d-1)+floor(m/2)+m(m+1).

All divisions are rational constant multiplications; no variable inverse,
Pfaffian primitive or free derivative appears in the scalar graph. This
formula counts a particular actual compiler, without claiming optimality.

## Aggregate candidate and remaining constructive lemma

For formal X, set U_e=x_e e_row(e), V_e=e_col(e), L=V^T X^{-1} U.
The determinant lemma gives

    det(X)det(L_S)=P_S det(X),
    P_X=det(X) sum_(S subset edges) Pf(K_ports(S)+dummy) det(L_S).

Incompatible S vanish by repeated incidence rows or columns. This removes
the matching constraint algebraically, but retains the synchronized-port
constraint. An ordinary Pfaffian minor sum selects arbitrary ports; here
a_e and b_e must both be present or both absent. No cancellation of all extra
port patterns has been established. The exact missing constructive lemma is
a polynomial scalar circuit for this paired-principal-Pfaffian/determinant
contraction, from the fixed K and the cheap incidence data, preserving every
formal entry. A costless contraction is explicitly forbidden.

Variable inverses need not be an independent obstacle IF that contraction
lemma is supplied: replace X by X_eps=I+eps(X-I), use the exact truncated
Neumann inverse sum_(j=0..n)(-eps)^j(X-I)^j modulo eps^(n+1), multiply by
det(X_eps), and evaluate the resulting degree-at-most-n target at eps=1.
Coefficient lists have length n+1 and every convolution can be charged.
This is a conditional route, not an implemented root-target extractor.

The classic minor summation identity sums Pfaffian weights times ordinary
minors of one fixed matrix [Ishikawa, FPSAC95, Theorem 2.1]:
https://fpsac-archive.github.io/FPSAC95/ARTICLES/38.ISHIKAWA.pdf
It does not by itself establish synchronized selection. No lower-bound or
counterexample experiment is performed in this leaf.
