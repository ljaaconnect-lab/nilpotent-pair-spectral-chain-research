import Mathlib.Data.Finset.Card
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Data.Nat.Basic
import Mathlib.Tactic.Linarith

/-!
Gate accounting for one fixed scalar DAG with stable gate identifiers.
G is its final set of reachable ordinary +/* gates. P is the gate set of
the actually constructed scalar coefficient prefix B -> C. Leaves and
wires are not elements of these sets. Both sets belong to the same graph.

The joint remainder G \ P includes every further gate needed by the chosen
compilation: fusion, normalization, sign and spectral processing together.
No intermediate amplitude, prescribed reader, or separate suffix is required.
This file counts supplied gate sets; it neither constructs another compiler
nor proves the polynomial bound on that joint remainder.
-/

open scoped BigOperators

namespace SameDAGCost

variable {V : Type*} [DecidableEq V]

def coefficientBound (n N ell : ℕ) : ℕ :=
  4 * n ^ 2 - 1 + 2 * n * N * ell + n * N

def jointCost (G P : Finset V) : ℕ := (G \ P).card

theorem same_dag_card (G P : Finset V) :
    G.card = (G ∩ P).card + jointCost G P := by
  exact (Finset.card_inter_add_card_sdiff G P).symm

theorem coefficient_bound (n N ell : ℕ)
    (hn : 1 ≤ n) (hN : N ≤ 2 * n) (hell : ell ≤ n) :
    coefficientBound n N ell ≤ 10 * n ^ 3 := by
  unfold coefficientBound
  nlinarith [Nat.sub_le (4 * n ^ 2) 1,
    Nat.mul_le_mul_left (2 * n) (Nat.mul_le_mul hN hell),
    Nat.mul_le_mul_left n hN, Nat.mul_le_mul_left (n * n) hn]

/-- The bound concerns the given final gate set, with one global joint budget. -/
theorem same_dag_polynomial_bound (G P : Finset V) (n N ell K d : ℕ)
    (hn : 1 ≤ n) (hN : N ≤ 2 * n) (hell : ell ≤ n)
    (hprefix : P.card ≤ coefficientBound n N ell)
    (hjoint : jointCost G P ≤ K * n ^ d) :
    G.card ≤ (10 + K) * n ^ max 3 d := by
  nlinarith [same_dag_card G P,
    Finset.card_le_card (Finset.inter_subset_right (s₁ := G) (s₂ := P)),
    coefficient_bound n N ell hn hN hell,
    Nat.mul_le_mul_left 10 (Nat.pow_le_pow_right hn (le_max_left 3 d)),
    Nat.mul_le_mul_left K (Nat.pow_le_pow_right hn (le_max_right 3 d))]

/-- K and d are fixed before quantification over n; G n and P n refer to one graph. -/
theorem same_dag_polynomial_family (G P : ℕ → Finset V) (N ell : ℕ → ℕ)
    (K d : ℕ)
    (hN : ∀ n, 1 ≤ n → N n ≤ 2 * n)
    (hell : ∀ n, 1 ≤ n → ell n ≤ n)
    (hprefix : ∀ n, 1 ≤ n → (P n).card ≤ coefficientBound n (N n) (ell n))
    (hjoint : ∀ n, 1 ≤ n → jointCost (G n) (P n) ≤ K * n ^ d) :
    ∀ n, 1 ≤ n → (G n).card ≤ (10 + K) * n ^ max 3 d := by
  exact fun n hn => same_dag_polynomial_bound (G n) (P n) n (N n) (ell n) K d
    hn (hN n hn) (hell n hn) (hprefix n hn) (hjoint n hn)

end SameDAGCost

#print axioms SameDAGCost.same_dag_card
#print axioms SameDAGCost.coefficient_bound
#print axioms SameDAGCost.same_dag_polynomial_bound
#print axioms SameDAGCost.same_dag_polynomial_family
