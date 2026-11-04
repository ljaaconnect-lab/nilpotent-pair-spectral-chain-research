import Mathlib.Data.Nat.Basic
import Mathlib.Tactic.Linarith

/-!
Arithmetic consequences of externally justified gate-count hypotheses.
These statements do not formalize the compiler, identify typed algebra
operations with scalar gates, or establish scalarization of oriented products.
The auxiliary Fourier representative retains its formal variables.
-/

namespace NativeCompositionBounds

theorem typed_with_spectral_bound (n N ell eps : ℕ)
    (hn : 1 ≤ n) (hN : N ≤ 2 * n) (hell : ell ≤ n) (heps : eps ≤ 1) :
    6 * n ^ 2 + n - 2 + eps + (2 * N * ell + 3 * N - 3) ≤ 17 * n ^ 2 := by
  have hbase : 2 ≤ 6 * n ^ 2 + n := by nlinarith
  nlinarith [Nat.sub_add_cancel hbase, Nat.mul_le_mul hN hell,
    Nat.mul_le_mul_left n hn, Nat.sub_le (2 * N * ell + 3 * N) 3]

theorem representative_with_spectral_bound (n N ell eps : ℕ)
    (hn : 1 ≤ n) (hN : N ≤ 2 * n) (hell : ell ≤ n) (heps : eps ≤ 1) :
    4 * n ^ 2 - 2 + 2 * n * N * ell + 3 * n * N + eps +
        (2 * N * ell + 3 * N - 3) ≤ 29 * n ^ 3 := by
  nlinarith [Nat.mul_le_mul_left (2 * n) (Nat.mul_le_mul hN hell),
    Nat.mul_le_mul_left (3 * n) hN, Nat.mul_le_mul hN hell,
    Nat.mul_le_mul_left (n * n) hn, Nat.mul_le_mul_left n hn,
    Nat.sub_le (4 * n ^ 2) 2, Nat.sub_le (2 * N * ell + 3 * N) 3]

theorem representative_preparation_bound (n N ell : ℕ)
    (hn : 1 ≤ n) (hN : N ≤ 2 * n) (hell : ell ≤ n) :
    4 * n ^ 2 - 2 + 2 * n * N * ell + 3 * n * N ≤ 18 * n ^ 3 := by
  nlinarith [Nat.mul_le_mul_left (2 * n) (Nat.mul_le_mul hN hell),
    Nat.mul_le_mul_left (3 * n) hN, Nat.mul_le_mul_left (n * n) hn,
    Nat.sub_le (4 * n ^ 2) 2]

theorem representative_routed_bound (n N ell eps : ℕ)
    (hn : 1 ≤ n) (hN : N ≤ 2 * n) (hell : ell ≤ n) (heps : eps ≤ 1) :
    4 * n ^ 2 - 2 + 2 * n * N * ell + 3 * n * N + eps ≤ 18 * n ^ 3 + 1 := by
  exact Nat.add_le_add (representative_preparation_bound n N ell hn hN hell) heps

theorem typed_routed_bound (n eps : ℕ) (hn : 1 ≤ n) (heps : eps ≤ 1) :
    6 * n ^ 2 + n - 2 + eps ≤ 7 * n ^ 2 := by
  have hbase : 2 ≤ 6 * n ^ 2 + n := by nlinarith
  nlinarith [Nat.sub_add_cancel hbase, Nat.mul_le_mul_left n hn]

end NativeCompositionBounds

#print axioms NativeCompositionBounds.typed_with_spectral_bound
#print axioms NativeCompositionBounds.representative_with_spectral_bound
#print axioms NativeCompositionBounds.representative_preparation_bound
#print axioms NativeCompositionBounds.representative_routed_bound
#print axioms NativeCompositionBounds.typed_routed_bound
