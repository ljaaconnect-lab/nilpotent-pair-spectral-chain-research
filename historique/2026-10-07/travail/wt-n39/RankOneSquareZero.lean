import Mathlib.Data.Matrix.Mul
import Mathlib.Tactic.LinearCombination

namespace SquareZeroRankOne

set_option maxHeartbeats 20000

variable {R ι : Type*} [CommRing R] [Fintype ι] [DecidableEq ι]

-- Active target first: this is a product equality, with no inverse gate.
theorem matrix_right_product
    (A G U : Matrix ι ι R) (x : R) (hx : x * x = 0) (hAG : A * G = 1) :
    (A - x • U) * (G + x • (G * U * G)) = 1 := by
  simp only [sub_mul, mul_add, Matrix.smul_mul, Matrix.mul_smul, smul_smul,
    ← mul_assoc, hAG, hx, zero_smul, one_mul, sub_zero, sub_add_cancel]

theorem matrix_left_product
    (A G U : Matrix ι ι R) (x : R) (hx : x * x = 0) (hGA : G * A = 1) :
    (G + x • (G * U * G)) * (A - x • U) = 1 := by
  simp only [add_mul, mul_sub, Matrix.smul_mul, Matrix.mul_smul, smul_smul,
    mul_assoc, hGA, hx, zero_smul, mul_one, add_zero, add_sub_cancel_right]

theorem scalar_product (x c : R) (hx : x * x = 0) :
    (1 - x * c) * (1 + x * c) = 1 := by
  linear_combination -c * c * hx

theorem rank_one_two_sided
    (A G : Matrix ι ι R) (u v : ι → R) (x : R) (hx : x * x = 0)
    (hAG : A * G = 1) (hGA : G * A = 1) :
    (A - x • Matrix.vecMulVec u v) *
        (G + x • (G * Matrix.vecMulVec u v * G)) = 1 ∧
    (G + x • (G * Matrix.vecMulVec u v * G)) *
        (A - x • Matrix.vecMulVec u v) = 1 := by
  exact ⟨matrix_right_product A G (Matrix.vecMulVec u v) x hx hAG,
    matrix_left_product A G (Matrix.vecMulVec u v) x hx hGA⟩

theorem propagate_left_factor
    (B G U : Matrix ι ι R) (x : R) :
    B * (G + x • (G * U * G)) = B * G + x • ((B * G) * U * G) := by
  simp only [mul_add, Matrix.mul_smul, mul_assoc]

-- Additional bridge lemma; it does not change the frozen score denominator.
theorem propagate_rank_one
    (B G : Matrix ι ι R) (u v : ι → R) (x : R) :
    B * (G + x • (G * Matrix.vecMulVec u v * G)) =
        B * G + x • Matrix.vecMulVec (Matrix.mulVec (B * G) u) (Matrix.vecMul v G) := by
  rw [propagate_left_factor, Matrix.mul_vecMulVec, Matrix.vecMulVec_mul]

end SquareZeroRankOne

#print axioms SquareZeroRankOne.matrix_right_product
#print axioms SquareZeroRankOne.matrix_left_product
#print axioms SquareZeroRankOne.scalar_product
#print axioms SquareZeroRankOne.rank_one_two_sided
#print axioms SquareZeroRankOne.propagate_left_factor
#print axioms SquareZeroRankOne.propagate_rank_one
