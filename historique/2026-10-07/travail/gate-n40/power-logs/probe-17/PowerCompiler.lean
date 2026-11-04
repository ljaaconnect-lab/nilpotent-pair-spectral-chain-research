import Std

namespace SharedBinaryPower

universe u

/-- Explicit arbitrary monoid laws; no commutativity is assumed. -/
structure MonoidData (α : Type u) where
  one : α
  mul : α → α → α
  assoc : ∀ x y z, mul (mul x y) z = mul x (mul y z)
  one_mul : ∀ x, mul one x = x
  mul_one : ∀ x, mul x one = x

def power {α : Type u} (M : MonoidData α) (a : α) : Nat → α
  | 0 => M.one
  | k + 1 => M.mul (power M a k) a

inductive Instruction where
  | square
  | multiplyBase
  deriving DecidableEq, Repr

def step {α : Type u} (M : MonoidData α) (a x : α) : Instruction → α
  | .square => M.mul x x
  | .multiplyBase => M.mul x a

def run {α : Type u} (M : MonoidData α) (a initial : α) (ops : List Instruction) : α :=
  ops.foldl (step M a) initial

theorem run_append {α : Type u} (M : MonoidData α) (a initial : α)
    (xs ys : List Instruction) :
    run M a initial (xs ++ ys) = run M a (run M a initial xs) ys :=
  List.foldl_append

#print axioms SharedBinaryPower.run_append

/-- One instruction means one shared multiplication node. -/
def binaryPlan (k : Nat) : List Instruction :=
  if h : k ≤ 1 then []
  else binaryPlan (k / 2) ++
    if k % 2 = 0 then [.square] else [.square, .multiplyBase]
termination_by k
decreasing_by exact Nat.div_lt_self (by omega) (by decide)

def compilePower {α : Type u} (M : MonoidData α) (a : α) (k : Nat) : α :=
  if k = 0 then M.one else run M a a (binaryPlan k)

theorem power_add {α : Type u} (M : MonoidData α) (a : α) (j k : Nat) :
    power M a (j + k) = M.mul (power M a j) (power M a k) := by
  exact Nat.rec (motive := fun k => power M a (j + k) = M.mul (power M a j) (power M a k))
    (M.mul_one (power M a j)).symm
    (fun k ih => Eq.trans (congrArg (fun x => M.mul x a) ih)
      (M.assoc (power M a j) (power M a k) a)) k

#print axioms SharedBinaryPower.power_add

theorem positive_plan_correct {α : Type u} (M : MonoidData α) (a : α)
    (k : Nat) (hk : 0 < k) : run M a a (binaryPlan k) = power M a k := by
  induction k using Nat.strongRecOn with
  | ind k ih =>
    by_cases hsmall : k ≤ 1
    · sorry
    · have hrec := ih (k / 2) (Nat.div_lt_self hk (by decide)) (by omega)
      rw [binaryPlan, dite_eq_right hsmall]
      rw [run_append, hrec]
      done

#print axioms SharedBinaryPower.positive_plan_correct

theorem central_exponent_log_bound (n : Nat) (hn : 2 ≤ n) :
    Nat.log2 (n ^ n - 1) ≤ n ^ 2 := by
  have hsmall : n ≤ 2 ^ n := Nat.le_of_lt (Nat.lt_pow_self (n := n) (a := 2) (by decide))
  have hbig : n ^ n ≤ 2 ^ (n * n) := by
    simpa [Nat.pow_mul] using Nat.pow_le_pow_left hsmall n
  have hnonzero : n ^ n - 1 ≠ 0 :=
    Nat.ne_of_gt (Nat.sub_pos_of_lt (Nat.lt_of_lt_of_le (by decide : 1 < 2)
      (Nat.le_trans hn (Nat.le_self_pow (by omega) n))))
  simpa [Nat.pow_two] using Nat.le_of_lt ((Nat.log2_lt hnonzero).2
    (Nat.lt_of_lt_of_le (Nat.sub_lt Nat.pow_self_pos (by decide)) hbig))

#print axioms SharedBinaryPower.central_exponent_log_bound

end SharedBinaryPower
