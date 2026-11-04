import EncodingBridge
import Mathlib.Algebra.MvPolynomial.Basic
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Data.Fintype.EquivFin
import Mathlib.Data.Fintype.Powerset

namespace ActualClosedSubsetTransfer

open scoped BigOperators
open MvPolynomial
open CollisionEncodingBridge

noncomputable section

variable {R : Type} [CommRing R] {n : Nat}

def subsetExponent (U : Finset (Fin n)) : Fin n →₀ Nat :=
  ∑ j ∈ U, Finsupp.single j 1

def occupation (f : Fin n → Fin n) : Fin n →₀ Nat :=
  ∑ i : Fin n, Finsupp.single (f i) 1

def linearForm (c : Fin n → R) : MvPolynomial (Fin n) R :=
  ∑ j : Fin n, C (c j) * X j

def rowProduct (b : Nat → Fin n → R) : Nat → MvPolynomial (Fin n) R
  | 0 => 1
  | k + 1 => linearForm (b k) * rowProduct b k

def state (b : Nat → Fin n → R) : Nat → Finset (Fin n) → R
  | 0, U => if U = ∅ then 1 else 0
  | k + 1, U => ∑ j ∈ U, b k j * state b k (U.erase j)

theorem occupation_eq_iff_bijective (f : Fin n → Fin n) :
    occupation f = subsetExponent Finset.univ ↔ Function.Bijective f := by
  classical
  constructor
  · intro h
    apply (Fintype.bijective_iff_surjective_and_card f).2
    refine ⟨?_, rfl⟩
    intro j
    by_contra! hno
    have hj := congrArg (fun m : Fin n →₀ Nat => m j) h
    simp [occupation, subsetExponent, Finsupp.finsetSum_apply,
      Finsupp.single_apply, hno] at hj
  · intro hf
    exact hf.sum_comp (fun j => Finsupp.single j 1)

theorem expanded_linear_product (b : Nat → Fin n → R) :
    (∏ i : Fin n, linearForm (b i.val)) =
      ∑ f : Fin n → Fin n,
        monomial (occupation f) (∏ i : Fin n, b i.val (f i)) := by
  classical
  simp only [linearForm, Fintype.prod_sum]
  apply Finset.sum_congr rfl
  intro f _
  simpa only [C_mul_X_eq_monomial, occupation] using
    (monomial_sum_prod (Finset.univ : Finset (Fin n))
      (fun i => Finsupp.single (f i) 1) (fun i => b i.val (f i))).symm

theorem sum_bijective_functions (w : (Fin n → Fin n) → R) :
    (∑ f : Fin n → Fin n, if Function.Bijective f then w f else 0) =
      ∑ σ : Equiv.Perm (Fin n), w σ := by
  classical
  rw [← Finset.sum_filter]
  refine Finset.sum_bij (fun f hf => Equiv.ofBijective f (Finset.mem_filter.mp hf).2)
    (fun _ _ => Finset.mem_univ _) ?_ ?_ ?_
  · intro f hf g hg h
    exact congrArg (fun e : Equiv.Perm (Fin n) => (e : Fin n → Fin n)) h
  · intro σ _
    refine ⟨(σ : Fin n → Fin n), ?_, ?_⟩
    · exact Finset.mem_filter.mpr ⟨Finset.mem_univ _, σ.bijective⟩
    · exact Equiv.ext (fun _ => rfl)
  · intro f hf
    rfl

theorem full_coefficient_permutation (b : Nat → Fin n → R) :
    (∏ i : Fin n, linearForm (b i.val)).coeff (subsetExponent Finset.univ) =
      ∑ σ : Equiv.Perm (Fin n), ∏ i : Fin n, b i.val (σ i) := by
  classical
  rw [expanded_linear_product, coeff_sum]
  simp only [coeff_monomial, occupation_eq_iff_bijective]
  exact sum_bijective_functions (fun f => ∏ i : Fin n, b i.val (f i))

theorem subsetExponent_apply (U : Finset (Fin n)) (j : Fin n) :
    subsetExponent U j = if j ∈ U then 1 else 0 := by
  classical
  simp [subsetExponent, Finsupp.finsetSum_apply, Finsupp.single_apply]

theorem subsetExponent_support (U : Finset (Fin n)) :
    (subsetExponent U).support = U := by
  classical
  ext j
  by_cases hj : j ∈ U <;>
    simp [Finsupp.mem_support_iff, subsetExponent_apply, hj]

theorem subsetExponent_zero_iff (U : Finset (Fin n)) :
    subsetExponent U = 0 ↔ U = ∅ := by
  classical
  constructor
  · intro h
    have hs := congrArg (fun e : Fin n →₀ Nat => e.support) h
    simpa only [subsetExponent_support, Finsupp.support_zero] using hs
  · intro h
    simp [h, subsetExponent]

theorem subsetExponent_erase (U : Finset (Fin n)) (j : Fin n) :
    subsetExponent U - Finsupp.single j 1 = subsetExponent (U.erase j) := by
  classical
  ext l
  by_cases hl : l = j
  · subst l
    by_cases hj : j ∈ U <;>
      simp [subsetExponent_apply, Finsupp.tsub_apply, hj]
  · simp [subsetExponent_apply, Finsupp.tsub_apply, Finset.mem_erase, hl]

theorem coefficient_step (c : Fin n → R) (p : MvPolynomial (Fin n) R)
    (U : Finset (Fin n)) :
    (linearForm c * p).coeff (subsetExponent U) =
      ∑ j ∈ U, c j * p.coeff (subsetExponent (U.erase j)) := by
  classical
  simp only [linearForm, Finset.sum_mul, coeff_sum, mul_assoc, coeff_C_mul,
    coeff_X_mul', subsetExponent_support, subsetExponent_erase, mul_ite, mul_zero]
  rw [← Finset.sum_filter]
  congr 1
  ext j
  simp

theorem coefficient_invariant (b : Nat → Fin n → R) (k : Nat)
    (U : Finset (Fin n)) :
    state b k U = (rowProduct b k).coeff (subsetExponent U) := by
  classical
  induction k generalizing U with
  | zero => simp [state, rowProduct, coeff_one, eq_comm, subsetExponent_zero_iff]
  | succ k ih => simp only [state, rowProduct, coefficient_step, ih]

theorem initial_state (b : Nat → Fin n → R) (U : Finset (Fin n)) :
    state b 0 U = if U = ∅ then 1 else 0 := by
  rfl

theorem step_state (b : Nat → Fin n → R) (k : Nat) (U : Finset (Fin n)) :
    state b (k + 1) U = ∑ j ∈ U, b k j * state b k (U.erase j) := by
  rfl

theorem rowProduct_eq (b : Nat → Fin n → R) (k : Nat) :
    rowProduct b k = ∏ i : Fin k, linearForm (b i.val) := by
  induction k with
  | zero => simp [rowProduct]
  | succ k ih =>
    rw [rowProduct, ih, Fin.prod_univ_castSucc]
    exact mul_comm _ _

theorem terminal_permutation (b : Nat → Fin n → R) :
    state b n Finset.univ =
      ∑ σ : Equiv.Perm (Fin n), ∏ i : Fin n, b i.val (σ i) := by
  rw [coefficient_invariant, rowProduct_eq]
  exact full_coefficient_permutation b

def matrixRows (B : Matrix (Fin n) (Fin n) R) : Nat → Fin n → R :=
  fun k j => if h : k < n then B ⟨k, h⟩ j else 0

theorem terminal_matrix (B : Matrix (Fin n) (Fin n) R) :
    state (matrixRows B) n Finset.univ =
      ∑ σ : Equiv.Perm (Fin n), ∏ i : Fin n, B i (σ i) := by
  classical
  rw [terminal_permutation]
  apply Finset.sum_congr rfl
  intro σ _
  apply Finset.prod_congr rfl
  intro i _
  simp [matrixRows, i.isLt]

theorem marked_central (n : Nat) (hn : 2 ≤ n)
    (A : Matrix (Fin n) (Fin n) Rat) :
    state (matrixRows (markedWeights A)) n Finset.univ =
      (markedHhat A).coeff (centralDegree n) := by
  rw [terminal_matrix]
  simpa only [markedHhat, CollisionDeterminantBridge.weight] using
    (hhat_central_coefficient n hn (markedWeights A)).symm

theorem marked_target (A : Matrix (Fin n) (Fin n) Rat) :
    state (matrixRows (markedWeights A)) n Finset.univ = markedPermanent A := by
  rw [terminal_matrix]
  change (∑ σ : Equiv.Perm (Fin n),
    CollisionDeterminantBridge.weight (markedWeights A) σ) = markedPermanent A
  simp only [markedPermanent, marked_weight_eq]

theorem state_dimension (n : Nat) :
    Fintype.card (Finset (Fin n)) = 2 ^ n := by
  simp only [Fintype.card_finset, Fintype.card_fin]

#print axioms ActualClosedSubsetTransfer.initial_state
#print axioms ActualClosedSubsetTransfer.step_state
#print axioms ActualClosedSubsetTransfer.rowProduct_eq
#print axioms ActualClosedSubsetTransfer.terminal_permutation
#print axioms ActualClosedSubsetTransfer.terminal_matrix
#print axioms ActualClosedSubsetTransfer.marked_central
#print axioms ActualClosedSubsetTransfer.marked_target
#print axioms ActualClosedSubsetTransfer.state_dimension
#print axioms ActualClosedSubsetTransfer.subsetExponent_apply
#print axioms ActualClosedSubsetTransfer.subsetExponent_support
#print axioms ActualClosedSubsetTransfer.subsetExponent_zero_iff
#print axioms ActualClosedSubsetTransfer.subsetExponent_erase
#print axioms ActualClosedSubsetTransfer.coefficient_step
#print axioms ActualClosedSubsetTransfer.coefficient_invariant
#print axioms ActualClosedSubsetTransfer.occupation_eq_iff_bijective
#print axioms ActualClosedSubsetTransfer.expanded_linear_product
#print axioms ActualClosedSubsetTransfer.sum_bijective_functions
#print axioms ActualClosedSubsetTransfer.full_coefficient_permutation

end
end ActualClosedSubsetTransfer
