import EncodingBridge
import Mathlib.Algebra.MvPolynomial.Basic
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Data.Fintype.EquivFin
import Mathlib.Data.Fintype.Powerset

namespace ActualClosedSubsetTransfer

open scoped BigOperators
open MvPolynomial

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

#print axioms ActualClosedSubsetTransfer.occupation_eq_iff_bijective
#print axioms ActualClosedSubsetTransfer.expanded_linear_product
#print axioms ActualClosedSubsetTransfer.sum_bijective_functions
#print axioms ActualClosedSubsetTransfer.full_coefficient_permutation

end
end ActualClosedSubsetTransfer
