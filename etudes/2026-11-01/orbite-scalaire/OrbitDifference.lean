import Mathlib.Algebra.Group.Hom.Basic
import Mathlib.Data.List.Basic

set_option Elab.async false

namespace OrientedOperators.OrbitDifference

variable {G E R : Type*} [AddMonoid G] [AddGroup E] [AddGroup R]

/-- Observation of the additive transport orbit, as a scalar-valued function. -/
def orbit (readout : E →+ R) (transport : G → E →+ E) (F : E) (s : G) : R :=
  readout (transport s F)

def operatorDiff (transport : G → E →+ E) (y : G) (F : E) : E :=
  transport y F - F

def scalarDiff (y : G) (g : G → R) (s : G) : R :=
  g (s + y) - g s

def operatorDiffs (transport : G → E →+ E) : List G → E → E
  | [], F => F
  | y :: ys, F => operatorDiff transport y (operatorDiffs transport ys F)

def scalarDiffs : List G → (G → R) → G → R
  | [], g => g
  | y :: ys, g => scalarDiff y (scalarDiffs ys g)

theorem intertwiner_diff (readout : E →+ R) (transport : G → E →+ E)
    (fusion : ∀ s y F, transport s (transport y F) = transport (s + y) F)
    (F : E) (s y : G) :
    orbit readout transport (operatorDiff transport y F) s =
      scalarDiff y (orbit readout transport F) s := by
  simp only [orbit, operatorDiff, scalarDiff, map_sub, fusion]

/-- Exact conjugation of a whole list of differences to scalar translations.
This identity does not assert a size bound for the resulting scalar circuit. -/
theorem intertwiner_iterated_diffs (readout : E →+ R) (transport : G → E →+ E)
    (fusion : ∀ s y F, transport s (transport y F) = transport (s + y) F)
    (ys : List G) (F : E) (s : G) :
    orbit readout transport (operatorDiffs transport ys F) s =
      scalarDiffs ys (orbit readout transport F) s := by
  induction ys generalizing s with
  | nil => rfl
  | cons y ys ih =>
    simp only [operatorDiffs, scalarDiffs, intertwiner_diff readout transport fusion,
      scalarDiff, ih]

#print axioms intertwiner_diff
#print axioms intertwiner_iterated_diffs

end OrientedOperators.OrbitDifference
