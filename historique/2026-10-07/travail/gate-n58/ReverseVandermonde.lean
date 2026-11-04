import Mathlib.LinearAlgebra.Vandermonde

namespace ReverseVandermonde

set_option maxHeartbeats 50000

variable {R : Type*} [CommRing R] {n : ℕ}

-- Hardest fixed target first; the projective determinant keeps orientation exact.
theorem reverse_vandermonde (v : Fin n → R) :
    (Matrix.of fun i j : Fin n => (v i) ^ (n - 1 - j.val)).det =
      ∏ i : Fin n, ∏ l ∈ Finset.Ioi i, (v i - v l) := by
  simpa only [Matrix.projVandermonde, Matrix.rectVandermonde,
    one_pow, one_mul, mul_one, Fin.val_rev, Nat.sub_sub, Nat.add_comm]
    using Matrix.det_projVandermonde (fun _ : Fin n => 1) v

theorem reverse_matrix_as_projective (v : Fin n → R) :
    (Matrix.of fun i j : Fin n => (v i) ^ (n - 1 - j.val)) =
      Matrix.projVandermonde (fun _ : Fin n => 1) v := by
  simp only [Matrix.projVandermonde, Matrix.rectVandermonde,
    one_pow, one_mul, Fin.val_rev, Nat.sub_sub, Nat.add_comm]

theorem power_entries (t : Polynomial R) (i j : Fin n) :
    (t ^ (n ^ i.val)) ^ (n - 1 - j.val) =
      t ^ ((n ^ i.val) * (n - 1 - j.val)) := by
  exact (pow_mul t (n ^ i.val) (n - 1 - j.val)).symm

theorem reverse_vandermonde_polynomial (t : Polynomial R) :
    (Matrix.of fun i j : Fin n => t ^ ((n ^ i.val) * (n - 1 - j.val))).det =
      ∏ i : Fin n, ∏ l ∈ Finset.Ioi i, (t ^ (n ^ i.val) - t ^ (n ^ l.val)) := by
  simpa only [← pow_mul] using
    (reverse_vandermonde (R := Polynomial R) (fun i : Fin n => t ^ (n ^ i.val)))

theorem complementary_exponent (n i j : ℕ) :
    (n - 1) * n ^ i - j * n ^ i = n ^ i * (n - 1 - j) := by
  rw [← Nat.mul_sub_right_distrib, Nat.mul_comm]

theorem paper_complementary_det (t : Polynomial R) :
    (Matrix.of fun i j : Fin n =>
      t ^ ((n - 1) * n ^ i.val - j.val * n ^ i.val)).det =
      ∏ i : Fin n, ∏ l ∈ Finset.Ioi i, (t ^ (n ^ i.val) - t ^ (n ^ l.val)) := by
  simpa only [complementary_exponent] using
    (reverse_vandermonde_polynomial (n := n) t)

-- Requested interface bridges are outside the frozen score denominator.
theorem unit_monomial_pow (m : ℕ) :
    Polynomial.monomial m (1 : R) = (Polynomial.X : Polynomial R) ^ m := by
  exact Polynomial.monomial_one_right_eq_X_pow m

theorem paper_monomial_matrix_eq :
    (fun i j : Fin n => Polynomial.monomial
      ((n - 1) * n ^ i.val - j.val * n ^ i.val) (1 : R)) =
    (Matrix.of fun i j : Fin n =>
      (Polynomial.X : Polynomial R) ^ ((n ^ i.val) * (n - 1 - j.val))) := by
  simp only [unit_monomial_pow, complementary_exponent]
  rfl

theorem paper_monomial_det :
    Matrix.det (fun i j : Fin n => Polynomial.monomial
      ((n - 1) * n ^ i.val - j.val * n ^ i.val) (1 : R)) =
      ∏ i : Fin n, ∏ l ∈ Finset.Ioi i,
        ((Polynomial.X : Polynomial R) ^ (n ^ i.val) - Polynomial.X ^ (n ^ l.val)) := by
  simpa only [paper_monomial_matrix_eq] using
    (reverse_vandermonde_polynomial (n := n) (Polynomial.X : Polynomial R))

end ReverseVandermonde

#print axioms ReverseVandermonde.reverse_vandermonde
#print axioms ReverseVandermonde.reverse_matrix_as_projective
#print axioms ReverseVandermonde.power_entries
#print axioms ReverseVandermonde.reverse_vandermonde_polynomial
#print axioms ReverseVandermonde.complementary_exponent
#print axioms ReverseVandermonde.paper_complementary_det
#print axioms ReverseVandermonde.unit_monomial_pow
#print axioms ReverseVandermonde.paper_monomial_matrix_eq
#print axioms ReverseVandermonde.paper_monomial_det
