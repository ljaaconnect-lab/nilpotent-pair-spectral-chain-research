import Std

set_option Elab.async false
set_option maxRecDepth 8192
set_option maxHeartbeats 10000000

/-!
Integer certificates in the free additive space of equality partitions.
There is no numerical matrix specialization in these checks.
`native_decide` is deliberately not used.
-/

namespace OrientedOperators.PartitionCertificate

universe u

abbrev Pattern := List Nat
abbrev Poly := List (Pattern × Int)

def factorial : Nat → Nat
  | 0 => 1
  | n + 1 => (n + 1) * factorial n

def choose : Nat → Nat → Nat
  | _, 0 => 1
  | 0, _ + 1 => 0
  | n + 1, k + 1 => choose n k + choose n (k + 1)

def canonicalAux : Pattern → Pattern → Pattern
  | [], _ => []
  | x :: xs, seen =>
    seen.idxOf x :: canonicalAux xs (if seen.contains x then seen else seen ++ [x])

def canonical (w : Pattern) : Pattern := canonicalAux w []

def arity (w : Pattern) : Nat := w.foldl (fun m j => max m (j + 1)) 0

def scale (c : Int) (p : Poly) : Poly := p.map fun (w, a) => (w, c * a)

def multiply (p q : Poly) : Poly := p.flatMap fun (u, a) =>
  q.map fun (v, b) => (canonical (u ++ v.map (· + arity u)), a * b)

def moment (k : Nat) (p : Poly) : Poly := p.flatMap fun (w, c) =>
  (List.range (k + 1)).map fun a =>
    (canonical (List.replicate a (arity w) ++ w ++
      List.replicate (k - a) (arity w)), c * (choose k a : Int))

def partitions : Nat → List Pattern
  | 0 => [[]]
  | r + 1 => (partitions r).flatMap fun w =>
      (List.range (arity w + 1)).map fun j => w ++ [j]

def blockSize (w : Pattern) (j : Nat) : Nat := (w.filter (· == j)).length

def mobius (w : Pattern) : Int := ((List.range (arity w)).map fun j =>
  (-1 : Int) ^ (blockSize w j - 1) * (factorial (blockSize w j - 1) : Int)).prod

def exact (r : Nat) : Poly := (partitions r).map fun w => (w, (2 : Int)^r * mobius w)

def coeff (w : Pattern) (p : Poly) : Int :=
  ((p.filter fun t => t.1 == w).map Prod.snd).sum

def sameAt (r : Nat) (p q : Poly) : Bool :=
  (partitions r).all fun w => coeff w p == coeff w q

def h0 : Poly := [([], 1)]
def h1 : Poly := moment 1 h0
def h2 : Poly := moment 1 h1 ++ scale (-1) (moment 2 h0)
def h3 : Poly := moment 1 h2 ++ scale (-2) (moment 2 h1) ++ scale 2 (moment 3 h0)

-- GENERATED COUNTERTERM TABLES
def c4 : Poly := [
    ([0, 0, 0, 1], 1),
    ([0, 0, 1, 0], -1),
    ([0, 0, 1, 1], -2),
    ([0, 0, 1, 2], 1),
    ([0, 1, 0, 0], -1),
    ([0, 1, 0, 1], 4),
    ([0, 1, 0, 2], -2),
    ([0, 1, 1, 0], -2),
    ([0, 1, 1, 1], 1),
    ([0, 1, 2, 0], 2),
    ([0, 1, 2, 1], -2),
    ([0, 1, 2, 2], 1)]

def c5 : Poly := [
    ([0, 0, 0, 0, 1], -3),
    ([0, 0, 0, 1, 1], 3),
    ([0, 0, 0, 1, 2], -2),
    ([0, 0, 1, 0, 0], 6),
    ([0, 0, 1, 0, 1], -4),
    ([0, 0, 1, 0, 2], 3),
    ([0, 0, 1, 1, 0], 5),
    ([0, 0, 1, 1, 1], 3),
    ([0, 0, 1, 1, 2], 1),
    ([0, 0, 1, 2, 0], -5),
    ([0, 0, 1, 2, 2], -2),
    ([0, 1, 0, 0, 1], -4),
    ([0, 1, 0, 0, 2], 3),
    ([0, 1, 0, 1, 0], -4),
    ([0, 1, 0, 1, 1], -4),
    ([0, 1, 0, 1, 2], -3),
    ([0, 1, 0, 2, 0], 4),
    ([0, 1, 0, 2, 1], 2),
    ([0, 1, 0, 2, 3], 1),
    ([0, 1, 1, 0, 0], 5),
    ([0, 1, 1, 0, 1], -4),
    ([0, 1, 1, 0, 2], 3),
    ([0, 1, 1, 1, 0], 4),
    ([0, 1, 1, 1, 1], -3),
    ([0, 1, 1, 1, 2], -2),
    ([0, 1, 1, 2, 0], -2),
    ([0, 1, 1, 2, 1], 3),
    ([0, 1, 1, 2, 2], 1),
    ([0, 1, 1, 2, 3], -1),
    ([0, 1, 2, 0, 0], -5),
    ([0, 1, 2, 0, 1], 2),
    ([0, 1, 2, 0, 2], 2),
    ([0, 1, 2, 0, 3], -3),
    ([0, 1, 2, 1, 0], -2),
    ([0, 1, 2, 1, 1], 3),
    ([0, 1, 2, 1, 2], -3),
    ([0, 1, 2, 1, 3], 4),
    ([0, 1, 2, 2, 0], -2),
    ([0, 1, 2, 2, 1], 3),
    ([0, 1, 2, 2, 2], -2),
    ([0, 1, 2, 2, 3], -1),
    ([0, 1, 2, 3, 0], 2),
    ([0, 1, 2, 3, 1], -3),
    ([0, 1, 2, 3, 2], 1)]

def h4 : Poly := moment 1 h3 ++ scale (-3) (moment 2 h2) ++
  scale 6 (moment 3 h1) ++ scale (-6) (moment 4 h0) ++ scale 4 c4

def h5 : Poly := moment 1 h4 ++ scale (-4) (moment 2 h3) ++
  scale 12 (moment 3 h2) ++ scale (-24) (moment 4 h1) ++ scale 24 (moment 5 h0) ++
  scale 8 (multiply c4 h1 ++ multiply h1 c4) ++ scale 16 c5

def normalForm (r : Nat) (p : Poly) : Poly :=
  (partitions r).map fun w => (w, coeff w p)

def supported (r : Nat) (p : Poly) : Bool :=
  p.all fun t => (partitions r).contains t.1

theorem order4_certificate : normalForm 4 h4 = normalForm 4 (exact 4) := by
  decide

theorem order5_certificate : normalForm 5 h5 = normalForm 5 (exact 5) := by
  decide

theorem certificates_have_complete_support :
    supported 4 h4 && supported 5 h5 = true := by
  decide

theorem lower_orders_certificate :
    normalForm 0 h0 = normalForm 0 (exact 0) ∧
    normalForm 1 h1 = normalForm 1 (exact 1) ∧
    normalForm 2 h2 = normalForm 2 (exact 2) ∧
    normalForm 3 h3 = normalForm 3 (exact 3) := by
  decide

def repeatedBlocks (w : Pattern) : Nat :=
  ((List.range (arity w)).filter fun j => 2 ≤ blockSize w j).length

theorem quintic_contraction_bound :
    c5.length = 44 ∧ (c5.all fun t => repeatedBlocks t.1 ≤ 2) = true := by
  decide

#print axioms order4_certificate
#print axioms order5_certificate
#print axioms certificates_have_complete_support
#print axioms lower_orders_certificate
#print axioms quintic_contraction_bound

end OrientedOperators.PartitionCertificate
