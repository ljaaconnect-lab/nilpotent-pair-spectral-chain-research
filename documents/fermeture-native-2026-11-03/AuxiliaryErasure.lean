import MatrixScalarCompiler

/-!
Explicit erasure of auxiliary inputs for the existing shared Circuit syntax.
The base semiring R is fixed in every independence and correctness statement.
The erasure circuit uses only wires and zero constants before the given circuit.
No coefficient-reading operation, quotient coordinate, or native independence
claim is introduced. Independence of a particular native output remains to prove.
For a tagged terminal representation (b, Omega), the intended scalar circuit
computes the coefficient b, not the homogeneous oriented representative H.
Support in the fixed module R * Omega alone does not imply AuxIndependent.
Formal markers require the appropriate coefficient semiring R; this file makes
no inference from equality of finite-field evaluations to a formal identity.
-/

open DenseScalar

namespace AuxiliaryErasure

universe u

def zeroAux {I X : Type} : Circuit I (Sum I X) :=
  .pair (.wire id) (.constant (fun _ => false))

def eraseAux {I X O : Type} (c : Circuit (Sum I X) O) : Circuit I O :=
  .comp zeroAux c

def AuxIndependent {I X O : Type} {R : Type u} [Semiring R]
    (c : Circuit (Sum I X) O) : Prop :=
  ∀ (a : I → R) (x y : X → R),
    c.eval (Sum.elim a x) = c.eval (Sum.elim a y)

theorem erase_correct {I X O : Type} {R : Type u} [Semiring R]
    (c : Circuit (Sum I X) O) (independent : AuxIndependent (R := R) c)
    (a : I → R) (x : X → R) :
    (eraseAux c).eval a = c.eval (Sum.elim a x) := by
  exact independent a (fun _ => 0) x

theorem erase_gates {I X O : Type} (c : Circuit (Sum I X) O) :
    (eraseAux c).gates = c.gates := by
  simp only [eraseAux, zeroAux, Circuit.gates, Nat.zero_add]

theorem erase_eval {I X O : Type} {R : Type u} [Semiring R]
    (c : Circuit (Sum I X) O) (a : I → R) :
    (eraseAux c).eval a = c.eval (Sum.elim a (fun _ => 0)) := by
  rfl

theorem independent_of_spec {I X O : Type} {R : Type u} [Semiring R]
    (c : Circuit (Sum I X) O) (target : (I → R) → O → R)
    (hspec : ∀ a x, c.eval (Sum.elim a x) = target a) :
    AuxIndependent (R := R) c := by
  exact fun a x y => (hspec a x).trans (hspec a y).symm

/-- The witness is eraseAux c, not an unspecified scalar reader. -/
theorem scalarization_sufficiency {I X O : Type} {R : Type u} [Semiring R]
    (c : Circuit (Sum I X) O) (target : (I → R) → O → R) (bound : ℕ)
    (hspec : ∀ a x, c.eval (Sum.elim a x) = target a) (hbudget : c.gates ≤ bound) :
    ∃ d : Circuit I O, (∀ a, d.eval a = target a) ∧ d.gates ≤ bound := by
  exact ⟨eraseAux c, fun a => hspec a (fun _ => 0), (erase_gates c).le.trans hbudget⟩

end AuxiliaryErasure

#print axioms AuxiliaryErasure.erase_correct
#print axioms AuxiliaryErasure.erase_gates
#print axioms AuxiliaryErasure.erase_eval
#print axioms AuxiliaryErasure.independent_of_spec
#print axioms AuxiliaryErasure.scalarization_sufficiency
