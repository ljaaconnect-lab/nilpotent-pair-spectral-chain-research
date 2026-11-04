import Mathlib.Data.Multiset.Bind

set_option Elab.async false

namespace OrientedOperators.FullInsertion

variable {α : Type*}

/-- Insert one letter at every position, with multiplicities. -/
def insert (a : α) : List α → Multiset (List α)
  | [] => {[a]}
  | x :: w => {a :: x :: w} + (insert a w).map (List.cons x)

theorem insert_after_prefix (s : Multiset (List α)) (a x : α) :
    (s.map (List.cons x)).bind (insert a) =
      s.map (fun w => a :: x :: w) + (s.bind (insert a)).map (List.cons x) := by
  simp only [Multiset.bind_map, insert, Multiset.bind_add,
    Multiset.bind_singleton, ← Multiset.map_bind]

/-- Full insertion operators commute at every word length. -/
theorem insertion_commutes (a b : α) (w : List α) :
    (insert b w).bind (insert a) = (insert a w).bind (insert b) := by
  induction w with
  | nil => simp [insert, Multiset.add_comm]
  | cons x w ih =>
      simp only [insert, Multiset.add_bind, Multiset.singleton_bind, insert_after_prefix,
        Multiset.map_add, Multiset.map_singleton, Multiset.map_map]
      rw [ih]
      simp only [Function.comp_def]
      ac_rfl

theorem insertion_commutes_on_polynomials (a b : α) (s : Multiset (List α)) :
    (s.bind (insert b)).bind (insert a) = (s.bind (insert a)).bind (insert b) := by
  simp only [Multiset.bind_assoc, insertion_commutes a b]

def derive (a : α) : List α → Multiset (List α)
  | [] => 0
  | x :: w => {a :: x :: w} + (derive a w).map (List.cons x)

theorem insertion_is_derivation_plus_right (a : α) (w : List α) :
    insert a w = derive a w + {w ++ [a]} := by
  induction w with
  | nil => simp [insert, derive]
  | cons x w ih =>
      simp only [insert, derive, ih, Multiset.map_add, Multiset.map_singleton,
        List.cons_append, add_assoc]

theorem derivation_product_rule (a : α) (u v : List α) :
    derive a (u ++ v) =
      (derive a u).map (fun w => w ++ v) + (derive a v).map (fun w => u ++ w) := by
  induction u with
  | nil => simp [derive]
  | cons x u ih =>
      simp only [List.cons_append, derive, ih, Multiset.map_add,
        Multiset.map_singleton, Multiset.map_map, Function.comp_def, add_assoc]

#print axioms insert_after_prefix
#print axioms insertion_commutes
#print axioms insertion_commutes_on_polynomials
#print axioms insertion_is_derivation_plus_right
#print axioms derivation_product_rule

end OrientedOperators.FullInsertion
