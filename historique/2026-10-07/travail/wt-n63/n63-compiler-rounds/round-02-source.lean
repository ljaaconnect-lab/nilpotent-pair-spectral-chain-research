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
      ← Nat.succ_eq_add_one, Nat.succ_sub, pow_succ, Finset.sum_neg_distrib,
      sub_eq_add_neg, add_comm]
  suffices hsum : (∑ T ∈ S.powerset, (-1 : Int) ^ (S.card.succ - T.card) * f T) =
      -(∑ T ∈ S.powerset, (-1 : Int) ^ (S.card - T.card) * f T) by omega
  done

#print axioms CollisionMobiusBridge.coefficient_insert

end CollisionMobiusBridge
