import Mathlib.Algebra.Polynomial.Degree.Domain

set_option Elab.async false

/-!
This file formalizes only a degree transfer from a supplied polynomial identity,
and the subsequent numerical obstruction to interpolation below degree L.
It does not formalize the existence of an invariant, Kempf's theorem,
semistability, the determinant rank-drop estimate, or any scalar-circuit bound.
-/

namespace DeformationDegreeBarrier

open Polynomial

theorem degree_transfer {K : Type*} [Field K]
    {A B C : K[X]} {n D h : ℕ}
    (hB : B ≠ 0) (hC : C ≠ 0) (hD : 0 < D)
    (hid : A ^ n = C * B ^ D) (hAdeg : A.natDegree ≤ D * h) :
    B.natDegree ≤ n * h := by
  have hdeg := congrArg Polynomial.natDegree hid
  simp only [Polynomial.natDegree_pow,
    Polynomial.natDegree_mul hC (pow_ne_zero D hB)] at hdeg
  exact Nat.le_of_mul_le_mul_left
    (calc
      D * B.natDegree ≤ C.natDegree + D * B.natDegree := Nat.le_add_left _ _
      _ = n * A.natDegree := hdeg.symm
      _ ≤ n * (D * h) := Nat.mul_le_mul_left n hAdeg
      _ = D * (n * h) := Nat.mul_left_comm n D h) hD

/-- Pure arithmetic: a nonzero rank defect forces at least L degrees. -/
theorem no_degree_below_sample_count {n L r h d : ℕ}
    (hn : 0 < n) (hr : r < n)
    (hlower : n * L * (n - r) ≤ d) (hupper : d ≤ n * h) :
    ¬ h < L := by
  exact not_lt_of_ge (Nat.le_of_mul_le_mul_left
    (calc
      n * L = n * L * 1 := (Nat.mul_one _).symm
      _ ≤ n * L * (n - r) :=
        Nat.mul_le_mul_left _ (Nat.succ_le_of_lt (Nat.sub_pos_of_lt hr))
      _ ≤ d := hlower
      _ ≤ n * h := hupper) hn)

/-- Combines the supplied identity with a supplied determinant-degree bound. -/
theorem identity_obstructs_short_interpolation {K : Type*} [Field K]
    {A B C : K[X]} {n D h L r : ℕ}
    (hB : B ≠ 0) (hC : C ≠ 0) (hD : 0 < D) (hn : 0 < n)
    (hr : r < n) (hid : A ^ n = C * B ^ D)
    (hAdeg : A.natDegree ≤ D * h)
    (hlower : n * L * (n - r) ≤ B.natDegree) :
    ¬ h < L := by
  exact no_degree_below_sample_count hn hr hlower
    (degree_transfer hB hC hD hid hAdeg)

#print axioms degree_transfer
#print axioms no_degree_below_sample_count
#print axioms identity_obstructs_short_interpolation

end DeformationDegreeBarrier
