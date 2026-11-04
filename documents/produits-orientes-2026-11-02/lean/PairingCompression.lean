import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.LinearAlgebra.FiniteDimensional.Defs
import Mathlib.Data.Matrix.Mul
import Mathlib.Data.Fintype.Powerset

set_option Elab.async false

/-!
# Exact linear compression of the coordinate pairing

These statements concern a supplied linear encoding and a supplied reader
which exactly reproduces the full coordinate pairing for every pair of inputs.
They do not formalize the oriented quotient, identify its products with this
pairing, or give a lower bound for arbitrary scalar arithmetic circuits.
The reader itself is not assumed linear or bilinear.
-/

namespace PairingCompression

variable {K : Type*} [Field K]
variable {ι : Type*} [Fintype ι]
variable {V : Type*} [AddCommGroup V] [Module K V]

/-- Exact recovery of every coordinate pairing forces the encoding to be injective. -/
theorem encoding_injective
    (E : (ι → K) →ₗ[K] V) (R : V → (ι → K) → K)
    (hR : ∀ x y, R (E x) y = ∑ i, x i * y i) :
    Function.Injective E := by
  intro x x' h
  exact letI : DecidableEq ι := Classical.decEq ι
    funext fun i =>
      (dotProduct_single_one x i).symm.trans
        ((hR x (Pi.single i 1)).symm.trans
          ((congrArg (fun w => R w (Pi.single i 1)) h).trans
            ((hR x' (Pi.single i 1)).trans (dotProduct_single_one x' i))))

/-- A finite-dimensional exact linear interface has at least one dimension per coordinate. -/
theorem card_le_finrank [FiniteDimensional K V]
    (E : (ι → K) →ₗ[K] V) (R : V → (ι → K) → K)
    (hR : ∀ x y, R (E x) y = ∑ i, x i * y i) :
    Fintype.card ι ≤ Module.finrank K V := by
  simpa only [Module.finrank_pi] using
    (LinearMap.finrank_le_finrank_of_injective (encoding_injective E R hR))

/-- Specialization to coordinates indexed by the k-element subsets of n labels.
This is a cardinality specialization, not a construction of the oriented quotient. -/
theorem choose_le_finrank [FiniteDimensional K V] (n k : ℕ)
    (E : ({S : Finset (Fin n) // S.card = k} → K) →ₗ[K] V)
    (R : V → ({S : Finset (Fin n) // S.card = k} → K) → K)
    (hR : ∀ x y, R (E x) y = ∑ i, x i * y i) :
    n.choose k ≤ Module.finrank K V := by
  simpa only [Fintype.card_finset_len, Fintype.card_fin] using card_le_finrank E R hR

end PairingCompression

#print axioms PairingCompression.encoding_injective
#print axioms PairingCompression.card_le_finrank
#print axioms PairingCompression.choose_le_finrank
