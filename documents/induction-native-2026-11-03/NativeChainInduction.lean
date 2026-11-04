import NativePrefixInduction
import Mathlib.Tactic.Linarith

/-!
A shared preparation, the actual row-product prefix, and a terminal circuit.
The preparation is composed once; later gates reuse its output references.
Its bundle may contain row forms and supplied spectral constants. The entire
bundle is passed to the suffix by wires, without reconstructing the preparation.
Semantics and gate count are proved for this Circuit program itself.
The bounds and admissible input provenance of both blocks remain hypotheses.
Interpreting the program in a quotient does not eliminate formal auxiliary
variables or scalarize arbitrary oriented products over the base field.
-/

open DenseScalar NativePrefixInduction

namespace NativeChainInduction

universe u

def chain {I J O : Type} (prepare : Circuit I J) (row : ℕ → J) (n : ℕ)
    (suffix : Circuit (Sum Unit J) O) : Circuit I O :=
  .comp prepare (.comp (.pair (prefixCircuit row n) (.wire id)) suffix)

theorem chain_eval {I J O : Type} {R : Type u} [Semiring R]
    (prepare : Circuit I J) (row : ℕ → J) (n : ℕ)
    (suffix : Circuit (Sum Unit J) O) (inputs : I → R) :
    (chain prepare row n suffix).eval inputs =
      suffix.eval (Sum.elim
        (fun _ => prefixValue (fun i => prepare.eval inputs (row i)) n)
        (prepare.eval inputs)) := by
  exact congrArg suffix.eval
    (funext (fun
      | .inl () => prefix_circuit_eval row (prepare.eval inputs) n
      | .inr _ => rfl))

theorem chain_gates {I J O : Type}
    (prepare : Circuit I J) (row : ℕ → J) (n : ℕ)
    (suffix : Circuit (Sum Unit J) O) :
    (chain prepare row n suffix).gates = prepare.gates + (n - 1) + suffix.gates := by
  simp only [chain, Circuit.gates, prefix_circuit_gates, Nat.add_zero, Nat.add_assoc]

/-- A bound on the actual composed program, conditional on its two supplied blocks. -/
theorem chain_polynomial_gate_bound {I J O : Type}
    (prepare : Circuit I J) (row : ℕ → J) (n N ell eps : ℕ)
    (suffix : Circuit (Sum Unit J) O)
    (hn : 1 ≤ n) (hN : N ≤ 2 * n) (hell : ell ≤ n) (heps : eps ≤ 1)
    (hprepare : prepare.gates ≤ 4 * n ^ 2 + 2 * n * N * ell + 3 * n * N)
    (hsuffix : suffix.gates ≤ eps + (2 * N * ell + 3 * N - 3)) :
    (chain prepare row n suffix).gates ≤ 29 * n ^ 3 := by
  nlinarith [chain_gates prepare row n suffix,
    Nat.mul_le_mul_left (2 * n) (Nat.mul_le_mul hN hell),
    Nat.mul_le_mul_left (3 * n) hN, Nat.mul_le_mul hN hell,
    Nat.mul_le_mul_left (n * n) hn, Nat.mul_le_mul_left n hn,
    Nat.sub_le n 1, Nat.sub_le (2 * N * ell + 3 * N) 3]

end NativeChainInduction

#print axioms NativeChainInduction.chain_eval
#print axioms NativeChainInduction.chain_gates
#print axioms NativeChainInduction.chain_polynomial_gate_bound
