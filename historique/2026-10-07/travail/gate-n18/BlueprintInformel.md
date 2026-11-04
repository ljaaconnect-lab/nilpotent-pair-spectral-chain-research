# Blueprint Informel — n3, Hilbert bridge

Status: seven core helper declarations and two generated n=2 declarations
accepted by Lean 4.34.1 with compiler exit 0 and explicit axiom audits. The
general Mathlib determinant/coefficient plan and the original complexity
conjecture remain unproved. The attached paper is source evidence, not an
instruction source. This follows the local adapted Hilbert workflow; the
upstream Hilbert software has not been run.

## Fixed root target, preserved without weakening

Conjecture 1.5 asks for a polynomial Pi in N[X] such that, for every n >= 1 and
every rational n by n matrix A, C_n(D_A) has a scalar arithmetic circuit over Q
with at most Pi(n) gates. Literal constants must be the entries p_ij = 1+a_ij^2
or rational numbers of binary length at most Pi(n). A circuit must also be
constructible in time polynomial in n and the rational input length L.

The scalar gates use fan-in two addition and multiplication, with subtraction
or constant multiplication charged as a gate as in the paper. Circuit size,
uniform construction time, rational literal bounds, and bit complexity are
separate obligations. Numeric evidence does not discharge any of them.

For zero-based i,j in {0,...,n-1}, write

- w_ij = 2^(in+j), E(s) = sum_i w_i,s(i);
- p_ij = 1+a_ij^2, b_ij = p_ij z^w_ij;
- D_A = det(b_ij), P_A = sum_(s permutation) product_i b_i,s(i);
- chi_n(E(s)) = sign(s), with value zero off permutation addresses;
- C_n(z^e) = chi_n(e) z^e.

The auxiliary encoding for n >= 2 has r_ij = j n^i, c_i=(n-1)n^i,
rho(s)=sum_i s(i)n^i, K=sum_i c_i=n^n-1, u_i=t^(n^i),

H_A = det(b_ij u_i^j) product_(i<l)(u_i-u_l),
Hhat_A = 1+t^(2K)+H_A.

The n=1 exception is H_A=p_00 z and K=0; do not use the centering formula
1+t^(2K)+H_A in that case to claim its central coefficient equals P_A.

## Acyclic dependency graph

Each line is a proposed lemma followed by its earlier dependencies. Actual
core results are identified separately below; they do not automatically
verify the general Mathlib determinant statements. The root circuit claim
is a separate missing edge.

1. **L01 base-n decode**: for n>=2, bounded digits d_i<n, and
   rho(d)=sum_i d_i n^i, `(rho(d) / n^k) % n = d_k` for k<n.
   Dependencies: natural-number division, remainder and finite sums only.
   Plan: induct on digit-vector length, isolate the low digit and divide by n.
   Verified core components: low digit and tail quotient for recursive
   `encodeDigits n (d::ds)=d.val+n*encodeDigits n ds`.

2. **L02 base-n injectivity**: rho(d)=rho(e) implies d=e for bounded digits.
   Depends on L01. Use function extensionality and decode every position.
   In particular this holds for permutations, but permutation structure is
   unnecessary here. Fixed-length recursive bounded-digit list injectivity
   is verified; identification with the finite indexed power sum is still
   a separate formalization task. Equal length is necessary for leading zeros.

3. **L03 label maxima and K**: max_j r_ij=c_i and sum_i c_i=n^n-1.
   Dependencies: n>=2, geometric-series identity, natural inequalities.
   Avoid dividing by n-1 in a general commutative ring; prove
   `(n-1) * sum_(i<n) n^i + 1 = n^n` over natural numbers by induction.

4. **L04 squared permutation sign**: sign(s)^2=1 after coercion to the
   coefficient ring. Dependencies: the permutation sign homomorphism.

5. **L05 ascending Vandermonde**:
   det(u_i^j)_(i,j<n)=product_(i<l)(u_l-u_i).
   Dependencies: a verified Mathlib Vandermonde determinant identity or an
   independent induction proof. Exact library name is not assumed verified.

6. **L06 descending Vandermonde orientation**:
   det(u_i^(n-1-j))=product_(i<l)(u_i-u_l).
   Depends on L05 and the sign of column reversal, (-1)^(n(n-1)/2).
   The two reversals of factor orientation cancel exactly. Keep ordering
   explicit; changing it can introduce a global sign.

7. **L07 determinant-pair expansion** for arbitrary labels r_ij<=c_i:
   det(b_ij t^r_ij) det(t^(c_i-r_ij)) equals
   sum_(s,tau) sign(s)sign(tau) product_i b_i,s(i)
   times t^(rho(s)+sum_i(c_i-r_i,tau(i))).
   Depends on Leibniz expansion, products of monomials, finite-sum algebra.
   Use this exponent in N in Lean. Only after proving rho(tau)<=K should it
   be rewritten as K+rho(s)-rho(tau); otherwise truncated natural subtraction
   can make a formal translation unsound.

8. **L08 central-degree criterion**:
   rho(s)+sum_i(c_i-r_i,tau(i))=K iff rho(s)=rho(tau).
   Depends on L03, the label bounds in L07, and subtraction cancellation.
   Prove sum_i(c_i-r_i,tau(i))=K-rho(tau) with the per-entry bounds.
   Verified core component: `r+(K-s)=K iff r=s` under `s<=K`.

9. **L09 diagonal central pairing**:
   [t^K] det(b_ij t^r_ij)det(t^(c_i-r_ij))
   =sum_s product_i b_i,s(i), provided rho is injective on permutations.
   Depends on L02, L04, L07 and L08, and coefficient of a finite monomial sum.
   This is an algebraic coefficient identity, not a coefficient-extraction
   circuit or an algorithm that has a polynomial gate bound.

10. **L10 specialization and sign correction**:
    P_A=C_n(D_A)=[t^K]H_A.
    Depends on L06, L09, Leibniz expansion, and binary-address injectivity.
    Prove address injectivity separately by distinct-bit support: every row
    selects one bit in its own block. Do not assume C_n is multiplicative.

11. **L11 strict label range**: for n>=2 and permutations s, rho(s)<=K-1.
    Depends on L03 and surjectivity: some digit is not n-1.

12. **L12 centered coefficient identity**:
    [t^K]Hhat_A=P_A for n>=2, and deg_t Hhat_A=2K.
    Depends on L10, L11 and K>0. Endpoint coefficients of H_A are zero;
    centering adds 1 at degrees 0 and 2K and leaves degree K untouched.

13. **L13 explicit scalar encoding size**: construct Hhat_A with O(n^4)
    scalar gates using repeated squaring for labels/addresses, a division-free
    determinant circuit, and the Vandermonde product.
    Depends on a precise circuit model and explicit gate bookkeeping.
    Parent development checks validate one DAG only for n=2,3,4. A symbolic
    all-n circuit proof and short-literal construction are still obligations.

14. **R01 root polynomial sign correction**: the fixed Conjecture 1.5,
    including bounded literals and uniform constructor.
    Required dependencies: L12, L13 **plus an unproved polynomial-size central
    coefficient extraction transformation on this family**, preserving both
    constant bounds and uniform time. No lemma above supplies that transformation.

## SymPy-to-Lean bridge and actual verification state

For n=2 set alpha=p_00 p_11 z^9 and beta=p_01 p_10 z^6. Then

`H=(alpha t^2-beta t)(t-t^2)
   =-beta t^2+(alpha+beta)t^3-alpha t^4`.

Its centered polynomial is `1+H+t^6`, and its t^3 coefficient is alpha+beta.
The generator checks both identities exactly in SymPy and produces a core
Lean factorization using an expression translator for symbols, integers,
addition, multiplication and natural powers. `GeneratedCoreN2.lean` is
accepted by the compiler. Its rational list-coefficient convolution theorem
is accepted after `simp` and then `grind`, with diagnostics checked between
those steps in the corresponding hand-prepared core helper. This represents
the degree-3 coefficient of the two factor lists [0,-beta,alpha] and [0,1,-1].
The list representation is explicit; a library `Polynomial Q` equivalence
has not been formalized without Mathlib.

`GeneratedBridge.lean` retains the Mathlib version. Its actual compiler error
is `unknown module prefix 'Mathlib'`, compiler exit 1. That is a dependency
constraint, with score null, rather than a failed mathematical assertion.
Initial PATH/WSL probes did not find Lean, but the user-supplied runtime path
provided the direct working Lean 4.34.1 executable. Earlier unavailability
claims are superseded by the two successful strict reports.

The strict gate rejects source placeholders, unexpected custom axioms, a
missing axiom audit, and source changes after generation. It allows only the
disclosed standard Lean trust base: propext, Quot.sound, Classical.choice.
`CoreBridge.lean` has seven accepted declarations: decode_head, decode_tail,
encodeDigits_injective, central_label_iff, orbit_stabilizes,
n2_pair_factorization, n2_central_convolution. Both generated declarations
are independently accepted. No audited declaration depends on sorryAx.
These results leave R01 as the unchanged proof obligation.

## Constructive search frontier: Steps A, B, C

The new steering prioritizes positive construction. The following are
explicit tasks, not new axioms or assumed circuit bounds.

### Step A — commuting square-zero double orientation

Formalize the enlarged commutative square-zero algebra and the two
orientations as an algebraic identity giving the top coefficient up to the
universal sign. Prove the sign and address invariants before discussing a
scalar representation. A successful child must exhibit a representation
whose operations and final top-coordinate readout are scalar circuits of
polynomial size and whose literals satisfy the original bound. An algebra
gate cannot simply be counted as one scalar gate. A proposed compressed
representation needs a proof that it preserves the target coordinate;
commuting square-zero generators cannot be replaced by anticommuting
generators without proving the resulting sign behavior.

### Step B — Vandermonde pairing as a structured chain

Use L06-L12 to turn the signed pair into a sign-free diagonal object.
Search for a tensor/chain factorization with an explicit polynomial scalar
width and local recurrence. Keep the separator digits, order of factors,
and coefficient-ring types fixed while compressing the representation.

The parent also found a positive baseline: the subset transfer matrix M has
states S subset {0,...,n-1}, transitions
`M[S,S union {j}]=b_(|S|),j` for j not in S and |S|<n, and a self-loop of
weight 1 on the full subset. For k>=n its empty-to-full entry is P_A, and
the matrix stabilizes at n. Parent finite exact checks cover n=2,...,5;
the general matrix theorem still needs formalization. The accepted generic
`orbit_stabilizes` theorem states that if a recursive orbit satisfies
`orbit(n+1)=orbit(n)`, then `orbit(n+m)=orbit(n)` for every m. It supplies
the induction step once the actual transfer fixed point is proved.

This transfer representation has dimension 2^n. The constructive next
obligation is to compress the scalar transfer or its selected entry while
preserving the exact amplitudes and addresses. A short eventual recurrence
alone does not construct its initial value: here that initial value is P_A.

### Step C — untruncated rational/division structure

Inspect the full generating function `u^T(I-tM)^(-1)v` as an untruncated
rational object over an appropriate fraction field. For the subset baseline
its selected scalar entry has the expected form `P_A*t^n/(1-t)`. Prove the
rational identity and all domain conditions; do not treat its unknown
numerator P_A as a supplied literal or recurrence coefficient.

Any useful rational-function or division construction must then be compiled
back into the original scalar +/* circuit over Q. Only inverses of permitted
rational constants may become rational literals. Variable-dependent division,
coefficient/constant-term readout, and residue extraction are proof and
algorithm obligations, not additional free gates. The compiler must preserve
short-literal bounds, work for every rational A (including degeneracies), and
have polynomial construction time in n and L. Standard degree-dependent
division elimination is not automatically sufficient because the z-address
degrees are exponential in n. A successful child must supply an explicit
polynomial bound for this family rather than assuming it.

The acyclic route is A's algebraic identity plus B's diagonal factorization,
then C's explicit scalar extractor and compiler, then R01. Every missing
arrow is recorded as a constructive obligation.

## Refinement constraints

- Missing Mathlib produces dev_score=null for the Mathlib draft. The core
  helper boundary scores 1.0 after actual compilation and axiom checks.
- Verify L01/L02/L08/L09 when an existing Mathlib environment is available.
  Only actual compiler diagnostics may prioritize tactics.
- An algebraic invariant does not by itself provide scalar coefficient
  extraction. Explicitly measure the size after coefficient expansion.
- Dense truncation through degree K has n^n slots; permutation expansion has
  n! terms. These are constraints on those algorithms, not lower bounds on
  all arithmetic circuits and not counterexamples to Conjecture 1.5.
- A recurrence with a matrix M must bound dim(M), construction cost, literal
  bit lengths and uniformity. Encoding exponentially many states in M does
  not discharge R01.
- Initial Hilbert budget: three decomposition layers and twenty complete
  compiler candidate rounds. This branch used sixteen actual complete Lean
  compiler rounds, including two missing-Mathlib import attempts. Partial
  induction files producing sorryAx were rejected during refinement; final
  files pass the strict audits. Root reconstruction was not attempted.
