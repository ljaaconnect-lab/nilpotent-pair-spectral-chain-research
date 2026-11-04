import Mathlib.GroupTheory.Perm.Fin
import DeterminantBridge

namespace CollisionDirectProjector

open scoped BigOperators
open CollisionDeterminantBridge

variable {R : Type} [CommRing R]

noncomputable section

abbrev bilinear (a b c d x y : R) : R := a + b * x + c * y + d * x * y

abbrev mixedCofactor (a b c d : R) : R :=
  bilinear a b c d 1 1 - bilinear a b c d 1 0 -
    bilinear a b c d 0 1 + bilinear a b c d 0 0

abbrev localCorrection (a b c d x y : R) : R :=
  bilinear a b c d x y - 2 * x * y * mixedCofactor a b c d

def phase {S : Type} (p : S → Prop) [DecidablePred p] (P : S → R) : S → R :=
  fun s => if p s then -P s else P s

def inversionPhase {n : Nat} (σ : Equiv.Perm (Fin n)) : R :=
  ∏ i : Fin n, ∏ l ∈ Finset.Ioi i, (if σ i < σ l then (1 : R) else -1)

theorem inversion_phase_eq_signCoeff {n : Nat} (σ : Equiv.Perm (Fin n)) :
    (inversionPhase σ : R) = signCoeff σ := by
  simpa [inversionPhase, signCoeff, Units.coe_prod, Int.cast_prod, apply_ite] using
    congrArg (fun u : Intˣ => ((u : Int) : R))
      (Equiv.Perm.sign_eq_prod_prod_Ioi σ).symm

#print axioms CollisionDirectProjector.inversion_phase_eq_signCoeff

theorem local_mixed_cofactor (a b c d : R) : mixedCofactor a b c d = d := by
  ring

#print axioms CollisionDirectProjector.local_mixed_cofactor

theorem local_xy_correction (a b c d x y : R) :
    localCorrection a b c d x y = a + b * x + c * y - d * x * y := by
  ring

#print axioms CollisionDirectProjector.local_xy_correction

end
end CollisionDirectProjector
