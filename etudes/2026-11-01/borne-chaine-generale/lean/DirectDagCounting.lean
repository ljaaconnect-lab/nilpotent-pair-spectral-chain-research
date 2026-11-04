import Mathlib.Data.Nat.Choose.Basic
import Mathlib.Data.Fintype.Card

/-!
Pure finite counting only. This file does not formalize a compiler, derivative
reachability, or a gate lower bound for an arithmetic circuit.
-/

namespace DirectDagCounting

theorem two_pow_le_middle_choose (m : Nat) :
    2 ^ m ≤ Nat.choose (2 * m) m := by
  induction m with
  | zero => exact Nat.le_refl 1
  | succ m ih =>
    change 2 ^ (m + 1) ≤ Nat.choose ((2 * m + 1) + 1) (m + 1)
    rw [Nat.choose_succ_succ', Nat.choose_symm_half, Nat.pow_succ', Nat.two_mul]
    exact Nat.add_le_add (ih.trans (Nat.choose_le_succ (2 * m) m))
      (ih.trans (Nat.choose_le_succ (2 * m) m))

/-- Counting transfer only; the injection must be constructed separately. -/
theorem choose_le_of_injective (m count : Nat)
    (f : Fin (Nat.choose (2 * m) m) → Fin count)
    (hf : Function.Injective f) :
    Nat.choose (2 * m) m ≤ count := by
  simpa only [Fintype.card_fin] using Fintype.card_le_of_injective f hf

/-- A conditional consequence of an explicitly supplied injection, not a
claim that such an injection exists for any particular circuit. -/
theorem two_pow_le_of_injective (m count : Nat)
    (f : Fin (Nat.choose (2 * m) m) → Fin count)
    (hf : Function.Injective f) : 2 ^ m ≤ count := by
  exact (two_pow_le_middle_choose m).trans (choose_le_of_injective m count f hf)

end DirectDagCounting

#print axioms DirectDagCounting.two_pow_le_middle_choose
#print axioms DirectDagCounting.choose_le_of_injective
#print axioms DirectDagCounting.two_pow_le_of_injective
