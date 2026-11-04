# Arbor n16: reciprocal-determinant and Laurent recurrence route

This node investigates a new positive construction. Every general mathematical
argument here is **UNVERIFIED by Lean** in this node. Exact SymPy evidence is
finite symbolic evidence. There is no claim to have resolved Conjecture 1.5.
The inherited subset-transfer baseline is not rerun or used as this node's metric.

## A short recurrence whose initial data are cheap

For independent formal amplitudes B_ij let X=diag(x_0,...,x_(n-1)) and set

`D(y,x)=det(I-y X B)=sum_(j=0)^n d_j(x) y^j`, with d_0=1.

Define the reciprocal series

`1/D(y,x)=sum_(k>=0) h_k(x) y^k`.

Multiplying series gives the initialized order-n recurrence

`h_0=1`, `h_k=0` for k<0, and
`h_k=-sum_(j=1)^min(n,k) d_j h_(k-j)` for k>=1.

Unlike a recurrence initialized with the unknown permanent, this recurrence
starts with the explicit scalar one and zeros. Its coefficients are cheap to
construct. If T=XB, Newton trace identities supply

`d_k=-(1/k)*sum_(j=1)^k d_(k-j) tr(T^j)` for k=1,...,n.

The only divisions in this construction are rational literal constants -1/k;
no variable division, residue, coefficient, or determinant is a free gate.
The actual `RationalDAG` compiles dense matrix products, traces, Newton sums,
and reciprocal sums into binary scalar addition/multiplication gates.

The marked target is

`P_A(z)=[x_0 ... x_(n-1)] h_n(x)` after `B_ij=p_ij z^w_ij`.

The reciprocal-determinant coefficient identity is the squarefree case of
MacMahon's master theorem. The classical relation is also discussed in the
primary proof [Good, A short proof of MacMahon's Master Theorem](https://doi.org/10.1017/S0305004100036318).
For this squarefree case, a direct route is the formal identity
`1/det(I-T)=exp(sum_(k>=1) tr(T^k)/k)`: selecting a squarefree occupancy monomial
organizes the trace terms into disjoint directed cycles. Their unordered cycle
sets are precisely permutations, and each has positive weight. This is an
informal proof sketch, not a compiler-verified identity.

The corresponding n-by-n companion matrix has first row `(-d_1,...,-d_n)` and
subdiagonal ones. Its initial vector is `(1,0,...,0)`, and its kth power returns
h_k. This is a genuine small matrix representation **over Q[B,x]** with cheaply
constructed coefficients and initial data. The remaining coefficient functional
in x is charged explicitly; it is not one scalar gate in Q[z].

## Gate accounting and exact validation

With generic B leaves, the explicit DAG uses

`S(n)=(n-1)*(2n^3-n^2)+4n^2+n`

scalar gates to construct d_1,...,d_n and h_0,...,h_n as polynomials in B and x.
The terms in this count are n^2 gates to form XB, n-1 dense matrix products,
n traces, and the two triangular Newton/reciprocal recurrence tables. Rational
literal denominators are among 1,...,n and have O(log n) binary length.
Substituting the original marked B entries adds `2n^2-1` gates. Thus the cheap
recurrence part is fully within the original scalar arithmetic model, with
additional auxiliary variables before the final contraction.

For validation only, the DAG is evaluated in

`Q[B][x_0,...,x_(n-1)]/(x_0^2,...,x_(n-1)^2)`.

The quotient map preserves the desired squarefree coefficient. Every projected
coordinate is an exact SymPy polynomial in independent B_ij. The implementation
counts each scalar coordinate multiplication and addition separately. For each
k=0,...,n it verifies that d_k coordinates are signed principal determinants
and h_k coordinates are principal permanents. The final full-occupancy
coordinate is independently compared with a permutation sum on generic B.
This is a test of a new reciprocal construction, not a repetition of the
chronological subset-product algorithm.

A safe dense compilation bound for this explicit quotient evaluation is
`S(n)*4^n`: an addition needs at most 2^n coordinate additions and a multiplication
at most 3^n disjoint-mask pair multiplications, with at most 3^n-2^n corresponding
additions; both are bounded by 4^n for n>=2. The implementation records a smaller
actual sparse count, including all Newton and trace intermediates. This charge
is essential: the quotient operation is not costless, even though the native
recurrence DAG has polynomial size.

Observed counts with generic B at n=2,3,4,5 are respectively **30,129,404,1005**
native gates and **29,135,565,2143** sparse compiled coefficient gates. Substituting
the source marked B entries adds respectively 7,17,31,49 gates. Sparse counts
use exact symbolic zero elimination at these finite instances; the general
uniformly describable dense charge remains the exponential bound above. These
figures count circuit operations on polynomial coefficient objects, not the
internal cost of expanding SymPy expressions for verification.

The frozen positive development boundary uses generic formal B for n=2,3,4,5,
with five exact assertions per n. The evaluator's hash is recorded before its
first execution, and it is not changed afterward. Exact numerical scores,
actual compiled gate counts, native counts, and timings are in `dev-rational.json`.
The evaluator never samples z, generates counterexamples, runs holdouts, or
interprets pass fractions as confidence in the conjecture.

The observed development score is **20/20=1.0**, with evaluator SHA-256
`903967655e28db2b7d1b4d33e6d98b09a46e0b132723494126150b7f6d1dfaed`.
Evaluation used local Python 3.12 with SymPy 1.14.0 and completed in approximately
30 seconds of measured case time. No Lean theorem was compiled in this node.

## A new lawful Laurent-label normalization

Start from the source pairing

`H(t)=det(B_ij t^(j*n^i)) * det(t^((n-1-j)*n^i))`.

Let `C=n(n-1)/2`, `q_i=(n^i-1)/(n-1)`, and `s=t^(n-1)`.
Since `n^i=1+(n-1)q_i`, pull t^j from column j of the first determinant and
t^(n-1-j) from column j of the second. Each determinant contributes t^C. Thus

`H(t)=t^(n(n-1))*H_normalized(t^(n-1))`,

where

`H_normalized(s)=det(B_ij s^(j*q_i))*det(s^((n-1-j)*q_i))`.

The new central index is

`K'=K/(n-1)-n`, where `K=n^n-1`.

For n=2,3,4,5 the new indices are **1,10,81,776**, compared with 3,26,255,3124.
The normalized permutation labels satisfy

`rho_original(sigma)=C+(n-1)*rho_normalized(sigma)`.

Consequently label injectivity on permutations is preserved and the source
central coefficient obeys

`[t^K] Hhat(t,z)=[s^K'] H_normalized(s,z)`.

The endpoint additions in Hhat do not contribute at K for n>=2. This identity
does not assert that the normalized polynomial has the original endpoint
coefficients or centering; the polynomial H itself is what is relabeled.

The evaluator checks every generic amplitude monomial and every determinant
pair contribution under this substitution through n=5. It also checks the
normalized central coefficient independently against the generic permanent.
No full Hhat evaluation is needed. The transform preserves original marked
amplitudes when B_ij are substituted afterward.

This supplies the Laurent constant-term expression

`P_A=CT_s det(B_ij s^(j*q_i))*det(s^(-j*q_i))`.

Writing it as a polynomial residue requires division by `s^(K'+1)` after
clearing negative powers. That denominator has a small repeated-squaring
circuit but its **degree** is K'+1. The normalized determinant pair and its
powers have polynomial circuit descriptions, while the scalar coefficient
extraction still requires a separately justified construction. Normalization
improves the concrete index without claiming an asymptotically polynomial one.

## Primary division/truncation theorem conditions

[Dutta, Jindal, Pandey and Sinhababu, Arithmetic Circuit Complexity of Division and Truncation](https://doi.org/10.4230/LIPIcs.CCC.2021.25)
prove low-degree division elimination for an actual polynomial quotient g/h.
Their Theorem 6/26 treats a univariate regular rational series g/h, with
deg(g)<=d, denominator degree d_h, and numerator circuit size s; its truncation
bound is polynomial in s,d_h,log d. Its proof uses partial fractions and field
constants. These are degree-sensitive bounds, not bounds in the denominator's
circuit size alone. A target application must also provide cheap rational
scalar realization of all coefficients/constants and preserve the source's
uniformity and literal-length requirements. Polynomial degree in auxiliary y
meets the recurrence-side condition here; the final multivariate diagonal is
an additional operation. The cleared Laurent denominator has high degree, so
the desired low-degree hypothesis has not yet been constructed. An actual
divisible polynomial quotient or a low-degree rational realization remains a
constructive sublemma, not an automatic consequence of writing a residue.

## Exact constructive obligations for the next node

1. **Cheap diagonal contraction for this reciprocal circuit family.** Construct
   a polynomial scalar circuit for `[x_0...x_(n-1)]h_n`, or a polynomial-size
   linear representation closed under its companion updates, with cheaply
   built scalar data. Current explicit compilation is charged above and is
   exponential. The cheap recurrence initialization itself is already supplied.
2. **Low-degree rational re-encoding of the Laurent extraction.** Produce
   explicitly constructed g,h with low denominator degree and regular expansion,
   together with an exact identity retrieving the normalized target coefficient.
   Include numerator degree, all constant circuits, and final scalar gate cost.
3. **Formal bridge.** Prove Newton trace identities over the intended coefficient
   ring, initialized reciprocal coefficient convolution, squarefree projection
   preservation, the reciprocal squarefree master identity, and column-factor
   normalization in Lean. These are supporting identities; the inexpensive
   diagonal contraction remains a separate theorem obligation.

This node advances a new cheaply initialized recurrence and an exact index
normalization. It has not supplied the missing polynomial contraction, and
does not conclude either proof or disproof of the conjecture.
