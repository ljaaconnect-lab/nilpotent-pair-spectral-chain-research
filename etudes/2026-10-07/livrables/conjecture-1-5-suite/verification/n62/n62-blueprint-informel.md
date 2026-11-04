# Blueprint Informel — n62

The root's seven development obligations are fixed in `n62-frozen-obligations.json`. Their exact Lean binder and definition plan was written to `n62-formal-obligations.json` before the first candidate compilation. The domain is an arbitrary commutative coefficient ring R, with arbitrary finite dimension n for permutations and arbitrary index type S for pointwise actions.

## Acyclic decomposition

1. `inversion_phase_eq_signCoeff` transports Mathlib's actual `Equiv.Perm.sign_eq_prod_prod_Ioi` from integer units to R. The ordered pair factors test the genuine permutation comparison; no signature formula is assumed.
2. `local_mixed_cofactor` computes the four scalar corner evaluations of the actual bilinear expression `a + b*x + c*y + d*x*y`, giving d by commutative ring algebra.
3. `local_xy_correction` computes `F(x,y) - 2*x*y*mixedCofactor`, changing precisely the mixed term to `-d*x*y`. The four corner evaluations and the scalar subtraction are explicit definitions.
4. `phase_involution` shows that applying the same pointwise conditional negation twice returns the original function. Its predicate and decidability instance are explicit.
5. `phase_commute` shows that two such actions commute for all predicates and all functions. These facts do not require an index enumeration or the permutation interpretation.
6. `corrected_signed_weight` combines step 1 with n55's verified `permutation_sign_square`, for the actual product weight of an arbitrary matrix b. Its inputs contain the signed weight and the correction phase, and its conclusion is the unsigned product.
7. `corrected_signed_sum` sums step 6 over all permutations. It is an equality of actual finite sums and has no n≥2 restriction.

## Scope

The scalar bilinear example is a complete local identity. The function-valued phase actions are a mathematical coefficient-action model. Their involutivity and commutation do not turn a coefficient-selection operation into an available scalar arithmetic gate. This node neither constructs the full scalar sign corrector nor grants a free pointwise access to polynomial coefficients. The original uniform constructor, polynomial gate count and bounded rational literals remain separate obligations of Conjecture 1.5.

All compiler attempts and source snapshots are journalled. Dependency builds and exact frozen replays are counted separately from the 12-candidate budget. No shared cache, Arbor state, outputs or held-out test boundary is modified. Inherited Lean sources remain byte-for-byte unchanged.

## Frozen verification evidence

All seven declarations compiled together at invocation 13, candidate 9, with exit code 0. Four inherited dependency builds are separate from these nine candidates. There were no probe compilations and no frozen replays. The strict development score is seven accepted fixed obligations out of seven.

The two local ring identities depend only on `propext`. The other five declarations use only the agreed Lean trust base `propext`, `Classical.choice`, and `Quot.sound`. Every declaration has an explicit `#print axioms` audit. `n62-strict-report.json` records the exact statements, source digest, both frozen contract digests, dependency source digests, compiler environments and invocation history.

An initial sequencing mistake launched the first candidate before the determinant dependency build completed. It exited 1 on the missing import, and both runners used the temporary journal number 4. The original report and overwritten snapshot remain in `n62-compiler-rounds/journal-collision-*`; the recovered entries disclose their provenance and have unique identifiers 4 and 5. `n62-journal-incident.json` records the actual tool session exits and repair. The failed candidate remains charged to the budget. An exclusive process lock and a source-byte digest captured before compilation prevent recurrence. The only subsequent mathematical proof-script failure was the cast of conditional unit factors; adding the existing `apply_ite` rewrite closed that interface without changing the statement.

The signature source and compiled Mathlib module have explicit SHA256 provenance. The cache is extracted source with no separate Mathlib Git repository, so no enclosing research-repository commit is represented as a Mathlib revision. The toolchain declaration is `leanprover/lean4:v4.34.1`.
