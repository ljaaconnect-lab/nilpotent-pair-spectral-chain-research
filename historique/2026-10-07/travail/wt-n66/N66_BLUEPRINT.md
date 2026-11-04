# n66: structured synchronization, exact interfaces still open

The fixed root protocol is n66-protocol.json, SHA256
8e60524976c79802c9828e6456d2cafee7576b7da064c2cd7f085cc5b4323f16.
This artifact does not implement the root extractor. It preserves two new
positive local constructions and states their missing global obligations.
The n64 unrestricted-master identity and the return to n15 are inherited
context, not rerun experiments or claimed new progress.

## Exact target and sign normalization

Write m=n², p=2m, and gamma_n=(-1)^(n(n-1)/2). With the n64 port order,

    F_Q = Pf Z[core,Q],  G_Q = Pf K[dummy,Q].

For a compatible matching S, Q=ports(S) consists of both a_e,b_e for e in S,
and the bordered determinant formula is

    F_Q = gamma_n (-1)^|S| Q_S,
    Q_S = (-1)^(sum I+sum J) sign(tau_S) b_S det B[I^c,J^c].

The target is therefore gamma_n sum_(paired Q) (-1)^(#a in Q) F_Q G_Q.
Absorb the degree sign by a FIXED congruence of K: D_a is -1 on every real
a_e, +1 on every real b_e and both dummy ports. Set Ktilde=D_a K D_a.
Then Gtilde_Q=(-1)^(#a in Q)G_Q. The exact synchronization interface becomes

    P(B) = gamma_n sum_(Q=union of edge pairs) F_Q Gtilde_Q.

The scalar leaves for this congruence are only ±1. It is a prescribed port
normalization, not an assumption about the arbitrary formal entries b_ij.

## Positive local holographic construction

The four tensor legs at edge e are (F_a,F_b,G_a,G_b). Their ordinary tensor
constraint is COPY4: nonzero only on 0000 and 1111, both with value one.
Let H=[[1,1],[1,-1]], H^-1=H/2. Exact finite tensor algebra gives

    H^(tensor4) COPY4 = 2 EVEN4.

EVEN4 has value one on even subsets and zero on odd subsets. It is the
principal-Pfaffian signature of J4 with all upper entries one: its pair
minors are one and its full Pfaffian is 1*1-1*1+1*1=1.

To preserve the scalar contraction, apply (H^-1)^(tensor p) to BOTH F and
Gtilde while replacing every COPY4 by 2 EVEN4. This is an exact change of
coordinates of the ordinary tensor network, with all normalization factors
specified. It uses no sign-average primitive. The transformed families are

    F'_x=2^-p sum_Q (-1)^|x intersection Q| F_Q,
    G'_x=2^-p sum_Q (-1)^|x intersection Q| Gtilde_Q.

The local transition in local_basis.py is an actual scalar butterfly DAG.
Forward H^(tensor4): 96 gates. Its inverse adds 112 gates; exact round trip:
208 gates. Direct construction of all n² LOCAL gadgets has 4n² positions
and 96n² gates. These costs concern the local basis operation only.

The direct transform of either whole p-port family has 2^p scalar values
and 3p*2^(p-1) forward butterfly gates. This is an exact upper bound for that
particular route, not a lower bound. No such whole-family vector is built or
tested in this leaf. The supporting n=2,3,4,5 layout checks explicitly record
that their generic b_ij are not processed by a complete extractor.

### Missing holographic construction, precise form

Produce matrices/auxiliary Gaussian kernels of order poly(n), from generic
B and the fixed incidence data, whose ordered signatures are exactly F' and
G'. An alternative is a polynomial-length coherent sum of such kernels,
with cheaply constructed coefficients and a polynomial charged contraction.
One cheap Pfaffian-sum calculation for EACH requested x does not establish
one coherent Gaussian family over ALL x.

The ordinary tensor Hadamard change is not being declared an automorphism
of the exterior algebra. Prove the port ordering, parity handling, and all
crossing signs when transporting the transformed network into a Gaussian
contraction. A drawing with reversed port order requires its explicit sign
normalization. The local EVEN4 identity alone does not prove these steps.

Primary background:
- Cai and Choudhary, Some Results on Matchgates and Holographic Algorithms,
  sections 2 and 6: https://pages.cs.wisc.edu/~jyc/papers/matchgate-holograph.pdf
- Bravyi, Contraction of matchgate tensor networks on non-planar graphs,
  sections 2-4: https://arxiv.org/html/0801.2989
  His compact Gaussian contraction theorem requires matchgate signatures
  and compatible index order. Those hypotheses are obligations here.

## Positive chiral elimination criterion

Split each family's Gaussian into a tail and the local two-port component.
For external odd covectors u,v and s,t, put U=u wedge v and V=s wedge t.
With the local ports first, their selected 11 coefficients have the form
a-U and b-V. A synchronized 00/11 contraction has residual scalar factor

    F=1+(a-U)(b-V), h=1+ab.

The following identity is division-free, over any commutative even algebra:

    h F - (h-bU)(h-aV) = UV.

local_basis.py constructs its left side using exactly 18 scalar add/mul
gates and verifies the universal symbolic identity in a,b,U,V. If UV=0 in a
proved context, this supplies a positive factorization. In a chart where h
is invertible it gives the corresponding normalized Gaussian step. Neither
UV=0 nor safe invertibility throughout a complete chain is assumed.

### Contextual Ward and Pluecker route

Let L_A(Q)=integral Q exp(theta^T A theta/2) with a fixed ordered Berezin
integral. A legitimate integration-by-parts identity is

    L_A(partial_i Q + (sum_j A_ij theta_j)Q)=0.

For one normalized Gaussian tail, Wick contraction of the four covectors is

    L_A(uvst)=L_A(uv)L_A(st)-L_A(us)L_A(vt)+L_A(ut)L_A(vs).

This is a four-by-four Pfaffian calculation from an explicit covariance.
It is a lawful cheap local calculation when its Gaussian-tail hypothesis
has been established. It does not automatically vanish.

For the actual iterative projection, Q must also include all synchronized
factors still present. Integration by parts differentiates those factors
as well. Keeping only the derivative of uvst drops specific terms from the
target. A quotient used to remove UV must therefore be stable under these
derivatives AND under all future target contractions.

An exact positive closure theorem could construct a polynomial-size module
of these contexts, explicit initialization, and transitions closing the
Ward/Pfaffian moments; or exhibit a target-preserving morphism in which the
four covectors are dependent. Dependence in the free algebra is sufficient
but is not required. No contextual cancellation has been assumed or proved.

The rank reduction in K's b-sector is genuine:

    K_bb = -C^T J_n C, C_(j,e)=delta_(j,col(e)).

Its rank is at most n. K_aa=J_lex is structured; it is not declared low rank.
Projection couples these sectors edge by edge, so the b-sector rank bound
alone is not a scalar compiler for the synchronized contraction.

## A constructive initial rational chart

This is an analytical proposal, not a tested or Lean-certified full chain.
For n>=2 choose B0_ij=1/(i+j+1), zero-based indices. Its explicit inverse is

    (B0^-1)_ij = (-1)^(i+j)(i+j+1)
      binom(n+i,n-j-1) binom(n+j,n-i-1) binom(i+j,i)^2.

Thus lambda_ij=B0_ij(B0^-1)_ji is the signed product of the three displayed
binomial factors. It is negative when i+j is odd. For i+j even its magnitude
is an integer greater than one: if i,j>0 then binom(i+j,i)>1; if one is zero,
one of the first two binomials has a strictly interior lower argument for
n>=2. Consequently all INITIAL h_ij=1-lambda_ij are nonzero.

All binomial coefficients involved have top argument at most 2n-1 and can
be constructed by a Pascal triangle in polynomial time. B0 entries have
O(log n) literal length; inverse entries and initial h_ij have O(n) length.
This provides safe det(B0) and safe initial one-edge normalizations. It does
not certify every later pivot after contextual synchronization. n=1 is a
separate trivial root instance and need not use this chart.

The displayed inverse formula is present in the official SciPy source:
https://github.com/scipy/scipy/blob/v1.18.0/scipy/linalg/_special_matrices.py
(invhilbert). This software source supplies the explicit formula; the
uniform closure and pivot obligations above remain mathematical obligations.

If a genuine polynomial-size rational root circuit and a globally safe B0
are constructed, use B(epsilon)=B0+epsilon(B-B0). The target has generic
total degree n before z markers, so length n+1 truncation in epsilon suffices
after denominator elimination. Every coefficient convolution is charged;
evaluation at epsilon=1 then gives the target. This route never truncates
at K=n^n-1 and never gives a free final coefficient operator.

The globally safe point must cover denominators of that ACTUAL rational
circuit. A safe initial inverse is not a certificate for an unspecified
future circuit. No whole rational root circuit is claimed in n66.

## Frozen evidence and exact remaining score

The supporting evaluator and source were frozen before execution in
n66-source-freeze.json. Its 53 exact symbolic checks pass: 16 forward local
transitions, 16 inverse transitions, 16 COPY4/J4 components, one universal
chiral-residual identity, and four counted local layouts.

These are supporting finite symbolic checks, not formal theorem proofs.
No Lean compiler run occurred in n66. LocalGadget.lean is an uncompiled
supporting draft; the coordinator assigned an independent formal bridge to
n67. No accepted declaration or axiom audit is claimed for this draft.

The three ORIGINAL root obligations remain unclosed:
1. A complete explicit scalar root transition from generic B.
2. Its polynomial gate/literal/initialization certificate.
3. Its exact root-target identity with a complete verified dependency chain.

Strict root development score: 0/3=0.0. Supporting pass fraction: 53/53=1.0,
reported separately. No B_test data were accessed. No counterexample or
lower-bound experiment was performed. The complete positive construction
remains open; the local identities are retained as inputs to later nodes.
