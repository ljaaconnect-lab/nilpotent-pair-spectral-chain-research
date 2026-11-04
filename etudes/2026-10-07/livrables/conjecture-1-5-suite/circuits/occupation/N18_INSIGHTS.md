# n18 measured result and remaining constructive step

Artifact version: n18-occupation-gram-v1. The new positive evaluator and its
36-assertion checklist were frozen before variant coding. Their hashes and
timestamp are in `n18-freeze.json`. The fixed proof blueprint and exact scalar
count derivation are in `N18_DESIGN.md`.

`python evaluate_occupation_gram.py --output n18-dev-report.json` exited 0
using SymPy 1.14.0. Development score: **36/36=1.0**. This is finite exact
identity/count success, not proof confidence. No n15 check was relabeled as new
evidence, no held-out data was accessed, and no counterexample generation or
negative lower-bound search was performed.

- n=2: T=4, actual encoding 16 gates, expanded support 4, extracted support 2.
- n=3: T=21, actual encoding 38 gates, expanded support 27, extracted support 6.
- n=4: T=156, actual encoding 71 gates, expanded support 256, extracted support 24.
- n=5: T=1555, actual encoding 110 gates, expanded support 3125, extracted support 120.

The predicted exact formula
4n^2-2+(n-1)(floor(log2(n+1))+popcount(n+1)-1) matched the actual binary +/*
nodes and their independently listed component totals. The full encoding has
polynomial scalar gate size, while its explicit expanded representation has
n^n terms in these marked tests. That observed representation size is not a
scalar circuit lower bound for its selected coefficient.

The nine assertions per dimension checked: the incidence Gram diagonal;
its determinant as a column product; the supported Cauchy-Binet sum with
actual incidence-minor determinants squared; the generic squarefree occupation
coefficient; the generic univariate coefficient after Kronecker substitution;
the exact original marked scalar DAG coefficient against an independent
permutation oracle; all scalar gate components; target-independent scalar
leaves; and the occupation-digit selector on all degree-n compositions.

At n=5 the Cauchy-Binet check enumerated 3125 supported edge sets and cached
120 actual incidence determinants. That symbolic check took 10.160 seconds;
generic occupation/Kronecker coefficient checks took 19.621 seconds; evaluating
the complete 110-gate marked DAG in Q[s,z] took 0.025 seconds. Total n5 elapsed
time was 29.820 seconds. The report preserves these real measurements and the
evaluator, checklist and implementation hashes.

The successful partial factorization is

    det(X diag(b_ij y_i) X^T) = product_j(sum_i b_ij y_i),

with n by n^2 fixed column-incidence X. Cauchy-Binet cancels the two local minor
orientations by squaring their signs. The remaining condition is row occupancy,
whose all-one coefficient equals P_A and therefore source Prop14.2's central
channel. Replacing y_i by s^((n+1)^i) makes occupancy injective with an explicit
polynomial-size power chain and target T=sum_i(n+1)^i.

All original p_ij=1+a_ij^2 and formal binary z addresses are retained. Neither
u/v initialization, the incidence factors, nor a scalar leaf contains P_A or
an unknown coefficient. The prescribed rational test A merely supplements
fully generic symbolic b_ij identities; z was never numerically specialized.

The exact remaining constructive sublemma is: from these cheap incidence and
diagonal factors, build a uniformly polynomial scalar circuit for the
squarefree occupation coefficient, or its Kronecker target T, preserving every
original z marker. This sublemma has not been supplied. Symbolic `coeff_monomial`
and dictionary filtering were development verification after expansion and
were not credited as scalar gates.

Hilbert reported that its recursive base-digit injectivity can support the
occupation selector once the indexed-sum encoding bridge is proved. General
Gram, Cauchy-Binet, coefficient-selector and circuit-bound claims in this leaf
remain UNVERIFIED until separately kernel checked. No original-target theorem
is established or refuted here.

Reproduce the new boundary with:

    python evaluate_occupation_gram.py --output n18-dev-report.json
