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
def Pi (c d : Nat) : Polynomial Nat :=
  Polynomial.X^c + Polynomial.C 4 * Polynomial.X^(3*d+2) +
    Polynomial.C 3 * Polynomial.X^(2*d)

theorem Pi_eval (c d n : Nat) :
    (Pi c d).eval n = n^c + 4*n^(3*d+2) + 3*n^(2*d) := by
  simp [Pi]

#print axioms ConditionalCriterion.compose_input_correct
#print axioms ConditionalCriterion.Pi_eval

end ConditionalCriterion
