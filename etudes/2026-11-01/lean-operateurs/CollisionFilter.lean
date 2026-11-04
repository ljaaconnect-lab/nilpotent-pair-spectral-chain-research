import Mathlib.LinearAlgebra.Matrix.Determinant.Basic

set_option Elab.async false

/-! An all-order certificate for the collision filter, independent of
the number of available columns. This is not a scalar contraction algorithm. -/

namespace OrientedOperators

def equalityMatrix {ι : Type*} [DecidableEq ι] {r : ℕ}
    (w : Fin r → ι) : Matrix (Fin r) (Fin r) ℤ :=
  fun i j => if w i = w j then 1 else 0

theorem equalityMatrix_det {ι : Type*} [DecidableEq ι] {r : ℕ}
    (w : Fin r → ι) :
    (equalityMatrix w).det = if Function.Injective w then 1 else 0 := by
  classical
  split_ifs with h
  · have hm : equalityMatrix w = 1 := by
      ext i j
      simp [equalityMatrix, Matrix.one_apply, h.eq_iff]
    simp [hm]
  · obtain ⟨i, j, hij, hne⟩ := Function.not_injective_iff.mp h
    apply Matrix.det_zero_of_row_eq hne
    funext k
    simp [equalityMatrix, hij]

#print axioms equalityMatrix_det

end OrientedOperators
