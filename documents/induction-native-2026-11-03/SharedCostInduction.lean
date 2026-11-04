import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Data.Nat.Basic
import Mathlib.Tactic.Linarith

/-!
Finite induction for an already shared scalar circuit.
S i denotes the total gate count of the same accumulated circuit after i steps.
An increment bounds new scalar gates only; existing predecessor wires are reused.
The recurrence and compatibility of the scalar interfaces are hypotheses.
This file does not establish such a recurrence for native oriented products,
does not formalize a native compiler, and does not remove auxiliary variables.
-/

open scoped BigOperators

namespace SharedCostInduction

theorem accumulated_cost (S increment : ℕ → ℕ) (m : ℕ)
    (hstep : ∀ i < m, S (i + 1) ≤ S i + increment i) :
    S m ≤ S 0 + ∑ i ∈ Finset.range m, increment i := by
  induction m with
  | zero => simp
  | succ m ih =>
    have hp := ih (fun i hi => hstep i (Nat.lt_succ_of_lt hi))
    simpa only [Finset.sum_range_succ, Nat.add_assoc] using
      (Nat.le_trans (hstep m (Nat.lt_succ_self m))
        (Nat.add_le_add_right hp (increment m)))

theorem uniform_increment_bound (S : ℕ → ℕ) (m n K c : ℕ)
    (hstep : ∀ i < m, S (i + 1) ≤ S i + K * n ^ c) :
    S m ≤ S 0 + m * (K * n ^ c) := by
  simpa using accumulated_cost S (fun _ => K * n ^ c) m hstep

theorem bounded_increment_bound (S increment : ℕ → ℕ) (m n K c : ℕ)
    (hstep : ∀ i < m, S (i + 1) ≤ S i + increment i)
    (hincrement : ∀ i < m, increment i ≤ K * n ^ c) :
    S m ≤ S 0 + m * (K * n ^ c) := by
  exact uniform_increment_bound S m n K c (fun i hi =>
    (hstep i hi).trans (Nat.add_le_add_left (hincrement i hi) (S i)))

theorem polynomial_two_term_bound (S : ℕ → ℕ) (m n K0 A K a b c : ℕ)
    (hstep : ∀ i < m, S (i + 1) ≤ S i + K * n ^ c)
    (hinit : S 0 ≤ K0 * n ^ a) (hlength : m ≤ A * n ^ b) :
    S m ≤ K0 * n ^ a + A * K * n ^ (b + c) := by
  nlinarith [uniform_increment_bound S m n K c hstep,
    Nat.mul_le_mul_right (K * n ^ c) hlength,
    congrArg (fun t : ℕ => A * K * t) (Nat.pow_add n b c)]

theorem polynomial_monomial_bound (S : ℕ → ℕ) (m n K0 A K a b c : ℕ)
    (hn : 1 ≤ n) (hstep : ∀ i < m, S (i + 1) ≤ S i + K * n ^ c)
    (hinit : S 0 ≤ K0 * n ^ a) (hlength : m ≤ A * n ^ b) :
    S m ≤ (K0 + A * K) * n ^ (max a (b + c)) := by
  nlinarith [polynomial_two_term_bound S m n K0 A K a b c hstep hinit hlength,
    Nat.mul_le_mul_left K0 (Nat.pow_le_pow_right hn (le_max_left a (b + c))),
    Nat.mul_le_mul_left (A * K) (Nat.pow_le_pow_right hn (le_max_right a (b + c)))]

/-- All six constants are fixed outside the quantifier over input size n. -/
theorem polynomial_family_bound (S : ℕ → ℕ → ℕ) (steps : ℕ → ℕ)
    (K0 A K a b c : ℕ)
    (hinit : ∀ n, 1 ≤ n → S n 0 ≤ K0 * n ^ a)
    (hlength : ∀ n, 1 ≤ n → steps n ≤ A * n ^ b)
    (hstep : ∀ n, 1 ≤ n → ∀ i < steps n,
      S n (i + 1) ≤ S n i + K * n ^ c) :
    ∀ n, 1 ≤ n → S n (steps n) ≤ (K0 + A * K) * n ^ (max a (b + c)) := by
  exact fun n hn => polynomial_monomial_bound (S n) (steps n) n K0 A K a b c hn
    (hstep n hn) (hinit n hn) (hlength n hn)

end SharedCostInduction

#print axioms SharedCostInduction.accumulated_cost
#print axioms SharedCostInduction.uniform_increment_bound
#print axioms SharedCostInduction.bounded_increment_bound
#print axioms SharedCostInduction.polynomial_two_term_bound
#print axioms SharedCostInduction.polynomial_monomial_bound
#print axioms SharedCostInduction.polynomial_family_bound
