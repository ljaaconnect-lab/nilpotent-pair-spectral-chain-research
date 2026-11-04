import Mathlib.Data.Nat.Basic
import Mathlib.Tactic.Linarith

/-!
Arithmetic bound for the single-frequency scalar preparation.
The gate-count formula is the separately justified input to this theorem.
No cost bound for oriented quotient reduction or terminal scalar reading
is assumed or established here.
-/

namespace LinearisedPreparationBound

theorem cubic_preparation_bound (n N ell : ℕ)
    (hn : 1 ≤ n) (hN : N ≤ 2 * n) (hell : ell ≤ n) :
    4 * n ^ 2 - 1 + 2 * n * N * ell + 3 * n * N - 1 ≤ 18 * n ^ 3 := by
  have hmul := Nat.mul_le_mul hN hell
  have hspectral := Nat.mul_le_mul_left (2 * n) hmul
  have hlinear := Nat.mul_le_mul_left (3 * n) hN
  have hdegree := Nat.mul_le_mul_left (n * n) hn
  nlinarith [Nat.sub_le (4 * n ^ 2) 1,
    Nat.sub_le (4 * n ^ 2 - 1 + 2 * n * N * ell + 3 * n * N) 1]

end LinearisedPreparationBound

#print axioms LinearisedPreparationBound.cubic_preparation_bound
