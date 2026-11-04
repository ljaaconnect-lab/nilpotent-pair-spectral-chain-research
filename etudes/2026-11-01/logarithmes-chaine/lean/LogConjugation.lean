import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Tactic.Ring

/-!
Algebraic logarithmic conjugation. No analytic logarithm is introduced.
The hypothesis `D H = H * v` is required; no initialization or complexity
bound for `v` is asserted by this file.
-/

namespace LogConjugation

open scoped BigOperators

variable {R : Type*} [CommRing R]

theorem conjugate_second_order (D : R →+ R)
    (hD : ∀ x y, D (x * y) = D x * y + x * D y) (H F v : R)
    (hH : D H = H * v) :
    D (D (H * F)) - D (H * F) =
      H * (D (D F) + (2 * v - 1) * D F + (D v + v ^ 2 - v) * F) := by
  simp only [hD, map_add, hH]
  ring

theorem conjugate_finite_sum {ι : Type*} (t : Finset ι) (c : R)
    (D : ι → R →+ R)
    (hD : ∀ j x y, D j (x * y) = D j x * y + x * D j y)
    (H F : R) (v : ι → R) (hH : ∀ j, D j H = H * v j) :
    c * (∑ j ∈ t, (D j (D j (H * F)) - D j (H * F))) =
      H * (c * ∑ j ∈ t,
        (D j (D j F) + (2 * v j - 1) * D j F +
          (D j (v j) + (v j) ^ 2 - v j) * F)) := by
  simp_rw [conjugate_second_order (D _) (hD _) H F (v _) (hH _)]
  simp only [← Finset.mul_sum, mul_left_comm]

theorem conjugate_reader_factor (L A : R → R) (H F rInv : R)
    (h : L (H * F) = H * A F) :
    H * F - rInv * L (H * F) = H * (F - rInv * A F) := by
  rw [h]
  ring

end LogConjugation

#print axioms LogConjugation.conjugate_second_order
#print axioms LogConjugation.conjugate_finite_sum
#print axioms LogConjugation.conjugate_reader_factor
