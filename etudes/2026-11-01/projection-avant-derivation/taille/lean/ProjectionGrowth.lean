import Mathlib.Data.Nat.Basic
import Mathlib.Algebra.Order.Monoid.Unbundled.Pow
import Mathlib.Tactic.Linarith

/-!
Pure natural-number arithmetic for the separately documented direct compiler.
The cost lower bound is an explicit hypothesis of the final theorem.
The compiler's syntactic reachability and node injection are not formalized here.
No impossibility statement for alternative scalar circuits is asserted.
-/

namespace ProjectionGrowth

theorem exponent_gap (K c : ℕ) :
    ∃ k ≥ 2, K + c * k < 2 ^ (k - 1) := by
  refine ⟨2 * (K + 2 * c + 2) + 1, ?_, ?_⟩
  · omega
  · have hbase : K + 2 * c + 2 + 1 ≤ 2 ^ (K + 2 * c + 2) :=
      Nat.succ_le_of_lt Nat.lt_two_pow_self
    have hsquare := Nat.mul_le_mul hbase hbase
    rw [← pow_add, ← two_mul] at hsquare
    simp only [Nat.add_sub_cancel]
    nlinarith

theorem exponential_beats_polynomial (K c : ℕ) :
    ∃ k ≥ 2, K * (2 ^ k) ^ c < 2 ^ (2 ^ (k - 1)) := by
  rcases exponent_gap K c with ⟨k, hk, hgap⟩
  refine ⟨k, hk, lt_of_le_of_lt
    (Nat.mul_le_mul_right ((2 ^ k) ^ c)
      (Nat.le_of_lt (Nat.lt_two_pow_self (n := K)))) ?_⟩
  simpa only [← pow_mul, ← pow_add, Nat.mul_comm k c] using
    (Nat.pow_lt_pow_right (by decide : 1 < (2 : ℕ)) hgap)

theorem no_uniform_polynomial_bound
    (C : ℕ → ℕ)
    (lower : ∀ k, 2 ≤ k → 2 ^ (2 ^ (k - 1)) ≤ C (2 ^ k)) :
    ¬ ∃ K c : ℕ, ∀ n : ℕ, C n ≤ K * n ^ c := by
  rintro ⟨K, c, upper⟩
  obtain ⟨k, hk, strict⟩ := exponential_beats_polynomial K c
  exact (not_lt_of_ge ((lower k hk).trans (upper (2 ^ k)))) strict

end ProjectionGrowth

#print axioms ProjectionGrowth.exponent_gap
#print axioms ProjectionGrowth.exponential_beats_polynomial
#print axioms ProjectionGrowth.no_uniform_polynomial_bound
