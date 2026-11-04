import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Tactic.Ring

/-!
Algebraic double-log conjugation. The hypothesis `D E = E * w`
represents the formal relation E = exp(V), w = D V.
No analytic logarithm, circuit bound, or complexity collapse is asserted.
-/

namespace DoubleLogConjugation

open scoped BigOperators

variable {R : Type*} [CommRing R]

theorem derivation_one (D : R →+ R)
    (hD : ∀ x y, D (x * y) = D x * y + x * D y) : D 1 = 0 := by
  apply add_left_cancel (a := D 1)
  simpa only [mul_one, one_mul, add_zero] using (hD 1 1).symm

theorem double_log_second_order (D : R →+ R)
    (hD : ∀ x y, D (x * y) = D x * y + x * D y) (E w : R)
    (hE : D E = E * w) :
    D (D (E - 1)) - D (E - 1) + (D (E - 1)) ^ 2 =
      E * (D w - w) + (E + E ^ 2) * w ^ 2 := by
  simp only [map_sub, derivation_one D hD, sub_zero, hD, hE]
  ring

theorem double_log_finite_sum {ι : Type*} (t : Finset ι) (c : R)
    (D : ι → R →+ R)
    (hD : ∀ j x y, D j (x * y) = D j x * y + x * D j y)
    (E : R) (w : ι → R) (hE : ∀ j, D j E = E * w j) :
    c * (∑ j ∈ t,
      (D j (D j (E - 1)) - D j (E - 1) + (D j (E - 1)) ^ 2)) =
      E * (c * ∑ j ∈ t, (D j (w j) - w j)) +
        (E + E ^ 2) * (c * ∑ j ∈ t, (w j) ^ 2) := by
  simp_rw [double_log_second_order (D _) (hD _) E (w _) (hE _)]
  simp only [Finset.sum_add_distrib, ← Finset.mul_sum, mul_add, mul_left_comm]

theorem double_log_reader_factor (H E a b rInv : R) :
    H - rInv * (H * (E * a + (E + E ^ 2) * b)) =
      H * (1 - rInv * E * (a + (1 + E) * b)) := by
  ring

end DoubleLogConjugation

#print axioms DoubleLogConjugation.derivation_one
#print axioms DoubleLogConjugation.double_log_second_order
#print axioms DoubleLogConjugation.double_log_finite_sum
#print axioms DoubleLogConjugation.double_log_reader_factor
