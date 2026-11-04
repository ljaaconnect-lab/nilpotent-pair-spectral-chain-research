import MatrixScalarCompiler

/-!
The same finite-input preparation circuit feeds every row form. The prefix
program appends only multiplication gates and wire references. Its scalar
interpretation retains the formal orientation coordinates. A ring homomorphism
is used exclusively to prove quotient semantics; it is not a circuit gate.
The construction and cost of the initial preparation are external parameters.
-/

open DenseScalar

namespace NativePrefixInduction

universe u v

def prefixValue {R : Type u} [Monoid R] (ell : ℕ → R) : ℕ → R
  | 0 => 1
  | k + 1 => prefixValue ell k * ell k

/-- Only the first k row references are used. They share the same input bundle. -/
def prefixCircuit {J : Type} (row : ℕ → J) : ℕ → Circuit J Unit
  | 0 => .constant (fun _ => true)
  | 1 => .wire (fun _ => row 0)
  | k + 2 => .comp
      (.pair (prefixCircuit row (k + 1)) (.wire (fun _ => row (k + 1))))
      (.mul (Sum.inl ()) (Sum.inr ()))

def composedPrefix {I J : Type} (prepare : Circuit I J) (row : ℕ → J) (n : ℕ) :
    Circuit I Unit :=
  .comp prepare (prefixCircuit row n)

theorem prefix_circuit_eval {J : Type} {R : Type u} [Semiring R]
    (row : ℕ → J) (inputs : J → R) (n : ℕ) :
    (prefixCircuit row n).eval inputs () = prefixValue (fun i => inputs (row i)) n := by
  exact Nat.twoStepInduction rfl (one_mul (inputs (row 0))).symm
    (fun k _ ih => congrArg (fun value => value * inputs (row (k + 1))) ih) n

theorem prefix_circuit_gates {J : Type} (row : ℕ → J) (n : ℕ) :
    (prefixCircuit row n).gates = n - 1 := by
  exact Nat.twoStepInduction rfl rfl
    (fun _ _ ih => congrArg (fun value => value + 1) ih) n

theorem map_prefix {R : Type u} {A : Type v} [Semiring R] [Semiring A]
    (rho : R →+* A) (ell : ℕ → R) (n : ℕ) :
    rho (prefixValue ell n) = prefixValue (fun i => rho (ell i)) n := by
  exact Nat.rec rho.map_one
    (fun k ih => (rho.map_mul _ _).trans
      (congrArg (fun value => value * rho (ell k)) ih)) n

theorem composed_prefix_eval {I J : Type} {R : Type u} [Semiring R]
    (prepare : Circuit I J) (row : ℕ → J) (inputs : I → R) (n : ℕ) :
    (composedPrefix prepare row n).eval inputs () =
      prefixValue (fun i => prepare.eval inputs (row i)) n := by
  exact prefix_circuit_eval row (prepare.eval inputs) n

theorem composed_prefix_gates {I J : Type}
    (prepare : Circuit I J) (row : ℕ → J) (n : ℕ) :
    (composedPrefix prepare row n).gates = prepare.gates + (n - 1) := by
  exact congrArg (fun value => prepare.gates + value) (prefix_circuit_gates row n)

/-- Actual program semantics and gate count, with quotient interpretation separate. -/
theorem native_prefix_compilation {I J : Type} {R : Type u} {A : Type v}
    [Semiring R] [Semiring A] (prepare : Circuit I J) (row : ℕ → J)
    (inputs : I → R) (rho : R →+* A) (n : ℕ) :
    rho ((composedPrefix prepare row n).eval inputs ()) =
        prefixValue (fun i => rho (prepare.eval inputs (row i))) n ∧
      (composedPrefix prepare row n).gates = prepare.gates + (n - 1) := by
  exact ⟨(congrArg rho (composed_prefix_eval prepare row inputs n)).trans
    (map_prefix rho (fun i => prepare.eval inputs (row i)) n),
    composed_prefix_gates prepare row n⟩

end NativePrefixInduction

#print axioms NativePrefixInduction.prefix_circuit_eval
#print axioms NativePrefixInduction.prefix_circuit_gates
#print axioms NativePrefixInduction.map_prefix
#print axioms NativePrefixInduction.composed_prefix_eval
#print axioms NativePrefixInduction.composed_prefix_gates
#print axioms NativePrefixInduction.native_prefix_compilation
