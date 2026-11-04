import Mathlib.LinearAlgebra.Matrix.SchurComplement
import Mathlib.Algebra.BigOperators.Group.Finset.Powerset
import Mathlib.Tactic.Ring

/-! Elementary first-prefix identities. These are algebraic identities, not a
polynomial-size contraction algorithm. The normalization h*u=b is local. -/

namespace AtomicFirstPrefix

open scoped BigOperators Matrix

variable {n : Nat} {R : Type*} [CommRing R]

def total (b : Fin n → R) : R := ∑ j, b j

def phase (J : Finset (Fin n)) : R := (-1 : R) ^ J.card

/-- Actual ambient matrix -I + u*1ᵀ, with the rank-one product over Unit. -/
def prefixMatrix (u : Fin n → R) : Matrix (Fin n) (Fin n) R :=
  -(1 : Matrix (Fin n) (Fin n) R) +
    Matrix.replicateCol Unit u * Matrix.replicateRow Unit (fun _ => 1)

/-- An actual principal submatrix, indexed by the elements of J. -/
def principalMinor (u : Fin n → R) (J : Finset (Fin n)) : Matrix J J R :=
  (prefixMatrix u).submatrix Subtype.val Subtype.val

/-- Coefficient array of q_j*q_J in the commuting square-zero basis. -/
def insertionCoefficient (j : Fin n) (J K : Finset (Fin n)) : R :=
  if j ∉ J ∧ K = insert j J then 1 else 0

/-- The actual signed sum of the post-insertion coefficient array. -/
def singleResponse (j : Fin n) (J : Finset (Fin n)) : R :=
  -∑ K : Finset (Fin n), phase K * insertionCoefficient j J K

def weightedResponse (b : Fin n → R) (J : Finset (Fin n)) : R :=
  ∑ j, b j * singleResponse j J

def familyResponse (b : Fin n → R) (f : Finset (Fin n) → R) : R :=
  ∑ J : Finset (Fin n), f J * weightedResponse b J

/-- A4: no nonempty hypothesis; the empty determinant is included. -/
theorem minor_determinant (u : Fin n → R) (J : Finset (Fin n)) :
    (principalMinor u J).det = phase J * (1 - ∑ j ∈ J, u j) := by
  classical
  have heq : principalMinor u J =
      -(1 + Matrix.replicateCol Unit (fun i : J => -u i) *
        Matrix.replicateRow Unit (fun _ : J => (1 : R))) := by
    ext i j
    by_cases hij : i = j
    · subst j
      simp [principalMinor, prefixMatrix, Matrix.submatrix, Matrix.mul_apply]
    · have hval : i.val ≠ j.val := fun h => hij (Subtype.ext h)
      simp [principalMinor, prefixMatrix, Matrix.submatrix, Matrix.mul_apply,
        Matrix.one_apply, hij, hval]
  rw [heq, Matrix.det_neg, Matrix.det_one_add_replicateCol_mul_replicateRow]
  simp [phase, dotProduct, Finset.sum_coe_sort, sub_eq_add_neg]

#print axioms minor_determinant

end AtomicFirstPrefix
