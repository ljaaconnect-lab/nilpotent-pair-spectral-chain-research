# Constructive characteristic-two lifting attempt

Status: an exact sign-correction identity, a polynomial first lift, a checked
normal-ordering formula, and two exact Fourier-rank calculations were obtained.
No uniform polynomial scalar source circuit was obtained. Nothing below is a
lower bound against arbitrary scalar DAGs. The original candidate, `dag.py`,
and the frozen evaluator were not changed. The development score is `null`:
there is no new exact scalar candidate to submit to that evaluator.

All identities are first proved with independent entries b_ij and can then be
substituted with b_ij = p_ij z^(2^(in+j)). Derivatives below are a derivation
device, not uncharged gates of the required output circuit.

## 1. An actual sequence of precision lifts

Write D(B)=det(B), d=n(n-1)/2, N_ij=b_ij ∂/∂b_ij, and

    Ω = Σ_{i<k, j>l} N_ij N_kl.

For a permutation monomial M_σ, Ω M_σ = inv(σ) M_σ. Consequently

    per(B) = Σ_{r=0}^d (-2)^r binom(Ω,r) D(B),                 (1)
    binom(Ω,r) = Ω(Ω-1)...(Ω-r+1)/r!.

Indeed, the coefficient multiplier on M_σ is

    (-1)^inv(σ) Σ_r binom(inv(σ),r)(-2)^r
      = (-1)^inv(σ) (1-2)^inv(σ) = 1.

This is also the exact Taylor expansion at q=-1 of
Q_B(q)=Σ_σ q^inv(σ) M_σ, evaluated at q=1. Its r-th Taylor
coefficient is (-1)^r binom(Ω,r)D.

Every binom(Ω,r)D has integral coefficients. Thus the terms with r<k
give per(B) modulo 2^k for integral inputs, coefficient by coefficient in z.
This does not use rational reconstruction, approximate arithmetic, or a
coefficient oracle. The issue is the increasing cost of producing the terms.

The first correction is genuinely polynomial:

    per(B) = D(B) - 2ΩD(B)  (mod 4),
    ΩD(B) = Σ_{i<k,j>l} b_ij b_kl ∂_ij∂_kl D(B).             (2)

Every displayed mixed derivative is a signed complementary (n-2)-minor.
Using an O(n^4) division-free determinant compiler gives a conservative
O(n^8) scalar gate bound for (2), including every minor; marked powers cost
an additional O(n^2). The only additional literals are small integers.
This first correction is an exact permanent circuit when n≤2, but not for
general n.

For n=3, p_ij=1, the six marked monomials have the following coefficients:

| σ (zero-based) | exponent | inv(σ) | D | D-2ΩD | per |
|---|---:|---:|---:|---:|---:|
| 012 | 273 | 0 | 1 | 1 | 1 |
| 021 | 161 | 1 | -1 | 1 | 1 |
| 102 | 266 | 1 | -1 | 1 | 1 |
| 120 | 98 | 2 | 1 | -3 | 1 |
| 201 | 140 | 2 | 1 | -3 | 1 |
| 210 | 84 | 3 | -1 | 5 | 1 |

The r=2 term corrects inversion count 2 but changes the last coefficient
from 5 to -7; the r=3 term adds 8 and completes the exact correction.
Keeping only a single lift cannot be justified by characteristic two.

## 2. Jacobi and a repaired normal-ordering recurrence

When B is invertible, C=B^(-1) gives the identity

    ΩD = D Σ_{i<k,j>l} b_ij b_kl (C_ji C_lk - C_jk C_li).     (3)

The products on the right are 2-by-2 minors of C. For larger derivative
orders Jacobi similarly gives complementary minors. Formula (3) is an
identity on invertible matrices and extends polynomially after clearing
denominators. It is not itself a legal compiler using inverse entries as
free leaves; complementary determinants provide the division-free version.

A common incorrect recurrence would treat repeated Ω applications as if
each new inversion used new cells. Repeated marks can share a cell. There
is an exact normal-ordering formula that handles this.

Let τ be a partial matching of rows to columns. Its vertices are its cells;
its inversion graph G_τ joins two cells whose row and column orders disagree.
Let c_r(G_τ) be the number of r-edge subsets of G_τ that cover all vertices.
The empty matching has c_0=1. Then

    binom(Ω,r)D
      = Σ_τ c_r(G_τ) (∏_{(i,j)∈τ} b_ij) ∂_τ D.             (4)

Only |τ|≤2r is needed. Proof: on a permutation monomial the left side
chooses r distinct inversion edges. The union of their endpoints is a
unique partial matching τ. Conversely every edge cover counted on the
right supplies one such choice. No endpoint is differentiated twice.

For a partial matching with sorted row list R and column sequence τ(R),

    ∂_τ D = (-1)^(ΣR+Στ(R)+inv(τ(R))) det B[R^c,τ(R)^c].     (5)

This gives a uniform scalar compiler for each fixed r: enumerate inversion
edge sets, combine equal endpoint matchings, and compile the complementary
determinants. A safe bound is n^(O(r)); auxiliary count literals have
O(r log(n+1)) bits. The constructor has the same n^(O(r)) dependence.
This does not become a fixed polynomial when r is allowed to grow with n.

Equivalently, repeatedly applying a scalar automatic-differentiation
compiler for Ω multiplies its size by a polynomial in n at each step.
Polynomially many steps are not a polynomial total bound. The coefficients
1/r! are harmless (O(n^2 log(n+1)) bits); circuit growth is the unresolved
part. The polynomial-dimensional Krylov span {D,ΩD,...,Ω^dD} also does not
supply its coordinates or a scalar implementation for free.

## 3. Resumming the marked inversions by a quadratic Gauss sum

The total coefficient of each partial matching in (1),(4) can be computed
without iterating all r-edge subsets. Inclusion-exclusion gives

    g(G) = Σ_r (-2)^r c_r(G)
         = Σ_{S⊆V(G)} (-1)^(|V|-|S|+|E(G[S])|).             (6)

This is a quadratic Boolean Gauss sum. There is a concrete O(|V|^3)-bit-
operation elimination algorithm. Pick a quadratic edge xy and write the
phase as xy+xL+yM+R, where L,M are affine linear forms in the remaining
variables. Summing x,y gives exactly 2(-1)^(R+LM). Replace the phase by
R+LM, reducing squares by v^2=v, and continue. At the end an isolated
nonzero linear term gives zero; otherwise the remaining sum is a signed
power of two. The resulting literal needs O(|V|) bits. This algorithm
is implemented as `gauss_elimination` and checked on all permutations
through n=6. Thus there is the exact resummed identity

    per(B) = Σ_partial matchings τ g(G_τ)
                    (∏_{(i,j)∈τ} b_ij) ∂_τD.              (7)

This is progress on the cost of each weight, not on the number of τ.
The displayed enumeration has Σ_s binom(n,s)^2 s! indices (1,441,729
at n=8), before zero pruning. No polynomial contraction of that sum was
found. In particular weights of large support do not all vanish:
for a reverse matching the graph is K_s and g(K_s), s=0,...,12, is

    1, 0, -2, 4, -4, 0, 8, -16, 16, 0, -32, 64, -64.

Jacobi rewrites every derivative factor as a minor, but standard
Cauchy–Binet sums products of two determinants over one common subset.
Here g depends jointly on the row order and the column order of each
bijection inside that subset. Treating it as an independent row weight or
column weight would discard that dependence. This identifies a specific
missing contraction identity; it is not a theorem forbidding one.

There is also a Pfaffian interpretation of each local weight: for an
even-size ordered subset S of a permutation's cells, the Pfaffian of the
skew matrix with upper entries sign(τ(j)-τ(i)) equals the sign of the
restricted permutation. An odd subset can be augmented by a final dummy
element. Hence (6) can be reorganized through Pfaffian minor identities.
This reorganizes a weight for a fixed τ. It does not remove the sum over
τ in (7); that latter step remains unconstructed.

## 4. Exact ranks of the global inversion chirp

On all m=n^2 Boolean cell variables put

    Q(x) = Σ_{i<k,j>l} x_ij x_kl  in F_2.

Its polar matrix K has entry 1 precisely for a crossing pair of cells.
The following rank is exact:

    rank_F2 K = n(n-1).                                    (8)

Proof. Regard an input to K as a matrix X. If Y=KX then

    Y_ij = Σ_{k>i,l<j} X_kl + Σ_{k<i,l>j} X_kl,
    Δ_i Δ_j Y_ij = X_(i+1),j + X_i,(j+1).

Thus a kernel vector must be Hankel, X_ij=h_(i+j). Vanishing boundary
differences impose

    Σ_{s=i+1}^{i+n-1} h_s = 0,  0≤i≤n-2.

These n-1 conditions on 2n-1 Hankel coefficients are independent. They
also suffice: they make the first row and column of Y zero, and mixed
differences then make all of Y zero. Hence nullity is n, proving (8).

For a quadratic Boolean phase with polar rank r, its Walsh transform
has exactly 2^r nonzero coefficients, all of absolute value
2^(m-r/2) before normalization. To see this, square the absolute Walsh
sum at a and shift one summation variable by v. The inner character sum
vanishes unless Kv=0; on the kernel the residual phase is linear. It
either sums to zero or to |ker K|. Thus the nonzero normalized magnitude
is 2^(-r/2), and Parseval gives support 2^r.

Consequently global Fourier expansion of the sign correction has exactly
2^(n(n-1)) terms. Each Fourier character would only change entry signs
in a determinant, but there are exponentially many such terms.

It is useful to exploit the row/column parity constraints first. On the
affine space where every row and column sum is 1 mod 2, use rectangle
basis vectors with ones at (i,j),(i,n-1),(n-1,j),(n-1,n-1), for i,j<n-1.
Set h=n-1. In these h^2 free variables the restricted polar matrix is

    K'_h = K_h + I⊗J + J⊗I,
    rank K'_h = h(h-1) = (n-1)(n-2).                       (9)

Here J is the all-ones matrix over F_2. For a proof apply the same mixed
difference argument. Kernel vectors are again Hankel X_ij=a_(i+j).
The boundary constraints now read

    Σ_{s=i}^{i+h} a_s = 0,  0≤i≤h-2,

giving h-1 independent conditions and nullity h. The base point of the
affine space only adds a linear term, which does not affect Walsh support
size. The restricted phase therefore still has exactly
2^((n-1)(n-2)) Fourier coefficients. This is an exact analysis of this
particular transform, not a lower bound on arbitrary representations
restricted to permutation matrices.

Finally, restricting the polar form to the n cells of an individual
matching gives its inversion-graph adjacency matrix, not the global K.
For the reverse matching this is J+I, of rank n for even n and n-1 for
odd n. Confusing these three ranks would incorrectly suggest a low-rank
quadratic correction. The verification script checks (8),(9) through
n=16 and explicitly computes Walsh support in small cases.

## 5. Two concrete failures of naive determinant/Pfaffian closure

For two row vectors a,b, the q-deformed two-column coefficients are
F_ij(q)=a_i b_j+q a_j b_i (i<j). If all of them were the 2-minors of a
single pair of deformed rows, they would satisfy the Plucker relation.
With a=(1,2,3,4), b=(5,6,7,8), q=-1+t,

    F_12 F_34 - F_13 F_24 + F_14 F_23 = -136t+280t^2.

Thus even the first infinitesimal correction does not preserve this
decomposable exterior state. This rules out that particular sharing
ansatz, not an enlarged Pfaffian matrix or a general scalar circuit.

Likewise a local number-conserving exterior crossing has vacuum weight
1, the one-particle block [[0,1],[1,0]], and necessarily the double-
occupancy weight det([[0,1],[1,0]])=-1. Changing that weight to q=-1+t
already violates the exterior-power rule at first order. A Gaussian
crossing network cannot absorb this local deformation without additional
structure. No claim is made about arbitrary Pfaffian gadgets.

There is also no entrywise rescaling b_ij↦s_ij b_ij that turns det into
per for a general 3-by-3 matrix. Multiplying the three even-permutation
coefficient equations uses every s_ij once and gives +1; multiplying
the three odd-permutation equations uses exactly the same entries and
gives -1. The contradiction holds over characteristic zero. For a
generic q deformation the analogous products require q^4=-q^5.

## 6. Why precision and reconstruction do not finish the scalar compiler

For a rational supplied a_ij=u_ij/v_ij of bit length at most L, scale row
i by D_i=∏_j v_ij^2. The entries' amplitudes become integers

    (u_ij^2+v_ij^2) ∏_{l≠j} v_il^2,

with O(nL) bits. Because the cell addresses distinguish permutations,
each coefficient of the scaled target has O(n^2 L+n) bits. Polynomially
many 2-adic digits would therefore suffice for *coefficientwise*
reconstruction if those coefficients were already accessible.

That observation supplies neither a polynomial compiler for all those
digits nor a legal scalar operation that extracts the bounded integer
representative of every coefficient in a compact circuit. Lifting
residue representatives at the circuit's literals and gates only gives
a polynomial congruent to the target. Coefficientwise carry removal is
an additional operation, absent from the +,-,* model. A single image
modulo 2 has no unique lift: D and D+2H have that image for arbitrary H.
Hensel lifting would require a supplied small system with a suitable
Jacobian and a uniquely specified solution; none has been constructed.

One precise next hypothesis is a polynomial-size implicit system
F(t,y)=0, with polynomially many unknown series, that contains the desired
q-deformation as one coordinate and has an invertible Jacobian at t=0.
If the system and its initial solution were uniformly supplied, Newton
iteration modulo t^K would indeed use polynomially many scalar gates
in the system size and K (truncated series multiplication is charged).
What is absent is that system, not the precision-doubling machinery.
The spectral equation for Ω alone does not provide it: the q-deformation
is annihilated by a degree-(d+1) Euler differential operator, but the
space of solutions has d+1 independent coefficients. Supplying only
the value at q=-1 leaves d initial data undetermined. Naming these
unknown jets or complementary minors in an implicit state vector does
not show that the state vector has polynomial size or a closed update.

Numerical evaluation does not repair the symbolic issue. Already for
p_ij=1, evaluating at z=2 produces an integer with at least
2^(n^2-1)+1 bits, while the polynomial is meant to stay compressed in z.
Interpolation at ordinary scalar points has degree at least 2^(n^2-1).
At z=0,1,-1 the outputs can be small, but those values do not reconstruct
the symbolic polynomial. Rational reconstruction alone is therefore
not a scalar-DAG construction of P_A(z).

## 7. Reproducibility and exact scope

Run `python verify_lifting.py`. The recorded `lifting_checks.json` reports:

* 15 exact instances of the full inversion lift and all precision truncations;
* 15 checks of the inverse-minor Jacobi formula using Fraction arithmetic;
* normal-ordering checks for r=0,1,2,3 on a 4-by-4 integer matrix;
* both polar rank formulas for n=1,...,16;
* explicit full-grid and affine-subspace Walsh transforms;
* the marked n=3 counterexample and exact Plucker polynomial.

These are checks of proved identities, not evidence for a uniform
polynomial permanent circuit. No held-out material was accessed and the
frozen development evaluator was not run without a new candidate.
