import Std

namespace SharedBinaryPower

theorem central_exponent_log_bound (n : Nat) (hn : 2 ≤ n) :
    Nat.log2 (n ^ n - 1) ≤ n ^ 2 := by
  have hsmall : n ≤ 2 ^ n := Nat.le_of_lt (Nat.lt_pow_self (n := n) (a := 2) (by decide))
  have hbig : n ^ n ≤ 2 ^ (n * n) := by
    simpa [Nat.pow_mul] using Nat.pow_le_pow_left hsmall n
  grind only [Nat.log2_lt, Nat.pow_two, Nat.le_self_pow, Nat.pow_self_pos]

#print axioms SharedBinaryPower.central_exponent_log_bound

end SharedBinaryPower
