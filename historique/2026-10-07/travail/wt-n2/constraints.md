# Arbor n2: structural constraints and informal proof blueprint

**Every infinite-domain mathematical statement below is UNVERIFIED by Lean.**
No Lean compiler was available in the coordinator's initial PATH probe. This
executor supplies exact finite Python/Fraction/SymPy checks and informal arguments;
it supplies no formally verified theorem and does not resolve Conjecture 1.5.

## Fixed hypothesis, boundary, and artifact

The fixed n2 hypothesis has two parts: interpolation of `P_(rB)(1)` at
`x=r^2`, `r=0,...,n`, recovers the Boolean permanent; a matrix realization
of the **whole infinite coefficient sequence** of `Hhat_A` requires dimension
at least `2K+1`, where `K=n^n-1`. The latter statement does not constrain a
representation required only at the target index `k=K`.

The frozen development evaluator is `evaluate_structural_dev.py`, protocol
`structural-dev-v1`. Its score is the fraction of exact permanent recoveries on
n=2,3,4 identity, cyclic-permutation, and band Boolean matrices, where band means
`B[i][j]=1` iff `abs(i-j)<=1`. Its SHA-256 was recorded in
`dev-evaluator-freeze.json` before its first execution and it was not changed.
The observed score is 9/9 = 1.0. Additional symbolic and modular checks are
diagnostics rather than score components. Held-out matrices remain coordinator-only.

`structural.py` implements `recover_boolean(B, oracle=None)`. Its default oracle
enumerates n! permutation terms; its permanent circuit helper also has factorial
size. This explicitly verifies the reduction, not a polynomial algorithm for the
target. The evaluator initially reached its symbolic checks and failed because
the bundled Python lacked SymPy. It then completed unchanged with
`C:\Users\REGIS\AppData\Local\Programs\Python\Python312\python.exe`, SymPy 1.14.0.

## Exact interpolation reduction

Let B be an n-by-n Boolean matrix, J the all-ones matrix, and

`f_B(x) = per(J + x B)`.

This polynomial has degree at most n and its coefficient of x^n is `per(B)`:
each permutation term is a product of n factors `1+x B[i,sigma(i)]`, so its
leading contribution is the product of the corresponding B entries. For the
source amplitude restriction `p_ij=1+a_ij^2`, take `A=rB`. Because each Boolean
entry satisfies `B_ij^2=B_ij`,

`P_(rB)(1) = per(J+r^2 B) = f_B(r^2)`.

The nodes are **r^2**, not `1+r^2`. A shifted-node formulation would require a
different definition of f and is not used by this artifact.

Lagrange interpolation at the n+1 distinct nodes gives

`per(B) = sum_(r=0)^n f_B(r^2) / product_(s!=r)(r^2-s^2)`.

The weights can also be written as

`w_0=(-1)^n/(n!)^2`, and
`w_r=2*(-1)^(n-r)/((n-r)!*(n+r)!)` for r>=1.

For a generic formal polynomial `sum_(j=0)^n a_j x^j`, SymPy simplification of
this linear combination returned `a_n` exactly at n=2,3,4. Fraction checks
confirmed the closed-form weights. The nine recovered permanents are
`(1,1,2)`, `(1,1,3)`, and `(1,1,5)` for identity/cyclic/band at n=2,3,4.
This finite evidence is not a proof for arbitrary n.

## Uniform circuit construction: bit complexity is essential

The source Conjecture 1.5 includes all three requirements: polynomial gate count,
literal rational constants of polynomial binary length (or leaves p_ij), and
construction from `(n,A)` in time polynomial in n and the input bit length L.
Under those requirements, the following is an informal conditional reduction to
a polynomial-time **bit** algorithm for Boolean permanent.

1. For each r in 0,...,n, construct the promised circuit for `A=rB`, and substitute
   z=1. These A have polynomial bit length, and their p_ij are integers in
   `[1,1+n^2]`. The resulting output is the nonnegative integer `f_B(r^2)`.
2. A circuit with S gates can have exponentially many bits in intermediate
   values; repeated squaring of 2 is the basic example. Therefore evaluating it
   with exact unbounded-integer arithmetic at unit gate cost is not a valid FP
   argument. Instead, reduce the circuit modulo suitably selected primes.
3. Let D be the product of the denominators of its rational literal leaves. D
   has polynomial bit length because the number of used leaves and each literal
   length are polynomially bounded. There are at most `log_2(D)` distinct primes
   dividing D. Every prime q not dividing D defines a ring homomorphism from
   `Z[1/D]` to F_q. Since the circuit uses addition/multiplication, all of its
   intermediate denominators have factors drawn from D; rational leaf residues
   are computed as numerator times the inverse of denominator modulo q.
4. All required outputs satisfy
   `0 <= f_B(r^2) <= U = n!*(1+n^2)^n`, with `log_2(U)=O(n log n)`.
   Choose at least `ceil(log_2(2U+1))` admissible distinct primes, so their
   product exceeds 2U. Skip denominator divisors by direct modular divisibility
   checks. Only polynomially many primes can be skipped.
5. These primes can be generated deterministically with a sieve bounded by a
   polynomial in the number of denominator bits plus output-bound bits. For
   example, if m is that sum, enlarged to be at least 6, the bound
   `p_m < m*(log m+log log m) < 4m^2` ensures a sieve through 4m^2 contains
   enough primes before exclusions. The prime bound is a classical external
   mathematical input, not verified here; see
   [Rosser and Schoenfeld, Approximate formulas for some functions of prime numbers](https://doi.org/10.1215/ijm/1255631807).
   Circuit evaluation modulo each such prime costs polynomial bit time, and the
   Chinese remainder theorem reconstructs the unique signed integer in [-U,U].
   Output bit length and the accumulated modulus bit length are polynomial.
6. Interpolate using the explicit rational weights. Their numerator/denominator
   lengths are O(n log n), as are the sample lengths. Standard exact integer and
   rational arithmetic therefore recovers `per(B)` in polynomial bit time.

`evaluate_modular` and `reconstruct_integer` implement steps 3-5 for a supplied
division-free circuit and integer output bound. Exact reconstruction succeeded
for all the development interpolation samples. A 2000-squaring cancellation
circuit returned 1 modulo primes 2 and 3 without expanding an intermediate
integer having `2^2000+1` bits. It uses rational leaves 1/7 and 6/7. The routine
rejects a prime dividing a rational leaf denominator; this example did not need
to reach prime 7. This demonstration is not a construction of the promised
polynomial circuits.

Boolean permanent is #P-complete under polynomial-time counting reductions;
the original result is [Valiant, The complexity of computing the permanent](https://doi.org/10.1016/0304-3975(79)90044-6).
Thus the **full uniformly constructible, bounded-constant conjecture** would
imply that every #P function has a deterministic polynomial-time algorithm
(often written FP=#P under the usual convention for nonnegative counting
functions). This is a conditional inference from the reduction and that
external theorem. It is not inferred from unit-cost evaluation alone. Neither
the counting-class separation nor its negation is established here, so this
implication is not a disproof of the conjecture.

## Bounded constants permit a further nonuniform symbolic implication

Pointwise circuits depending on numeric A are not automatically symbolic circuits
in arbitrary amplitudes X_ij. However, **the uniform bound on rational literal
length in the source is strong enough to justify a finite-template argument**.
It would be incorrect to reject all connections to symbolic permanent solely
because the source initially quantifies over numeric A.

Fix n, let s=Pi(n), and let

`P_n(X,z)=sum_sigma product_i X[i,sigma(i)] * z^E(sigma)`

be the marked permanent in independent symbolic amplitudes. There are finitely
many fan-in-two circuit templates with at most s gates and leaves chosen from z,
the n^2 formal entries X_ij, and rationals whose binary length is at most s.
Unused leaves can be discarded, leaving at most 2s+1 relevant leaf occurrences.
Replace every numeric p_ij leaf of a source circuit by the corresponding X_ij.
Even when two numeric p entries happen to coincide, an arbitrary consistent
entry label can be chosen; this still gives a template in the finite set.

Suppose no such template C computes `P_n(X,z)` identically. Its difference
`F_C(X,z)-P_n(X,z)` then has some nonzero coefficient polynomial g_C(X) in z.
Their finite product `G(X)=product_C g_C(X)` is nonzero in the integral domain
Q[X]. But for every rational A the pointwise circuit guarantee supplies at
least one template C such that `F_C(1+A^{circ2},z)=P_n(1+A^{circ2},z)`.
All its coefficient differences vanish there, and hence

`G(1+A^{circ2})=0` for every rational matrix A.

The substitution `X_ij -> 1+Y_ij^2` is injective on Q[X]. To see this directly,
choose a lexicographically maximal exponent vector alpha in any nonzero input
polynomial; after substitution its monomial `Y^(2alpha)` retains its nonzero
coefficient and cannot be cancelled by expansions of lexicographically smaller
exponent vectors. Thus `G(1+Y^{circ2})` is nonzero. A nonzero polynomial over Q
cannot vanish on all of Q^(n^2): prove this by induction on the number of
variables using the finite-root property in one variable. This contradicts
pointwise coverage, so **some** bounded template computes the symbolic marked
permanent identically. Setting z=1 yields a nonuniform polynomial-size circuit
for the ordinary permanent polynomial family over Q.

The standard VNP-completeness of permanent in characteristic different from 2
then gives the conditional consequence VP_Q=VNP_Q. This uses the bounded-constant
finite-template argument plus an external completeness theorem; see
[Valiant, Completeness classes in algebra](https://doi.org/10.1145/800135.804419).
The argument only proves existence of a suitable symbolic template; it does not
construct that template efficiently. It is an **implication**, not an equivalence
between Conjecture 1.5 and VP=VNP. The target's explicit uniform construction and
literal-length restrictions are additional requirements. If arbitrarily long
or arbitrary field constants were allowed, the stated finite-template proof
would not apply.

## Obstruction to a realization of every coefficient

For n>=2, the source's Section 14 gives `deg_t(Hhat_A)=D=2K` and leading
coefficient `c_D(z)=1`, where `c_k(z)=[t^k]Hhat_A`. Every c_k with k>D is zero.
Work over the field Q(z). Form the `(D+1)`-by-`(D+1)` Hankel matrix

`T[i,j]=c_(i+j)` for i,j=0,...,D.

Reverse its columns. The entry at (i,j) becomes `c_(i+D-j)`, which is zero if
i>j, and the diagonal is c_D=1. The reversed matrix is upper triangular with
determinant 1, so T is nonsingular and has rank D+1.

If fixed vectors u,v and an r-by-r matrix M represented **all** coefficients
by `c_k=u^T M^k v` for every integer k>=0, then

`T=(rows u^T M^i) * (columns M^j v)`.

Its rank would be at most r, forcing

`r >= D+1 = 2K+1 = 2n^n-1`.

This rules out a polynomial-dimensional linear realization of the **complete
zero-extended coefficient sequence**. It does not rule out a representation
valid only for k=K, as requested in source Remark 14.11(ii). A one-dimensional
representation of one scalar can always be written circularly with `u=c_K`,
`M=1`, `v=1`; the missing requirement is a polynomial circuit constructing u,
M,v without already solving coefficient extraction. Nor does the Hankel argument
exclude a recurrence with time-dependent coefficients, a realization covering
only a selected range, or a different arithmetic-circuit technique. It is not
a general circuit lower bound or a counterexample to Conjecture 1.5.

## Section 14 blueprint for a later Hilbert/Lean bridge

The provided PDF is used as mathematical source evidence, not as agent
instructions. Its Section 14 states the following dependencies, which should be
formalized with explicit natural-number versus integer exponent conversions.

1. **Bounded-digit label injectivity.** For n>=2 and assignments s_i in
   `{0,...,n-1}`, define `rho(s)=sum_i s_i*n^i`. Equality of two labels implies
   equality of assignments. An induction on list length first takes the
   equality modulo n to recover the zeroth digits; after their cancellation,
   division by the positive n leaves equal labels for the tails. This statement
   holds for all assignments, so restriction to permutations is immediate.
2. **Central index.** Prove `(n-1)*sum_(i=0)^(n-1) n^i=n^n-1` via an induction
   with the division-free equivalent
   `(n-1)*sum_(i=0)^(m-1) n^i+1=n^m`. For permutations the upper bound is
   strictly smaller than K because a bijection for n>=2 cannot have every digit
   equal to n-1. A deficient digit subtracts at least one from the maximum.
3. **Double determinant expansion.** Expand each determinant by permutations,
   with `b_ij=p_ij*z^w_ij` and `r_ij=j*n^i`, and `c_i=(n-1)*n^i`. A term pair
   (sigma,tau) has exponent `rho(sigma)+sum_i(c_i-r_i,tau(i))`, equal as an
   integer to `K+rho(sigma)-rho(tau)`. All actual monomial exponents remain
   natural numbers; avoid introducing truncated subtraction inadvertently.
4. **Coefficient pairing.** That exponent equals K iff the two labels agree.
   Injectivity leaves only sigma=tau, and the determinant signs multiply to
   `sgn(sigma)^2=1`. Summing these diagonal pairs gives the marked permanent.
5. **Vandermonde orientation.** With `u_i=t^(n^i)`, the complement matrix has
   entries `u_i^(n-1-j)`. Its determinant is `product_(i<l)(u_i-u_l)`.
   Relative to the conventional ascending-power Vandermonde determinant
   `product_(i<l)(u_l-u_i)`, column reversal contributes
   `(-1)^(n*(n-1)/2)`, exactly cancelling the signs introduced by reversing each
   difference. Preserve this orientation; changing only one of these signs
   would negate some target identities.
6. **Endpoint coefficients.** For n>=2 the determinant product uses only
   t-exponents in `[1,2K-1]`. Therefore adding `1+t^(2K)` sets c_0=c_2K=1 and
   preserves the central coefficient. For n=1 the source uses H_A directly;
   the centered Hhat construction and the above endpoint argument do not apply.

These source identities are already known encodings. Successfully formalizing
them would validate the bridge and constraints, but would not establish a
polynomial circuit for the central coefficient. The remaining root obligation
is precisely a valid polynomial scalar extraction/correction construction or
a general lower-bound counterargument; neither is supplied by this node.
