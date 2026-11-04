import Mathlib.Tactic.Ring
import Mathlib.Algebra.BigOperators.Group.List.Basic

set_option Elab.async false

namespace OrientedOperators.SchurJet

variable {R : Type*} [CommRing R]

/-- Constant and linear coefficients of a product, stored as two scalars. -/
def jetFold : List (R × R) → R × R
  | [] => (1, 0)
  | dc :: xs =>
      (dc.1 * (jetFold xs).1,
       dc.1 * (jetFold xs).2 + dc.2 * (jetFold xs).1)

def evalProduct (xs : List (R × R)) (q : R) : R :=
  (xs.map (fun dc => dc.1 + q * dc.2)).prod

def scaleSecond (r : R) (xs : List (R × R)) : List (R × R) :=
  xs.map (fun dc => (dc.1, r * dc.2))

theorem jet_eval (xs : List (R × R)) (q : R) (hq : q ^ 2 = 0) :
    evalProduct xs q = (jetFold xs).1 + q * (jetFold xs).2 := by
  induction xs with
  | nil => simp [evalProduct, jetFold]
  | cons dc xs ih =>
    rw [evalProduct, List.map_cons, List.prod_cons, ← evalProduct, ih]
    calc
      _ = dc.1 * (jetFold xs).1 +
          q * (dc.1 * (jetFold xs).2 + dc.2 * (jetFold xs).1) +
          q ^ 2 * dc.2 * (jetFold xs).2 := by ring
      _ = _ := by simp [hq, jetFold]

theorem jet_scale (xs : List (R × R)) (r : R) :
    jetFold (scaleSecond r xs) = ((jetFold xs).1, r * (jetFold xs).2) := by
  induction xs with
  | nil => simp [scaleSecond, jetFold]
  | cons dc xs ih =>
    simp only [scaleSecond, List.map_cons, jetFold] at ih ⊢
    rw [ih]
    congr 1
    ring

/-- Exact terminal block elimination. The degree condition is represented
by the explicit hypothesis `r * P = 0`, rather than assumed implicitly. -/
theorem block_eliminate (xs : List (R × R)) (a r q : R)
    (hq : q ^ 2 = 0) (hr : r * (jetFold xs).1 = 0) :
    (a * q + r) * evalProduct xs q =
      q * (a * (jetFold (scaleSecond r xs)).1 +
        (jetFold (scaleSecond r xs)).2) := by
  rw [jet_eval xs q hq, jet_scale xs r]
  calc
    _ = q * (a * (jetFold xs).1 + r * (jetFold xs).2) +
        a * q ^ 2 * (jetFold xs).2 + r * (jetFold xs).1 := by ring
    _ = _ := by simp [hq, hr]

#print axioms jet_eval
#print axioms jet_scale
#print axioms block_eliminate

end OrientedOperators.SchurJet
