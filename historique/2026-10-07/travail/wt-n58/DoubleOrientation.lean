import Mathlib.Data.Matrix.Mul
import Mathlib.Algebra.Ring.Commute
import Mathlib.Tactic.Ring
import Mathlib.Data.Nat.Choose.Basic

namespace DoubleOrientation

set_option maxHeartbeats 50000

variable {R I : Type*} [Ring R]

structure OddRelations (x y : I → R) : Prop where
  square_x : ∀ i, x i * x i = 0
  square_y : ∀ i, y i * y i = 0
  anti_x : ∀ i j, x i * x j = -(x j * x i)
  anti_y : ∀ i j, y i * y j = -(y j * y i)
  anti_cross : ∀ i j, y i * x j = -(x j * y i)

theorem sign_central (a : R) (n : ℕ) : a * (-1 : R) ^ n = (-1 : R) ^ n * a := by
  exact ((Commute.neg_one_right a).pow_right n).eq

theorem cross_middle (a b c d : R) (hbc : b * c = -(c * b)) :
    (a * b) * (c * d) = -((a * c) * (b * d)) := by
  simpa only [mul_assoc, mul_neg, neg_mul] using congrArg (fun z => a * z * d) hbc

theorem pair_square_zero (x y : I → R) (h : OddRelations x y) (i : I) :
    (x i * y i) * (x i * y i) = 0 := by
  rw [cross_middle (x i) (y i) (x i) (y i) (h.anti_cross i i),
    h.square_x i, zero_mul, neg_zero]

theorem pairs_commute (x y : I → R) (h : OddRelations x y) (i j : I) :
    (x i * y i) * (x j * y j) = (x j * y j) * (x i * y i) := by
  rw [cross_middle (x i) (y i) (x j) (y j) (h.anti_cross i j),
    cross_middle (x j) (y j) (x i) (y i) (h.anti_cross j i),
    h.anti_x i j, h.anti_y i j, neg_mul_neg]

theorem triangular_step (n : ℕ) : (n + 1) * n / 2 = n * (n - 1) / 2 + n := by
  simpa only [Nat.add_sub_cancel] using Nat.triangle_succ n

theorem cross_list (x y : I → R) (h : OddRelations x y) (i : I) (L : List I) :
    y i * (L.map x).prod = (-1 : R) ^ L.length * (L.map x).prod * y i := by
  induction L with
  | nil => simp
  | cons j L ih =>
    rw [List.map_cons, List.prod_cons, List.length_cons, ← mul_assoc,
      h.anti_cross i j, neg_mul, mul_assoc, ih]
    simp only [← mul_assoc, sign_central (x j) L.length, pow_succ,
      mul_neg_one, neg_mul]

theorem orientation_factorization (x y : I → R) (h : OddRelations x y) (L : List I) :
    (L.map (fun i => x i * y i)).prod =
      (-1 : R) ^ (L.length * (L.length - 1) / 2) * (L.map x).prod * (L.map y).prod := by
  induction L with
  | nil => simp
  | cons i L ih =>
    simpa only [List.map_cons, List.prod_cons, List.length_cons, ih,
      Nat.add_sub_cancel, triangular_step, pow_add, ← mul_assoc,
      sign_central (x i * y i) (L.length * (L.length - 1) / 2),
      sign_central (((-1 : R) ^ (L.length * (L.length - 1) / 2)) * x i) L.length,
      sign_central ((-1 : R) ^ (L.length * (L.length - 1) / 2)) L.length]
      using congrArg
        (fun z => (-1 : R) ^ (L.length * (L.length - 1) / 2) * x i * z * (L.map y).prod)
        (cross_list x y h i L)

end DoubleOrientation

#print axioms DoubleOrientation.sign_central
#print axioms DoubleOrientation.cross_middle
#print axioms DoubleOrientation.pair_square_zero
#print axioms DoubleOrientation.pairs_commute
#print axioms DoubleOrientation.triangular_step
#print axioms DoubleOrientation.cross_list
#print axioms DoubleOrientation.orientation_factorization
