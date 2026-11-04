import Mathlib.Algebra.Ring.Basic
import Mathlib.Algebra.BigOperators.Ring.Finset

set_option Elab.async false

namespace OrientedOperators.ResolventFusion

variable {R : Type*} [Ring R]

/-- The noncommutative resolvent factorization uses a left inverse only. -/
theorem factorization (Y Z Ry : R) (hy : Ry * (1 - Y) = 1) :
    1 - Ry * Z = Ry * (1 - Y - Z) := by
  rw [mul_sub, hy]

/-- A resolvent update followed by the preceding resolvent equals the
resolvent at the sum.  All hypotheses are explicit one-sided inverses. -/
theorem fusion (Y Z Ry S T : R)
    (hy : Ry * (1 - Y) = 1)
    (hs : S * (1 - Ry * Z) = 1)
    (ht : (1 - Y - Z) * T = 1) :
    S * Ry = T := by
  calc
    S * Ry = S * Ry * ((1 - Y - Z) * T) := by rw [ht, mul_one]
    _ = (S * (Ry * (1 - Y - Z))) * T := by simp only [mul_assoc]
    _ = T := by rw [← factorization Y Z Ry hy, hs, one_mul]

/-- The same fusion preserves any right-hand input, such as a generator
or an observer vector encoded as a matrix. -/
theorem observer_fusion (Y Z Ry S T v : R)
    (hy : Ry * (1 - Y) = 1)
    (hs : S * (1 - Ry * Z) = 1)
    (ht : (1 - Y - Z) * T = 1) :
    S * (Ry * v) = T * v := by
  rw [← mul_assoc, fusion Y Z Ry S T hy hs ht]

/-- A division-free finite geometric resolvent. -/
def finiteResolvent (Y : R) (d : ℕ) : R :=
  ∑ k ∈ Finset.range d, Y ^ k

theorem finite_mul_sub (Y : R) (d : ℕ) :
    finiteResolvent Y d * (1 - Y) = 1 - Y ^ d := by
  induction d with
  | zero => simp [finiteResolvent]
  | succ d ih =>
    rw [finiteResolvent, Finset.sum_range_succ, add_mul, ← finiteResolvent,
      ih, mul_sub, mul_one, ← pow_succ, sub_add_sub_cancel]

theorem sub_mul_finite (Y : R) (d : ℕ) :
    (1 - Y) * finiteResolvent Y d = 1 - Y ^ d := by
  induction d with
  | zero => simp [finiteResolvent]
  | succ d ih =>
    rw [finiteResolvent, Finset.sum_range_succ, mul_add, ← finiteResolvent,
      ih, sub_mul, one_mul, ← pow_succ', sub_add_sub_cancel]

theorem finite_left_inverse (Y : R) (d : ℕ) (hy : Y ^ d = 0) :
    finiteResolvent Y d * (1 - Y) = 1 := by
  simpa only [hy, sub_zero] using finite_mul_sub Y d

theorem finite_right_inverse (Y : R) (d : ℕ) (hy : Y ^ d = 0) :
    (1 - Y) * finiteResolvent Y d = 1 := by
  simpa only [hy, sub_zero] using sub_mul_finite Y d

/-- All inverses in the fusion formula are explicit finite sums. -/
theorem finite_fusion (Y Z : R) (d : ℕ)
    (hy : Y ^ d = 0)
    (hz : (finiteResolvent Y d * Z) ^ d = 0)
    (hyz : (Y + Z) ^ d = 0) :
    finiteResolvent (finiteResolvent Y d * Z) d * finiteResolvent Y d =
      finiteResolvent (Y + Z) d := by
  apply fusion Y Z (finiteResolvent Y d)
  case ht => simpa only [sub_sub] using finite_right_inverse (Y + Z) d hyz
  all_goals exact finite_left_inverse _ _ (by assumption)

#print axioms factorization
#print axioms fusion
#print axioms observer_fusion
#print axioms finite_mul_sub
#print axioms sub_mul_finite
#print axioms finite_left_inverse
#print axioms finite_right_inverse
#print axioms finite_fusion

end OrientedOperators.ResolventFusion
