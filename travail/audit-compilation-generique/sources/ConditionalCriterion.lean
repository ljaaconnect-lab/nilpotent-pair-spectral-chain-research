import MatrixScalarCompiler
import Mathlib.Algebra.Polynomial.Eval.Defs

open scoped BigOperators
open DenseScalar

namespace ConditionalCriterion

universe u

/-- The actual supplied initialization graph is included in the construction. -/
def composedCircuit {I : Type} (r k : Nat) (initial : Circuit I (Inputs r)) :
    Circuit I Unit :=
  .comp initial (scalarCircuit r k)

theorem compose_input_correct {I : Type} (r k : Nat) {R : Type u} [Semiring R]
    (initial : Circuit I (Inputs r)) (inputs : I → R)
    (M : Matrix (Fin r) (Fin r) R) (u v : Fin r → R)
    (hinputs : initial.eval inputs = inputData r M u v) :
    (composedCircuit r k initial).eval inputs () =
      (∑ i, u i * (∑ j, (M^k) i j * v j)) ∧
    (composedCircuit r k initial).gates = initial.gates + (scalarCircuit r k).gates := by
  constructor
  · change (scalarCircuit r k).eval (initial.eval inputs) () = _
    rw [hinputs]
    exact scalar_compiler_correct r M u v k
  · rfl

/-- An actual polynomial with natural coefficients, with fixed c,d. -/
noncomputable def Pi (c d : Nat) : Polynomial Nat :=
  Polynomial.X^c + Polynomial.C 4 * Polynomial.X^(3*d+2) +
    Polynomial.C 3 * Polynomial.X^(2*d)

theorem Pi_eval (c d n : Nat) :
    (Pi c d).eval n = n^c + 4*n^(3*d+2) + 3*n^(2*d) := by
  simp [Pi]

theorem polynomial_composed_budget {I : Type} (r n c d S : Nat)
    (initial : Circuit I (Inputs r)) (hr : 1 ≤ r) (hn : 2 ≤ n)
    (hdim : r ≤ n^d) (hinit : initial.gates ≤ S) (hS : S ≤ n^c) :
    (composedCircuit r (n^n-1) initial).gates ≤ (Pi c d).eval n := by
  have hr3 : r^3 ≤ (n^d)^3 := Nat.pow_le_pow_left hdim 3
  have hterm3 : 4*r^3*n^2 ≤ 4*n^(3*d+2) := by
    calc
      _ ≤ 4*(n^d)^3*n^2 := Nat.mul_le_mul_right (n^2) (Nat.mul_le_mul_left 4 hr3)
      _ = 4*n^(3*d+2) := by
        rw [Nat.mul_assoc, ← Nat.pow_mul, ← Nat.pow_add, Nat.mul_comm d 3]
  have hr2 : r^2 ≤ n^(2*d) := by
    simpa only [← Nat.pow_mul, Nat.mul_comm d 2] using Nat.pow_le_pow_left hdim 2
  have hterm2 : 3*r^2 ≤ 3*n^(2*d) := Nat.mul_le_mul_left 3 hr2
  change initial.gates + (scalarCircuit r (n^n-1)).gates ≤ _
  calc
    _ ≤ S + (scalarCircuit r (n^n-1)).gates := Nat.add_le_add_right hinit _
    _ ≤ S + 4*r^3*n^2+3*r^2 := conditional_scalar_budget r n S hr hn
    _ ≤ n^c + 4*n^(3*d+2) + 3*n^(2*d) := Nat.add_le_add (Nat.add_le_add hS hterm3) hterm2
    _ = (Pi c d).eval n := (Pi_eval c d n).symm

/-- A conditional coefficient result: representation is an explicit argument. -/
theorem conditional_target_coefficient {I : Type} {R : Type u} [Semiring R]
    (r n c d S : Nat) (initial : Circuit I (Inputs r)) (inputs : I → R)
    (M : Matrix (Fin r) (Fin r) R) (u v : Fin r → R) (H : Polynomial R)
    (hr : 1 ≤ r) (hn : 2 ≤ n) (hdim : r ≤ n^d)
    (hinit : initial.gates ≤ S) (hS : S ≤ n^c)
    (hinputs : initial.eval inputs = inputData r M u v)
    (hrepresentation : H.coeff (n^n-1) = ∑ i, u i * (∑ j, (M^(n^n-1)) i j * v j)) :
    (composedCircuit r (n^n-1) initial).eval inputs () = H.coeff (n^n-1) ∧
      (composedCircuit r (n^n-1) initial).gates ≤ (Pi c d).eval n := by
  constructor
  · exact (compose_input_correct r (n^n-1) initial inputs M u v hinputs).1.trans
      hrepresentation.symm
  · exact polynomial_composed_budget r n c d S initial hr hn hdim hinit hS

#print axioms ConditionalCriterion.compose_input_correct
#print axioms ConditionalCriterion.Pi_eval
#print axioms ConditionalCriterion.polynomial_composed_budget
#print axioms ConditionalCriterion.conditional_target_coefficient

end ConditionalCriterion
