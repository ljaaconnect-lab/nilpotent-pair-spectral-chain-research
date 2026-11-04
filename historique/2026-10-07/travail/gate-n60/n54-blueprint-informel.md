# Blueprint Informel — n54

## Fixed objective and domain

For an arbitrary `R : Type` with `[CommRing R]`, define `interp p` to be the actual Mathlib polynomial obtained by summing `Polynomial.monomial exponent coefficient` over the finite sparse list `p : List (Nat × R)`. Repeated exponents are permitted and their coefficients add. Sparse multiplication is the existing Cartesian product of terms, adding exponents and multiplying coefficients; it is not defined through the target coefficient.

The intended conclusion is an equality of an actual `Polynomial.coeff` of an actual polynomial product. The signed pairing requires the unchanged hypotheses: nonnegative natural-number labels, no repeated labels, every label at most K, and signs equal to 1 or −1. The indexed corollary uses fixed-length functions `Fin length → Fin base`, a positive base and a list of distinct assignments. It does not weaken the distinctness or length conditions.

## Acyclic dependencies

1. `interp_append`: interpretation sends append to polynomial addition. List sum and monomial definitions suffice.
2. `interp_monomial_multiply`: multiply every sparse term by one monomial, then interpret. This uses the Mathlib identity `monomial n r * monomial m s = monomial (n + m) (r * s)` and distributivity, by induction on the right list.
3. `interp_multiply`: interpret the actual Cartesian sparse product. Induct on the left list using steps 1 and 2. No coefficient extraction appears in this proof.
4. `coeff_interp`: polynomial coefficient equals the original sparse sum of coefficients with matching exponents. Use the independently established Mathlib list-sum identity `Polynomial.coeff_list_sum_map` and `Polynomial.coeff_monomial`.
5. `central_polynomial_coefficient`: rewrite the actual polynomial product by step 3 and its actual coefficient by step 4, then apply the independently verified `GeneralCollisionPairingRing.central_product_coefficient`.
6. `indexed_assignment_polynomial_coefficient`: the same interpretation rewrites, followed by the independently verified `CollisionLabelBridge.indexed_assignment_pairing`. Its separating-label and bound obligations were already proved in n38.

Each final declaration has an explicit `#print axioms` audit. Historical candidate snapshots can contain open goals; they are rejected compiler evidence, not accepted declarations. The accepted source must contain no placeholder and its exact digest must match an exit-zero round.

## Mathematical and complexity boundary

This bridge lets weights themselves be polynomials in z by taking `R = Polynomial Q`. It transfers a proven sparse coefficient identity to the established polynomial library without assigning a new computational primitive to coefficient extraction.

The document's full determinant and Vandermonde expansions must still be connected to these two signed polynomial sums, with their exact permutation signs and exponents. Even after that algebraic connection, the conjecture's uniform polynomial-size scalar extraction circuit over Q remains a separate proof obligation: only the allowed scalar arithmetic gates and bounded rational literals may be used. Neither finite list enumeration nor `Polynomial.coeff` is a free gate, and this node assumes no size bound for an extractor.

## Evaluation boundary

Only Lean development compilations and source/axiom audit are executed in this worktree. Shared Mathlib cache, Arbor state and held-out boundaries remain outside the node's mutations. A helper score of 1 means these declared identities are verified; it is not a score for the unresolved root conjecture.
