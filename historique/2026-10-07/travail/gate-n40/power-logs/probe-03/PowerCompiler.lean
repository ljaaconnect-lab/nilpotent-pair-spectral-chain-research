import Std

namespace SharedBinaryPower

theorem central_exponent_log_bound (n : Nat) (hn : 2 ≤ n) :
    Nat.log2 (n ^ n - 1) ≤ n ^ 2 := by
  have hsmall : n ≤ 2 ^ n := Nat.le_of_lt (Nat.lt_pow_self (n := n) (a := 2) (by decide))
  done

#print axioms SharedBinaryPower.central_exponent_log_bound

end SharedBinaryPower
