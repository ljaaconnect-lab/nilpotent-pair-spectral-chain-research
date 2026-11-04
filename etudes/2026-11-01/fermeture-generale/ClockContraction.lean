import Mathlib.Algebra.BigOperators.Ring.Finset

set_option Elab.async false

open scoped BigOperators

namespace OrientedOperators.ClockContraction

variable {P B J R : Type*} [Fintype P] [Fintype B] [Fintype J]
  [DecidableEq B] [CommSemiring R]

/-- A collision diagram on a clock path. Each block chooses its column
independently; different blocks are allowed to choose equal columns. -/
def contraction (π : P → B) (a : P → J → R) : R :=
  ∑ f : B → J, ∏ p : P, a p (f (π p))

/-- Exact factorization, uniform in the number of positions, blocks and columns.
This theorem concerns one diagram, rather than the sum of every diagram. -/
theorem factorization (π : P → B) (a : P → J → R) :
    contraction π a =
      ∏ b : B, ∑ j : J, ∏ p ∈ Finset.univ.filter (fun p => π p = b), a p j := by
  unfold contraction
  rw [Fintype.prod_sum]
  apply Finset.sum_congr rfl
  intro f hf
  rw [← Finset.prod_fiberwise (Finset.univ : Finset P) π]
  apply Finset.prod_congr rfl
  intro b hb
  apply Finset.prod_congr rfl
  intro p hp
  rw [(Finset.mem_filter.mp hp).2]

#print axioms factorization

end OrientedOperators.ClockContraction
