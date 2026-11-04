# Frequency-conditioned Gaussian compilation: exact partial construction

This report records the first experiment at commit `3fa7c38`. The subsequent
regular-completion experiment and current executable candidate are described
in `REGULAR_COMPLETION.md`; its two-component fourth layer supersedes the
five-component construction below.

This work uses the corrected full-chain contract, baseline `1cd3db9`. The
inputs are the original `p_ij,z,omega`, not a supplied permanent amplitude.
The output is the entire inverse spectral table. The unknown is a uniform
polynomial-size Gaussian fusion from these original inputs. That unknown
is not resolved here. The positive results are a single general Gaussian
for the third layer, a five-Gaussian fourth-layer continuation, and a charged
division-free scalar terminal reader. All three have executable scalar DAGs.

The matrices below use paired order `(x1,y1,x2,y2,...)`; its top Pfaffian
has the required positive paired orientation. Let `J` have blocks
`[[0,1],[-1,0]]`. A Gaussian `G(K)=exp(1/2 theta^T K theta)` has coefficient
`Pf(K_I)` on an even mode subset I. Write Pi for projection onto subsets
that contain both modes or neither mode of every column. Unpaired
coefficients are allowed in the representation; they are not silently
declared zero during fusion.

## A single Gaussian represents the entire third paired layer

Take three arbitrary row factors `a,b,c`. Initially work over their rational
function field and put `r_j=b_j/a_j`, `s_j=c_j/a_j`. The normalized kernel
has blocks, written in grouped x/y notation,

```
X_jk = r_k-r_j,
Y_jk = (s_k-s_j)/3,
C_jk = delta_jk - 1/3 + 2*r_j*s_k,
K = [[X,C],[-C^T,Y]].
```

Congruence-scale x_j by a_j and y_j by 1. Call the resulting paired-order
kernel `K3(a,b,c)`. For every column subset S of cardinality k,

```
Pf(K3[S])/prod_(j in S) a_j
  = 1-k/3 + (2-k)*sum_(j in S) r_j*s_j
              + (sum_(j in S) r_j)*(sum_(j in S) s_j).                 (1)
```

In particular, when k=3 the right side is
`sum_(j != l in S) r_j*s_l`. Multiplication by `prod a_j` gives exactly
`per([a;b;c]_[S])`. Thus one 2n by 2n antisymmetric matrix represents the
whole third paired layer, even though its other paired layers have different
values. The xx and yy blocks matter: this is broader than a determinant
represented only by a cross block.

Here is a short proof of (1). Set U_j=(1,r_j), V_j=(-1/3,2s_j), and let
J2 be the two-dimensional standard skew matrix. Then

```
X=U J2 U^T,  Y=-(1/2) V J2 V^T,  C=I+U V^T.
```

For this rank-four skew update the paired Pfaffian is
`1+tr(T)+(3/2)det(T)`, where `T=V^T U` on S. This follows either by the
Pfaffian minor-summation expansion, or by taking the zero-, two-, and
four-auxiliary-mode terms; all higher terms vanish by rank. Explicitly,

```
T = [[-k/3,          -(sum r)/3],
     [2*sum s,        2*sum rs]],
tr(T)=-k/3+2*sum rs,
det(T)=-(2/3)*(k*sum rs-(sum r)*(sum s)).
```

Substitution proves the formula. `gaussian_experiments.py` also expands the
six-mode Pfaffian symbolically and verifies (1) at six different sizes.

This is a formula from the original factors. Its parameters do not use any
unknown high permanent, and the assertion is only about the paired third
layer. At `a=b=c=1`, X=Y=0 and C=`I+(5/3)11^T`; the full normalized
Pfaffian is `1+5n/3`. In particular, this gauge has no structural singularity
at the all-ones base point.

## Removing input divisions in the state, not only in its final value

The x-mode congruence by a_j alone does **not** remove every denominator.
Scaling both modes by a_j gives the polynomial homogeneous kernel

```
Xhat_jk=a_j*b_k-b_j*a_k,
Yhat_jk=(a_j*c_k-c_j*a_k)/3,
Chat_jk=a_j^2*delta_jk-a_j*a_k/3+2*b_j*c_k.
```

Its size-six paired Pfaffian is `prod a_j` times the desired permanent.
Dividing by this product for free would violate the contract; this is not
the implementation used.

Instead deform every original unmarked entry `B_ij` as
`B_ij(t)=1+t*(B_ij-1)` and work modulo `t^(D+1)`. Every inverse of a_j(t)
is represented explicitly by

```
1/a_j(t) = sum_(h=0)^D (-(B_1j-1))^h t^h mod t^(D+1).                (2)
```

Each kernel entry is now a tuple of D+1 ordinary scalar nodes. Addition,
negation and convolution are expanded into scalar + and * gates, with no
inverse nodes. At D=3, the Pfaffian of any three-column minor is the exact
degree-at-most-three polynomial `per(B(t)_[first3,S])`; summing its four
coefficients evaluates it at t=1. This equality is established before
substituting the marked inputs `B_ij=p_ij*z^(2^(i*n+j))`, so large z degrees
do not increase the jet order.

For a prospective full n-row fusion one may keep D=n from the start.
If its rational formulas have polynomial count, and all denominators have
controlled nonzero rational values at B=J, this replacement costs polynomial
overhead. It does not establish that the missing fusion formulas exist.
When further formulas have new denominators, their base-point values still
need checking. Truncating at D=3 is justified for the current third-layer
readout, not for arbitrary later rational operations without such an audit.

`gaussian_layer_three.py` implements (2) and every kernel operation. A
scalar jet multiplication uses exactly `(D+1)^2` gates; a jet addition or
negation uses D+1 gates. The implemented kernel construction uses

```
6n+nD+2n(D+1)^2
 + binom(n,2)*(3(D+1)^2+6(D+1))
 + n^2*(3(D+1)^2+4(D+1))                                      (3)
```

gates, excluding preparation of the marked B entries. Its memory is
O(n^2(D+1)) scalar coordinates. All literal denominators here are 3; they
are rational constants independent of inputs.

## Fourth-row fusion is exact, with five Gaussian components

Let `J_d=direct_sum_j [[0,d_j],[-d_j,0]]`. For every four-column S,

```
[u] Pf((K3+u J_d)[S])
   = sum_(j in S) d_j*Pf(K3[S minus j])
   = per([a;b;c;d]_[S]).                                      (4)
```

Only one selected diagonal pair can contribute to [u]; removing this pair
has positive sign in paired order. Other paired layers of K3 do not enter
this coefficient. A degree-at-most-four polynomial satisfies

```
[u] f(u)= -25/12*f(0)+4*f(1)-3*f(2)+4/3*f(3)-1/4*f(4).         (5)
```

Equations (4)-(5) give a uniform five-component Gaussian representation of
the fourth paired layer for any number of columns. The components and
weights are explicit from a,b,c,d. Jets D=4 remove all variable divisions
before the terminal reader. The routine `build_four` compiles the complete
n=4 chain from the original marked inputs to all eight inverse slots.

For a homogeneous paired layer of degree i already represented by a sum
of Gaussians, exactly the same construction advances one row, using i+2
components per previous component. For degree bound m=i+1 the interpolation
weights at u=0,...,m are

```
w_0=-sum_(l=1)^m 1/l,
w_l=(-1)^(l-1)*binom(m,l)/l,  1<=l<=m.
```

They have polynomial bit length and can be generated in polynomial time.
However literal repeated fusion from layer3 has `(n+1)!/24` components.
This is an explicit exact fusion, not a polynomial closed fusion. Neither
the coefficient operator nor a polynomial component count is assumed free.

## Charged scalar Pfaffian readout and the whole inverse table

For a provided 2n by 2n skew K in paired order, set `A=-J K`. Since
`Pf(J)=1`,

```
det(I+tA)=Pf(J+tK)^2.
```

With c_0=1, logarithmic differentiation gives

```
c_k = (1/(2k))*sum_(r=1)^k (-1)^(r-1)*tr(A^r)*c_(k-r).         (6)
```

The degree-n coefficient c_n is Pf(K). The code forms the matrix powers
explicitly and uses only scalar +,-,* and rational constants 1/(2k).
There is no division by a data value. Its exact naive gate count, excluding
construction of the provided kernel, is

```
G(n) = (n-1)*4n^2*(4n-1)+5n^2+floor(n^2/4).                   (7)
```

Applied over order-D jets, the actual count is

```
(n-1)*4n^2*(2n(D+1)^2+(2n-1)(D+1))
 + n(n+3)/2*(D+1)^2
 + (2n^2+n(2n-1)+n(n-1)/2+floor(n^2/4))*(D+1).                (8)
```

This is O(n^4(D+1)^2), with rational literal bit lengths O(log n).
`pfaffian_scalar.py` implements the reader. Pfaffian contraction as a
scalar Gaussian observer is consistent with the matchgate formalism in
[Valiant's original STOC paper](https://people.seas.harvard.edu/~valiant/stoc01.pdf).
The concrete recurrence and cost above are proved and implemented here;
they are not an uncharged invocation of a matchgate library.

Let `zeta_j=omega^(f*d_j)` and let D_f multiply x_j by zeta_j and leave
y_j unchanged. Under the columnwise frequency modulation of every original
row, r_j and s_j stay unchanged and the constructed kernel transforms as
`K_f=D_f K D_f^T`. The diagonal row update transforms by the same congruence.
Consequently each component satisfies

```
Pf(K_f)=omega^(f*sum_j d_j)*Pf(K).
```

Fourier orthogonality routes each component's scalar terminal coefficient
directly to `k*=sum labels mod N`. Summing components commutes with this
routing. The routines return N scalar nodes, zero outside k*. They do not
require a corrected amplitude input or impose its computation before the
spectral layer. Analytically eliminating these known phases is an exact
joint compilation; no omega-dependent scalar gate remains necessary after
orthogonality. This does not by itself generate the missing prefix kernel.

## Why adding Gaussian kernels is not a valid general fusion

The projection onto complete mode pairs matters. For n=2, take K with
paired diagonal a1,a2 and xx edge K_13=1, and L with paired diagonal b1,b2
and yy edge L_24=1 (one-based mode indices). Their degree-one paired
shadows are exactly `a1*q1+a2*q2` and `b1*q1+b2*q2`. Nevertheless,

```
[uv] Pf(uK+vL) = a1*b2+a2*b1-1.
```

The extra -1 comes from two unpaired terms recombining into paired output.
At all-ones rows, labels (0,1), N=4, omega=i, naive fusion returns inverse
table `(0,1,0,0)`, whereas the correct table is `(0,2,0,0)`. The unwanted
term has the same total column phase; the natural spectrum does not remove
it. This rejects this addition rule, not every frequency-dependent state.

There is an exact general rule. For signs epsilon_j in {+1,-1}, let E_epsilon
multiply both modes of column j by epsilon_j. Averaging characters gives

```
Pi G(K) * Pi G(L)
 = 2^(-(n-1))*sum_(epsilon_n=1) Pi G(E_epsilon K E_epsilon + L). (9)
```

Proof: the sign average projects the first factor onto even occupancy at
every column; after the final Pi, an unpaired monomial of the second factor
cannot survive against a paired first factor. Gaussian exterior products
obey G(K)G(L)=G(K+L). The global sign flip acts trivially on even states,
so n-1 signs suffice. Homogeneous-degree extraction can be compiled by
interpolation, but (9) already has 2^(n-1) components. This is not a lower
bound on every alternative suffix-adapted representation.

The local even-parity projection has Choi signature
`|0000>+|1111>`. It violates the four-mode Gaussian relation
`g_empty*g_1234=g_12*g_34-g_13*g_24+g_14*g_23`; its left side is 1 and its
right side is 0. Thus that literal projector is not one Gaussian operator.
Replacing it by its two Gaussian branches explains the parity expansion,
but it does not exclude a state-dependent replacement that is correct only
for the authorized terminal observation.

## The rank-six affine-feature repair has a precise limitation

For the proposed `K=J+U C U^T` with constant skew C and endpoint features
`U_xj=(1,r_j,s_j,0,0,0)`, `U_yj=(0,0,0,1,s_j,t_j)`, Pf(K) depends only
on the small skew moment matrix `U^T J U`. The same holds with any number
of fixed affine features of (r,s,t): this moment matrix depends only on
the Gram matrix of (1,r,s,t). This follows from the Pfaffian determinant
lemma, with the sign fixed by the constant term of the polynomial pencil
`Pf(J+v U C U^T)` at v=0. C need not be invertible for the polynomial identity.

Here are two exact inputs with identical full Gram matrices:

```
r  = (3,1,1,3),
s  = (1,3,5,7),
t+ = (5,1,7,3),
t- = (3,7,1,5).
```

The common Gram matrix is

```
[[4,8,16,16],
 [8,20,32,32],
 [16,32,84,64],
 [16,32,64,84]].
```

But `sum rst` is respectively 116 and140, and
`per([1;r;s;t])` is 744 and792. Thus no choice of constant C in this
affine-feature family works universally. The argument also permits C to
depend only on this same Gram matrix. It does not cover a data-dependent
diagonal background, nonlinear features, fixed column-label features,
parameters using further moments, or a suffix-dependent state. Such changes
remain possible repairs.

The separate exploratory `layer_four_search.py` tests a larger 32-parameter
family: a data-dependent diagonal linear form plus a rank-eight skew update
built from the endpoint vectors (1,r,s,t). Three least-squares runs on 160
training samples and 160 independent validation samples did not find an
identity. Their training L2 residuals were 125.37,117.82,122.37 and validation
residuals 279.94,220.75,196.11. These numerical failures are not an algebraic
non-existence result. No approximate fit is used by the compiler.

## Reproduction and scope of the result

Run `python gaussian_experiments.py` to reproduce the exact evidence in
`gaussian_results.json`. It includes a symbolic six-mode identity, exact
parity fusion at n=1,...,4, 36 numeric complete-table checks of the supplied-
kernel scalar reader, 12 original-input complete-table checks of the third
layer including zero input, two formal marked-polynomial complete-table
checks, three original-input complete-table checks of the fourth layer,
and the exact affine-feature witness.

The third-row original-input implementation costs 9583 gates; the fourth-row
implementation costs 232378 gates. These are dense proof-of-concept scalar
compilations, not improved asymptotic or benchmark candidates. `candidate.py`,
`dag.py`, and `evaluate_dev.py` are unchanged. The frozen dev evaluator has
not been run for a purported new all-n candidate, and no held-out protocol
was read or run. The appropriate new-node dev score is null.

What is now explicit is initialization from three original rows, one exact
next-row fusion, all variable-division removal in their represented states,
and scalar observation of every inverse spectral slot. What remains is a
uniform rule that keeps the number and dimensions of Gaussian components
polynomial after arbitrary further rows. The exact twirl and interpolation
rules establish valid continuations with exponential or factorial counts;
neither proves that another jointly spectral, context-dependent closure is
impossible.
