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
    Matrix.replicateCol Unit u * Matrix.replicateRow Unit (fun _ : Fin n => (1 : R))

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
      simp [principalMinor, prefixMatrix, Matrix.submatrix, Matrix.mul_apply, add_comm]
    · simp [principalMinor, prefixMatrix, Matrix.submatrix, Matrix.mul_apply,
        Matrix.one_apply, hij]
  rw [heq, Matrix.det_neg, Matrix.det_one_add_replicateCol_mul_replicateRow]
  simp [phase, dotProduct, Finset.sum_attach, sub_eq_add_neg]

#print axioms minor_determinant

/-- A1: partition the supplied vector into J and its complement. -/
theorem sum_complement (b : Fin n → R) (J : Finset (Fin n)) :
    (∑ j ∈ Jᶜ, b j) = total b - ∑ j ∈ J, b j := by
  exact eq_sub_iff_add_eq.mpr (Finset.sum_compl_add_sum J b)

#print axioms sum_complement

/-- A2: the coefficient-array insertion has precisely its signed basis response. -/
theorem single_response (j : Fin n) (J : Finset (Fin n)) :
    singleResponse (R := R) j J = if j ∉ J then phase J else 0 := by
  classical
  by_cases hj : j ∈ J
  · simp [singleResponse, insertionCoefficient, hj]
  · simp [singleResponse, insertionCoefficient, hj, mul_ite, phase,
      Finset.card_insert_of_notMem hj, pow_succ]

#print axioms single_response

/-- A3: sum the one-column responses with the actual weights b_j. -/
theorem weighted_response (b : Fin n → R) (J : Finset (Fin n)) :
    weightedResponse b J = phase J * (total b - ∑ j ∈ J, b j) := by
  classical
  unfold weightedResponse
  simp_rw [single_response, mul_ite, mul_zero]
  rw [← Finset.sum_filter]
  have hfilter : Finset.univ.filter (fun j : Fin n => j ∉ J) = Jᶜ := by
    ext j
    simp
  rw [hfilter, Finset.sum_mul, sum_complement, mul_comm]

#print axioms weighted_response

end AtomicFirstPrefix
