# Projector research n1: rational collision resolvent and marked Bell recurrence

Branch: research/projector. Authoritative context: RESEARCH_CONTRACT.txt and
B.11, pp. 59-63 of the supplied paper. This note contains exact identities and
counted scalar constructions. It does not establish a polynomial compiler for
the requested permanent. No new theorem below is Lean-certified.

The submitted candidate is an exact exponential compiler. Its development
score is 1912 scalar gates at n=8, versus the supplied baseline 1920. The saving
is precisely the n unnecessary multiplications of singleton coefficients by 1.
It is not a compression of the subset state space.

## 1. A genuinely scalar rational generating function of polynomial degree

Write H_B(t)=product_i sum_j B_ij t_j = sum_m h_m t^m, where |m|=n.
Let kappa(m)=sum_j binom(m_j,2), h=binom(n,2), and set

    C_lambda(B) = sum_{m:kappa(m)=lambda} h_m,
    Z_B(q) = sum_lambda C_lambda(B) q^lambda.

The invariant is that each row assignment contributes its product of B entries
multiplied by q to the number of pairs of rows assigned the same column. Thus
Z_B(0)=per(B), Z_B(1)=product_i sum_j B_ij, and deg Z_B <= h.

Let Lambda_n be the energies of partitions of n, including zero, and let
 d=|Lambda_n|-1. They can be constructed without B by

    E_0={0},
    E_s=union_{1<=r<=s} {e+binom(r,2): e in E_{s-r}}.

Every composition gives a partition with the same energy, and every partition
of n fits into n columns by padding zeros. Therefore E_n=Lambda_n. A boolean
array indexed by s<=n and energy<=h gives a polynomial construction (the direct
triple loop is O(n^4) elementary operations). At n=8, |Lambda_8|=18, whereas
h+1=29. Thus the reduced projector has 17 factors, not 28:

    pi_red(T)=product_{lambda in Lambda_n, lambda>0}(1-T/lambda).

For M_r=(L^r H_B)(1), define the scalar ordinary generating function

    F_B(s)=sum_{r>=0} M_r s^r
          =sum_{lambda in Lambda_n} C_lambda(B)/(1-lambda s).
    D_n(s)=product_{lambda>0}(1-lambda s),
    N_B(s)=D_n(s) F_B(s).

The zero-energy summand is C_0, using 0^0=1 in M_0. Consequently

    deg D_n=d, deg N_B<=d,
    [s^d]N_B = [s^d]D_n * per(B),
    per(B)=sum_{r=0}^d [T^r]pi_red(T) M_r.

If D_n=sum_{k=0}^d d_k s^k, then for r>d,

    M_r = -sum_{k=1}^d d_k M_{r-k}.

Equivalently the homogeneous moment recurrence has characteristic polynomial
T product_{lambda>0}(T-lambda). The root zero accounts for the initial impulse;
there are d+1 initial values M_0,...,M_d, not merely d values for the whole
sequence. The rational constants of pi_red have polynomial bit length:
O(d log(h+1)) per numerator/denominator suffices.

This establishes a polynomial-order recurrence and an exact terminal readout.
It does not construct N_B. Its highest coefficient is already a known nonzero
constant times the desired answer. Specifying N_B as unknown input-dependent
coefficients cannot count as a compiler for it.

## 2. Exact initialization from the row factors: q shifts

For the first i rows define

    Z_i(q;t)=sum_{|m|=i} h_{i,m} q^{kappa(m)} t^m.

With T_{q,j} replacing t_j by q t_j, the exact update is

    Z_0=1,
    Z_{i+1}(q;t)=sum_j B_{i+1,j} t_j T_{q,j} Z_i(q;t).

Indeed kappa(m+e_j)-kappa(m)=m_j. This is a closed update as a polynomial in
marked variables; it is not a closed scalar update at t=1. Repeated shifts
request values at a grid of marked points. The occupation implementation has
binom(n+i-1,i) states at layer i. Their total through layer n is binom(2n,n).

A fully counted initializer can first compute all h_{i,m}, independently of q.
There are

    R=binom(2n,n) states,
    E=n binom(2n-1,n-1) incoming terms.

Skipping multiplication by the initial 1 and assigning the first incoming
term gives 2E-R+1-n scalar gates, before forming collision energy groups.
The final layer has T=binom(2n-1,n) entries; summing them into d+1 nonempty
energy groups uses T-d-1 additions. Once these groups are supplied, all moments
M_0,...,M_d and N_B can be computed with polynomial additional scalar gates.
This initializer is exponential; its small final rational representation does
not change the cost of constructing it.

At q=0 the update deletes precisely repeated columns. The retained coefficient
for a used-column subset S after |S| rows is

    f(S)=sum_{j in S} B_{|S|,j} f(S minus {j}),  f(empty)=1.

This gives the exact candidate.py, with singleton states assigned directly to
B_1j. It is the q=0 boundary of the deformation, not a claim that a general
q-dependent circuit has been compressed.

## 3. The exact moment hierarchy behind the initialization

Let E_j=t_j partial_j. Since L and all E_j commute, and

    L(t_j f)=t_j(L+E_j)f,

induction gives

    L^k(t_j f)=t_j(L+E_j)^k f.

Hence the row update for unmarked collision moments is

    M_{i+1,k}=sum_j B_{i+1,j} sum_{r=0}^k binom(k,r)
                           (E_j^r L^{k-r} H_i)(1).

The extra marked moments are genuine. For a multiindex alpha define
T_{i,k,alpha}=(L^k product_l E_l^{alpha_l} H_i)(1). Then the closed hierarchy is

    T_{i+1,k,alpha}
      =sum_j B_{i+1,j} sum_{r=0}^k sum_{s=0}^{alpha_j}
         binom(k,r) binom(alpha_j,s)
         T_{i,k-r,alpha+(r+s-alpha_j)e_j}.

The invariant follows by commuting E operators through multiplication by t_j;
E_j becomes E_j+1, while the other E_l do not change. This explicitly identifies
which extra derivatives a moment initializer must produce. Keeping only k
cannot implement it. Occupancy identities E_j in {0,...,i} make the hierarchy
finite, but the occupation realization above is still exponential.

This does not rule out a different, input-dependent implementation of these
moments. It rules out calling the scalar moment recurrence an initialization
algorithm without additional data.

## 4. Connected collision cumulants and the polynomial compact block circuit

For a nonempty row set C, write

    S_C=sum_j product_{i in C} B_ij.

Let a_k(q)=q^{binom(k,2)} and define c_1=1 and

    c_k(q)=a_k(q)-sum_{r=1}^{k-1} binom(k-1,r-1)c_r(q)a_{k-r}(q).

Then the exact connected-component expansion is

    Z_B(q)=sum_{set partitions pi of [n]} product_{C in pi} c_|C|(q) S_C.

Proof: expand product_{i<r}(1+(q-1) 1_{j_i=j_r}) over graphs on the row labels.
A graph component C forces its rows to the same column, giving S_C. Its sum of
connected graph weights is c_|C|. Splitting a graph according to the component
of a distinguished vertex gives the displayed recurrence for c_k. Components
may be assigned the same column; this is accounted for by the graph expansion
and is why the formula holds for every q. At q=0,

    c_k(0)=(-1)^{k-1}(k-1)!.

These scalars have an O(n^2)-gate construction as circuits in q, with shared
powers a_k and polynomial-bit binomial constants.

Introduce squarefree block marks x_C and

    K_B(x,q)=sum_{nonempty C} c_|C|(q) S_C x_C.

This entire polynomial has a polynomial scalar circuit: for each column j,
compute all degree components of product_i(1+B_ij x_i u) by the ordinary
triangular elementary-symmetric recurrence; sum columns and weight component
k by c_k(q). There are O(n^3) scalar gates, including all component construction.
It is not necessary to expand the exponentially many S_C individually to
construct this circuit in x.

There is also a polynomial circuit for the degree-n truncation of the ordinary
exponential of K. If K=sum_{k=1}^n K_k with K_k homogeneous of degree k, set

    G_0=1,
    G_m=(1/m) sum_{k=1}^m k K_k G_{m-k},  1<=m<=n.

This adds O(n^2) gates to the shared K circuit. However, G_n is not in general
squarefree. The desired answer is [x_1...x_n]G_n, not G_n(1).

In the quotient algebra Q[x]/(x_1^2,...,x_n^2), exp(K) gives the set-partition
contraction exactly. At q=0 this simplifies to

    K_B = sum_j log(1+sum_i B_ij x_i),
    exp(K_B)=product_j(1+sum_i B_ij x_i).

For the first identity, a degree-k power of sum_i B_ij x_i equals k! times
its squarefree elementary symmetric component in this quotient. Thus the
coefficient is (-1)^{k-1}(k-1)!, exactly c_k(0). The contraction is the original
product by columns, i.e. the transposed permanent. The closed scalar Bell
recurrence before quotienting has not removed the row-collision filter.

There is a small admissible counterexample to the cardinality-only version:

    B  = [[1,  2], [5, 10]],   per(B)=20,
    B' = [[1, 10], [5,  2]],   per(B')=52.

At z=1 these entries all are 1+a_ij^2 with a_ij in {0,1,2,3}. Both matrices have
sum_{|C|=1} S_C=18 and S_{12}=25. Therefore both give

    K(u,0)=18u-25u^2,
    [u^2]exp(K)=137,

although the desired answers differ. All scalar Bell data after x_i=u agree,
so no decoder from those data can work, even one nonlinear in those scalars.
This is a statement about that particular data reduction, not all adaptive
representations.

For comparison, expanding the marked Bell contraction gives a fully counted
alternative scalar compiler. Compute all S_C with
(2n-1)(2^n-1)-n^2 gates; multiply the nonsingleton S_C by c_|C|(0) using
2^n-1-n gates. With an anchor r in S, compute

    F(empty)=1,
    F(S)=sum_{C subset S, r in C} c_|C|(0) S_C F(S minus C).

There are (3^n-1)/2 summands over all nonempty S. Skip F(empty) multiplications
and the first addition at every S. The contraction uses
3^n-2^(n+1)+1 gates. Including marked-input preparation, this explicit bound is

    3^n+(2n-2)2^n+n^2-3n.

It is worse than the subset source. It precisely counts the contraction that
is absent from the polynomial compact K and G circuits.

## 5. Input-dependent rational repair of the determinant generating function

The squarefree coefficient identity

    per(B)=[x_1...x_n] 1/det(I-diag(x)B)

follows directly from

    1/det(I-XB)=exp(sum_{k>=1} tr((XB)^k)/k).

A squarefree coefficient selects disjoint directed cycles. The factors 1/k
cancel the k cyclic rotations, and the exponential factorial cancels orders
of cycles. The resulting cycle covers are exactly the permutations, all with
positive sign. This proof only uses formal power series at the origin.

The ordinary specialization x_i=t has a degree-n denominator and a scalar
coefficient recurrence, but repeated vertices contribute. For n=2 its degree-2
coefficient is per(B)+b_11^2+b_22^2.

A nontrivial input-dependent repair is

    x_i(t)=t/(1+b_ii t).

Let D=diag(b_11,...,b_nn) and C=B-D. Direct determinant multiplication yields

    R_B(t)=1/det(I-diag(x(t))B)
          =product_i(1+b_ii t)/det(I-tC).

This identity is exact, including cases b_ii=0. No division by an input scalar
is needed in its coefficient implementation. Write A(t)=product_i(1+b_ii t)
and Q(t)=det(I-tC)=sum q_k t^k, with q_0=1. Then

    r_0=1,
    r_m=A_m-sum_{k=1}^{min(m,n)} q_k r_{m-k},  m=1,...,n.

All A_m and q_k have a polynomial scalar construction, using the paper's
division-free determinant circuit and ordinary univariate degree-n jets.
Once prepared, the recurrence takes O(n^2) scalar gates. It really constructs
a polynomial-size scalar candidate r_n; the issue here is its target identity.

Positive cases: for every 2x2 B, r_2=per(B), since C has zero diagonal and
Q=1-b_12 b_21 t^2. For every diagonal n x n B, Q=1 and r_n=product_i b_ii=per(B).
This repair exactly limits isolated diagonal loops to multiplicity at most one.

For n=3 its exact error is

    r_3-per(B)=sum_{i<j} b_ij b_ji (b_ii+b_jj).

Proof: Q=1-(sum_{i<j}b_ij b_ji)t^2
          -(b_12b_23b_31+b_13b_21b_32)t^3.
Multiply its reciprocal by A. The 2-cycle terms in degree three are multiplied
by every diagonal entry, while only the entry at the remaining vertex belongs
to a cycle cover. The extra terms are exactly the displayed error.

For the admissible all-ones matrix J_3 (A=0, z=1), R=(1+t)/(1-2t), so r_3=12
and per(J_3)=6. Thus this rational repair is not submitted as candidate.py.
Cycles of length >=2 and overlapping loops still require an exclusion rule.
An adaptive implicit-series/Jacobian correction is a possible subsequent
hypothesis, not an established step of this branch.

## 6. Submitted scalar compiler, complete count, and evidence

For the submitted q=0 recurrence, there are E=n 2^(n-1) terms and 2^n-1
nonempty subset states. The n singleton terms need no multiplication.
Accordingly it uses

    E-n multiplications,
    E-(2^n-1) additions,
    (n-1)2^n+1-n source recurrence gates.

marked_inputs uses n^2-1 squarings and n^2 marked products. The total is

    s(n)=(n-1)2^n+2n^2-n.

It uses no nontrivial auxiliary rational constants. Its constructor runs in
O(n2^n) elementary Python iterations (with polynomial bit overhead for masks
and gate IDs). It is uniform but not polynomial in n. The downstream spectral
bound B(N) from the paper adds separately and cannot remove this exponential
source term.

The frozen evaluate_dev.py passed all 56 exact finite-field cases and reports
n=8 score 1912. Sizes 1 through 7 use 1,10,31,76,173,386,859 gates. The gate
formula was additionally checked against the actual DAG for n=1,...,12.
The frozen evaluator and dag.py were not modified, and no held-out protocol
was read or run.

verify_projector.py independently verifies the q-shift, cumulant/Bell,
rational-resolvent, reduced-projector and marked-moment identities for 20
positive integer matrices at n=1,...,5, with q in {0,1,-1,2,2/3}. The count
reported in projector_verification.json is 260 aggregate exact checks, plus
27 checks of the normalized determinant repair; inner identities and cumulant
specializations are also asserted. The scalar-Bell and normalized-resolvent
counterexamples are reproduced there. Exhaustive assignment enumeration is
used only as a small-case verifier, never as a purported polynomial compiler.

Conclusion of hypothesis n1: polynomial-degree rational representations and
closed scalar recurrences have been obtained, and several proposed initializers
or input-dependent substitutions have been made explicit. None provides a
polynomial initialization and correct terminal readout for general B. The
reported 1912 score is an exact modest baseline improvement, not resolution
of the user's general scalar-source objective.
