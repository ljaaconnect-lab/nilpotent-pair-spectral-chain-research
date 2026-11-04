import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Data.Fintype.BigOperators
import AuxiliaryErasure

/-!
The scalar coefficient and its fixed terminal orientation label are separate.
The tag is a semantic map, never a scalar primitive or a supplied answer.
These lemmas construct the closure laws for represented terminal coefficients.
They do not construct a coefficient circuit from an arbitrary oriented prefix.
-/

namespace TerminalTaggedClosure

open scoped BigOperators

variable {R A I J : Type*} [Semiring R] [Semiring A]

def tag (sigma : R →+* A) (label : A) (value : R) : A := sigma value * label

theorem tag_add (sigma : R →+* A) (label : A) (u v : R) :
    tag sigma label (u + v) = tag sigma label u + tag sigma label v := by
  simp only [tag, map_add, add_mul]

theorem tag_scalar_mul (sigma : R →+* A) (label : A) (r u : R) :
    tag sigma label (r * u) = sigma r * tag sigma label u := by
  simp only [tag, map_mul, mul_assoc]

theorem tag_linear_readout [Fintype I] (sigma : R →+* A) (label : A)
    (coeff : J → I → R) (value : I → R) (k : J) :
    tag sigma label (∑ f, coeff k f * value f) =
      ∑ f, sigma (coeff k f) * tag sigma label (value f) := by
  simp only [tag, map_sum, map_mul, Finset.sum_mul, mul_assoc]

theorem tagged_scalar_closure {P X O : Type}
    (sigma : R →+* A) (label : A)
    (faithful : Function.Injective (tag sigma label))
    (c : DenseScalar.Circuit (Sum P X) O)
    (target : (P → R) → O → R) (bound : ℕ)
    (normalized : ∀ a x o,
      tag sigma label (c.eval (Sum.elim a x) o) = tag sigma label (target a o))
    (budget : c.gates ≤ bound) :
    ∃ d : DenseScalar.Circuit P O,
      (∀ a, d.eval a = target a) ∧ d.gates ≤ bound := by
  exact AuxiliaryErasure.scalarization_sufficiency c target bound
    (fun a x => funext (fun o => faithful (normalized a x o))) budget

theorem native_tagged_readout {P X O : Type}
    (sigma : R →+* A) (label : A)
    (c : DenseScalar.Circuit (Sum P X) O)
    (native : (P → R) → O → A) (bound : ℕ)
    (normalized : ∀ a x o,
      tag sigma label (c.eval (Sum.elim a x) o) = native a o)
    (budget : c.gates ≤ bound) :
    ∃ d : DenseScalar.Circuit P O,
      (∀ a o, tag sigma label (d.eval a o) = native a o) ∧ d.gates ≤ bound := by
  exact ⟨AuxiliaryErasure.eraseAux c,
    fun a o => normalized a (fun _ => 0) o,
    (AuxiliaryErasure.erase_gates c).le.trans budget⟩

end TerminalTaggedClosure

#print axioms TerminalTaggedClosure.tag_add
#print axioms TerminalTaggedClosure.tag_scalar_mul
#print axioms TerminalTaggedClosure.tag_linear_readout
#print axioms TerminalTaggedClosure.tagged_scalar_closure
#print axioms TerminalTaggedClosure.native_tagged_readout
