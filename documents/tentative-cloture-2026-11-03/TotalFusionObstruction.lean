import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

/-!
A concrete obstruction to replacing a product of two transport differences
by a reader of the sum of their parameters alone. Every counterexample row
has the native form (1+a^2, 1+b^2), at z=1, in ZMod 97.
This does not exclude a reader retaining further data, another shared circuit,
or a polynomial scalar implementation of the full oriented architecture.
-/

namespace TotalFusionObstruction

abbrev K := ZMod 97
abbrev Vec := K × K

def D (p : Vec) : K := p.1 * p.2

def delta (u v : Vec) : K := D (u + v) - D u - D v + D 0

def nativeRow (a b : K) : Vec := (1 + a ^ 2, 1 + b ^ 2)

def u : Vec := (1, 5)
def v : Vec := (5, 1)
def u' : Vec := (3, 3)
def v' : Vec := (3, 3)

theorem delta_bilinear (p q : Vec) :
    delta p q = p.1 * q.2 + p.2 * q.1 := by
  dsimp [delta, D]
  ring

theorem native_examples :
    nativeRow 0 2 = u ∧ nativeRow 2 0 = v ∧
    nativeRow 14 14 = u' ∧ nativeRow 14 14 = v' := by
  decide

theorem equal_parameter_sum : u + v = u' + v' ∧ u + v = (6, 6) := by
  decide

theorem delta_values : delta u v = 26 ∧ delta u' v' = 18 := by
  decide

/-- Only the two concrete native pairs are needed to refute a sum-only reader. -/
theorem no_reader_of_sum :
    ¬ ∃ reader : Vec → K,
      delta u v = reader (u + v) ∧ delta u' v' = reader (u' + v') := by
  rintro ⟨reader, hleft, hright⟩
  exact (of_decide_eq_true rfl : (26 : K) ≠ 18)
    (delta_values.1.symm.trans (hleft.trans
      ((congrArg reader equal_parameter_sum.1).trans (hright.symm.trans delta_values.2))))

end TotalFusionObstruction

#print axioms TotalFusionObstruction.delta_bilinear
#print axioms TotalFusionObstruction.native_examples
#print axioms TotalFusionObstruction.equal_parameter_sum
#print axioms TotalFusionObstruction.delta_values
#print axioms TotalFusionObstruction.no_reader_of_sum
