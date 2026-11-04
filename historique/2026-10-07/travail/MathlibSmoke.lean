import Mathlib.Data.Matrix.Mul
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.LinearAlgebra.Vandermonde
import Mathlib.Algebra.Polynomial.Coeff
import Mathlib.Tactic.Ring
import Mathlib.Tactic.LinearCombination

#check Matrix.mul_assoc
#check Matrix.det_vandermonde
#check Polynomial.coeff_mul

example {R : Type*} [CommRing R] : Lean.Grind.CommRing R := inferInstance

example {R : Type*} [CommRing R] (a b : R) :
    (a + b)^2 = a^2 + 2*a*b + b^2 := by ring
