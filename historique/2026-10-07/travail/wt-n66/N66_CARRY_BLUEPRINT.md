# n66 carry supplement v1 — exact coherent family, open global routing

This is a separate continuation of base n66 commit
`5aa4033e3b0e0093a473d4f229e9ed02ca8a2f0a`. The base frozen files are
unchanged. All universal mathematics below is **informal and unverified in
Lean in this artifact**. The independent n67 verifier belongs to the
coordinator, not to this supplement. This artifact does not prove
Conjecture 1.5, and does not introduce an assumption on B or its marked entries.

## 1. Local tensor and coherent carry family

For Boolean p,x,y,q, put

`T(p,x,y,q) = 1_(p+x+y+q even) (-1)^(xy+py)`.

In the order [p,x,y,q], its empty coefficient is 1, its six pair
coefficients (01,02,03,12,13,23) are (1,-1,1,-1,1,1), and its top
coefficient is 1. The Pfaffian expression for the top coefficient is
`1*1 - (-1)*1 + 1*(-1) = 1`. The code constructs an actual binary
addition/multiplication circuit for T, and an independent principal
Pfaffian evaluator checks all 16 coefficients.

Chain N such tensors with p0=0 and
`p_(i+1) = p_i xor x_i xor y_i`.
The external order is **[x0,y0,...,x_(N-1),y_(N-1),q]**, with q=pN.
The phase from the unique carry path is

`h(x,y) = sum_(j<=i) x_j y_i + binom(|y|,2)`.

Thus the native family has component

`C_native(x,y,q) = 1_(q=|x|+|y| mod2) (-1)^h(x,y)`.

This is one coherent family, rather than a separate matrix selected for each
output. Its explicit skew matrix is constructed by port permutation from
the matrix in the next paragraph. It uses 2N+1 external positions and only
the literals -1,0,1. A local network presentation uses N four-leg tensors
and N-1 internal carry edges. No tensor coefficient is declared to be a
costless scalar gate.

## 2. Exact port permutation — the missing Hadamard identification

The permutation from the native order to [all x, all y, q] has selected
inversion parity

`s(x,y) = sum_(i<j) y_i x_j`.

Its action on a Grassmann coefficient multiplies it by (-1)^s. Since
`h+s = |x||y| + binom(|y|,2) (mod2)`, the actual grouped family is

`C_grouped(x,y,q) = 1_(q=|x|+|y| mod2)
                   (-1)^(|x||y|+binom(|y|,2))`.

In grouped order its single skew matrix has blocks

`A_xx = J_N, A_yy = -J_N, A_xy = -ones(N,N),
 A_xq = ones(N,1), A_yq = ones(N,1)`;

J_N has entries +1 above its diagonal. The code implements this matrix
directly and checks its principal Pfaffians independently.

An informal uniform derivation uses fully anticommuting odd variables
xi_i,eta_i,q and odd linear forms X=sum xi_i, Y=sum eta_i. Write

`E_x = exp(sum_(i<j) xi_i xi_j)` and
`E_y = exp(-sum_(i<j) eta_i eta_j)`.

All quadratic forms here are even. X²=Y²=q²=0, so the Gaussian series is

`E_x E_y [1 - X Y + (X+Y)q]`.

The principal Pfaffian of J_(2r) is 1, by the alternating-sum expansion
along its first row. Consequently E_x has coefficient 1 on every even
x subset, while E_y has coefficient (-1)^r on every y subset of size
2r. Multiplication by X or Y gives the corresponding odd coefficients,
using the alternating sum over the removed position. These four parity
cases give C_grouped exactly. This argument treats the odd variables as
anticommuting; it does not replace them by commuting even generators.

When a family F has even y support, |x||y| disappears and the grouped
kernel coefficient is independent of the individual x positions. Therefore
the coherent Gaussian carry representation alone has **not** provided the
ordinary Hadamard-transformed family F'. An actual insertion or contraction
must supply the required selected shuffle signs. This is an exact open
interface, rather than an impossibility statement.

## 3. Useful abstract basis identity with synchronized ports

Ignore port permutations only for this explicitly labelled ordinary
component-array identity. Let U be the upper triangular all-ones binary
matrix. Removing the unique final carry gives

`C(x,y) = (-1)^(x^T U y + binom(|y|,2))`.

U is invertible over F2: y_i = (Uy)_i xor (Uy)_(i+1), with the last
suffix value zero. Character orthogonality gives
`C C^T = 2^N I`; thus the ordinary inverse transpose is `2^(-N) C`.
This is an abstract basis change. It has not been implemented as the
Gaussian contraction of the previous sections with F or G.

For N=2m, label x=(a0,b0,...,a_(m-1),b_(m-1)). A synchronized input
has y=(r0,r0,...,r_(m-1),r_(m-1)). Its suffix vector Uy has coordinates
(0,r0,...,0,r_(m-1)), and binom(2|r|,2) has parity |r|. Hence

`sum_r C(xF,paired(r)) C(xG,paired(r))
 = 2^m product_e 1_(bF_e=bG_e)`.

The final carries must still be qF=|xF| mod2 and qG=|xG| mod2. Inserting
the inverse basis maps requires their factors 2^(-N); no scale is discarded.
The code checks the identity, orthogonality, and exact carry constraints.

There is a useful factorization of this abstract output constraint. Put
t=|bF| mod2, define

`A_F,t(aF,qF) = 1_(|aF|+qF=t mod2)`, and analogously A_G,t.

For equal bF=bG=s, put k=|s|. The b factor is

`B_t(bF,bG) = (1/2) 1_(bF=bG) [1+(-1)^(t+k)]`.

In the factor order

`P=[all aF,qF, all aG,qG, bF0,bG0,...,bF_(m-1),bG_(m-1)]`,

each A_t is an all-ones even/odd parity signature: the odd one may be
represented using a fixed occupied anchor. The two terms of B_t are the
Gaussian products `product_e(1+bF_e bG_e)` and
`product_e(1-bF_e bG_e)` in their stated interleaved b order. Thus the
ordinary constraint factorizes into four Gaussian component factors in
P order. This does not establish that the constraint is the required
Gaussian tensor in the boundary order of F and G.

That boundary order is

`O=[aF0,bF0,...,aF_(m-1),bF_(m-1),qF,
    aG0,bG0,...,aG_(m-1),bG_(m-1),qG]`.

On the support bF=bG=s, qF=|aF|+|s|, qG=|aG|+|s|, the selected
permutation O -> P contributes the exact sign (-1)^chi, where

`chi = sum_e s_e sum_(f<=e)(aF_f+aG_f) + binom(k+1,2) (mod2)`.

The evaluator counts the actual permutation inversions independently.
The still-needed theorem is a coherent insertion that handles this sign
and the earlier F/G input shuffles together, without a free projection or
an enumeration of tensor components. No such insertion is supplied here.

## 4. Actual scalar costs and reproducibility

`compile_native_kernel(N)` constructs, rather than estimates, a scalar
addition/multiplication DAG for **one Boolean component**. XOR is compiled
as a+b-2ab, phases as 1-2ab, and the final equality is compiled as
1-XOR(pN,q). Without any gate shortcuts the count is 18N+7. Rational
literals have constant bit length. This circuit's inputs are tensor-label
bits x,y,q, not the generic entries B; it is not the scalar extractor.

For n=2,3,4,5 and N=2n², the constructed gate counts are respectively
151,331,583,907. Their explicit coherent skew matrices have orders
17,37,65,101 and respectively 136,666,2080,5050 upper entries. An eventual
fully closed polynomial-size skew matrix could be compiled by the inherited
scalar Pfaffian construction, but this supplement does not have the closed
root matrix or the required full contraction identity. Its Pfaffian oracle
is used only for small supporting coefficient checks, not as a circuit gate.

The frozen protocol has forty aggregate supporting checks: one local
16-component identity, four kinds of identities for N=0,...,5, and three
kinds for m=0,...,4. It was frozen with the source hashes before evaluation.
All forty checks passed in exact rational/integer arithmetic. For the cap
factorization, unequal bF,bG vanish identically on both sides by their
explicit equality factor, and synchronized words were checked exhaustively.

Reproduce in this worktree:

```powershell
& 'C:\Users\REGIS\AppData\Local\Programs\Python\Python312\python.exe' .\evaluate_carry_basis.py
```

The evaluator verifies both the base n66 and supplement source freezes.
It writes `n66-carry-report.json`. No Lean candidate was compiled in this
supplement, no held-out case was accessed, and no root B extraction was
evaluated. The supporting fraction is 40/40; the original n66 development
score remains **0/3 = 0**, because the three root construction obligations
remain open. Neither fraction is a proof-confidence score.
