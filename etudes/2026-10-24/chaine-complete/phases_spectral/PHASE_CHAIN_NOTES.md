# Cell phases and the complete spectral output

Status: exact constructions for n <= 4 and an exact uniform exponential
construction. The proposed finite abelian cell-score family cannot have a
polynomial-size group for all n. This is a theorem about that family, not a
lower bound for arbitrary scalar compilers of the complete oriented chain.
`candidate.py`, `dag.py`, and `evaluate_dev.py` are unchanged. There is no
general candidate submitted to the development evaluator, so dev_score=null.

## 1. Integrating the original spectral register

Let B_ij=p_ij z^(2^(in+j)), with zero-based indices. Let N=2^bit_length(n),
and d_j be the original column labels. Suppose a finite abelian group G,
cell labels r_ij in G, and a function chi:G -> Q obey

    chi(rho(sigma)) = sgn(sigma),
    rho(sigma) = sum_i r_i,sigma(i)

for every permutation sigma. Only signs must be separated; permutations
with the same sign may have the same score. No injectivity hypothesis is
used in the construction or lower bound below.

Work in the explicitly represented rational group algebra
R=Q[G x (Z/N)], with basis e_(g,t), and form

    M_ij = B_ij e_(r_ij,d_j mod N).

Its determinant is

    det(M) = sum_sigma sgn(sigma) product_i B_i,sigma(i)
                         e_(rho(sigma),sum_j d_j mod N).

The terminal scalar output in slot t is the linear map

    L_t(sum_(g,s) v_(g,s)e_(g,s)) = sum_g chi(g) v_(g,t).

Thus all slots are the required marked permanent table. The global
orientation gamma_n is already normalized in the contract. The determinant
removes column collisions; chi corrects its permutation signs; the original
spectral slot is carried from each cell through every intermediate product.
There is no corrected amplitude leaf, and no requirement to first expose a
scalar permanent before the spectral computation. Cyclic convolution
implements the original frequency multiplication and inverse transform
jointly, so the supplied omega need not be used as an input.

The code computes the determinant by the division-free-in-the-data
Faddeev-LeVerrier recurrence over R:

    C_0 = I;
    T_k = M C_(k-1);
    c_k = -(1/k) tr(T_k);
    C_k = T_k + c_k I;
    det(M) = (-1)^n c_n.

Newton's identities for det(I-tM) prove this recurrence over any commutative
Q-algebra. Its divisions are only literals 1/k. In particular, zero divisors
in a group algebra do not require an inverse of any input-dependent value.

If m=|G| and D=mN, dense multiplication takes at most D^2 scalar
multiplications and D^2 scalar additions. There are at most n^4 ring
multiplications, O(n^4) ring additions, and O(n^2) scalar/ring scalings.
The total scalar bound is O(n^4 D^2), or O(m^2 n^6), plus O(n^2) marking
gates and O(mN) terminal-reader gates. This is a deliberately simple upper
bound. Sparse structural coordinates can lower the actual count, but no
nonconstant arithmetic operation on those coordinates is free.

A supplied explicit certificate yields a uniform compiler in time polynomial
in n,m,the certificate size,and the input-label bit length, assuming group
addition has polynomial cost in its representation. For the cyclic/XOR
groups implemented here it does. Constants in the determinant have O(log n)
bits; the reader additionally uses the specified chi constants. Binary
addresses are prepared by n^2-1 shared squarings; their exponentially large
values are not rational literals. These bounds become polynomial in n only
if the certificate itself, including m, is polynomial, which Section 4 rules
out for this family.

## 2. Exact small constructions

For n=1 the lone marked cell goes to its labelled slot. For n=2, use the
F2 matrix r=[[0,0],[0,1]], chi(0)=-1,chi(1)=1. Equivalently the sign-corrected
determinant is -det([[B00,B01],[B10,-B11]]), with each cell also carrying d_j.

For n=3 index rows and columns by F3 and set r_ij=-ij mod 3:

    0 0 0
    0 2 1
    0 1 2

All six permutations have the form sigma(x)=a*x+b, a in {1,2}. Since
sum x=0 and sum x^2=-1 in F3, rho(sigma)=a. Translations are 3-cycles or the
identity, hence even; multiplication by 2 is odd. Therefore chi(1)=1 and
chi(2)=-1; score 0 is unused and may be assigned zero.

There is a smaller rational representation of these phases. Let alpha obey
alpha^2+alpha+1=0, and use entries B_ij alpha^r_ij with their spectral slots.
Write E and O for the even and odd unsigned monomial sums, respectively.
The determinant is E alpha - O alpha^2 = O+(E+O)alpha. Its alpha coordinate
is the desired output. Multiplication is explicitly

    (a+b alpha)(c+d alpha) = (ac-bd)+(ad+bc-bd)alpha.

`phase_chain.py` implements this two-coordinate algebra tensored with the
original Z/N register using only rational scalar operations. Alpha is not
an additional root-of-unity input or a free algebra-valued gate.

For n=4 index by F4={0,1,u,u+1}, u^2+u+1=0, and set r_ij=i*j in F4,
viewed as an additive group F2^2. Every permutation is affine over F2,
because AGL(2,2) has 4*6=24 elements. Its linear part has form a*x+b*x^2;
invertibility forces exactly one of a,b nonzero. If both were nonzero,
x=a/b would be a nonzero root, and both zero is not invertible. We have
sum x=sum x^2=0 and sum x^3=1, so rho(sigma)=b.

Translations are even (nonzero translations are two disjoint swaps), and
nonzero multiplications are even (the two nonidentity ones are 3-cycles).
Frobenius x -> x^2 is odd (it interchanges u,u+1). Thus rho=0 exactly for
even permutations, and each of the three nonzero scores contains four odd
permutations. Take chi(0)=1 and chi(g)=-1 for g != 0.

For t in F2^2 let D_t be the determinant with each cell multiplied by
(-1)^(t dot r_ij), again computed over Q[Z/N] with the original column
labels. Fourier inversion of chi gives the entire vector identity

    output = (-D_0 + D_1 + D_2 + D_3)/2.

All four phase matrices have rational entries +/-1; the only reader
constant is 1/2. This avoids any undeclared roots of unity.

Both the full group-coordinate and specialized quotient/Fourier versions
are implemented. The latter have a smaller coefficient algebra or an
explicit character formula, but are not gate optimizations of this sparse
implementation. For labels d_j=j their charged gate counts are:

| n | group coordinates | specialized |
|---|---:|---:|
| 1 | 4 | 1 |
| 2 | 39 | 39 |
| 3 | 375 | 647 |
| 4 | 3435 | 6505 |

All preparation and terminal readout gates are included.

## 3. Exact extension with a large group

There is a uniform certificate for every n, but it is exponential. Take
G=Z/(n^(n-1)) and

    r_0j=0;
    r_ij=j*n^(i-1) for 1 <= i < n.

A permutation score is the base-n encoding of sigma(1),...,sigma(n-1).
There is no carry or wraparound: each digit lies in [0,n-1]. Recover sigma(0)
as the missing digit. Set chi to the parity of this recovered permutation;
set it to zero for codes with repeated digits. This construction is only an
upper bound, and its injectivity is not assumed anywhere in the lower bound.

Each label has O(n log n) bits, and decoding one score takes polynomial time.
Materializing chi and the group coordinates takes n^(n-1) time/space. The
explicit scalar construction from Section 1 consequently has upper bound
O(n^(2n+4)). No claim of polynomial size or compilation time follows from
short labels or a polynomial-time decoder for an individual score.

The simple F4 pattern does not extend by just replacing F4 by F8. For the
binary polynomial x^3+x+1, r_ij=i*j in F8, these opposite-parity pairs have
equal scores (indices as the integers encoding polynomial basis elements):

| n | first permutation | second permutation | score |
|---|---|---|---:|
| 5 | (0,1,3,4,2) | (0,2,1,3,4) | 3 |
| 6 | (0,1,2,4,5,3) | (0,2,1,3,4,5) | 4 |
| 8 | (0,1,2,3,4,6,5,7) | (0,1,2,4,5,3,6,7) | 5 |

These are failures of that particular extension, not assertions about all
finite fields, all score functions, or all scalar constructions.

## 4. A general bound for this cell-score hypothesis

The following proof is self-contained and does not rely on a complexity
assumption or on the stronger requirement that all permutation labels differ.

For an arbitrary sign-separating G and cell labels, put

    a_g = sum_(sigma:rho(sigma)=g) sgn(sigma).

Every occupied score contains only one sign. Hence

    sum_g |a_g| = n!.

Let G-hat be the group of its complex unitary characters, and define the
unnormalized Fourier transform

    a-hat(psi) = sum_g a_g psi(g).

By the determinant expansion,

    a-hat(psi) = det(psi(r_ij)).

Every entry has absolute value one; every row has Euclidean norm sqrt(n).
Hadamard's determinant inequality therefore gives
|a-hat(psi)|^2 <= n^n. Character orthogonality gives Parseval exactly as

    sum_g |a_g|^2 = (1/|G|) sum_psi |a-hat(psi)|^2 <= n^n.

Let s be the number of occupied scores. Cauchy-Schwarz now yields

    (n!)^2 = (sum_g |a_g|)^2 <= s sum_g |a_g|^2 <= s*n^n.

Consequently

    |G| >= s >= (n!)^2/n^n.

In particular, n! >= (n/e)^n implies the lower bound (n/e^2)^n, which
eventually exceeds every fixed polynomial. The factorial estimate follows
already by comparing sum_(k=1)^n log k with the integral of log x from 1 to n.
This also rules out a polynomial number of occupied coordinates, not only
an excessively large but sparsely used ambient group.

Adaptively choosing r from the data does not remove this bound when the
claimed identity preserves the formal markers: specialize to A=0, hence
p_ij=1. Every permutation has a distinct binary address and a nonzero
coefficient; the sign-separation condition is still necessary. The group
labels for that particular data instance must obey the same bound.

There is a related bound on a direct character implementation. Suppose chi
is extended to all unused scores with |chi(g)| <= 1 (zero is allowed), and
write chi(g)=sum_psi c_psi psi(g), with normalized Fourier coefficients.
Then sum |c_psi|^2 = (1/|G|)sum |chi(g)|^2 <= 1. At B_ij=1,

    n! = sum_psi c_psi det(psi(r_ij)).

If L is the number of nonzero c_psi, Cauchy-Schwarz and Hadamard imply
(n!)^2 <= L*n^n. Thus merely using only the nonzero Fourier terms does not
make this bounded-reader construction polynomial either. This support
claim explicitly assumes the bounded extension; the group-size bound above
does not depend on the arbitrary values of chi at unused scores.

The proofs use complex characters only as mathematical witnesses. The
rational implementation of Sections 1-3 does not import them as uncharged
constants. These bounds count coordinates/character terms, not gates in an
arbitrary circuit that might implicitly represent many coordinates and share
work through a different rule. They do not rule out the corrected objective
of a general joint orientation-and-spectral scalar compiler.

## 5. A terminal nonlinear reader alone does not repair this family

A precise proposed repair is to keep the same group-valued determinant but
replace its terminal linear reader by an arbitrary polynomial circuit F in
its terminal coordinates, with coefficients polynomial in z. Assume it gets
no other p-dependent intermediates. All determinant coordinates are
homogeneous of degree n in the independent p_ij. Decompose F by its degree
in those coordinates. Its degree-k part has p-degree kn; therefore only
its degree-one part can contribute to the required output of p-degree n.

That degree-one part is sum_g c_g(z) D_g (other spectral slots vanish at the
terminal determinant). For a permutation sigma, compare the coefficient of
the distinct p-monomial product_i p_i,sigma(i):

    c_(rho(sigma))(z) sgn(sigma) z^E(sigma) = z^E(sigma).

In the polynomial integral domain this forces c_(rho(sigma))(z)=sgn(sigma).
Thus the group score must still separate the signs, and Section 4 applies.
Nonlinear terms may vanish by algebraic identities, but cannot supply the
missing degree-n component. The same argument permits extra terminal
z-only coefficients; it does not presume a scalar permanent intermediate.

This lemma concerns a fixed certificate and a polynomial terminal reader.
It does not address readers with additional lower-degree p-dependent wires,
fusion-dependent phases, rational divisions, or different intermediate
representations. Supplying such wires creates a genuinely different search
problem; no closed polynomial rule for them is obtained here. Thus the
positive constructions are retained, but no unsupported repair is promoted
to a general solution.

## 6. Checks and reproducibility

Run `python verify_phase_chain.py`. It validates all permutations for the
small certificates, the large cyclic certificate through n=6, and the F8
collision examples. It then checks both scalar constructions for n=1..4 on
four label patterns (including repeated, negative and random labels), eight
legal numerical inputs each, and one full formal-z table per pattern.
Total: 256 numerical tables and 32 formal polynomial tables, including every
zero output slot. It records exact scalar counts and literal bit lengths in
`phase_chain_checks.json`. The maximum literal bit length in these builds
is 3, coming from the determinant's small integer denominators.

The bounded exploratory CP-SAT script uses a gauge with first row/column
zero and one unrestricted parity bit for every group element. This gauge
loses no solution: adding row/column potentials translates every permutation
score by the same group element, which can be absorbed into the reader.
For n=5 it returned INFEASIBLE for cyclic orders 3,4,5 and XOR order 4;
cyclic orders 6,7,8 and XOR orders 8,16 timed out with UNKNOWN. The latter
are not infeasibility results. These finite searches are not needed for
the analytic lower bound. Their parameters and outputs are preserved in
`search_phases.py`, `search_n5_cyclic.json`, and `search_n5_xor.json`.

The frozen full-size development evaluator was not run because these
small-case constructions do not supply a general polynomial candidate.
No coordinator held-out evaluation was accessed.
