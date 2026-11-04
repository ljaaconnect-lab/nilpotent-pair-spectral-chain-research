import Mathlib.Algebra.Polynomial.Coeff
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import GeneralPairingRing

namespace CollisionDeterminantBridge

open scoped BigOperators

variable {R : Type} [CommRing R]

noncomputable section

def rho {n : Nat} (r : Matrix (Fin n) (Fin n) Nat)
    (σ : Equiv.Perm (Fin n)) : Nat := ∑ i, r i (σ i)

def centralIndex {n : Nat} (c : Fin n → Nat) : Nat := ∑ i, c i

def weight {n : Nat} (b : Matrix (Fin n) (Fin n) R)
    (σ : Equiv.Perm (Fin n)) : R := ∏ i, b i (σ i)

def signCoeff {n : Nat} (σ : Equiv.Perm (Fin n)) : R :=
  ((Equiv.Perm.sign σ : Int) : R)

def forwardMatrix {n : Nat} (b : Matrix (Fin n) (Fin n) R)
    (r : Matrix (Fin n) (Fin n) Nat) : Matrix (Fin n) (Fin n) (Polynomial R) :=
  fun i j => Polynomial.monomial (r i j) (b i j)

def reverseMatrix {n : Nat} (r : Matrix (Fin n) (Fin n) Nat)
    (c : Fin n → Nat) : Matrix (Fin n) (Fin n) (Polynomial R) :=
  fun i j => Polynomial.monomial (c i - r i j) 1

-- The hardest algebraic contraction is first proved for finite sums;
-- determinant expansion and permutation sign-square will discharge its hypotheses.
theorem central_sum_pairing {S : Type} [Fintype S] [DecidableEq S]
    (K : Nat) (label : S → Nat) (w e : S → R)
    (hinj : Function.Injective label) (hbound : ∀ s, label s ≤ K)
    (hsquare : ∀ s, e s * e s = 1) :
    ((∑ s, Polynomial.monomial (label s) (e s * w s)) *
      (∑ t, Polynomial.monomial (K - label t) (e t))).coeff K = ∑ s, w s := by
  classical
  rw [Finset.sum_mul]
  simp only [Finset.mul_sum, Polynomial.finsetSum_coeff,
    Polynomial.monomial_mul_monomial, Polynomial.coeff_monomial]
  simp only [show ∀ s t, label s + (K - label t) = K ↔ s = t from fun s t =>
      (GeneralCollisionPairingRing.central_label_iff K (label s) (label t) (hbound t)).trans
        ⟨fun h => hinj h, fun h => congrArg label h⟩,
    Finset.sum_ite_eq, Finset.mem_univ, ite_true]
  exact Finset.sum_congr rfl (fun s _ =>
    (mul_right_comm (e s) (w s) (e s)).trans
      ((congrArg (fun v : R => v * w s) (hsquare s)).trans (one_mul (w s))))

#print axioms CollisionDeterminantBridge.central_sum_pairing

end
end CollisionDeterminantBridge
