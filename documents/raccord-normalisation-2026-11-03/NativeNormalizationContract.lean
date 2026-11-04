import TerminalTaggedClosure
import Mathlib.Data.ZMod.Basic

/-!
Contract check for the existing homogeneous representative program.
The coefficient forms, product and linear spectral readout are retained.
The result concerns applying zero-substitution to these exact output wires;
it makes no impossibility claim about other scalar compilations.
-/

namespace NativeNormalizationContract

open scoped BigOperators

universe u v

def linearRow {R : Type u} [Semiring R] {N : ℕ}
    (c : Fin N → R) (reverse : Fin N → Fin N) (x : Fin N → R) : R :=
  ∑ r, c r * x (reverse r)

def orientedProduct {R : Type u} [CommSemiring R] {n N : ℕ}
    (c : Fin n → Fin N → R) (reverse : Fin N → Fin N)
    (x : Fin N → R) : R :=
  ∏ i, linearRow (c i) reverse x

def spectralOutput {R : Type u} [CommSemiring R] {n N : ℕ}
    (c : Fin n → Fin N → R) (reverse : Fin N → Fin N)
    (gamma : R) (phase : Fin N → R) (inverse : Fin N → Fin N → R)
    (x : Fin N → R) (k : Fin N) : R :=
  ∑ f, inverse k f * (phase f * (gamma * orientedProduct c reverse x))

theorem linear_row_zero {R : Type u} [Semiring R] {N : ℕ}
    (c : Fin N → R) (reverse : Fin N → Fin N) :
    linearRow c reverse (fun _ => 0) = 0 := by
  simp [linearRow]

theorem oriented_product_zero {R : Type u} [CommSemiring R] {n N : ℕ}
    (c : Fin n → Fin N → R) (reverse : Fin N → Fin N) (hn : 0 < n) :
    orientedProduct c reverse (fun _ => 0) = 0 := by
  exact Finset.prod_eq_zero (Finset.mem_univ (⟨0, hn⟩ : Fin n))
    (linear_row_zero (c ⟨0, hn⟩) reverse)

#print axioms linear_row_zero
#print axioms oriented_product_zero

theorem spectral_output_zero {R : Type u} [CommSemiring R] {n N : ℕ}
    (c : Fin n → Fin N → R) (reverse : Fin N → Fin N)
    (gamma : R) (phase : Fin N → R) (inverse : Fin N → Fin N → R)
    (hn : 0 < n) (k : Fin N) :
    spectralOutput c reverse gamma phase inverse (fun _ => 0) k = 0 := by
  simp only [spectralOutput, oriented_product_zero c reverse hn, mul_zero,
    Finset.sum_const_zero]

#print axioms spectral_output_zero

theorem tagged_spectral_zero {R : Type u} {A : Type v}
    [CommSemiring R] [Semiring A] {n N : ℕ}
    (sigma : R →+* A) (label : A)
    (c : Fin n → Fin N → R) (reverse : Fin N → Fin N)
    (gamma : R) (phase : Fin N → R) (inverse : Fin N → Fin N → R)
    (hn : 0 < n) (k : Fin N) :
    TerminalTaggedClosure.tag sigma label
      (spectralOutput c reverse gamma phase inverse (fun _ => 0) k) = 0 := by
  simp only [spectral_output_zero c reverse gamma phase inverse hn k,
    TerminalTaggedClosure.tag, map_zero, zero_mul]

#print axioms tagged_spectral_zero

/-- This is the same universal tag equation as `normalized` in
CertifiedScalarClosure, applied to the retained representative formula. -/
theorem representative_normalized_forces_zero {R : Type u} {A : Type v}
    [CommSemiring R] [Semiring A] {n N : ℕ}
    (sigma : R →+* A) (label : A)
    (c : Fin n → Fin N → R) (reverse : Fin N → Fin N)
    (gamma : R) (phase : Fin N → R) (inverse : Fin N → Fin N → R)
    (hn : 0 < n) (native : Fin N → A)
    (normalized : ∀ (x : Fin N → R) (k : Fin N),
      TerminalTaggedClosure.tag sigma label
        (spectralOutput c reverse gamma phase inverse x k) = native k)
    (k : Fin N) : native k = 0 := by
  exact (normalized (fun _ => 0) k).symm.trans
    (tagged_spectral_zero sigma label c reverse gamma phase inverse hn k)

#print axioms representative_normalized_forces_zero

/-- The contract also applies literally to selected wires of any existing
DenseScalar circuit. The zero hypothesis can be supplied by the formula above. -/
theorem circuit_normalized_forces_zero {R : Type u} {A : Type v}
    [Semiring R] [Semiring A] {P X J O : Type}
    (sigma : R →+* A) (label : A)
    (circuit : DenseScalar.Circuit (Sum P X) J) (select : O → J)
    (native : (P → R) → O → A)
    (at_zero : ∀ (a : P → R) (o : O),
      circuit.eval (Sum.elim a (fun _ => 0)) (select o) = 0)
    (normalized : ∀ (a : P → R) (x : X → R) (o : O),
      TerminalTaggedClosure.tag sigma label
        (circuit.eval (Sum.elim a x) (select o)) = native a o)
    (a : P → R) (o : O) : native a o = 0 := by
  simpa only [at_zero a o, TerminalTaggedClosure.tag, map_zero, zero_mul] using
    (normalized a (fun _ => 0) o).symm

#print axioms circuit_normalized_forces_zero

/-- Parameters Q=5, N=4, omega=2, N^{-1}=4 and a=0,z=1 give B=1.
The two-row normalized coefficient B00*B11+B01*B10 is nonzero. -/
theorem q5_witness_arithmetic :
    (3 : ZMod 5) * 2 = 1 ∧ (2 : ZMod 5) ≠ 0 ∧
    (2 : ZMod 5) ^ 4 = 1 ∧ (2 : ZMod 5) ^ 2 ≠ 1 ∧
    (4 : ZMod 5) * 4 = 1 ∧
    (1 + (0 : ZMod 5) ^ 2) * 1 ^ 1 = 1 ∧
    (1 + (0 : ZMod 5) ^ 2) * 1 ^ 2 = 1 ∧
    (1 + (0 : ZMod 5) ^ 2) * 1 ^ 4 = 1 ∧
    (1 + (0 : ZMod 5) ^ 2) * 1 ^ 8 = 1 ∧
    (1 : ZMod 5) * 1 + 1 * 1 = 2 := by
  decide

#print axioms q5_witness_arithmetic

theorem tag_two_left_inverse {A : Type v} [Semiring A]
    (sigma : ZMod 5 →+* A) (label : A) :
    label = sigma 3 * TerminalTaggedClosure.tag sigma label 2 := by
  rw [TerminalTaggedClosure.tag, ← mul_assoc, ← map_mul,
    q5_witness_arithmetic.1, map_one, one_mul]

#print axioms tag_two_left_inverse

theorem tag_two_ne_zero {A : Type v} [Semiring A]
    (sigma : ZMod 5 →+* A) (label : A) (nonzero : label ≠ 0) :
    TerminalTaggedClosure.tag sigma label 2 ≠ 0 := by
  exact fun h => nonzero ((tag_two_left_inverse sigma label).trans
    ((congrArg (fun value => sigma 3 * value) h).trans (mul_zero _)))

#print axioms tag_two_ne_zero

theorem nonzero_native_rejects_normalized {R : Type u} {A : Type v}
    [CommSemiring R] [Semiring A] {n N : ℕ}
    (sigma : R →+* A) (label : A)
    (c : Fin n → Fin N → R) (reverse : Fin N → Fin N)
    (gamma : R) (phase : Fin N → R) (inverse : Fin N → Fin N → R)
    (hn : 0 < n) (native : Fin N → A) (k : Fin N)
    (nonzero : native k ≠ 0) :
    ¬ (∀ (x : Fin N → R) (out : Fin N),
      TerminalTaggedClosure.tag sigma label
        (spectralOutput c reverse gamma phase inverse x out) = native out) := by
  exact fun normalized => nonzero (representative_normalized_forces_zero
    sigma label c reverse gamma phase inverse hn native normalized k)

#print axioms nonzero_native_rejects_normalized

end NativeNormalizationContract
