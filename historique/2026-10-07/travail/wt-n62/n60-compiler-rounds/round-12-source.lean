import Mathlib.Algebra.Polynomial.Coeff
import Mathlib.Algebra.Ring.Rat
import DeterminantBridge
import ReverseVandermonde

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

theorem marked_weight_eq {n : Nat} (A : Matrix (Fin n) (Fin n) Rat)
    (σ : Equiv.Perm (Fin n)) :
    weight (markedWeights A) σ = Polynomial.C (∏ i, amplitude A i (σ i)) *
      Polynomial.X ^ (∑ i, address i (σ i)) := by
  simpa only [weight, markedWeights, Polynomial.C_mul_X_pow_eq_monomial] using
    prod_monomials (R := Rat) (Finset.univ : Finset (Fin n))
      (fun i => address i (σ i)) (fun i => amplitude A i (σ i))

#print axioms CollisionEncodingBridge.marked_weight_eq

theorem padded_determinant_coefficient (n : Nat) (hn : 2 ≤ n)
    (b : Matrix (Fin n) (Fin n) R) :
    (1 + Polynomial.X ^ (2 * centralDegree n) +
      (forwardMatrix b (baseLabels n)).det *
        (reverseMatrix (R := R) (baseLabels n) (baseCaps n)).det).coeff (centralDegree n) =
      ∑ σ : Equiv.Perm (Fin n), weight b σ := by
  exact (padding_coefficient (centralDegree n) (centralDegree_pos n hn)
    ((forwardMatrix b (baseLabels n)).det *
      (reverseMatrix (R := R) (baseLabels n) (baseCaps n)).det)).trans
    (base_n_determinant_pairing n (Nat.lt_of_lt_of_le Nat.zero_lt_two hn) b)

#print axioms CollisionEncodingBridge.padded_determinant_coefficient

theorem reverse_factor (n : Nat) :
    (reverseMatrix (R := R) (baseLabels n) (baseCaps n)).det = pairFactor n := by
  simpa only [reverseMatrix, baseLabels, baseCaps, pairFactor] using
    (ReverseVandermonde.paper_monomial_det (R := R) (n := n))

#print axioms CollisionEncodingBridge.reverse_factor

end
end CollisionEncodingBridge
