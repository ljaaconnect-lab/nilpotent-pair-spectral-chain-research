# n69: simultaneous contraction and contextual covariance transport

Artifact version: n69-joint-interfaces-v1. Base:
`1c3ee90c7cd972413db18112a8578ea96a34b2bb`. Frozen code commit:
`b21247cf54158fc650ece31705b97ce344a084a6`.

All universal identities in this blueprint are **informal**. Zero Lean
compiles were allocated or run. Three analytical candidates were considered
under the unchanged n69 hypothesis. None supplies the complete polynomial
scalar construction, so the development score is null. Constructed DAGs
were counted but not interpreted on any B input. No held-out data or shared
Arbor state was read or written.

The generic entries b_ij are retained throughout. The prescribed substitution
is b_ij=(1+a_ij²)z^(2^(i*n+j)); no marker is erased and no hypothesis is
imposed on rational A. Exterior modes below are odd and anticommute. Only
their named even products commute.

## Candidate 1: exact combined input/cap phase

Let m=n², with edge ports a_e,b_e in row-major order. On the transformed cap
support write output xF=(u_e,s_e), xG=(v_e,s_e). Write input yF=(aF_e,bF_e)
and yG=(aG_e,bG_e). Both original coefficient families have even total
input degree, so the final carries are the parity of the respective output.
The two native-to-grouped input shuffles are

    sF = sum_e aF_e*s_e + sum_(e<f)(aF_e+bF_e)(u_f+s_f),
    sG = sum_e aG_e*s_e + sum_(e<f)(aG_e+bG_e)(v_f+s_f).

The previously fixed cap shuffle is

    chi = sum_e s_e sum_(f<=e)(u_f+v_f) + binom(|s|+1,2).

All expressions here are modulo two. Define explicit prefix/suffix bits

    pF_e = sum_(h<e)(aF_h+bF_h),
    pG_e = sum_(h<e)(aG_h+bG_h),
    t_e  = sum_(h>=e)s_h.

Then the exact combined phase is

    Gamma = sF+sG+chi
      = sum_e [u_e(pF_e+t_e)+v_e(pG_e+t_e)
               +s_e(aF_e+aG_e+pF_e+pG_e)] + binom(|s|+1,2).

The combined scalar *bit-component* circuit is explicit. XOR uses a+b-2ab,
each bilinear phase uses 1-2ab, and the degree phase uses the running
prefix parity of s. The no-fold constructor uses 73m binary gates. For
n=2,3,4,5 the actually emitted counts are 292,657,1168,1825.

This does not lift Gamma to a coherent Gaussian insertion. A scalar
circuit that evaluates a requested bit component does not evaluate the
whole contraction over those bit components.

The original F input support has distinct selected a rows, distinct
selected b columns, and equal a/b counts. This support can be used only
at its actual input interface. It cannot be assigned to the transformed
F family or the independent transformed G input by assumption. The n68
pointwise contextual replacement Ktilde -> Krow is retained before the
joint transformation. No new port permutation is silently dropped.

Required construction: a single explicitly ordered insertion or stable
context quotient implementing Gamma simultaneously with both full families
and the cap, with polynomial scalar cost. This construction is open.

## Candidate 2: fixed low-dimensional Wick functional for the whole contraction

Use 2n+2 odd modes alpha_i,beta_j,g_a,g_b in that block order. H has blocks

    H_alpha,alpha=J_n, H_beta,beta=-J_n, H_alpha,beta=0,
    H_alpha,g_a=-1, H_beta,g_b=-1, H_g_a,g_b=1,

with every other dummy coupling zero. J_n has +1 above its diagonal.
Define W_H on exterior monomials by their principal Pfaffians, and
extend it linearly. This specifies a functional, not a circuit gate.

The n68 reduced kernel is Dpair+P^T H P, where each real local a,b pair
has Dpair coupling +1. Expanding a principal Pfaffian over those adjacent
local pairs gives, for every selected complete edge-pair set S,

    Grow_S = sum_(T subset S)
                W_H[g_a*g_b*product_(e=(i,j) in T) alpha_i*beta_j].

Deleting an adjacent pair has positive cofactor sign; the displayed
ordered product retains all signs in the incidence restriction. Therefore
the entire paired generator is

    g(x) = W_H[g_a*g_b*
                 product_(i,j)(1+x_ij*(1+alpha_i*beta_j))].

The first paired generator is the previously derived
f(x)=gamma_n det(B-B circ X). Linearity and this particular coefficient
identity yield a simultaneous contraction, rather than an independent
evaluation of g_S for every S:

    P(B)=W_H[g_a*g_b*det(-b_ij*alpha_i*beta_j)].            (W)

Indeed det(-b_ij alpha_i beta_j)=(-1)^n gamma_n
per(B) alpha_all beta_all. The independent fixed value is
Pf(H)=(-1)^n gamma_n, as follows by separating the two even blocks when
n is even, or appending one dummy to each odd block when n is odd.
These are informal orientation calculations, not Lean-certified results.

The fixed normalization Pf(H) is charged by actual inherited
trace_circuit(2n+2), with upper entries wired to the literal H entries.
The emitted counts for n=2,3,4,5 are 853,2990,7772,16809. The rational
literal denominators in that compiler are at most 2(n+1), with
O(log n) bits. No Pfaffian oracle is an arithmetic gate.

Equation (W) has not supplied a scalar extractor: its determinant is in
the even exterior algebra, and W_H must still be intertwined with every
multiplication. Linearity permits additions but does not permit pushing
W_H through products. The familiar double-orientation identity is not
counted as a new scalar construction.

## Candidate 3: true row prefixes, exact contextual Gaussian sectors

Conditioning the two dummies gives L(f)=W_H[g_a*g_b*f]. Its covariance
in alpha/beta block order is

    A = [[J_n,-ones],[ones,-J_n]].

Set q_j=alpha_j beta_j. These are commuting even square-zero elements.
In this *paired diagonal* algebra,

    L(q_S)=(-1)^|S|.

Consequently L restricted to every polynomial f(q) is also the Gaussian
functional with zero alpha/alpha and beta/beta blocks and cross covariance
-I. This is an exact contextual replacement: all future factors in q
remain inside the same subalgebra. It asserts neither equality on arbitrary
exterior polynomials nor free differentiation of a quotient ideal.

Define actual row-prefix polynomials

    P_0=1, P_(i+1)=-(sum_j b_ij*q_j)P_i.

At the full prefix, P_n=(-1)^n per(B)q_all, hence L(P_n)=P(B).
This is a target-preserving joint transport of (W); it does not use an
unknown permanent coefficient as input.

### Exact Gaussian branches preserve every future paired context

For occupied column set S define a Gaussian functional G_S with cross
covariance -diag(1_(j not in S)) and zero same-sector blocks. Its moments are

    G_S(q_J)=(-1)^|J| if J intersect S is empty, and 0 otherwise.

Writing w_i(S) for the coefficients produced by row-prefix multiplication,
the exact identity is

    for EVERY polynomial f(q),
    L(P_i*f)=sum_(|S|=i) w_i(S)G_S(f),

    w_0(empty)=1,
    w_(i+1)(S union {j}) += b_ij*w_i(S), j not in S.

The proof is termwise: P_i=(-1)^i sum_S w_i(S)q_S, and multiplying q_S
by q_J is zero exactly when their supports intersect. In particular
-q_j G_S maps to G_(S union {j}) when j is available, and to zero
otherwise. Each branch is genuinely Gaussian in the future-q quotient;
its update sets one diagonal covariance entry to zero. It requires no
division by b_ij and remains valid at zero weights or singular B.

There are binom(n,i) sectors in this explicit representation. Their weights
are updated by charged scalar multiplication and addition, rather than
being supplied as unknown input coefficients. A direct no-fold sector
constructor would use n*2^n gates; this formula is analytical, not a new
measured DAG here. This is the size of this representation, not a lower
bound on another representation.

### One exact fusion, with its rational chart charged

For the first row put h=sum_j b_0j, u_j=b_0j/h on the chart h nonzero.
The entire mixture fuses, for every f(q), to mass h and a single Gaussian
cross covariance

    M_1=-I+u*1^T.

For every J, the determinant lemma gives

    h det(M_1[J,J])=(-1)^|J|(h-sum_(j in J)b_0j),

which equals the true row-prefix moment. This proves the full future-q
interface informally, beyond matching its diagonal or low-order covariance.

The ratios u_j are not allowed rational leaves and are not costless
divisions. One may store the projective data h and h*M_1, or eliminate
the division by the safe homotopy below, once a global fusion is available.
This one fusion does not establish fusion for all subsequent rows.

### Exact derivative/minor equation for the next fusion

A Gaussian cross covariance M has paired principal moments det(M[J,J]).
Its generating polynomial is R_M(t)=det(I+diag(t)M). Let D_b=diag(b_j)
for the next row, tau=Tr(D_b M), h=-tau. The next normalized moment
generator must be

    R_new(t)=-(sum_j b_j*partial_(t_j))R_M(t)/h.

A rank-one covariance update M'=M+uv^T works exactly if, for every formal
diagonal T,

    v^T(I+TM)^(-1)T u
      =-Tr(MD_bM(I+TM)^(-1)T)/tau.                       (R1)

Define the resolvent-context annihilator

    N(M)={N:Tr(N(I+TM)^(-1)T)=0 for every diagonal T}.

Thus a rank-one Delta must obey Delta+MD_bM/tau in N(M). At M=-I,
all off-diagonal matrices lie in N(M), which supplies the first-row fusion.
For M=-I+u*1^T, sum u=1, the annihilator is exactly

    N_jj=0,  u_j*N_ij+u_i*N_ji=0 for i not equal j.

To see this, write lambda_j=t_j/(1-t_j). Sherman-Morrison gives
(I+TM)^(-1)T=diag(lambda)-
diag(lambda)u*1^T diag(lambda)/(1+sum u_j lambda_j).
The linear coefficients enforce zero diagonal; the remaining quadratic
coefficients are the displayed weighted skew conditions. No division by
u_j is needed to state them. This provides actual off-diagonal freedom
in the contextual quotient, rather than preserving the raw covariance.

The remaining positive theorem is an explicitly constructed low-rank
update, or polynomial family of updates, whose ALL paired principal
minors obey this directional derivative, uniformly under subsequent rows.
No such all-prefix update is established here.

One derivative can also be represented by n+1 Gaussian sectors by exact
univariate interpolation of det(I+(T+sD_b)M). For an invertible chart
A_s=I+sD_b M, its sector has mass det(A_s) and cross covariance
M_s=M A_s^(-1). This covariance and mass both require charged scalar
construction; singular sectors require the safe homotopy. Repeated
directional derivatives have independent row directions. A polynomial
merge of their successive interpolation sectors is a separate requirement;
their iteration is not counted as a polynomial root compiler.

### What a covariance-only update omits

For a genuinely Gaussian current state of mass m and covariance C in
2n odd modes, an insertion -(sum b_j alpha_j beta_j) gives the exact
source-variable generating function

    m exp(1/2 z*C*z) [h+Q(z)],
    h=-sum_j b_j C_(alpha_j,beta_j),
    Q(z)=sum_j b_j (z*C_alpha_j)(z*C_beta_j).

Its covariance is C+h^(-1) times the displayed sum of column wedges.
The full function is Gaussian when Q²=0. Alternatively its higher
defects must vanish in a proved context quotient stable under every
future factor. A single-column branch has decomposable Q and supplies
such a closure. A row's sum of branches cannot be merged merely by
matching the covariance or asserting Q²=0. The exact sector and
principal-minor interfaces above are the constructive ways to study the
remaining quotient, without assuming full Gaussianity in z.

### Explicit full-jet reference and charged initialization

Define canonical lowering delta_j(q_S)=q_(S minus {j}) if j in S, zero
otherwise. This is a vector-space operator, not an assumed derivation on
the square-zero quotient. For J_i(S)=L(delta_S P_i), the exact update is

    J_(i+1)(S)
      = sum_(j not in S) b_ij [J_i(S)+J_i(S union {j})]
        -sum_(j in S) b_ij [J_i(S minus {j})+J_i(S)].

Initialization is J_0(empty)=1 and J_0(nonempty)=0. The terminal output
is J_n(empty). In particular its scalar mass update asks for first jets,
first jets ask for second jets, and so on. A complete implementation
retains 2^n scalar state values and charges every update. There is no
unknown target leaf, Wick gate, derivative gate, or coefficient gate.

The actual no-fold row-jet circuit has n(7n-2)2^(n-1) binary gates. Its
measured n=2,3,4,5 counts are 48,228,832,2640. Original markers are
compiled by sharing z,z²,z⁴,... across all edges: n²-1 squarings and
n² weight multiplications. The measured marked counts are 55,245,863,2689.
Only ordinary constants -1,0,1 occur beyond the prescribed p_ij leaves.
This complete reference remains exponential; it is not an eligible
polynomial candidate and was not numerically validated in this node.

## Safe true-prefix initialization and conditional division elimination

At B0=ones, true prefixes have

    m_i=L(P_i)=n!/(n-i)!,
    h_i=m_(i+1)/m_i=n-i,
    J_i(S)=(-1)^|S| i! binom(n-|S|,i-|S|), |S|<=i,

and zero jets for larger S. These explicit integers have O(n log n) bits
and can be constructed by products and Pascal's recurrence. They prove
safe mass charts for the true prefix functionals, not Gaussianity of
those prefixes. The first merged chart has h0=n.

If an actual globally correct rational state fusion is constructed with
these chart pivots, put B(epsilon)=ones+epsilon(B-ones). The final target
has degree at most n in epsilon. Arrays of length n+1 suffice; no
truncation at the enormous t exponent K is used. One scalar array product
costs (n+1)² gates by convolution, and one reciprocal with known nonzero
constant h0 costs n(n+1) gates using

    v0=1/h0,
    vk=-(1/h0) sum_(r=1..k) h_r v_(k-r).

The only reciprocal leaves are the explicitly known constant pivots;
for h_i=n-i they have O(log n) bits. Summing the output's n+1 coefficients
uses n more additions. Initializing B-ones and later substituting the
original marked B must also be charged. This is a compilation mechanism
conditional on a correct full fusion and complete pivot certificate,
not a construction of that missing fusion.

## Reproducibility, status, and next obligation

`n69-source-freeze.json` was created before any construction counts.
`compile_n69_references.py` builds the actual +/* DAGs and writes
`n69-construction-costs.json`; it never interprets them at B values.
Serialized nodes are topologically ordered. Constant nodes have exact
rational `value` strings, variable nodes have input labels, and add/mul
nodes have previous-node `left`/`right` indices. The explicit `output`
index determines the result; it need not be the final node because other
state coordinates are also computed and charged.

```powershell
& 'C:\Users\REGIS\AppData\Local\Programs\Python\Python312\python.exe' .\compile_n69_references.py
```

The coordinator may validate the exponential reference under a separately
frozen development-only protocol. Such validation belongs to that supplement,
and cannot change the main n69 development score into a polynomial success.

The three root obligations remain undischarged. There is no successful
Lean axiom audit to report: no Lean source or new axiom was added here.
The exact next constructive theorem is a polynomial representation of
the joint phase/cap contraction, equivalently a proved all-prefix
contextual Gaussian or moment-sector fusion with cheaply initialized
data, charged multiplication and terminal scalar output. The new exact
sector quotient, first-row fusion, and resolvent equation support that
search; none claims root closure or impossibility.
