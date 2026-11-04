import Mathlib.Algebra.Polynomial.Coeff
import Mathlib.Algebra.Ring.Rat
import DeterminantBridge

namespace CollisionEncodingBridge

open scoped BigOperators
open CollisionDeterminantBridge

variable {R : Type} [CommRing R]

noncomputable section

def centralDegree (n : Nat) : Nat := n ^ n - 1

def pairFactor (n : Nat) : Polynomial R :=
  ∏ i : Fin n, ∏ l ∈ Finset.Ioi i,
    ((Polynomial.X : Polynomial R) ^ (n ^ i.val) - Polynomial.X ^ (n ^ l.val))

def Hhat (n : Nat) (b : Matrix (Fin n) (Fin n) R) : Polynomial R :=
  1 + Polynomial.X ^ (2 * centralDegree n) +
    (forwardMatrix b (baseLabels n)).det * pairFactor n

def address {n : Nat} (i j : Fin n) : Nat := 2 ^ (i.val * n + j.val)

def amplitude {n : Nat} (A : Matrix (Fin n) (Fin n) Rat) (i j : Fin n) : Rat :=
  1 + (A i j) ^ 2

def markedWeights {n : Nat} (A : Matrix (Fin n) (Fin n) Rat) :
    Matrix (Fin n) (Fin n) (Polynomial Rat) :=
  fun i j => Polynomial.C (amplitude A i j) * Polynomial.X ^ (address i j)

def markedPermanent {n : Nat} (A : Matrix (Fin n) (Fin n) Rat) : Polynomial Rat :=
  ∑ σ : Equiv.Perm (Fin n), Polynomial.C (∏ i, amplitude A i (σ i)) *
    Polynomial.X ^ (∑ i, address i (σ i))

def markedHhat {n : Nat} (A : Matrix (Fin n) (Fin n) Rat) : Polynomial (Polynomial Rat) :=
  Hhat n (markedWeights A)

theorem centralDegree_pos (n : Nat) (hn : 2 ≤ n) : 0 < centralDegree n := by
  exact Nat.sub_pos_of_lt (Nat.one_lt_pow
    (Nat.ne_of_gt (Nat.lt_of_lt_of_le Nat.zero_lt_two hn))
    (Nat.lt_of_lt_of_le (Nat.lt_succ_self 1) hn))

#print axioms CollisionEncodingBridge.centralDegree_pos

theorem padding_coefficient (K : Nat) (hK : 0 < K) (p : Polynomial R) :
    (1 + Polynomial.X ^ (2 * K) + p).coeff K = p.coeff K := by
  simp only [Polynomial.coeff_add, Polynomial.coeff_one, Polynomial.coeff_X_pow]
  simp [Nat.ne_of_gt hK, show K ≠ 2 * K from by omega]

#print axioms CollisionEncodingBridge.padding_coefficient

end
end CollisionEncodingBridge
