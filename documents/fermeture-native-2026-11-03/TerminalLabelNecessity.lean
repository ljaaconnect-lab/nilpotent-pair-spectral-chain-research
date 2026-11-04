import Mathlib.Algebra.BigOperators.Ring.Finset

/-!
A nonzero output in the augmentation kernel cannot be represented by a
constant scalar embedded in the same algebra. Auxiliary erasure must act
on a represented coefficient while preserving its terminal basis label.
No coefficient-extraction circuit or complexity bound is assumed here.
-/

namespace TerminalLabelNecessity

variable {R A : Type*} [Semiring R] [Semiring A]

theorem scalar_representative_eq_zero (sigma : R →+* A) (epsilon : A →+* R)
    (hsection : Function.LeftInverse epsilon sigma) (b : R) (V : A)
    (hzero : epsilon V = 0) (hrep : sigma b = V) : b = 0 :=
  (hsection b).symm.trans ((congrArg epsilon hrep).trans hzero)

theorem scalar_representative_forces_zero (sigma : R →+* A) (epsilon : A →+* R)
    (hsection : Function.LeftInverse epsilon sigma) (b : R) (V : A)
    (hzero : epsilon V = 0) (hrep : sigma b = V) : b = 0 ∧ V = 0 :=
  let hb := scalar_representative_eq_zero sigma epsilon hsection b V hzero hrep
  ⟨hb, hrep.symm.trans ((congrArg sigma hb).trans (map_zero sigma))⟩

theorem nonzero_terminal_has_no_scalar_representative
    (sigma : R →+* A) (epsilon : A →+* R)
    (hsection : Function.LeftInverse epsilon sigma) (V : A)
    (hzero : epsilon V = 0) (hne : V ≠ 0) : ∀ b, sigma b ≠ V :=
  fun b hrep => hne (scalar_representative_forces_zero
    sigma epsilon hsection b V hzero hrep).2

end TerminalLabelNecessity

#print axioms TerminalLabelNecessity.scalar_representative_eq_zero
#print axioms TerminalLabelNecessity.scalar_representative_forces_zero
#print axioms TerminalLabelNecessity.nonzero_terminal_has_no_scalar_representative
