# n2 — Adaptive rank-one pivot jets

Status: an exact initialized scalar compiler was obtained, but its proved
size is exponential and it is slower than the development baseline.
The nonlinear rank-one exchange is valid. It does not, by itself,
reinitialize the mixed jets or produce a polynomial scalar readout.
Nothing here rules out an unrestricted nonlinear factor-based compiler.

## 1. Input, initialization, fusion and readout

Write a matrix of size m+1 as B = [[a,r^T],[c,D]]. Over any commutative
Q-algebra,

    per(B) = a per(D) + [t] per(D+t c r^T).                 (1)

Proof: the constant term accounts for permutations matching the first row
to the first column. Every other permutation chooses exactly one entry
of c and one of r, with the remaining rows and columns matched in D.
Differentiating the permanent in the rank-one direction sums exactly
these choices, once each.

The full univariate response is

    per(D+t c r^T) = sum_{q=0}^m t^q q!
      sum_{|I|=|J|=q} c_I r_J per(D_{I^c,J^c}).           (2)

This follows by choosing the q updated entries, then assigning the
selected rows to selected columns in q! ways.

For an actual division-free implementation, introduce a fresh commuting
square-zero variable t at each pivot. Work temporarily over

    Z_d = Q[t_0,...,t_(d-1)]/(t_0^2,...,t_(d-1)^2).

Initialize each matrix entry by its original marked scalar B_ij; this is
the one-coordinate polynomial {0:B_ij}. At depth d, form

    D'_(i,j) = D_(i,j) + t_d c_i r_j

over Z_(d+1), recursively compute its permanent F, split F=F0+t_d F1,
and return a F0+F1. At a 1x1 matrix return its entry. This is an induction
proof of (1) over the current coefficient algebra, with no scalar oracle.
All temporary variables have been removed on returning from the recursion.
The final result is the single coefficient at the empty mask.

`jet_compiler.py` implements every Z_d operation by scalar gates, and
`candidate.py` exposes that compiler to the frozen evaluator. Multiplication
uses disjoint mask pairs only. Extraction of F0/F1 is a partition of an
already explicitly computed coefficient array, not an uncharged extraction
from a scalar circuit. There are no variable divisions. The only auxiliary
literal used is zero. The z powers and their products with p_ij are built
by the frozen marked_inputs routine.

## 2. Complete cost

At depth d there are m=n-d rows. A dense Z_d multiplication uses at most
3^d scalar multiplications and 3^d-2^d additions. The (m-1)^2 rank-one
updates therefore use at most

    (m-1)^2 (2*3^d-2^d)

gates. The old entries have t_d-degree zero and the updates degree one, so
their union requires no scalar additions. Reconstruction a F0+F1 costs
at most 2*3^d gates. Including the 2n^2-1 marking gates gives

    T(n) <= 2n^2-1 + sum_{d=0}^{n-2}
             (((n-d-1)^2+1)*2*3^d - (n-d-1)^2*2^d)
         = 4*3^(n-1) - 3*2^n + 2n^2+n.                  (3)

The actual gate counts for n=1,...,8 are

    1, 10, 33, 96, 283, 858, 2637, 8116.

They attain (3) in these cases. The constructor uses exponential time and
space, bounded by O(poly(n)3^n), and hence does not meet the polynomial
constructor requirement. If p_ij must first be formed from supplied a_ij,
the extra n^2 squarings and n^2 additions are polynomial and do not change
this conclusion. There is no dependence on expanded z-degree in the bound.

The unchanged `evaluate_dev.py` passed all 56 prescribed finite checks and
reported score 8116; its output is in `dev_results.json`. An earlier
independent check also tested eight cases at each n=1,...,8, including
z=0,1,-1, and passed all 64. Passing these tests is distinct from the
inductive proof above and is not a polynomial-size claim.

## 3. Genuine local nonlinear closure

Suppose an old rank-one perturbation has pivot blocks alpha beta,
beta x, alpha y, and x y^T. Introduce the new pivot variable u. Modulo
t^2=u^2=0, the following exact exchange holds:

    E+txy^T+u(c+t beta x)(r+t alpha y)^T
      = E+ucr^T+t(x+u alpha c)(y+u beta r)^T.             (4)

Thus an old rank-one direction remains rank one after a new pivot, with
vectors adapted to the remaining matrix. This is a real positive closure
result for the directions, not merely an exponential-coordinate argument.
However, the old pivot multiplier also changes to a+t alpha beta; its
product with the remaining response transports mixed derivatives. The
functional L_a(F0+tF1)=aF0+F1 is not multiplicative on the dual-number
algebra. Equation (4) alone cannot turn their composition into a product
of scalar evaluations.

A concrete first-jet collision: along directions E_11,E_22, the matrices

    all-ones(3,3),
    [[1/3,1,1],[1,1/3,1],[1,1,3]]

both have permanent 6 and separate first jets 2,2, but their mixed jets
are respectively 1 and 3. This only rejects resetting a response to its
value and those two first-jet numbers. It does not reject retaining the
original factor matrices or another nonlinear description.

## 4. Small cases, Gaussian repair, and connected interactions

Replacing t by 1/a before enforcing t^2=0 loses the filter. For n=3,

    a per(D+cr^T/a) = per(B) + 2 b c d g/a

for B=[[a,b,c],[d,e,f],[g,h,i]]. For n=4, the excess is

    (2/a) sum_{|I|=|J|=2} c_I r_J D_{I^c,J^c}
      + (6/a^2) product_i c_i product_j r_j.

All these terms are symbolically checked in the derivation from (2).

An equivalent exact way to retain the corrections uses commuting
square-zero x_i,y_j. Integrating one pair, i.e. reading its coefficient,
changes exp(x^T D y) to

    (a+UV) exp(x^T D y),  U=x^T c, V=r^T y.

When a is invertible, its connected logarithm is the finite polynomial

    log a + x^T D y
      + sum_{q=1}^m (-1)^(q+1) (UV)^q/(q a^q).           (5)

The logarithm here is formal on the nilpotent part; no analytic logarithm
is required. Its quadratic term is the Gaussian rank-one update, but its
quartic term -(UV)^2/(2a^2) is generically nonzero. Equation (5) repairs
the Gaussian ansatz exactly with a compact sum of powers at the first
pivot. Subsequent pivots require their mixed responses.

For a 2x2 eliminated block A=[[a,b],[c,d]], set P=ad+bc,
M=[[d,b],[c,a]], and source variables U_1,U_2,V_1,V_2. The exact boundary
factor is

    F = P + Q + R,
    Q = U^T M V,
    R = U_1 U_2 V_1 V_2.

Its connected quartic term is R/P-Q^2/(2P^2). If U=C^T x and V=R0 y,
the coefficient matrix indexed by pairs of remaining x and y variables
has entries

    per(C_(I,[2])) per((R0)_([2],J))/P
        - per((C M R0)_(I,J))/P^2.                      (6)

For the completely allowed input (at z=1)

    A=[[1,1],[1,2]], C=[[1,2],[2,1],[1,1]], R0=C^T,

all entries are 1+a_ij^2 for integer a_ij. Matrix (6) is

    [[-176/9, -112/9, -134/9],
     [-112/9, -8,     -28/3 ],
     [-134/9, -28/3,  -34/3 ]],

whose determinant is 32/81. Thus even this first repaired connected
interaction needs rank three, not a single rank-one channel.

`jet_experiments.py` also constructs the exact boundary polynomial after
a k-by-k block has been removed:

    F(x,y) = sum_{q=0}^k sum_{|S|=|T|=q}
        per(A_(T^c,S^c)) product_{j in S} U_j
                              product_{i in T} V_i,
    U=C^T x, V=R0 y.                                   (7)

Every coefficient in (7) is explicitly computed in the experiment; (7)
is not offered as a fast compiler. Taking the finite nilpotent logarithm
and reducing modulo 1000003 gives the stored rank certificates:

    removed k=2, remaining m=3: order 2 has rank 3 of 3;
    removed k=3, remaining m=4: order 2 has rank 6 of 6;
    removed k=4, remaining m=5: orders 2 and 3 have rank 10 of 10.

The complete integer instances and ranks are in `jet_results.json`.
All entries of A,C,R0 in the final witnesses are 1+s^2 for integer s,
and z=1, so these witnesses are inside the requested input family. Their
nonzero denominators modulo the displayed prime make each computed rank
a valid lower bound on the corresponding rational matrix rank. They
reject the tested bounded Gaussian/rank-one response classes; they do not
prove a general asymptotic lower bound for nonlinear arithmetic circuits.

## 5. Adaptive basis and divisions

A linear change of the commuting nilpotent generators cannot rotate a
dense U into one square-zero coordinate. Indeed

    (sum_i c_i x_i)^2 = 2 sum_{i<j} c_i c_j x_i x_j,

so its square is zero only when at most one c_i is nonzero. More generally,
the degree-one part of an algebra automorphism of Q[x]/(x_i^2) must be a
monomial matrix; higher-degree changes cannot cancel the degree-two part
of these squares. This closes one concrete adaptive-basis repair, while
leaving unrestricted nonlinear encodings open.

The implemented compiler avoids all divisions. If a future small rational
identity for the permanent in the formal entries B_ij is found, removing
divisions need not use its exponential degree in z: deform the independent
matrix entries along B(t)=B0+t(B-B0), choosing B0 with nonzero denominator
constants, and expand through degree n. An inverse with invertible rational
constant has an explicit truncated-series recurrence, and each rational
gate can be compiled in O(n^2) scalar operations. The determinant or
permanent's degree in the independent B entries is n; marking is done
afterward. This observation is conditional on providing such an identity,
an explicit suitable B0, and polynomial-bit rational constants. It does
not supply the missing rational identity.

## Conclusion for this node

The pivot hypothesis has a nontrivial exact local closure (4), explicit
mixed-interaction repairs (5)-(7), and a complete division-free scalar
realization with bound (3). Its direct scalar readout remains exponential.
The obstruction established is to the tested reset, Gaussian and rank-one
closures, not to all factor-origin nonlinear representations. The root
polynomial compiler objective remains unresolved by this node.
