import Std

set_option maxHeartbeats 20000

namespace LocalGadget

def bitSign (b : Bool) : Int := if b then -1 else 1

def selected (a b c d : Bool) : List Nat :=
  (if a then [0] else []) ++ (if b then [1] else []) ++
  (if c then [2] else []) ++ (if d then [3] else [])

def skewEntry (i j : Nat) : Int := if i < j then 1 else if j < i then -1 else 0

def pfMinor4 (l : List Nat) : Int :=
  match l with
  | [] => 1
  | [i,j] => skewEntry i j
  | [i,j,k,l] => skewEntry i j * skewEntry k l -
      skewEntry i k * skewEntry j l + skewEntry i l * skewEntry j k
  | _ => 0

theorem copy4_hadamard : ∀ (a b c d : Bool),
    (1 : Int) + bitSign a * bitSign b * bitSign c * bitSign d =
      if Bool.xor (Bool.xor a b) (Bool.xor c d) then 0 else 2 := by
  decide

theorem copy4_to_pfMinor4 : ∀ (a b c d : Bool),
    (1 : Int) + bitSign a * bitSign b * bitSign c * bitSign d =
      2 * pfMinor4 (selected a b c d) := by
  decide

end LocalGadget

#print axioms LocalGadget.copy4_hadamard
#print axioms LocalGadget.copy4_to_pfMinor4
