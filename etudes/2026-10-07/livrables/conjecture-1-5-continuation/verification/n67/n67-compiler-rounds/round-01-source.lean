import Mathlib.Data.Matrix.Basic
import Mathlib.Algebra.Ring.Rat

namespace CollisionHadamardPfaffian

open scoped BigOperators

set_option maxRecDepth 4096
set_option maxHeartbeats 400000

def H (a b : Bool) : Rat := if a && b then -1 else 1

def parity4 (y : Fin 4 → Bool) : Bool :=
  Bool.xor (Bool.xor (y 0) (y 1)) (Bool.xor (y 2) (y 3))

def EVEN4 (y : Fin 4 → Bool) : Rat := if parity4 y then 0 else 1

def COPY4 (x : Fin 4 → Bool) : Rat :=
  if (∀ i : Fin 4, x i = false) ∨ (∀ i : Fin 4, x i = true) then 1 else 0

def tensorCopy4 (y : Fin 4 → Bool) : Rat :=
  ∑ x : Fin 4 → Bool, (∏ i : Fin 4, H (y i) (x i)) * COPY4 x

def gaussian4 (a01 a02 a03 a12 a13 a23 : Rat) (y : Fin 4 → Bool) : Rat :=
  match y 0, y 1, y 2, y 3 with
  | false, false, false, false => 1
  | true, true, false, false => a01
  | true, false, true, false => a02
  | true, false, false, true => a03
  | false, true, true, false => a12
  | false, true, false, true => a13
  | false, false, true, true => a23
  | true, true, true, true => a01 * a23 - a02 * a13 + a03 * a12
  | _, _, _, _ => 0

def hMatrix : Matrix Bool Bool Rat := H

def hInverse : Matrix Bool Bool Rat := fun a b => H a b / 2

theorem tensor_copy_even :
    ∀ y : Fin 4 → Bool, tensorCopy4 y = 2 * EVEN4 y := by
  decide

#print axioms CollisionHadamardPfaffian.tensor_copy_even
#print axioms CollisionHadamardPfaffian.gaussian4

end CollisionHadamardPfaffian
