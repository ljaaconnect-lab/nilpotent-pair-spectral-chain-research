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
  | succ k ih =>
    change power (matrixMonoid r R) M k * M = M ^ k * M
    exact congrArg (fun N => N * M) ih

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
  | @Circuit.parallel _ _ _ _ family => fun o => (family o.1).eval inputs o.2
  | .comp first next => next.eval (first.eval inputs)

def Circuit.gates {I O : Type} (c : Circuit I O) : Nat :=
  match c with
  | .wire _ => 0
  | .constant _ => 0
  | .add _ _ => 1
  | .mul _ _ => 1
  | .pair left right => left.gates + right.gates
  | @Circuit.parallel _ J _ inst family =>
    letI := inst
    ∑ j : J, (family j).gates
  | .comp first next => first.gates + next.gates

def sumCircuit : (r : Nat) → Circuit (Fin r) Unit
  | 0 => .constant (fun _ => false)
  | 1 => .wire (fun _ => 0)
  | r + 2 => .comp
      (.pair (.comp (.wire (fun i : Fin (r+1) => i.castSucc)) (sumCircuit (r+1)))
        (.wire (fun _ => Fin.last (r+1))))
      (.add (Sum.inl ()) (Sum.inr ()))

theorem sumCircuit_eval (r : Nat) {R : Type u} [Semiring R] (inputs : Fin r → R) :
    (sumCircuit r).eval inputs () = ∑ i, inputs i := by
  induction r with
  | zero => simp [sumCircuit, Circuit.eval]
  | succ r ih =>
    cases r with
    | zero => simp [sumCircuit, Circuit.eval, Fin.sum_univ_one]
    | succ r =>
      change (sumCircuit (r+1)).eval (fun i => inputs i.castSucc) () +
        inputs (Fin.last (r+1)) = ∑ i, inputs i
      rw [ih]
      exact (Fin.sum_univ_castSucc inputs).symm

theorem sumCircuit_gates (r : Nat) : (sumCircuit r).gates = r - 1 := by
  induction r with
  | zero => rfl
  | succ r ih =>
    cases r with
    | zero => rfl
    | succ r =>
      change (sumCircuit (r+1)).gates + 0 + 0 + 1 = (r+1+1)-1
      rw [ih]
      omega

def dotCircuit (r : Nat) : Circuit (Sum (Fin r) (Fin r)) Unit :=
  .comp (.parallel (J := Fin r) (fun k => .mul (Sum.inl k) (Sum.inr k)))
    (.comp (.wire (fun k => (k, ()))) (sumCircuit r))

theorem dotCircuit_eval (r : Nat) {R : Type u} [Semiring R]
    (inputs : Sum (Fin r) (Fin r) → R) :
    (dotCircuit r).eval inputs () = ∑ k, inputs (Sum.inl k) * inputs (Sum.inr k) := by
  exact sumCircuit_eval r (fun k => inputs (Sum.inl k) * inputs (Sum.inr k))

theorem dotCircuit_gates (r : Nat) : (dotCircuit r).gates = r + (r-1) := by
  simp [dotCircuit, Circuit.gates, sumCircuit_gates]

abbrev Cell (r : Nat) := Fin r × Fin r

def denseProduct (r : Nat) : Circuit (Sum (Cell r) (Cell r)) (Cell r) :=
  .comp (.parallel (J := Cell r) (fun cell =>
      .comp (.wire (Sum.elim (fun k => Sum.inl (cell.1, k))
        (fun k => Sum.inr (k, cell.2)))) (dotCircuit r)))
    (.wire (fun cell => (cell, ())))

theorem denseProduct_eval (r : Nat) {R : Type u} [Semiring R]
    (inputs : Sum (Cell r) (Cell r) → R) (cell : Cell r) :
    (denseProduct r).eval inputs cell =
      ∑ k, inputs (Sum.inl (cell.1, k)) * inputs (Sum.inr (k, cell.2)) := by
  exact dotCircuit_eval r (Sum.elim (fun k => inputs (Sum.inl (cell.1, k)))
    (fun k => inputs (Sum.inr (k, cell.2))))

theorem denseProduct_matrix (r : Nat) {R : Type u} [Semiring R]
    (A B : Matrix (Fin r) (Fin r) R) (i j : Fin r) :
    (denseProduct r).eval (Sum.elim (fun c => A c.1 c.2) (fun c => B c.1 c.2)) (i,j) =
      (A * B) i j := by
  exact denseProduct_eval r (Sum.elim (fun c => A c.1 c.2) (fun c => B c.1 c.2)) (i,j)

theorem denseProduct_raw_gates (r : Nat) :
    (denseProduct r).gates = (r*r)*(r+(r-1)) := by
  simp [denseProduct, Circuit.gates, dotCircuit_gates]

theorem dense_product_gate_count (r : Nat) (hr : 1 ≤ r) :
    (denseProduct r).gates = 2*r^3-r^2 := by
  rw [denseProduct_raw_gates, show r+(r-1)=2*r-1 from by omega,
    Nat.mul_sub_left_distrib]
  congr 1 <;> ring

#print axioms DenseScalar.matrix_power_correct
#print axioms DenseScalar.sumCircuit_eval
#print axioms DenseScalar.sumCircuit_gates
#print axioms DenseScalar.dotCircuit_eval
#print axioms DenseScalar.dotCircuit_gates
#print axioms DenseScalar.denseProduct_eval
#print axioms DenseScalar.denseProduct_matrix
#print axioms DenseScalar.denseProduct_raw_gates
#print axioms DenseScalar.dense_product_gate_count

end DenseScalar
