import Mathlib.Data.Nat.Basic
import Mathlib.Tactic.Linarith

/-!
Arithmetic consequences of separately justified gate counts.
This file does not formalize a compiler or prove polynomial construction
of the collision observations. In particular the hypotheses about costs
must not be replaced by the size of a symbolic expression.
-/

namespace SharedChainBounds

theorem coefficient_preparation_bound (n N ell : ℕ)
    (hn : 1 ≤ n) (hN : N ≤ 2 * n) (hell : ell ≤ n) :
    4 * n ^ 2 - 1 + 2 * n * N * ell + n * N ≤ 10 * n ^ 3 := by
  nlinarith [Nat.mul_le_mul_left (2 * n) (Nat.mul_le_mul hN hell),
    Nat.mul_le_mul_left n hN, Nat.mul_le_mul_left (n * n) hn,
    Nat.sub_le (4 * n ^ 2) 1]

theorem closed_state_compositions (n h : ℕ) (hh : h ≤ n ^ 2) :
    h * (4 * h + 2) ≤ 6 * n ^ 4 := by
  nlinarith [Nat.mul_self_le_mul_self hh, Nat.le_mul_self (n * n)]

theorem fused_reader_total (n h init total : ℕ) (hh : h ≤ n ^ 2)
    (hcost : total ≤ init + h ^ 2 + 2 * h) :
    total ≤ init + n ^ 4 + 2 * n ^ 2 := by
  nlinarith [Nat.mul_self_le_mul_self hh]

theorem explicit_spectral_overhead (n N ell base total : ℕ)
    (hn : 1 ≤ n) (hN : N ≤ 2 * n) (hell : ell ≤ n)
    (hcost : total ≤ base + 2 * N * ell + 2 * N) :
    total ≤ base + 8 * n ^ 2 := by
  nlinarith [Nat.mul_le_mul hN hell, Nat.mul_le_mul_left n hn]

theorem linearised_source_budget (n N h prep : ℕ)
    (hn : 1 ≤ n) (hN : N ≤ 2 * n) (hh : h ≤ n ^ 2)
    (hp : prep ≤ 18 * n ^ 3) :
    prep + 2 * n * N + h * (3 * n + 2) ≤ 27 * n ^ 3 := by
  nlinarith [Nat.mul_le_mul_left (2 * n) hN,
    Nat.mul_le_mul_right (3 * n + 2) hh, Nat.mul_le_mul_left (n * n) hn]

end SharedChainBounds

#print axioms SharedChainBounds.coefficient_preparation_bound
#print axioms SharedChainBounds.closed_state_compositions
#print axioms SharedChainBounds.fused_reader_total
#print axioms SharedChainBounds.explicit_spectral_overhead
#print axioms SharedChainBounds.linearised_source_budget
