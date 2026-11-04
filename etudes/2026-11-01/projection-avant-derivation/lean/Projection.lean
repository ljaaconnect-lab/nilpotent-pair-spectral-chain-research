import LocalPolynomialDerivative

/-!
The real formal derivative from Mathlib is used here. Its source is compiled
unchanged under the local module name LocalPolynomialDerivative by the replay
script because the installed cache lacks Mathlib's Derivative object file.

These identities verify one coordinate projection over an arbitrary coefficient
semiring. They do not formalize the complete multivariate compiler or gate cost.
-/

namespace DirectProjection

variable {R : Type*} [Semiring R]

theorem derivative_at_zero_eq_coeff_one (p : Polynomial R) :
    p.derivative.eval 0 = p.coeff 1 := by
  simp [← Polynomial.coeff_zero_eq_eval_zero, Polynomial.coeff_derivative]

theorem derivative_monomial_at_zero (a : R) (k : Nat) :
    (Polynomial.monomial k a).derivative.eval 0 = if k = 1 then a else 0 := by
  rw [derivative_at_zero_eq_coeff_one, Polynomial.coeff_monomial]

end DirectProjection

#print axioms DirectProjection.derivative_at_zero_eq_coeff_one
#print axioms DirectProjection.derivative_monomial_at_zero
