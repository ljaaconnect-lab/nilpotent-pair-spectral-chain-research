# Permanental-adjugate implicit lift

Result: an exact square Newton system was constructed and executed for
n=3 and n=4. Its Newton compiler has polynomial overhead, a constant
invertible Jacobian at the identity, and no division gates. For general n
its coefficients still contain selected smaller permanents and explicit
Dodgson defects. The exact defect recurrence and index sharing were
counted; this recurrence has exponentially many states even with a common
pivot. No uniform polynomial closed system was obtained.

The frozen candidate and evaluator were not changed or run. The score
for a new general candidate is therefore null. This branch adds exact
polynomial identities and verification scripts, not a general lower bound
or a Lean certificate.

## 1. Exact permanental Dodgson defect

Let P=per(B), G_ij=∂_ijP, and
H_(ik;jl)=per(B with rows i,k and columns j,l removed), for distinct
rows and columns. Define

    K_(ik;jl) = (G_ij G_kl + G_il G_kj - P H_(ik;jl))/2.     (1)

This is an integral polynomial. It is not generally zero.
For the first two rows/columns write

    B = [ a  b  u^T ]
        [ c  d  v^T ]
        [ w  x   C  ],    h=per(C),  g_rj=∂_rj per(C).

The block expansion gives

    G_11 = d h + Σ_rj v_j x_r g_rj,
    G_22 = a h + Σ_rj u_j w_r g_rj,
    G_12 = c h + Σ_rj v_j w_r g_rj,
    G_21 = b h + Σ_rj u_j x_r g_rj.

Expanding P similarly and cancelling the terms involving a,b,c,d yields
the exact recursion

    K_B = Σ_{r=s or j=k} u_j v_k w_r x_s g_rj g_sk
        + Σ_{r≠s and j≠k} u_j v_k w_r x_s K_C(r,s;j,k).    (2)

Both sums use ordered r,s,j,k. The union condition in the first sum is
counted once. To prove (2), the coefficient of u_j v_k w_r x_s in
P h-G_11G_22-G_12G_21 is

    1_(r≠s,j≠k) h H_C(r,s;j,k) - g_rj g_sk - g_rk g_sj.

For distinct indices it is -2K_C. With a repeated row or column the two
products coincide, giving -2g_rj g_sk. This also proves integrality
and coefficientwise nonnegativity of K by induction.

For n=2 the defect is zero. For n=3, C has one entry and

    K_B = u v w x.

For n=4, C is 2-by-2, all nested K_C are zero, and the first sum of (2)
has exactly twelve monomials. These identities were verified as symbolic
polynomial identities, including all adjugate identities below.

Thus the permanent's plus-plus Dodgson relation differs from the
determinantal relation already at n=3. Replacing H by a quotient of two
products of G loses the explicit term 2K.

## 2. Adjugate defects and the first closed precision step

Use the orientation

    G B^T = P I + 2R,
    R_ik = Σ_{j<l} b_kj b_kl H_(ik;jl)  (i≠k),  R_ii=0.    (3)

The off-diagonal entry is half the permanent with row i replaced by
row k; the two equal rows account for the factor 2. This orientation
matches the verification code. Transposing R gives the corresponding
formula for B G^T and leaves the determinant expressions unchanged.

Also put

    S = (det(G)-P^(n-1))/2.                                 (4)

This is integral because modulo 2, P=D=det(B) and G is the cofactor
matrix. Let Ω be the inversion-counting operator of LIFTING_NOTES.md.
The following are polynomial-size first corrections:

    R0_ik = Σ_{j<l} b_kj b_kl det B_(ik)^(jl),
    S0 = -D^(n-2) ΩD.                                      (5)

They satisfy R0=R mod2 and S0=S mod2. The first follows directly from
(3). For the second, write P=D+2A mod4 with A=-ΩD, so
G=∇D+2∇A mod4. The cofactor matrix of ∇D is D^(n-2)B, hence

    det(G) = D^(n-1)+2D^(n-2)Σ_ij b_ij ∂_ijA  (mod4)
           = D^(n-1)+2nD^(n-2)A  (mod4).

Subtracting P^(n-1) leaves 2D^(n-2)A, proving (5).

These first corrections do not give an exact closure. In particular,
setting R=(GB^T-PI)/2 or S=(det G-P^(n-1))/2 as functions of the
unknowns simply makes the corresponding equations tautologies. Their
coefficients contain 1/2, so they cannot be used as smooth equations
modulo 2 after cancelling the very defect they were meant to determine.

There is also immediate growth under row replacements. If
E_ik=Σ_j b_kj ∂_ij and i,j,k are distinct, then

    E_jk R_ik = 3 T_(ijk;k),
    T_(ijk;k) = Σ_{|J|=3} (∏_{l∈J} b_kl)
                         per B_[i,j,k]^[J].                (6)

The corresponding matrix has three equal rows and permanent 6T.
Since v2(2!)=v2(3!)=1, this new state does not disappear at a higher
2-adic precision merely because another row was duplicated. More
generally repeated-row multiplicities generate divided-power states
indexed by compositions of n. Their distinct row multidegrees imply
linear independence over constant scalars; a full linear row-replacement
state representation has binom(2n-1,n) coordinates. This statement does
not exclude a nonlinear representation with input-dependent operations.

## 3. A genuine Newton system with an explicit inverse Jacobian

For every i≠j choose k(i,j) to be the smallest index outside {i,j}.
Use n^2+1 unknowns y=(P,G). The equations are:

* n row expansions Σ_j b_ij G_ij-P=0;
* for every i≠j, the Dodgson equation (1) for rows (i,k) and columns (j,k);
* one additional principal Dodgson equation for rows/columns (0,1).

Here H and K are coefficients of the system, meaning functions of the
input B which must themselves be constructed and charged.

At B=I, P=1 and G=I. If the right side of a linearized row equation is
u_i, of an off-diagonal equation is v_ij, and of the last equation is w,
the inverse Jacobian is explicitly

    δP = w-u_0-u_1,
    δG_ii = u_i+δP,
    δG_ij = v_ij  (i≠j).                                   (7)

Thus the Jacobian has determinant ±1 over the integers. No assumption
that det(B) is a unit for the final input is necessary: use the formal
path B(t)=I+t(B-I), start at t=0, and double t-adic precision.

Let total scalar circuit size of the required H,K coefficient functions
be s. Evaluating those circuits as truncated series through t^n costs
O(s n^2) gates using ordinary charged convolution. The equations and
their Jacobian have O(n^2) nonzero polynomial entries. Solving the
Newton linear system coefficient by coefficient uses (7) at each
degree, and costs O(n^2 m^2) gates at precision m. Summing doubling
precisions through n+1 gives O(n^4) additional gates. All added literals
are 0,1,-1,2; the constructor obeys the same polynomial bound.

The target has degree at most n in t. Once its n+1 coefficients have
been obtained, setting t=1 is an O(n)-gate sum and gives the exact
permanent. This argument works over the coefficient ring containing
the formal marked variable z: it never expands in z or interpolates
across its exponentially large degree.

This is a conditional scalar compiler of size O(s n^2+n^4), not a
proof that s is polynomial. For n=3 and n=4 the coefficients H,K above
use only permanents of size at most 2, so they really are explicit.
The implemented integer-arithmetic Newton solver returns:

| n | coefficients of per(I+t(B-I)) | value at t=1 |
|---|---|---:|
| 3 | 1, 9, 41, 98 | 149 |
| 4 | 1, 4, 30, 151, 217 | 403 |

The matrices are recorded in implicit_checks.json. For general n,
(2) reintroduces smaller permanents and K tensors. Polynomial precision
does not bound their construction cost.

## 4. Exact sharing counts, including the common-pivot proposal

Two coefficient-request patterns are distinguished below. The implemented
square Newton system uses k(i,j) above. The additional common-pivot probe
requests every H_(0i;0j), K_(0i;0j), i,j>0, recursively using each
submatrix's smallest row and column. This complete common-pivot family
is not identical to the square system's request list; in particular it
includes all its diagonal pivot pairs. Counts are reported separately.

For the common-pivot H recursion, after r descents a deleted row set has
size 2r and contains the first r indices. Necessity follows because each
step removes the current minimum. Sufficiency follows by pairing the
first r indices with the r other deleted indices. Columns are independent,
so the exact number of distinct submatrices at size n-2r is

    binom(n-r,r)^2.                                        (8)

At n=12 the counts are 1,121,2025,7056,4900,441, totaling 14,544.
These sets were explicitly generated for every n through 12.

K alone requires more states. After the first removal of an anchored
pair, recurrence (2) requests all internal row and column pairs. At
depth r≥1, its base matrix has deleted 2r rows and columns, each deleted
set containing index 0. Every such choice is reachable: select the
first anchored pair inside it, then remove its remaining elements in
arbitrary pairs. Each base needs all distinguished pairs. Hence its
exact K count is

    binom(n-1,2r-1)^2 binom(n-2r,2)^2,                      (9)

plus (n-1)^2 initial states. Stop at size 3 or 4, where K is explicit.
At n=12 these counts total 73,534,846. At the same time K requests
cofactor permanents after deleting any odd number d≥3 of rows and
columns including the original pivot. Their counts are
binom(n-1,d-1)^2. These are actual coefficient demands of (2), not
an assumption that all minors must be materialized.

Closing these permanent calls under the same common-pivot H,K recursions,
the number of distinct size-(n-d) permanent inputs, restricting to
size at least 2, is exactly

    1                                      for d=0;
    binom(n-1,d-1)^2                        for d=2 or odd d≥3;
    binom(n-2,d-2)^2                        for even d≥4.    (10)

Proof: an elementary call deletes either 2 elements or an odd number
at least 3, always including the current pivot. An odd total can be
deleted in one call, so precisely the original pivot is forced. An even
total ≥4 needs at least two calls, forcing the first two pivots. Conversely
use 2+2 for d=4 and 3+(d-3) for even d≥6; all remaining choices are free.
The construction can be made independently for row and column sets.
At n=12 this is 444,966 different permanent submatrices of size ≥2.

For the actual square Newton requests, the script directly generates
all H states through n=12. At n=12 the H layer counts are

    1, 133, 2868, 12249, 10211, 1008,   total 26,470.

Its K base sets are counted exactly by the following containment test.
A pair of deleted 2r-element sets is reachable iff it contains one of
the original requested row-pair/column-pair combinations; all subsequent
K pairs are unrestricted. Counting this test over sets and multiplying
by binom(n-2r,2)^2 avoids materializing all K tensors. At n=12 the
actual-square K count is 117,339,118. Even one fixed initial pair gives
binom(n-2,2r-2)^2 possible bases, so this particular recurrence's index
family is already exponential asymptotically.

The formulas for the common-pivot K and full permanent-call closures
were independently checked by explicit sets through n=8 and n=9,
respectively; their formulas give exact counts through n=12 and beyond.
These are statements about these explicit recurrences, not lower bounds
against arbitrary arithmetic circuits or a future contracted update.

## 5. Actual Newton convergence to a wrong lift when defects are frozen

There is an instructive scalar system with polynomial coefficients if
one freezes (5) instead of constructing exact R,S. Eliminating G gives

    f(X)=det(XI+2R0)-D X^(n-1)-2D S0.                       (11)

Modulo 2, f(X)=X^(n-1)(X-D). When D is odd the root X=D mod2 is
simple, so ordinary Hensel–Newton really does double precision.
Nevertheless this is generally the wrong root for the permanent.

For the legal amplitudes at z=1

    B = [[5,2,5],[5,2,2],[1,1,5]],

D=9, P=149, S0=288, and f(P)=-209124=4 mod8. The Newton root is
1 mod4, 9 mod16, and 2457 mod65536, whereas P is 1 mod4, 5 mod16,
and 149 mod65536. A second exact counterexample is recorded at n=4.
Thus a simple Jacobian and demonstrated precision doubling are not
sufficient evidence that the limiting solution is the intended source.

## 6. Verification and outcome

`python verify_implicit.py` performs symbolic n=3,4 block/adjugate/triple-
row checks, fifteen exact n=3,4,5 numerical identity checks, Jacobian
rank checks, actual integer formal-Newton construction at n=3,4, and
the incorrect frozen-defect Hensel lifts. `python count_shared_indices.py`
reproduces all counts and its independent set checks.

The positive result is the explicit inverse-Jacobian system and the
conditional polynomial compiler, with actual complete n=3,4 executions.
The missing general construction is a polynomial-cost computation of
its H,K coefficients or a different closed system that avoids this
recurrence's exponential index family. Merely adding R, K, or a matrix
of pair minors does not close the demonstrated update.
