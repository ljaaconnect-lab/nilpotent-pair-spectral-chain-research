import Mathlib.Algebra.Polynomial.Coeff
import Mathlib.Algebra.BigOperators.Group.List.Basic

set_option Elab.async false

namespace OrientedOperators.TerminalDifference

open Polynomial

variable {R : Type*} [Semiring R]

/-- A product of `n` factors with zero constant term has no terms below degree `n`.
The coefficient semiring need not be commutative. -/
theorem coeff_product_below_length
    (ps : List R[X]) (hz : ∀ p ∈ ps, p.coeff 0 = 0)
    (k : ℕ) (hk : k < ps.length) :
    ps.prod.coeff k = 0 := by
  induction ps generalizing k with
  | nil => simp at hk
  | cons p ps ih =>
    rw [List.prod_cons, coeff_mul]
    apply Finset.sum_eq_zero
    rintro ⟨a, b⟩ hab
    by_cases ha : a = 0
    · simp [ha, hz p List.mem_cons_self]
    · have hab' := Finset.mem_antidiagonal.mp hab
      have hb : b < ps.length := by
        simp only [List.length_cons] at hk
        omega
      simp only [ih (fun q hq => hz q (List.mem_cons_of_mem p hq)) b hb, mul_zero]

/-- At degree `n`, the ordered product of `n` factors with zero constant term
depends only on their linear coefficients. -/
theorem coeff_product_at_length
    (ps : List R[X]) (hz : ∀ p ∈ ps, p.coeff 0 = 0) :
    ps.prod.coeff ps.length = (ps.map (fun p => p.coeff 1)).prod := by
  induction ps with
  | nil => simp
  | cons p ps ih =>
    simp only [List.prod_cons, List.length_cons, List.map_cons, coeff_mul]
    rw [Finset.sum_eq_single (1, ps.length)]
    · rw [ih (fun q hq => hz q (List.mem_cons_of_mem p hq))]
    · rintro ⟨a, b⟩ hab hne
      by_cases ha : a = 0
      · simp [ha, hz p List.mem_cons_self]
      · have hab' := Finset.mem_antidiagonal.mp hab
        have hb : b < ps.length := by grind
        simp only [coeff_product_below_length ps (fun q hq => hz q (List.mem_cons_of_mem p hq)) b hb, mul_zero]
    · simp [Finset.mem_antidiagonal, Nat.add_comm]

section Ring

variable {S : Type*} [Ring S]

/-- Exact terminal-degree rule for products of transport differences. -/
theorem coeff_transport_differences
    (ts : List S[X]) (h : ∀ t ∈ ts, t.coeff 0 = 1) :
    (ts.map (fun t => t - 1)).prod.coeff ts.length =
      (ts.map (fun t => t.coeff 1)).prod := by
  have hz : ∀ p ∈ ts.map (fun t => t - 1), p.coeff 0 = 0 := by
    intro p hp
    obtain ⟨t, ht, rfl⟩ := List.mem_map.mp hp
    simp [h t ht]
  simpa [Function.comp_def, coeff_one] using
    coeff_product_at_length (ts.map (fun t => t - 1)) hz

end Ring

#print axioms coeff_product_below_length
#print axioms coeff_product_at_length
#print axioms coeff_transport_differences

end OrientedOperators.TerminalDifference
