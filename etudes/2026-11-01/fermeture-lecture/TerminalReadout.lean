import TerminalDifference
import Mathlib.Tactic.Ring
import Mathlib.Data.Fintype.Perm
import Mathlib.Data.List.FinRange

set_option Elab.async false

namespace OrientedOperators.TerminalReadout

open Polynomial

/-- Terminal-degree readout commutes with any finite sum of products.
Every product has `n` zero-constant factors. -/
theorem coeff_sum_products {R A : Type*} [Semiring R]
    (s : Finset A) (ps : A → List R[X]) (n : ℕ)
    (hlen : ∀ a ∈ s, (ps a).length = n)
    (hz : ∀ a ∈ s, ∀ p ∈ ps a, p.coeff 0 = 0) :
    (∑ a ∈ s, (ps a).prod).coeff n =
      ∑ a ∈ s, ((ps a).map (fun p => p.coeff 1)).prod := by
  rw [Polynomial.finsetSum_coeff]
  refine Finset.sum_congr rfl (fun a ha => ?_)
  simpa only [hlen a ha] using
    TerminalDifference.coeff_product_at_length (ps a) (hz a ha)

/-- Specializing the finite family to permutations reads the permanent
of the linear coefficients, without requiring a matrix-valued oracle. -/
theorem coeff_permutation_sum {R : Type*} [Semiring R] (n : ℕ)
    (p : Fin n → Fin n → R[X]) (x : Fin n → Fin n → R)
    (hz : ∀ r c, (p r c).coeff 0 = 0)
    (hx : ∀ r c, (p r c).coeff 1 = x r c) :
    (∑ σ : Equiv.Perm (Fin n),
      ((List.finRange n).map (fun r => p r (σ r))).prod).coeff n =
      ∑ σ : Equiv.Perm (Fin n),
        ((List.finRange n).map (fun r => x r (σ r))).prod := by
  have hl : ∀ σ : Equiv.Perm (Fin n),
      ((List.finRange n).map (fun r => p r (σ r))).length = n := by simp
  have hz' : ∀ σ : Equiv.Perm (Fin n),
      ∀ q ∈ (List.finRange n).map (fun r => p r (σ r)), q.coeff 0 = 0 := by
    simp [hz]
  simpa only [List.map_map, Function.comp_def, hx] using
    coeff_sum_products Finset.univ
      (fun σ : Equiv.Perm (Fin n) => (List.finRange n).map (fun r => p r (σ r))) n
      (fun σ _ => hl σ) (fun σ _ => hz' σ)

/-- An affine substitution into the original weight `1 + a^2` exposes
an arbitrary entry as the linear term.  `h` is any inverse of two, and
`i` may lie in the uniform quadratic algebra adjoining a root of -1. -/
theorem affine_weight {R : Type*} [CommRing R]
    (i h t x : R) (hi : i ^ 2 = -1) (hh : 2 * h = 1) :
    1 + (i - i * h * t * x) ^ 2 = t * x - h ^ 2 * t ^ 2 * x ^ 2 := by
  calc
    1 + (i - i * h * t * x) ^ 2 =
        1 + i ^ 2 - i ^ 2 * (2 * h) * (t * x) + i ^ 2 * h ^ 2 * t ^ 2 * x ^ 2 := by ring
    _ = t * x - h ^ 2 * t ^ 2 * x ^ 2 := by simp [hi, hh, sub_eq_add_neg]

#print axioms coeff_sum_products
#print axioms coeff_permutation_sum
#print axioms affine_weight

end OrientedOperators.TerminalReadout
