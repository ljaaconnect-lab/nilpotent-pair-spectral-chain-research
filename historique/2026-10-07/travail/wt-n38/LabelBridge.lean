import CoreBridge
import GeneralPairingRing

namespace CollisionLabelBridge

open CollisionCoreBridge

theorem digit_step_bound (n d tail top : Nat) (hd : d < n) (ht : tail < top) :
    d + n * tail < n * top := by
  have hmul := Nat.mul_le_mul_left n (Nat.succ_le_of_lt ht)
  grind
  done

#print axioms CollisionLabelBridge.digit_step_bound

theorem encodeDigits_lt_pow (n : Nat) (_hn : 0 < n) (xs : List (Fin n)) :
    encodeDigits n xs < n ^ xs.length := by
  induction xs
  case nil => simp [encodeDigits]
  case cons d ds ih =>
    simpa [encodeDigits, Nat.pow_succ, Nat.mul_comm] using
      digit_step_bound n d.val (encodeDigits n ds) (n ^ ds.length) d.isLt ih
  done

#print axioms CollisionLabelBridge.encodeDigits_lt_pow

def indexedLabelFrom (n start : Nat) (xs : List (Fin n)) : Nat :=
  (xs.mapIdx (fun i d => d.val * n ^ (start + i))).sum

theorem indexedLabelFrom_eq (n start : Nat) (xs : List (Fin n)) :
    indexedLabelFrom n start xs = n ^ start * encodeDigits n xs := by
  induction xs generalizing start
  case nil => simp [indexedLabelFrom, encodeDigits]
  case cons d ds ih =>
    have hshift : (ds.mapIdx (fun i d => d.val * n ^ (start + (i + 1)))).sum =
        n ^ (start + 1) * encodeDigits n ds :=
      (congrArg (fun (f : Nat → Fin n → Nat) => (ds.mapIdx f).sum)
        (funext (fun i => funext (fun (e : Fin n) =>
          congrArg (fun k => e.val * n ^ k)
            ((Nat.add_assoc start i 1).symm.trans (Nat.add_right_comm start i 1)))))).trans
        (ih (start + 1))
    simp only [indexedLabelFrom, List.mapIdx_cons, List.sum_cons, Nat.add_zero,
      encodeDigits, hshift, Nat.pow_succ]
    grind
  done

#print axioms CollisionLabelBridge.indexedLabelFrom_eq

def indexedLabel (n : Nat) (xs : List (Fin n)) : Nat :=
  (xs.mapIdx (fun i d => d.val * n ^ i)).sum

theorem indexedLabel_eq (n : Nat) (xs : List (Fin n)) :
    indexedLabel n xs = encodeDigits n xs := by
  simpa [indexedLabelFrom, indexedLabel] using indexedLabelFrom_eq n 0 xs

#print axioms CollisionLabelBridge.indexedLabel_eq

theorem indexedLabel_injective (n : Nat) (hn : 0 < n) (xs ys : List (Fin n))
    (hlen : xs.length = ys.length) (hlabel : indexedLabel n xs = indexedLabel n ys) :
    xs = ys := by
  exact encodeDigits_injective n hn xs ys hlen
    ((indexedLabel_eq n xs).symm.trans (hlabel.trans (indexedLabel_eq n ys)))

#print axioms CollisionLabelBridge.indexedLabel_injective

theorem indexedLabel_le_max (n : Nat) (hn : 0 < n) (xs : List (Fin n)) :
    indexedLabel n xs ≤ n ^ xs.length - 1 := by
  simpa only [indexedLabel_eq] using Nat.le_sub_one_of_lt (encodeDigits_lt_pow n hn xs)

#print axioms CollisionLabelBridge.indexedLabel_le_max

def assignmentLabel (base length : Nat) (f : Fin length → Fin base) : Nat :=
  indexedLabel base (List.ofFn f)

theorem assignmentLabel_le_max (base length : Nat) (hbase : 0 < base)
    (f : Fin length → Fin base) :
    assignmentLabel base length f ≤ base ^ length - 1 := by
  simpa [assignmentLabel, List.length_ofFn] using
    indexedLabel_le_max base hbase (List.ofFn f)

#print axioms CollisionLabelBridge.assignmentLabel_le_max

theorem assignmentLabel_injective (base length : Nat) (hbase : 0 < base)
    (f g : Fin length → Fin base)
    (hlabel : assignmentLabel base length f = assignmentLabel base length g) :
    f = g := by
  have hlist : List.ofFn f = List.ofFn g :=
    indexedLabel_injective base hbase (List.ofFn f) (List.ofFn g)
      ((List.length_ofFn).trans (List.length_ofFn).symm) hlabel
  exact funext (fun i => Option.some.inj (by
    simpa [List.getElem?_ofFn, i.isLt] using
      congrArg (fun (xs : List (Fin base)) => xs[i.val]?) hlist))
  done

#print axioms CollisionLabelBridge.assignmentLabel_injective

def occupationLabel (n length : Nat) (count : Fin length → Nat)
    (hcount : ∀ i, count i ≤ n) : Nat :=
  assignmentLabel (n + 1) length
    (fun i => ⟨count i, Nat.lt_succ_of_le (hcount i)⟩)

def allOnesLabel (n length : Nat) (hn : 0 < n) : Nat :=
  assignmentLabel (n + 1) length
    (fun _ => ⟨1, Nat.lt_succ_of_le (Nat.succ_le_of_lt hn)⟩)

theorem occupation_all_ones_selector (n length : Nat) (hn : 0 < n)
    (count : Fin length → Nat) (hcount : ∀ i, count i ≤ n)
    (hlabel : occupationLabel n length count hcount = allOnesLabel n length hn) :
    ∀ i, count i = 1 := by
  exact fun i => congrArg Fin.val (congrFun
    (assignmentLabel_injective (n + 1) length (Nat.succ_pos n)
      (fun j => ⟨count j, Nat.lt_succ_of_le (hcount j)⟩)
      (fun _ => ⟨1, Nat.lt_succ_of_le (Nat.succ_le_of_lt hn)⟩) hlabel) i)

#print axioms CollisionLabelBridge.occupation_all_ones_selector

theorem assignmentLabel_sum_eq (base length : Nat) (f : Fin length → Fin base) :
    assignmentLabel base length f =
      (List.ofFn (fun i => (f i).val * base ^ i.val)).sum := by
  exact congrArg List.sum (List.ext_getElem? (fun i => by
    simp [List.getElem?_mapIdx, List.getElem?_ofFn]))

#print axioms CollisionLabelBridge.assignmentLabel_sum_eq

theorem occupation_sum_selector (n length : Nat) (hn : 0 < n)
    (count : Fin length → Nat) (hcount : ∀ i, count i ≤ n)
    (hsum : (List.ofFn (fun i => count i * (n + 1) ^ i.val)).sum =
      (List.ofFn (fun i : Fin length => (n + 1) ^ i.val)).sum) :
    ∀ i, count i = 1 := by
  exact occupation_all_ones_selector n length hn count hcount (by
    simpa [occupationLabel, allOnesLabel, assignmentLabel_sum_eq] using hsum)

#print axioms CollisionLabelBridge.occupation_sum_selector

theorem assignmentLabels_nodup (base length : Nat) (hbase : 0 < base)
    (assignments : List (Fin length → Fin base)) (hnodup : assignments.Nodup) :
    (assignments.map (assignmentLabel base length)).Nodup := by
  exact List.Pairwise.map (assignmentLabel base length)
    (fun f g hne heq => hne (assignmentLabel_injective base length hbase f g heq)) hnodup

#print axioms CollisionLabelBridge.assignmentLabels_nodup

theorem indexed_assignment_pairing {R : Type} [Lean.Grind.CommRing R]
    (base length : Nat) (hbase : 0 < base)
    (assignments : List (Fin length → Fin base)) (hnodup : assignments.Nodup)
    (weight sign : Nat → R)
    (hsign : ∀ r ∈ assignments.map (assignmentLabel base length),
      sign r = 1 ∨ sign r = -1) :
    GeneralCollisionPairingRing.coefficient
      (GeneralCollisionPairingRing.multiply
        (GeneralCollisionPairingRing.signedForward
          (assignments.map (assignmentLabel base length)) weight sign)
        (GeneralCollisionPairingRing.signedReverse (base ^ length - 1)
          (assignments.map (assignmentLabel base length)) sign))
      (base ^ length - 1) =
        ((assignments.map (assignmentLabel base length)).map weight).sum := by
  exact GeneralCollisionPairingRing.central_product_coefficient
    (base ^ length - 1) (assignments.map (assignmentLabel base length)) weight sign
    (assignmentLabels_nodup base length hbase assignments hnodup)
    (fun r hr => Exists.elim (List.mem_map.mp hr)
      (fun f h => h.2 ▸ assignmentLabel_le_max base length hbase f)) hsign

#print axioms CollisionLabelBridge.indexed_assignment_pairing

end CollisionLabelBridge
