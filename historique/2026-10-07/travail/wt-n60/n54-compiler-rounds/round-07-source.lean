import Mathlib.Algebra.Polynomial.Coeff
import GeneralPairingRing

namespace GeneralCollisionPolynomialBridge

open GeneralCollisionPairingRing

variable {R : Type} [CommRing R]

-- This is an actual polynomial, defined by summing the indicated monomials.
noncomputable def interp (p : SparsePolynomial R) : Polynomial R :=
  (p.map (fun term => Polynomial.monomial term.1 term.2)).sum

theorem interp_append (p q : SparsePolynomial R) :
    interp (p ++ q) = interp p + interp q := by
  simp [interp, List.sum_append]

#print axioms GeneralCollisionPolynomialBridge.interp_append

theorem interp_monomial_multiply (a : Nat × R) (q : SparsePolynomial R) :
    interp (q.map (fun b => (a.1 + b.1, a.2 * b.2))) =
      Polynomial.monomial a.1 a.2 * interp q := by
  induction q
  all_goals simp_all [interp, List.map_map, mul_add, Polynomial.monomial_mul_monomial]

#print axioms GeneralCollisionPolynomialBridge.interp_monomial_multiply

theorem interp_multiply (p q : SparsePolynomial R) :
    interp (multiply p q) = interp p * interp q := by
  induction p
  all_goals simp_all [multiply, interp, add_mul]
  case cons a p ih =>
    simpa [interp, List.map_map] using interp_monomial_multiply a q

#print axioms GeneralCollisionPolynomialBridge.interp_multiply

theorem coeff_interp (p : SparsePolynomial R) (k : Nat) :
    (interp p).coeff k = coefficient p k := by
  simp [interp, coefficient, Polynomial.coeff_list_sum_map, Polynomial.coeff_monomial]

#print axioms GeneralCollisionPolynomialBridge.coeff_interp

end GeneralCollisionPolynomialBridge
