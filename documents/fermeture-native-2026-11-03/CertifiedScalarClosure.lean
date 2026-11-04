import SharedStateClosure
import TerminalTaggedClosure
import SharedCostInduction

/-!
End-to-end closure for a shared chain whose selected coefficient wires carry
an explicit terminal normalization certificate. The scalar reader is built
from wire selection and zero substitution and has exactly the chain budget.
The normalization certificate is not proved for arbitrary oriented products.
The native output is a logical specification, never an input of the program.
-/

open DenseScalar SharedStateClosure

namespace CertifiedScalarClosure

universe u v

def coefficientView {P X J O : Type} (chain : SharedChain (Sum P X) J)
    (select : O → J) : Circuit (Sum P X) O :=
  .comp chain.compile (.wire select)

def reader {P X J O : Type} (chain : SharedChain (Sum P X) J)
    (select : O → J) : Circuit P O :=
  AuxiliaryErasure.eraseAux (coefficientView chain select)

theorem reader_gates {P X J O : Type} (chain : SharedChain (Sum P X) J)
    (select : O → J) :
    (reader chain select).gates = chain.gateBudget := by
  simp only [reader, AuxiliaryErasure.erase_gates, coefficientView,
    Circuit.gates, shared_chain_gates, Nat.add_zero]

theorem reader_tagged_correct {R : Type u} {A : Type v}
    [Semiring R] [Semiring A] {P X J O : Type}
    (chain : SharedChain (Sum P X) J) (select : O → J)
    (sigma : R →+* A) (label : A) (native : (P → R) → O → A)
    (normalized : ∀ (a : P → R) (x : X → R) (o : O),
      TerminalTaggedClosure.tag sigma label
        (chain.eval (Sum.elim a x) (select o)) = native a o)
    (a : P → R) (o : O) :
    TerminalTaggedClosure.tag sigma label ((reader chain select).eval a o) =
      native a o := by
  exact (congrArg
    (fun values => TerminalTaggedClosure.tag sigma label (values (select o)))
    (shared_chain_eval chain (Sum.elim a (fun _ => 0)))).trans
      (normalized a (fun _ => 0) o)

theorem certified_scalar_closure {R : Type u} {A : Type v}
    [Semiring R] [Semiring A] {P X J O : Type}
    (chain : SharedChain (Sum P X) J) (select : O → J)
    (sigma : R →+* A) (label : A) (native : (P → R) → O → A)
    (bound : ℕ)
    (normalized : ∀ (a : P → R) (x : X → R) (o : O),
      TerminalTaggedClosure.tag sigma label
        (chain.eval (Sum.elim a x) (select o)) = native a o)
    (budget : chain.gateBudget ≤ bound) :
    ∃ d : Circuit P O,
      (∀ (a : P → R) (o : O),
        TerminalTaggedClosure.tag sigma label (d.eval a o) = native a o) ∧
      d.gates ≤ bound := by
  exact ⟨reader chain select,
    fun a o => reader_tagged_correct chain select sigma label native normalized a o,
    (reader_gates chain select).le.trans budget⟩

/-- The constants are fixed before the input size is quantified.
The native normalization and the scalar increments remain explicit obligations. -/
theorem certified_polynomial_family {R : Type u} {Alg : Type v}
    [Semiring R] [Semiring Alg] (P X J O : ℕ → Type)
    (chain : ∀ n, SharedChain (Sum (P n) (X n)) (J n))
    (select : ∀ n, O n → J n)
    (sigma : R →+* Alg) (label : ℕ → Alg)
    (native : ∀ n, (P n → R) → O n → Alg)
    (S : ℕ → ℕ → ℕ) (steps : ℕ → ℕ) (K0 Klen K a b c : ℕ)
    (normalized : ∀ n, 1 ≤ n → ∀ (input : P n → R) (x : X n → R) (o : O n),
      TerminalTaggedClosure.tag sigma (label n)
        ((chain n).eval (Sum.elim input x) (select n o)) = native n input o)
    (cost_at_end : ∀ n, 1 ≤ n → (chain n).gateBudget ≤ S n (steps n))
    (hinit : ∀ n, 1 ≤ n → S n 0 ≤ K0 * n ^ a)
    (hlength : ∀ n, 1 ≤ n → steps n ≤ Klen * n ^ b)
    (hstep : ∀ n, 1 ≤ n → ∀ i < steps n,
      S n (i + 1) ≤ S n i + K * n ^ c) :
    ∀ n, 1 ≤ n → ∃ d : Circuit (P n) (O n),
      (∀ (input : P n → R) (o : O n),
        TerminalTaggedClosure.tag sigma (label n) (d.eval input o) = native n input o) ∧
      d.gates ≤ (K0 + Klen * K) * n ^ (max a (b + c)) := by
  exact fun n hn => certified_scalar_closure (chain n) (select n) sigma (label n)
    (native n) ((K0 + Klen * K) * n ^ (max a (b + c))) (normalized n hn)
    ((cost_at_end n hn).trans
      (SharedCostInduction.polynomial_family_bound S steps K0 Klen K a b c
        hinit hlength hstep n hn))

end CertifiedScalarClosure

#print axioms CertifiedScalarClosure.reader_gates
#print axioms CertifiedScalarClosure.reader_tagged_correct
#print axioms CertifiedScalarClosure.certified_scalar_closure
#print axioms CertifiedScalarClosure.certified_polynomial_family
