import Std

namespace CollisionCoreBridge

def encodeDigits (n : Nat) : List (Fin n) → Nat
  | [] => 0
  | d :: ds => d.val + n * encodeDigits n ds

theorem decode_head (n : Nat) (d : Fin n) (ds : List (Fin n)) :
    encodeDigits n (d :: ds) % n = d.val := by
  simp [encodeDigits, Nat.mod_eq_of_lt d.isLt]

#print axioms CollisionCoreBridge.decode_head

theorem decode_tail (n : Nat) (hn : 0 < n) (d : Fin n) (ds : List (Fin n)) :
    encodeDigits n (d :: ds) / n = encodeDigits n ds := by
  simp [encodeDigits, Nat.add_mul_div_left _ _ hn, Nat.div_eq_of_lt d.isLt]

#print axioms CollisionCoreBridge.decode_tail

theorem encodeDigits_injective (n : Nat) (hn : 0 < n) (xs ys : List (Fin n))
    (hlen : xs.length = ys.length) (henc : encodeDigits n xs = encodeDigits n ys) :
    xs = ys := by
  induction xs generalizing ys
  all_goals cases ys
  all_goals grind [List.length, decode_head, decode_tail]
  done

#print axioms CollisionCoreBridge.encodeDigits_injective

theorem central_label_iff (K r s : Nat) (hs : s ≤ K) :
    r + (K - s) = K ↔ r = s := by
  omega

#print axioms CollisionCoreBridge.central_label_iff

def orbit {T : Type} (step : T → T) (x : T) : Nat → T
  | 0 => x
  | k + 1 => step (orbit step x k)

theorem orbit_stabilizes {T : Type} (step : T → T) (x : T) (n : Nat)
    (hfix : orbit step x (n + 1) = orbit step x n) (m : Nat) :
    orbit step x (n + m) = orbit step x n := by
  induction m
  all_goals simp_all [orbit]
  done

#print axioms CollisionCoreBridge.orbit_stabilizes

theorem n2_pair_factorization {R : Type} [Lean.Grind.CommRing R] (a b t : R) :
    (a * t ^ 2 - b * t) * (t - t ^ 2) =
      -b * t ^ 2 + (a + b) * t ^ 3 - a * t ^ 4 := by
  grind

#print axioms CollisionCoreBridge.n2_pair_factorization

def listCoeff (p : List Rat) (k : Nat) : Rat := (p[k]?).getD 0

def convolutionCoeff (p q : List Rat) (k : Nat) : Rat :=
  ((List.range (k + 1)).map
    (fun i => listCoeff p i * listCoeff q (k - i))).foldr (· + ·) 0

theorem n2_central_convolution (a b : Rat) :
    convolutionCoeff [0, -b, a] [0, 1, -1] 3 = a + b := by
  simp [convolutionCoeff, listCoeff, List.range_succ]
  grind
  done

#print axioms CollisionCoreBridge.n2_central_convolution

end CollisionCoreBridge
