import Mathlib.Algebra.BigOperators.Group.Finset.Powerset
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Data.Nat.Choose.Sum

namespace CollisionMobiusBridge

open scoped BigOperators

variable {α : Type*} [DecidableEq α]

def coefficient (f : Finset α → Int) (S : Finset α) : Int :=
  ∑ T ∈ S.powerset, (-1 : Int) ^ (S.card - T.card) * f T

theorem coefficient_insert (f : Finset α → Int) (S : Finset α) (a : α) (ha : a ∉ S) :
    coefficient f (insert a S) =
      coefficient (fun T => f (insert a T)) S - coefficient f S := by
  simp (disch := grind [Finset.card_le_card])
    [coefficient, Finset.sum_powerset_insert ha, Finset.card_insert_of_notMem,
      ← Nat.succ_eq_add_one, sub_eq_add_neg, add_comm]
  suffices hsum : (∑ T ∈ S.powerset, (-1 : Int) ^ (S.card.succ - T.card) * f T) =
      -(∑ T ∈ S.powerset, (-1 : Int) ^ (S.card - T.card) * f T) by omega
  simpa only [Finset.sum_neg_distrib] using
    (Finset.sum_congr (s₁ := S.powerset) (s₂ := S.powerset)
      (f := fun T => (-1 : Int) ^ (S.card.succ - T.card) * f T)
      (g := fun T => -((-1 : Int) ^ (S.card - T.card) * f T)) rfl
      (fun T hT => by
        simp [Nat.succ_sub (Finset.card_le_card (Finset.mem_powerset.mp hT)), pow_succ]))

#print axioms CollisionMobiusBridge.coefficient_insert

theorem zeta_reconstruction (f : Finset α → Int) (S : Finset α) :
    (∑ T ∈ S.powerset, coefficient f T) = f S := by
  induction S using Finset.induction_on generalizing f
  case insert a S ha ih =>
    simp (disch := grind) [Finset.sum_powerset_insert ha, coefficient_insert,
      Finset.sum_sub_distrib, ih]
  case empty => done

#print axioms CollisionMobiusBridge.zeta_reconstruction

end CollisionMobiusBridge
