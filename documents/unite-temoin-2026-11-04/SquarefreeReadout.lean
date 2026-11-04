import Mathlib.Algebra.MvPolynomial.Basic

/-!
The native squarefree coefficient reader annihilates a collision factor.
These are identities for formal polynomials over any commutative semiring;
no coefficient oracle or scalar circuit-size conclusion is introduced.
-/

namespace SquarefreeReadout

open MvPolynomial

variable {R : Type*} [CommSemiring R] {σ : Type*}

theorem coeff_mul_square_eq_zero (p : MvPolynomial σ R)
    (d : σ →₀ ℕ) (j : σ) (hd : d j = 1) :
    (p * X j ^ 2).coeff d = 0 := by
  simp [X_pow_eq_monomial, coeff_mul_monomial', Finsupp.single_le_iff, hd]

theorem coeff_sum_square_multiples_eq_zero {n : ℕ}
    (p : Fin n → MvPolynomial (Fin n) R) (d : Fin n →₀ ℕ)
    (hd : ∀ j, d j = 1) :
    (∑ j : Fin n, p j * X j ^ 2).coeff d = 0 := by
  simp [coeff_mul_square_eq_zero, hd]

theorem coeff_add_square_multiples {n : ℕ}
    (f : MvPolynomial (Fin n) R) (p : Fin n → MvPolynomial (Fin n) R)
    (d : Fin n →₀ ℕ) (hd : ∀ j, d j = 1) :
    (f + ∑ j : Fin n, p j * X j ^ 2).coeff d = f.coeff d := by
  simp [coeff_mul_square_eq_zero, hd]

theorem exponent_ne_zero (d : σ →₀ ℕ) (j : σ) (hd : d j = 1) :
    d ≠ 0 := by
  exact fun h => Nat.zero_ne_one ((congrArg (fun e : σ →₀ ℕ => e j) h).symm.trans hd)

theorem coeff_one_eq_zero (d : σ →₀ ℕ) (j : σ) (hd : d j = 1) :
    (1 : MvPolynomial σ R).coeff d = 0 := by
  simpa only [map_one] using (coeff_C_of_ne_zero (exponent_ne_zero d j hd) (1 : R))

#print axioms coeff_mul_square_eq_zero
#print axioms coeff_sum_square_multiples_eq_zero
#print axioms coeff_add_square_multiples
#print axioms exponent_ne_zero
#print axioms coeff_one_eq_zero

end SquarefreeReadout
