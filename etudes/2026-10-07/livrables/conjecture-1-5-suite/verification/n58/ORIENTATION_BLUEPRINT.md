# n56 verified double orientation

The fixed boundary is `orientation-obligations.json`. Its six obligations were
frozen before any candidate proof attempt. The domain is an arbitrary `Ring R`,
which permits noncommutative multiplication, and an arbitrary index type `I`.
The source never assumes `CommRing R`.

`OddRelations x y` explicitly records these relations for every index pair:

- `x_i*x_i=0` and `y_i*y_i=0`;
- `x_i*x_j=-(x_j*x_i)`;
- `y_i*y_j=-(y_j*y_i)`;
- `y_i*x_j=-(x_j*y_i)`.

The same-index x/x and y/y relations already follow from square-zero. Including
them in the all-pairs statement preserves the ordinary exterior-like relations
without a hidden characteristic assumption. No finite-dimensional model or
coordinate projection is assumed.

## Accepted invariant

For `q_i=x_i*y_i`, Lean verifies `q_i*q_i=0` and `q_i*q_j=q_j*q_i`. It also verifies,
for every finite index list L with n=length(L),

    prod_i_in_L (x_i*y_i)
      = (-1)^(n*(n-1)/2) * (prod_i_in_L x_i) * (prod_i_in_L y_i).

All three products retain the order of L. The theorem requires no `Nodup` or
distinct-index assumption; its explicit relations suffice for arbitrary lists.
This is the global double-orientation sign gamma_n requested by Step A.

The dependency chain is acyclic. The extra local crossing lemma derives
`(ab)(cd)=-(ac)(bd)` from `bc=-(cb)` by applying `congrArg` and associativity.
It supplies paired nilpotence and paired commutation. `sign_central` establishes
centrality of powers of -1, while `cross_list` uses length induction to move y_i
past n x-generators with factor `(-1)^n`. The existing, pinned Mathlib theorem
`Nat.triangle_succ` gives the exact exponent recurrence. Applying `congrArg` to
the verified list-crossing equality reconstructs the global induction step.

## Actual verification evidence

The final source `DoubleOrientation.lean` compiled with Lean 4.34.1, exit code 0,
in complete candidate round 13. Every one of its seven theorem axiom audits is
exactly `[propext]`. There are no incomplete goals, placeholders, added axioms,
or forbidden trust extensions. The frozen development score is 6/6=1.0, an
obligation pass fraction rather than confidence in the root conjecture.

Exactly thirteen complete candidate compiles were consumed from the twenty-round
budget. One import/name probe was run separately. Actual diagnostics and hashes
are retained in `orientation-progress.json`; `orientation-report.json` checks
the final source and frozen protocol hashes before distilling the accepted run.
The verifier supplies all three exported Lean environment fields and invokes
the existing pinned compiler directly. No additional cache dependency was
downloaded or built, and no held-out data or shared Arbor state was accessed.

## Constructive boundary

The paired generators commute inside the explicitly specified ring. This does
not make arithmetic on an exterior-algebra representation unit-cost scalar
arithmetic over Q. No top-coordinate, residue, coefficient, or diagonal is
introduced as a free gate. The root polynomial sign-correction conjecture is
not proved by this artifact. The next constructive theorem must compile the
required contraction into a polynomial-size scalar circuit with cheaply
computed initialization and the original gate restrictions.
