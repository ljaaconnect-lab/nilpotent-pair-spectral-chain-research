import MatrixScalarCompiler
import Mathlib.Tactic.LinearCombination
import Mathlib.Algebra.Algebra.Basic

/-!
Exact normalization for n = 2 and N = 4 in any commutative algebra.
The ambient ring may contain nilpotents.  The six displayed relations are
the four cyclic convolutions and the two padded inverse Fourier coordinates.
The scalar coefficient circuit is constructed explicitly below; no inverse
of an auxiliary coordinate is used.  No all-order complexity claim is made.
-/

namespace Fourier4Normalization

universe u v

variable {A : Type u} [CommRing A]

structure Relations (w c : A) (x : Fin 4 → A) : Prop where
  root : w ^ 2 = -1
  quarter : 4 * c = 1
  conv0 : x 0 ^ 2 + 2 * x 1 * x 3 + x 2 ^ 2 = 0
  conv1 : 2 * x 0 * x 1 + 2 * x 2 * x 3 = 0
  conv2 : 2 * x 0 * x 2 + x 1 ^ 2 + x 3 ^ 2 = 0
  conv3 : 2 * x 0 * x 3 + 2 * x 1 * x 2 = 0
  pad2 : x 0 - x 1 + x 2 - x 3 = 0
  pad3 : x 0 + w * x 1 - x 2 - w * x 3 = 0

def q0 (c : A) (x : Fin 4 → A) : A :=
  c * (x 0 + x 1 + x 2 + x 3)

def q1 (w c : A) (x : Fin 4 → A) : A :=
  c * (x 0 - w * x 1 - x 2 + w * x 3)

/-- The linearized row sum C_r x_{-r}, with C_r = (b0+b1*w^r)/4. -/
def row (w c b0 b1 : A) (x : Fin 4 → A) : A :=
  c * ((b0 + b1) * x 0 + (b0 + w * b1) * x 3 +
    (b0 - b1) * x 2 + (b0 - w * b1) * x 1)

theorem q0_square_zero {w c : A} {x : Fin 4 → A}
    (h : Relations w c x) : q0 c x ^ 2 = 0 := by
  dsimp [q0]
  linear_combination c ^ 2 * h.conv0 + c ^ 2 * h.conv1 +
    c ^ 2 * h.conv2 + c ^ 2 * h.conv3

theorem q1_square_zero {w c : A} {x : Fin 4 → A}
    (h : Relations w c x) : q1 w c x ^ 2 = 0 := by
  dsimp [q1]
  linear_combination c ^ 2 * h.conv0 - (w * c ^ 2) * h.conv1 -
    c ^ 2 * h.conv2 + (w * c ^ 2) * h.conv3 +
    (c ^ 2 * (x 1 - x 3) ^ 2) * h.root

theorem row_coordinates (w c b0 b1 : A) (x : Fin 4 → A) :
    row w c b0 b1 x = b0 * q0 c x + b1 * q1 w c x := by
  dsimp [row, q0, q1]
  ring

theorem normalized_product {w c : A} {x : Fin 4 → A}
    (h : Relations w c x) (b00 b01 b10 b11 : A) :
    row w c b00 b01 x * row w c b10 b11 x =
      (b00 * b11 + b01 * b10) * (q0 c x * q1 w c x) := by
  rw [row_coordinates, row_coordinates]
  linear_combination (b00 * b10) * (q0_square_zero h) +
    (b01 * b11) * (q1_square_zero h)

theorem padding_sum {w c : A} {x : Fin 4 → A}
    (h : Relations w c x) : q0 c x + q1 w c x = x 0 := by
  dsimp [q0, q1]
  linear_combination x 0 * h.quarter - c * h.pad2 - c * h.pad3

theorem terminal_label {w c : A} {x : Fin 4 → A}
    (h : Relations w c x) : x 0 ^ 2 = 2 * (q0 c x * q1 w c x) := by
  rw [← padding_sum h]
  linear_combination q0_square_zero h + q1_square_zero h

/-- Two multiplications and one addition, with the prepared B values as inputs. -/
def coefficientCircuit : DenseScalar.Circuit (Fin 4) Unit :=
  .comp (.pair (.mul 0 3) (.mul 1 2))
    (.add (Sum.inl ()) (Sum.inr ()))

theorem coefficient_circuit {R : Type v} [Semiring R] (b : Fin 4 → R) :
    coefficientCircuit.eval b () = b 0 * b 3 + b 1 * b 2 ∧
      coefficientCircuit.gates = 3 := by
  exact ⟨rfl, rfl⟩

/-- The coefficient is computed in R, while the oriented product lives in A.
    Input order is B00, B01, B10, B11. -/
theorem scalar_normalization {R : Type v} [CommRing R] [Algebra R A]
    {w c : A} {x : Fin 4 → A} (h : Relations w c x) (b : Fin 4 → R) :
    row w c (algebraMap R A (b 0)) (algebraMap R A (b 1)) x *
      row w c (algebraMap R A (b 2)) (algebraMap R A (b 3)) x =
      algebraMap R A (coefficientCircuit.eval b ()) * (q0 c x * q1 w c x) := by
  simpa only [(coefficient_circuit b).1, map_add, map_mul] using
    normalized_product h (algebraMap R A (b 0)) (algebraMap R A (b 1))
      (algebraMap R A (b 2)) (algebraMap R A (b 3))

#print axioms q0_square_zero
#print axioms q1_square_zero
#print axioms row_coordinates
#print axioms normalized_product
#print axioms padding_sum
#print axioms terminal_label
#print axioms coefficient_circuit
#print axioms scalar_normalization

end Fourier4Normalization
