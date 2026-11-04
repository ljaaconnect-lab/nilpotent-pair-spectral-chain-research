import Mathlib.Data.Nat.Choose.Basic
import Mathlib.Data.Fintype.Fin
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Tactic.Ring

set_option Elab.async false

namespace OrientedOperators.DualReader

open scoped BigOperators

def collisions {n : Nat} (u : Fin n → Nat) : Nat :=
  ∑ j, (u j).choose 2

def overlap {n : Nat} (u v : Fin n → Nat) : Nat :=
  ∑ j, u j * v j

private theorem choose_two_add (a b : Nat) :
    (a + b).choose 2 = a.choose 2 + b.choose 2 + a * b := by
  induction b with
  | zero => simp
  | succ b ih =>
    simp only [Nat.add_succ, Nat.choose_succ_succ, Nat.choose_one_right, ih, Nat.mul_succ]
    ring

theorem collisions_add {n : Nat} (u v : Fin n → Nat) :
    collisions (u + v) = collisions u + collisions v + overlap u v := by
  simp only [collisions, overlap, Pi.add_apply, choose_two_add, Finset.sum_add_distrib]

variable {R : Type*} [CommSemiring R]

def monomialValue {n : Nat} (t : Fin n → R) (u : Fin n → Nat) : R :=
  ∏ j, t j ^ u j

def diagonalRead {n : Nat} (p : Nat → R) (t : Fin n → R)
    (u : Fin n → Nat) : R :=
  p (collisions u) * monomialValue t u

def shiftedRead {n : Nat} (p : Nat → R) (t : Fin n → R)
    (u v : Fin n → Nat) : R :=
  p (collisions u + collisions v + overlap u v) * monomialValue t v

theorem monomialValue_add {n : Nat} (t : Fin n → R) (u v : Fin n → Nat) :
    monomialValue t (u + v) = monomialValue t u * monomialValue t v := by
  simp only [monomialValue, Pi.add_apply, pow_add, Finset.prod_mul_distrib]

theorem monomial_pullthrough {n : Nat} (p : Nat → R) (t : Fin n → R)
    (u v : Fin n → Nat) :
    diagonalRead p t (u + v) = monomialValue t u * shiftedRead p t u v := by
  simp only [diagonalRead, collisions_add, monomialValue_add, shiftedRead]
  ring
theorem shiftedRead_zero {n : Nat} (p : Nat → R) (t : Fin n → R)
    (u : Fin n → Nat) : shiftedRead p t u 0 = p (collisions u) := by
  simp [shiftedRead, collisions, overlap, monomialValue]

#print axioms collisions_add
#print axioms monomialValue_add
#print axioms monomial_pullthrough
#print axioms shiftedRead_zero
end OrientedOperators.DualReader
