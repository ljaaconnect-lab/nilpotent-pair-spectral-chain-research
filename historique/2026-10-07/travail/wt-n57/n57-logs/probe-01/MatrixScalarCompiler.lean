import PowerCompiler
import Mathlib.Data.Matrix.Mul
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Tactic.Ring

open scoped BigOperators
open SharedBinaryPower

namespace DenseScalar

universe u

def matrixMonoid (r : Nat) (R : Type u) [Semiring R] :
    MonoidData (Matrix (Fin r) (Fin r) R) where
  one := 1
  mul := (· * ·)
  assoc := Matrix.mul_assoc
  one_mul := Matrix.one_mul
  mul_one := Matrix.mul_one

theorem matrix_power_correct (r : Nat) {R : Type u} [Semiring R]
    (M : Matrix (Fin r) (Fin r) R) (k : Nat) :
    compilePower (matrixMonoid r R) M k = M ^ k := by
  rw [binary_plan_correct]
  induction k with
  | zero => rfl
  | succ k ih => simpa only [power, matrixMonoid, pow_succ, ih]

/-- Compositional scalar DAG: wiring reuses existing outputs. -/
inductive Circuit : Type → Type → Type 1 where
  | wire {I O : Type} (read : O → I) : Circuit I O
  | constant {I O : Type} (bits : O → Bool) : Circuit I O
  | add {I : Type} (left right : I) : Circuit I Unit
  | mul {I : Type} (left right : I) : Circuit I Unit
  | pair {I O P : Type} (left : Circuit I O) (right : Circuit I P) : Circuit I (Sum O P)
  | parallel {I J O : Type} [Fintype J] (family : J → Circuit I O) : Circuit I (J × O)
  | comp {I J O : Type} (first : Circuit I J) (next : Circuit J O) : Circuit I O

def Circuit.eval {I O : Type} {R : Type u} [Semiring R]
    (c : Circuit I O) (inputs : I → R) : O → R :=
  match c with
  | .wire read => inputs ∘ read
  | .constant bits => fun o => if bits o then 1 else 0
  | .add left right => fun _ => inputs left + inputs right
  | .mul left right => fun _ => inputs left * inputs right
  | .pair left right => Sum.elim (left.eval inputs) (right.eval inputs)
  | .parallel family => fun o => (family o.1).eval inputs o.2
  | .comp first next => next.eval (first.eval inputs)

def Circuit.gates {I O : Type} (c : Circuit I O) : Nat :=
  match c with
  | .wire _ => 0
  | .constant _ => 0
  | .add _ _ => 1
  | .mul _ _ => 1
  | .pair left right => left.gates + right.gates
  | .parallel family => ∑ j, (family j).gates
  | .comp first next => first.gates + next.gates

def sumCircuit : (r : Nat) → Circuit (Fin r) Unit
  | 0 => .constant (fun _ => false)
  | 1 => .wire (fun _ => 0)
  | r + 2 => .comp
      (.pair (.comp (.wire (fun i : Fin (r+1) => i.castSucc)) (sumCircuit (r+1)))
        (.wire (fun _ => Fin.last (r+1))))
      (.add (Sum.inl ()) (Sum.inr ()))

#check Fin.sum_univ_castSucc
#check Fin.sum_univ_one
#print axioms DenseScalar.matrix_power_correct

end DenseScalar
