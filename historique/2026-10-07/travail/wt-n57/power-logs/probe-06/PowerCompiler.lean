import Std

namespace SharedBinaryPower

theorem central_exponent_log_bound (n : Nat) (hn : 2 ≤ n) :
    Nat.log2 (n ^ n - 1) ≤ n ^ 2 := by
  have hsmall : n ≤ 2 ^ n := Nat.le_of_lt (Nat.lt_pow_self (n := n) (a := 2) (by decide))
  have hbig : n ^ n ≤ 2 ^ (n * n) := by
    simpa [Nat.pow_mul] using Nat.pow_le_pow_left hsmall n
  have hnonzero : n ^ n - 1 ≠ 0 :=
    Nat.ne_of_gt (Nat.sub_pos_of_lt (Nat.lt_of_lt_of_le (by decide : 1 < 2)
      (Nat.le_trans hn (Nat.le_self_pow (by omega) n))))
  done

#print axioms SharedBinaryPower.central_exponent_log_bound

end SharedBinaryPower
