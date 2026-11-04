import ActualClosedSubsetTransfer
import Mathlib.Data.Finsupp.Order
import Mathlib.Algebra.BigOperators.Ring.Finset

namespace AtomicSecondPrefix

open scoped BigOperators
open MvPolynomial
open ActualClosedSubsetTransfer

noncomputable section

variable {R : Type} [CommRing R] {n : Nat}

theorem B1_distribution (H : Finset (Fin n)) (b c : Fin n → R) :
    (∑ j ∈ H, b j) * (∑ k ∈ H, c k) =
      ∑ j ∈ H, ∑ k ∈ H, b j * c k := by
  exact Finset.sum_mul_sum H H b c

theorem erase_diagonal (H : Finset (Fin n)) (b c : Fin n → R)
    (j : Fin n) (hj : j ∈ H) :
    (∑ k ∈ H.erase j, b j * c k) =
      (∑ k ∈ H, b j * c k) - b j * c j := by
  exact (eq_sub_iff_add_eq).2 (Finset.sum_erase_add H (fun k => b j * c k) hj)

theorem B2_remove_diagonal (H : Finset (Fin n)) (b c : Fin n → R) :
    (∑ j ∈ H, ∑ k ∈ H.erase j, b j * c k) =
      (∑ j ∈ H, b j) * (∑ k ∈ H, c k) - ∑ j ∈ H, b j * c j := by
  classical
  calc
    _ = ∑ j ∈ H, ((∑ k ∈ H, b j * c k) - b j * c j) :=
      Finset.sum_congr rfl (fun j hj => erase_diagonal H b c j hj)
    _ = (∑ j ∈ H, ∑ k ∈ H, b j * c k) - ∑ j ∈ H, b j * c j :=
      Finset.sum_sub_distrib (fun j => ∑ k ∈ H, b j * c k) (fun j => b j * c j)
    _ = _ := by rw [← B1_distribution H b c]

def twoRows (b c : Fin n → R) : Nat → Fin n → R :=
  fun k j => if k = 0 then b j else c j

def actualTable (b c : Fin n → R) (U : Finset (Fin n)) : R :=
  state (twoRows b c) 2 U

def available (J : Finset (Fin n)) : Finset (Fin n) := Finset.univ \ J

def actualResponse (b c : Fin n → R) (J : Finset (Fin n)) : R :=
  ∑ U ∈ (available J).powerset,
    (-1 : R) ^ (U.card + J.card) * actualTable b c U

theorem seed_is_empty (b c : Fin n → R) (U : Finset (Fin n)) :
    state (twoRows b c) 0 U = if U = ∅ then 1 else 0 := by
  rfl

theorem insertion_is_erase (b c : Fin n → R) (k : Nat)
    (U : Finset (Fin n)) :
    state (twoRows b c) (k + 1) U =
      ∑ j ∈ U, twoRows b c k j * state (twoRows b c) k (U.erase j) := by
  rfl

theorem pair_exponent_iff (j k : Fin n) (U : Finset (Fin n)) :
    (Finsupp.single j 1 + Finsupp.single k 1 : Fin n →₀ Nat) = subsetExponent U ↔
      j ≠ k ∧ U = {j, k} := by
  classical
  constructor
  · intro h
    have hne : j ≠ k := by
      intro hjk
      subst k
      have hj := congrArg (fun e : Fin n →₀ Nat => e j) h
      by_cases hju : j ∈ U <;>
        simp [Finsupp.add_apply, Finsupp.single_apply, subsetExponent_apply, hju] at hj
    have hs := congrArg (fun e : Fin n →₀ Nat => e.support) h
    refine ⟨hne, ?_⟩
    simpa [Finsupp.support_add_eq_union, subsetExponent_support] using hs.symm
  · rintro ⟨hne, rfl⟩
    ext l
    by_cases hlj : l = j
    · subst l
      simp [subsetExponent_apply, Finsupp.single_apply, hne, Ne.symm hne]
    · by_cases hlk : l = k
      · subst l
        simp [subsetExponent_apply, Finsupp.single_apply, hne, Ne.symm hne]
      · simp [subsetExponent_apply, Finsupp.single_apply, hlj, hlk]

theorem table_two_pair_expansion (b c : Fin n → R) (U : Finset (Fin n)) :
    actualTable b c U =
      ∑ j : Fin n, ∑ k : Fin n,
        if j ≠ k ∧ U = {j,k} then b j * c k else 0 := by
  classical
  have h0 : twoRows b c 0 = b := by
    funext j
    simp [twoRows]
  have h1 : twoRows b c 1 = c := by
    funext j
    simp [twoRows]
  have hp : rowProduct (twoRows b c) 2 = linearForm b * linearForm c := by
    simp [rowProduct, h0, h1, mul_comm]
  rw [actualTable, coefficient_invariant, hp]
  simp only [linearForm, Finset.sum_mul, Finset.mul_sum, coeff_sum,
    C_mul_X_eq_monomial, monomial_mul_monomial, coeff_monomial, pair_exponent_iff]
  rw [Finset.sum_comm]

theorem table_two_zero_of_card_ne (b c : Fin n → R) (U : Finset (Fin n))
    (hcard : U.card ≠ 2) : actualTable b c U = 0 := by
  classical
  rw [table_two_pair_expansion]
  apply Finset.sum_eq_zero
  intro j _
  apply Finset.sum_eq_zero
  intro k _
  have hpair : ¬ (j ≠ k ∧ U = {j,k}) := by
    rintro ⟨hne, rfl⟩
    exact hcard (Finset.card_pair hne)
  simp [hpair]

theorem signed_response_eq_mass (b c : Fin n → R) (J : Finset (Fin n)) :
    actualResponse b c J =
      (-1 : R) ^ J.card * ∑ U ∈ (available J).powerset, actualTable b c U := by
  classical
  unfold actualResponse
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro U _
  by_cases hcard : U.card = 2
  · simp [hcard, pow_add, pow_two]
  · rw [table_two_zero_of_card_ne b c U hcard, mul_zero, mul_zero]

theorem powerset_pair_indicator (H : Finset (Fin n)) (b c : Fin n → R)
    (j k : Fin n) :
    (∑ U ∈ H.powerset, if j ≠ k ∧ U = {j,k} then b j * c k else 0) =
      if j ∈ H then (if k ∈ H.erase j then b j * c k else 0) else 0 := by
  classical
  by_cases hjk : j = k
  · subst k
    simp [Finset.mem_erase]
  · by_cases hj : j ∈ H <;> by_cases hk : k ∈ H <;>
      simp [hjk, Ne.symm hjk, hj, hk, Finset.sum_ite_eq', Finset.mem_powerset,
        Finset.insert_subset_iff, Finset.singleton_subset_iff, Finset.mem_erase]

theorem table_two_mass (H : Finset (Fin n)) (b c : Fin n → R) :
    (∑ U ∈ H.powerset, actualTable b c U) =
      ∑ j ∈ H, ∑ k ∈ H.erase j, b j * c k := by
  classical
  simp_rw [table_two_pair_expansion]
  calc
    _ = ∑ j : Fin n, ∑ k : Fin n,
          ∑ U ∈ H.powerset, if j ≠ k ∧ U = {j,k} then b j * c k else 0 := by
      rw [Finset.sum_comm]
      apply Finset.sum_congr rfl
      intro j _
      rw [Finset.sum_comm]
    _ = ∑ j : Fin n, if j ∈ H then (∑ k ∈ H.erase j, b j * c k) else 0 := by
      apply Finset.sum_congr rfl
      intro j _
      simp_rw [powerset_pair_indicator]
      by_cases hj : j ∈ H <;>
        simp only [hj, if_true, if_false, Finset.sum_ite_mem_eq, Finset.sum_const_zero]
    _ = _ := by simp only [Finset.sum_ite_mem_eq]

theorem B3_actual_response (b c : Fin n → R) (J : Finset (Fin n)) :
    actualResponse b c J = (-1 : R) ^ J.card *
      ((∑ j ∈ available J, b j) * (∑ j ∈ available J, c j) -
        ∑ j ∈ available J, b j * c j) := by
  rw [signed_response_eq_mass, table_two_mass, B2_remove_diagonal]

structure InitializedData (n : Nat) (R : Type) where
  b : Fin n → R
  c : Fin n → R
  diagonal : Fin n → R
  totalB : R
  totalC : R
  totalDiagonal : R

def initData (b c : Fin n → R) : InitializedData n R :=
  ⟨b, c, (fun j => b j * c j), ∑ j : Fin n, b j,
    ∑ j : Fin n, c j, ∑ j : Fin n, b j * c j⟩

def query (D : InitializedData n R) (J : Finset (Fin n)) : R :=
  (-1 : R) ^ J.card *
    ((D.totalB - ∑ j ∈ J, D.b j) * (D.totalC - ∑ j ∈ J, D.c j) -
      (D.totalDiagonal - ∑ j ∈ J, D.diagonal j))

theorem complement_sum (f : Fin n → R) (J : Finset (Fin n)) :
    (∑ j ∈ Finset.univ \ J, f j) = (∑ j : Fin n, f j) - ∑ j ∈ J, f j := by
  classical
  exact (eq_sub_iff_add_eq).2 (Finset.sum_sdiff (Finset.subset_univ J))

theorem initialized_diagonal (b c : Fin n → R) (j : Fin n) :
    (initData b c).diagonal j = b j * c j := by
  rfl

theorem initialized_totals (b c : Fin n → R) :
    (initData b c).totalB = (∑ j : Fin n, b j) ∧
    (initData b c).totalC = (∑ j : Fin n, c j) ∧
    (initData b c).totalDiagonal = (∑ j : Fin n, b j * c j) := by
  exact ⟨rfl,rfl,rfl⟩

theorem B4_initialized_query (b c : Fin n → R) (J : Finset (Fin n)) :
    query (initData b c) J = actualResponse b c J := by
  rw [B3_actual_response]
  simp only [query, initData, available, complement_sum]

#print axioms AtomicSecondPrefix.B1_distribution
#print axioms AtomicSecondPrefix.erase_diagonal
#print axioms AtomicSecondPrefix.B2_remove_diagonal
#print axioms AtomicSecondPrefix.seed_is_empty
#print axioms AtomicSecondPrefix.insertion_is_erase
#print axioms AtomicSecondPrefix.pair_exponent_iff
#print axioms AtomicSecondPrefix.table_two_pair_expansion
#print axioms AtomicSecondPrefix.table_two_zero_of_card_ne
#print axioms AtomicSecondPrefix.signed_response_eq_mass
#print axioms AtomicSecondPrefix.powerset_pair_indicator
#print axioms AtomicSecondPrefix.table_two_mass
#print axioms AtomicSecondPrefix.B3_actual_response
#print axioms AtomicSecondPrefix.complement_sum
#print axioms AtomicSecondPrefix.initialized_diagonal
#print axioms AtomicSecondPrefix.initialized_totals
#print axioms AtomicSecondPrefix.B4_initialized_query

end
end AtomicSecondPrefix
