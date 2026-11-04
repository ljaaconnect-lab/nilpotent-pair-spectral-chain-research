import Std

namespace GeneralCollisionPairingRing

abbrev SparsePolynomial (R : Type) := List (Nat × R)

variable {R : Type} [Lean.Grind.CommRing R]

-- These are derived law instances, not additional hypotheses or axioms.
local instance : Std.LawfulLeftIdentity (α := R) (· + ·) (0 : R) where
  left_id a := (Lean.Grind.Semiring.add_comm 0 a).trans (Lean.Grind.Semiring.add_zero a)

local instance : Std.Associative (α := R) (· + ·) where
  assoc a b c := Lean.Grind.Semiring.add_assoc a b c


def coefficient (p : SparsePolynomial R) (k : Nat) : R :=
  (p.map (fun term => if term.1 = k then term.2 else 0)).sum

def multiply (p q : SparsePolynomial R) : SparsePolynomial R :=
  p.flatMap (fun left =>
    q.map (fun right => (left.1 + right.1, left.2 * right.2)))

def convolutionCoefficient (p q : SparsePolynomial R) (k : Nat) : R :=
  (p.map (fun left =>
    (q.map (fun right =>
      if left.1 + right.1 = k then left.2 * right.2 else 0)).sum)).sum

def signedForward (labels : List Nat) (weight sign : Nat → R) : SparsePolynomial R :=
  labels.map (fun r => (r, sign r * weight r))

def signedReverse (K : Nat) (labels : List Nat) (sign : Nat → R) : SparsePolynomial R :=
  labels.map (fun r => (K - r, sign r))

def selectSum (labels : List Nat) (r : Nat) (value : Nat → R) : R :=
  (labels.map (fun s => if r = s then value s else 0)).sum

theorem sign_square (s : R) (hs : s = 1 ∨ s = -1) : s * s = 1 := by
  grind

#print axioms GeneralCollisionPairingRing.sign_square

theorem selectSum_nodup (labels : List Nat) (hnodup : labels.Nodup)
    (r : Nat) (value : Nat → R) :
    selectSum labels r value = if r ∈ labels then value r else 0 := by
  induction labels
  all_goals simp_all [selectSum, List.nodup_cons]
  grind
  done

#print axioms GeneralCollisionPairingRing.selectSum_nodup

theorem central_label_iff (K r s : Nat) (hs : s ≤ K) :
    r + (K - s) = K ↔ r = s := by
  omega

#print axioms GeneralCollisionPairingRing.central_label_iff

theorem central_row_select (K : Nat) (labels : List Nat)
    (hbound : ∀ s ∈ labels, s ≤ K) (r : Nat) (value : Nat → R) :
    (labels.map (fun s => if r + (K - s) = K then value s else 0)).sum =
      selectSum labels r value := by
  apply congrArg List.sum
  exact List.map_congr_left (fun s hs =>
    ite_cond_congr (propext (central_label_iff K r s (hbound s hs))))
  done

#print axioms GeneralCollisionPairingRing.central_row_select

theorem central_row (K : Nat) (labels : List Nat) (hnodup : labels.Nodup)
    (hbound : ∀ s ∈ labels, s ≤ K) (r : Nat) (hr : r ∈ labels)
    (weight sign : Nat → R) (hsign : sign r = 1 ∨ sign r = -1) :
    (labels.map (fun s =>
      if r + (K - s) = K then (sign r * weight r) * sign s else 0)).sum =
      weight r := by
  rw [central_row_select K labels hbound r (fun s => (sign r * weight r) * sign s)]
  rw [selectSum_nodup labels hnodup r (fun s => (sign r * weight r) * sign s), ite_eq_left hr]
  grind [sign_square]
  done

#print axioms GeneralCollisionPairingRing.central_row

theorem central_pairing (K : Nat) (labels : List Nat)
    (weight sign : Nat → R) (hnodup : labels.Nodup)
    (hbound : ∀ r ∈ labels, r ≤ K)
    (hsign : ∀ r ∈ labels, sign r = 1 ∨ sign r = -1) :
    convolutionCoefficient (signedForward labels weight sign)
      (signedReverse K labels sign) K = (labels.map weight).sum := by
  simp only [convolutionCoefficient, signedForward, signedReverse, List.map_map]
  exact congrArg List.sum (List.map_congr_left (fun r hr =>
    central_row K labels hnodup hbound r hr weight sign (hsign r hr)))
  done

#print axioms GeneralCollisionPairingRing.central_pairing

theorem coefficient_append (p q : SparsePolynomial R) (k : Nat) :
    coefficient (p ++ q) k = coefficient p k + coefficient q k := by
  simp [coefficient, List.sum_append]

#print axioms GeneralCollisionPairingRing.coefficient_append

theorem coefficient_multiply (p q : SparsePolynomial R) (k : Nat) :
    coefficient (multiply p q) k = convolutionCoefficient p q k := by
  induction p
  all_goals simp_all [multiply, coefficient, convolutionCoefficient, List.sum_append, List.map_map]
  rfl
  done

#print axioms GeneralCollisionPairingRing.coefficient_multiply

theorem central_product_coefficient (K : Nat) (labels : List Nat)
    (weight sign : Nat → R) (hnodup : labels.Nodup)
    (hbound : ∀ r ∈ labels, r ≤ K)
    (hsign : ∀ r ∈ labels, sign r = 1 ∨ sign r = -1) :
    coefficient (multiply (signedForward labels weight sign)
      (signedReverse K labels sign)) K = (labels.map weight).sum := by
  rw [coefficient_multiply, central_pairing K labels weight sign hnodup hbound hsign]

#print axioms GeneralCollisionPairingRing.central_product_coefficient

end GeneralCollisionPairingRing
