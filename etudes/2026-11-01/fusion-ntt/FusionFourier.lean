import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Data.Fintype.BigOperators

set_option Elab.async false

namespace OrientedOperators.FusionFourier

variable {G R : Type*} [Add G] [Fintype G] [Semiring R]

/-- The convolution theorem before grouping pairs with equal total index.
The coefficients may belong to a noncommutative operator semiring. -/
theorem fourier_pairs (χ A B : G → R)
    (hχ : ∀ r s, χ (r + s) = χ r * χ s)
    (hcentral : ∀ r s, Commute (A r) (χ s)) :
    (∑ r, χ r * A r) * (∑ s, χ s * B s) =
      ∑ r, ∑ s, χ (r + s) * (A r * B s) := by
  rw [Fintype.sum_mul_sum]
  refine Finset.sum_congr rfl (fun r hr => ?_)
  refine Finset.sum_congr rfl (fun s hs => ?_)
  simpa only [hχ] using (hcentral r s).mul_mul_mul_comm (χ r) (B s)

/-- Fourier multiplication and the additive transport fusion law coexist:
each pair carries its summed frequency index and its summed parameter. -/
theorem fourier_fused {P : Type*} [Add P]
    (T : P → R) (hfuse : ∀ u v, T (u + v) = T u * T v)
    (χ : G → R) (u v : G → P)
    (hχ : ∀ r s, χ (r + s) = χ r * χ s)
    (hcentral : ∀ r s, Commute (T (u r)) (χ s)) :
    (∑ r, χ r * T (u r)) * (∑ s, χ s * T (v s)) =
      ∑ r, ∑ s, χ (r + s) * T (u r + v s) := by
  simpa only [← hfuse] using
    fourier_pairs χ (fun r => T (u r)) (fun s => T (v s)) hχ hcentral

/-- Exact multiplication law for finite transport differences. -/
theorem difference_fusion {P S : Type*} [Add P] [Ring S]
    (T : P → S) (u v : P) (hfuse : T u * T v = T (u + v)) :
    (T u - 1) * (T v - 1) =
      (T (u + v) - 1) - (T u - 1) - (T v - 1) := by
  rw [sub_mul, mul_sub, mul_one, one_mul, hfuse, sub_sub_sub_cancel_right]

/-- Convolution grouped by the sum of the two frequency indices.  Taking
G = ZMod N gives circular convolution, with operator-valued coefficients. -/
def convolution [DecidableEq G] (A B : G → R) (k : G) : R :=
  ∑ p ∈ (Finset.univ : Finset (G × G)).filter (fun p => p.1 + p.2 = k),
    A p.1 * B p.2

theorem fourier_convolution [DecidableEq G] (χ A B : G → R)
    (hχ : ∀ r s, χ (r + s) = χ r * χ s)
    (hcentral : ∀ r s, Commute (A r) (χ s)) :
    (∑ k, χ k * convolution A B k) =
      (∑ r, χ r * A r) * (∑ s, χ s * B s) := by
  rw [fourier_pairs χ A B hχ hcentral, ← Fintype.sum_prod_type',
    ← Finset.sum_fiberwise (Finset.univ : Finset (G × G)) (fun p => p.1 + p.2)]
  simp only [convolution, Finset.mul_sum]
  refine Finset.sum_congr rfl (fun k hk => ?_)
  refine Finset.sum_congr rfl (fun p hp => ?_)
  rw [(Finset.mem_filter.mp hp).2]

#print axioms fourier_pairs
#print axioms fourier_fused
#print axioms difference_fusion
#print axioms fourier_convolution

end OrientedOperators.FusionFourier
