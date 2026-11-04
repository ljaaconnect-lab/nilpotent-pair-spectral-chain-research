# Blueprint Informel — n55

The development contract is frozen in `n55-frozen-obligations.json`. Its four obligations concern actual Mathlib `Matrix.det` expressions over `Polynomial R`, not lists already declared to be determinant expansions. Here R is a commutative ring, rows and columns are `Fin n`, r is a matrix of natural-number labels, and the explicit row bounds are `r i j ≤ c i`. The central index is `K = ∑ i, c i`, the permutation label is `ρ(σ) = ∑ i, r i (σ i)`, and the weight is `∏ i, b i (σ i)`.

The main identity requires precisely the additional separating-label assumption `Function.Injective (rho r)`. The two matrices are independently defined entry by entry: forward entries are `Polynomial.monomial (r i j) (b i j)` and reverse entries are `Polynomial.monomial (c i - r i j) 1`.

## Acyclic proof graph

1. `central_sum_pairing` expands a real polynomial product of two finite sums. Mathlib's actual coefficient operation, its finite-sum linearity and monomial multiplication reduce the coefficient K to the equality of labels. The inherited `central_label_iff`, label injectivity and a sign-square hypothesis select diagonal terms. Commutativity gives `(e*w)*e = (e*e)*w`, then the weight remains.
2. `prod_monomials` proves the product-of-monomials identity by Finset induction, independently of coefficient extraction.
3. `permutation_sign_square` proves the needed square identity for the actual permutation sign cast into R. The two-unit theorem for the integers and cast identities discharge it; it is not an extra axiom.
4. `det_row_expansion` derives the row-indexed Leibniz formula from `Matrix.det_transpose` and `Matrix.det_apply'`. It gives precisely the entries `(i, σ i)`.
5. `forward_determinant_expansion` combines steps 2 and 4. The integer sign in `Polynomial R` is the constant polynomial of its cast in R, giving each monomial coefficient `εσ * weight b σ`.
6. `rho_le_index` sums the explicit row bounds.
7. `complement_label` uses finite-sum subtraction under those same bounds, yielding `∑ i, (c i - r i (σ i)) = K - ρ(σ)` over Nat. Parentheses keep both occurrences of i inside the sum binder.
8. `reverse_determinant_expansion` combines steps 2, 4 and 7. Every entry coefficient is 1, so the permutation coefficient is exactly εσ.
9. `central_determinant_pairing` applies step 1 to the two actual determinant expansions, discharging the bound by step 6 and the sign-square hypothesis by step 3.

The base-n specialization derives the separating-label condition from the n38 fixed-length assignment theorem, via `Fin.sum_ofFn` and permutation extensionality. `base_capacity_sum_add_one` proves the capacity sum by induction on an independent length: the inductive step uses `Fin.sum_univ_castSucc`, the previous sum plus 1, `Nat.succ_mul`, the positive-base predecessor identity and `Nat.pow_succ`. The exact canonical index is obtained by subtracting 1 through that proved equality. This proof is embedded explicitly in `base_n_determinant_pairing`; K is not assumed.

## Boundary and evaluation

The verified statement is an algebraic interface for Lemma 14.1(d) and the determinant mechanism in Proposition 14.2. The original marked weights can be supplied as elements of `R = Polynomial Q`. A formal equality to a separately defined marked permanent or a Vandermonde product requires its own Lean declarations; this node's report identifies exactly which declarations were accepted.

The original uniform polynomial scalar extractor remains an independent obligation. A coefficient operation on polynomials is not an allowed free scalar circuit gate; the finite permutation sums above do not establish a polynomial-size extraction algorithm. No arithmetic circuit size or bounded-literal construction hypothesis is introduced here.

Every invocation has an exact source snapshot, digest and diagnostics. The accepted file must match an exit-zero compiler invocation and all of its `#print axioms` outputs must lie in the standard trust base. Historical open-goal snapshots are rejected candidates. Shared Mathlib cache, Arbor state and held-out test boundaries are not modified.
