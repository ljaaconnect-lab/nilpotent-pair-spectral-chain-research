import ForwardDiffLocal

set_option Elab.async false

/-!
# Local division-free readout from finite differences

Only the reading identity for supplied polynomial evaluations is proved here.
No polynomial scalar-circuit bound for constructing those evaluations is
assumed or established. Indices `i` in `range L` correspond to samples
`t = i + 1`, hence to the points 1, ..., L.
-/

namespace FiniteDifferenceReadout

open Finset Polynomial
open scoped fwdDiff

variable {R : Type*} [CommRing R]

def translate (u : R) (f : R → R) : R → R := fun x => f (x + u)

/-- Fusion of translations is an identity of operators, without a cost claim. -/
theorem translate_fusion (u v : R) (f : R → R) :
    translate u (translate v f) = translate (u + v) f :=
  funext fun x => congrArg f (add_assoc x u v)

private theorem sign_factor (L t : ℕ) (ht : t ≤ L) :
    (-1 : R) ^ (L - t) = (-1 : R) ^ L * (-1 : R) ^ t := by
  simpa only [pow_add, mul_assoc, ← mul_pow, neg_mul_neg, one_mul, one_pow, mul_one] using
    congrArg (fun k => (-1 : R) ^ k * (-1 : R) ^ t) (Nat.sub_add_cancel ht)

/-- The local reader uses only values at the positive integer sample points. -/
theorem eval_zero_from_positive_samples (H : R[X]) (L : ℕ)
    (hH : H.natDegree < L) :
    H.eval 0 = ∑ i ∈ range L,
      (-1 : R) ^ i * (L.choose (i + 1) : R) * H.eval ((i + 1 : ℕ) : R) := by
  have hz := congrFun (Polynomial.fwdDiff_iter_eq_zero_of_degree_lt hH) (0 : R)
  simp only [fwdDiff_iter_eq_sum_shift, zero_add, nsmul_one, zsmul_eq_mul,
    Int.cast_mul, Int.cast_pow, Int.cast_neg, Int.cast_one, Int.cast_natCast,
    Pi.zero_apply] at hz
  have hs : (∑ t ∈ range (L + 1),
      ((-1 : R) ^ L * (-1 : R) ^ t) * (L.choose t : R) * H.eval (t : R)) = 0 :=
    (Finset.sum_congr rfl (fun t ht =>
      congrArg (fun c : R => c * (L.choose t : R) * H.eval (t : R))
        (sign_factor L t (Nat.le_of_lt_succ (mem_range.mp ht))))).symm.trans hz
  simp only [mul_assoc, ← Finset.mul_sum, neg_one_pow_mul_eq_zero_iff] at hs
  simp only [Finset.sum_range_succ', pow_zero, Nat.choose_zero_right,
    Nat.cast_one, one_mul, Nat.cast_zero, pow_succ, mul_neg_one, neg_mul] at hs
  symm
  simpa only [Finset.sum_neg_distrib, neg_add_eq_zero, mul_assoc] using hs

end FiniteDifferenceReadout

#print axioms FiniteDifferenceReadout.eval_zero_from_positive_samples
#print axioms FiniteDifferenceReadout.translate_fusion
