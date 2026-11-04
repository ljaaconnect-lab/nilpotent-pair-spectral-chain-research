# n15 result and distilled insight

Artifact version: n15-gray-half-character-v1. The implementation, hypothesis,
28-check positive boundary and complete gate derivation were frozen before the
first run. `n15-freeze.json` records their hashes and the pre-execution time.
The fixed design is in `N15_DESIGN.md`; the machine-readable persistent
hypothesis is `n15-hypothesis.json`.

`python validate_half_character.py --output n15-dev-report.json` exited 0
with SymPy 1.14.0. Development assertion score: **28/28=1.0**. The held-out
boundary was not accessed. No baseline subset-transfer validation was repeated.
The positive checks compare generic symbolic identities and the new actual
marked scalar DAG with independently enumerated permutation products.

- n=2: half-character dimension 2, actual scalar DAG 18 gates, marked support 2.
- n=3: half-character dimension 4, actual scalar DAG 54 gates, marked support 6.
- n=4: half-character dimension 8, actual scalar DAG 124 gates, marked support 24.
- n=5: half-character dimension 16, actual scalar DAG 260 gates, marked support 120.

All original amplitudes p_ij=1+a_ij^2 and addresses 2^(i*n+j) are retained.
The marked test matrices use the prescribed rational input formula from the
frozen hypothesis; z is formal throughout. Generic SymPy x_ij validations
supplement those finite rational checks without replacing the original target.

At n=5 the direct symbolic diagonal contraction took 45.065 seconds and the
symbolic Gray contraction took 23.461 seconds. Exact Q[z] evaluation of all
260 actual gates took 0.620 seconds. Total n5 validation took 69.393 seconds.
The report separates verification expansion costs from the counted scalar
graph and records polynomial term/storage measurements and every Gray mask.

The lawful compression is the global sign pairing delta ~ -delta, leaving
2^(n-1) sign channels. The left covector, right vector and each diagonal row
factor are explicitly constructed from marked entries and small constants.
Their initialization does not contain P_A, a central coefficient, or an unknown
terminal value. Gray sharing proves the exact implementation count
5n(n-1)+n*2^n, including marker preparation and signed normalization.

This produces a different factorization from nilpotent subset transfer, but its
gate counts exceed the existing subset DP counts in these small dimensions.
Its principal value is a cheap-initialized character representation and a
precise bridge obligation for a kernel proof; it supplies no polynomial gate
bound. The growth formula is derived from the graph, not curve-fitted, and it
is not a lower bound against other algorithms.

The exact bridge lemma sent to the coordinator is the half-character
assignment projector: its sign sum equals 2^(n-1) for a bijection and zero for
every other assignment. `N15_DESIGN.md` lists the fiber regrouping, independent
sign summation, parity and degree-budget sublemmas. All general proof claims
remain conditional until Lean verifies those statements. This leaf's SymPy
success is not a kernel check.

Path adjustment: a further compression must eliminate the remaining
exponential character contraction while retaining cheap scalar initial data.
Do not promote the r diagonal channels into a polynomial-size representation
by treating their sum or the product of tensor factors as one scalar gate.
The required polynomial contraction lemma is not supplied or assumed here.
No original-target theorem is proved or disproved by this node.
