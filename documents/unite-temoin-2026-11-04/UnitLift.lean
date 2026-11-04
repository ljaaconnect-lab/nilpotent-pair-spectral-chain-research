import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Algebra.Module.LinearMap.Basic
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Data.ZMod.Basic

/-!
The unit insertion preserves a positive-degree coefficient, not the whole
oriented value. It changes augmentation to one, not to the desired coefficient.
The native quotient has an augmentation because all its defining relations
vanish at zero. That native presentation is justified in the accompanying text.
-/

namespace UnitLift

open scoped BigOperators

variable {P A R I : Type*} [CommRing P] [CommRing A] [CommRing R]

theorem unit_preserves_top (projection : A →+ R)
    (unit_zero : projection 1 = 0) (core : A) :
    projection (1 + core) = projection core :=
  (map_add projection 1 core).trans
    ((congrArg (fun value => value + projection core) unit_zero).trans
      (zero_add (projection core)))

theorem unit_augmentation (augmentation : P →+* R) (core : P)
    (core_zero : augmentation core = 0) :
    augmentation (1 + core) = 1 := by
  simp only [map_add, map_one, core_zero, add_zero]

#print axioms unit_preserves_top
#print axioms unit_augmentation

theorem equivalent_representatives_same_augmentation
    (quotient : P →+* A) (augmentation : A →+* R) (left right : P)
    (equivalent : quotient left = quotient right) :
    (augmentation.comp quotient) left = (augmentation.comp quotient) right :=
  congrArg augmentation equivalent

theorem equivalent_representative_still_zero
    (quotient : P →+* A) (augmentation : A →+* R) (candidate core : P)
    (equivalent : quotient candidate = quotient core)
    (core_zero : (augmentation.comp quotient) core = 0) :
    (augmentation.comp quotient) candidate = 0 :=
  (equivalent_representatives_same_augmentation quotient augmentation
    candidate core equivalent).trans core_zero

theorem unit_augmentation_not_answer (augmentation : P →+* R) (core : P)
    (core_zero : augmentation core = 0) (answer : R) (answer_ne_one : answer ≠ 1) :
    augmentation (1 + core) ≠ answer :=
  fun h => answer_ne_one (h.symm.trans (unit_augmentation augmentation core core_zero))

theorem unit_budget (cost n : ℕ) (bound : cost ≤ 29 * n ^ 3) :
    cost + 1 ≤ 29 * n ^ 3 + 1 :=
  Nat.add_le_add_right bound 1

#print axioms equivalent_representatives_same_augmentation
#print axioms equivalent_representative_still_zero
#print axioms unit_augmentation_not_answer
#print axioms unit_budget

theorem fused_unit_target [Fintype I] (weights : I → R)
    (kernel : (∑ f, weights f) = 1) (core : R) :
    (∑ f, weights f * (1 + core)) = 1 + core := by
  simpa only [Finset.sum_mul, one_mul] using
    congrArg (fun total : R => total * (1 + core)) kernel

#print axioms fused_unit_target

/-- The same native spectral linear map preserves the readout under unit insertion. -/
theorem spectral_unit_readout_preserved [Fintype I] [Module R A]
    (reader : A →ₗ[R] R) (unit_zero : reader 1 = 0)
    (weights phase : I → R) (core : A) :
    reader (∑ f, weights f • (phase f • (1 + core))) =
      reader (∑ f, weights f • (phase f • core)) := by
  simp only [map_sum, map_smul, map_add, unit_zero, zero_add]

#print axioms spectral_unit_readout_preserved

theorem spectral_unit_readout_formula [Fintype I] [Module R A]
    (reader : A →ₗ[R] R) (unit_zero : reader 1 = 0)
    (weights phase : I → R) (core : A) :
    reader (∑ f, weights f • (phase f • (1 + core))) =
      (∑ f, weights f * phase f) * reader core := by
  simp only [map_sum, map_smul, map_add, unit_zero, zero_add,
    smul_eq_mul, Finset.sum_mul, mul_assoc]

#print axioms spectral_unit_readout_formula

theorem spectral_unit_readout_routed [Fintype I] [Module R A]
    {J : Type*} [DecidableEq J]
    (reader : A →ₗ[R] R) (unit_zero : reader 1 = 0)
    (coeff : J → I → R) (phase : I → R) (core : A) (target : J)
    (kernel : ∀ k, (∑ f, coeff k f * phase f) = if k = target then 1 else 0)
    (k : J) :
    reader (∑ f, coeff k f • (phase f • (1 + core))) =
      if k = target then reader core else 0 := by
  simpa only [ite_mul, one_mul, zero_mul] using
    (spectral_unit_readout_formula reader unit_zero (coeff k) phase core).trans
      (congrArg (fun total : R => total * reader core) (kernel k))

#print axioms spectral_unit_readout_routed

end UnitLift
