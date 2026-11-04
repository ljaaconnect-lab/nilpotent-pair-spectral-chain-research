import Mathlib

/- Generated from exact SymPy n = 2 checks. This file is an UNVERIFIED
   candidate until the strict compiler and axiom checks have succeeded.
   It makes no asymptotic arithmetic circuit assertion. -/

namespace CollisionBridge

theorem n2_pair_factorization {R : Type*} [CommRing R] (a b t : R) :
    (a * t ^ 2 - b * t) * (t - t ^ 2) =
      -b * t ^ 2 + (a + b) * t ^ 3 - a * t ^ 4 := by
  ring

theorem n2_central_coeff (a b : ℚ) :
    ((1 : Polynomial ℚ) - Polynomial.C b * Polynomial.X ^ 2 +
      Polynomial.C (a + b) * Polynomial.X ^ 3 -
      Polynomial.C a * Polynomial.X ^ 4 + Polynomial.X ^ 6).coeff 3 =
      a + b := by
  simp

#print axioms CollisionBridge.n2_pair_factorization
#print axioms CollisionBridge.n2_central_coeff

end CollisionBridge
