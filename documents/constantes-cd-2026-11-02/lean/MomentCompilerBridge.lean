import Mathlib.Data.Matrix.Mul
import Mathlib.Data.Nat.Choose.Basic
import Mathlib.Algebra.Group.Idempotent
import Mathlib.Tactic.Linarith

set_option Elab.async false

/-!
# Moment-state bridge to the generic scalar compiler

The coordinates `mu` are supplied scalar inputs here. These theorems prove the
dimension bound and a matrix-power representation of their weighted reading.
They do not assume or establish any polynomial circuit for constructing `mu`
from the original coefficients.
-/

namespace MomentCompilerBridge

def momentDimension (n : ℕ) : ℕ := 1 + n.choose 2

theorem momentDimension_le_square (n : ℕ) (hn : 1 ≤ n) :
    momentDimension n ≤ n ^ 2 := by
  rw [momentDimension, Nat.choose_two_right]
  nlinarith [Nat.div_le_self (n * (n - 1)) 2, Nat.sub_add_cancel hn]

/-- Arithmetic bound for the already counted preparation of B only. -/
theorem preparationB_le_fourth (n : ℕ) (hn : 2 ≤ n) :
    4 * n ^ 2 - 1 ≤ n ^ 4 := by
  nlinarith [Nat.mul_le_mul_right (n * n) (Nat.mul_self_le_mul_self hn),
    Nat.sub_le (4 * n ^ 2) 1]

/-- Arithmetic bound for the counted generator circuit only, not its moment reader. -/
theorem generator_le_fifth (n : ℕ) (hn : 2 ≤ n) :
    7 * n ^ 2 - n - 1 ≤ n ^ 5 := by
  nlinarith [Nat.mul_le_mul_right (n * n) (Nat.mul_le_mul hn (Nat.mul_self_le_mul_self hn)),
    Nat.sub_le (7 * n ^ 2) n, Nat.sub_le (7 * n ^ 2 - n) 1]

variable {R : Type*} [CommRing R] {h : ℕ}

def momentMatrix (p : Fin (h + 1) → R) : Matrix (Fin (h + 1)) (Fin (h + 1)) R :=
  fun i j => if i = 0 then p j else 0

def firstRow : Fin (h + 1) → R := Pi.single 0 1

theorem momentMatrix_idempotent (p : Fin (h + 1) → R) (hp : p 0 = 1) :
    IsIdempotentElem (momentMatrix p) := by
  apply Matrix.ext
  intro i j
  simp [Matrix.mul_apply, momentMatrix, mul_ite, ite_mul, hp]

theorem momentMatrix_pow (p : Fin (h + 1) → R) (hp : p 0 = 1)
    (K : ℕ) (hK : 1 ≤ K) : momentMatrix p ^ K = momentMatrix p := by
  exact (momentMatrix_idempotent p hp).pow_eq (Nat.ne_zero_of_lt hK)

theorem momentMatrix_read (p mu : Fin (h + 1) → R) (hp : p 0 = 1)
    (K : ℕ) (hK : 1 ≤ K) :
    firstRow ⬝ᵥ ((momentMatrix p ^ K).mulVec mu) = ∑ j, p j * mu j := by
  simp [momentMatrix_pow p hp K hK, firstRow, momentMatrix, Matrix.mulVec, dotProduct]

end MomentCompilerBridge

#print axioms MomentCompilerBridge.momentDimension_le_square
#print axioms MomentCompilerBridge.preparationB_le_fourth
#print axioms MomentCompilerBridge.generator_le_fifth
#print axioms MomentCompilerBridge.momentMatrix_idempotent
#print axioms MomentCompilerBridge.momentMatrix_pow
#print axioms MomentCompilerBridge.momentMatrix_read
