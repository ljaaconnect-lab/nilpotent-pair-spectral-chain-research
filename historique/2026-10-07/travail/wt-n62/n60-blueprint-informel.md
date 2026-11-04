# Blueprint Informel — n60

The two main obligations are frozen in `n60-frozen-obligations.json`. For an arbitrary commutative coefficient ring R and n≥2, Hhat is the actual polynomial

`1 + X^(2K) + det(forwardMatrix b (baseLabels n)) * ∏ i, ∏ l ∈ Ioi i, (X^(n^i.val) - X^(n^l.val))`,

where K=`n^n−1`. The target is its actual Mathlib coefficient at K, equal to the unsigned permutation-weight sum. The second target supplies the original rational matrix A, with inner polynomial weights `C(1 + a_ij^2) * z^(2^(i*n+j))`, and equates that coefficient with the explicit marked permanent polynomial.

## Acyclic proof dependencies

1. `centralDegree_pos` derives K>0 from n≥2 using the natural power inequality and subtraction positivity. K>0 is not added as an independent hypothesis of the main theorem.
2. `padding_coefficient` computes the actual coefficients of 1 and X^(2K). Their conditional degrees are K=0 and K=2K; both are impossible from K>0. Linearity therefore preserves the central coefficient of any polynomial p under padding.
3. The n55 `base_n_determinant_pairing` gives the coefficient K of the product of the two actual labelled determinants. Its label injection and exact K were already separately proved.
4. A frozen, source-hash-audited n58 reverse Vandermonde bridge rewrites the complementary determinant as the correctly oriented product over i<l. Its source may be copied and imported only after the committed ref is supplied; provenance is recorded separately.
5. `hhat_central_coefficient` combines steps 1–4. It asserts the coefficient of the explicit padded polynomial, without granting a coefficient operation as an arithmetic circuit gate.
6. `marked_weight_eq` uses the n55 finite product of monomials to combine the original marked entries. The coefficient becomes the product of amplitudes; the exponent becomes the sum of binary cell addresses.
7. `marked_A_central_identity` instantiates step 5 with `R = Polynomial Rat` and uses step 6 on each permutation. The outer X is t and the inner X is z; both are actual polynomial types.

## Accepted scope and limits

The final strict report identifies the declarations that compiled and their exact source digest. It audits the imported frozen n58 source as a locally rebuilt dependency and retains every compiler diagnostic and source snapshot. The two main frozen statements cannot be removed or changed to simplify their proofs.

This node closes the specified encoding identity. It does not provide the conjecture's uniform polynomial-size scalar extraction circuit, a proof of its bounded rational literals, or a free coefficient/residue operation. Gate bounds in other nodes remain separate evidence; this node introduces no new circuit complexity claim.

Only development compilation and source/axiom audits are run. Shared Mathlib cache, Arbor state and held-out test boundaries are not modified.

## Frozen execution evidence

The dependency is the exact `ReverseVandermonde.lean` from n58 commit `96fdd0ca11ad17b0824d213539cc6166df569de0`, SHA256 `457aacf7229668489f1750f68ffdee9e7a497773e9ed7b60ba80135486f6c88a`. Its nine axiom audits were reproduced locally at compiler round 11. The helper `reverse_factor` uses its `paper_monomial_det` theorem by definitional equality with the n55 matrix definitions.

The final source compiled at round 15: candidate 10, after five dependency builds. All seven new declarations have explicit axiom audits. Both frozen main obligations are accepted. Three earlier candidate failures are retained as full source snapshots and diagnostics: padding simplification left natural-degree conditions open; a premature simplification of `centralDegree` hid the padding rewrite; and simplification did not unfold the complete matrix under the determinant. The final proof discharges the degree conditions and uses explicit proof terms for the latter two interfaces. These were proof-script constraints and do not supply any mathematical counterexample.

The exact source and contract digests, theorem statements, local dependency builds, imported-source provenance, complete invocation history and accepted axiom sets appear in `n60-strict-report.json`. This score is two accepted frozen development obligations out of two; it is not a score for the unresolved complexity conjecture.
