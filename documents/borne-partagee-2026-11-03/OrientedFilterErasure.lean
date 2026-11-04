import Mathlib.Algebra.BigOperators.Ring.Finset

/-!
An explicit collision operator maps into the square-zero ideal.
Consequently its filters disappear after the oriented quotient map.
This proves redundancy of the auxiliary filter, not a circuit bound
for quotient multiplication or terminal scalar reading.
-/

namespace OrientedFilterErasure

variable {R S J : Type*} [CommRing R] [CommRing S] [Fintype J]

def collision (q : J → R) (D : J → R → R) (half F : R) : R :=
  half * ∑ j, q j ^ 2 * D j (D j F)

theorem collision_maps_to_zero (rho : R →+* S) (q : J → R)
    (D : J → R → R) (half F : R) (hq : ∀ j, rho (q j) ^ 2 = 0) :
    rho (collision q D half F) = 0 := by
  simp [collision, hq]

theorem filter_preserves_quotient (rho : R →+* S) (q : J → R)
    (D : J → R → R) (half F a : R) (hq : ∀ j, rho (q j) ^ 2 = 0) :
    rho (F - a * collision q D half F) = rho F := by
  simp [collision_maps_to_zero rho q D half F hq]

def filters (q : J → R) (D : J → R → R) (half : R) : List R → R → R
  | [], F => F
  | a :: weights, F =>
      let H := filters q D half weights F
      H - a * collision q D half H

theorem all_filters_preserve_quotient (rho : R →+* S) (q : J → R)
    (D : J → R → R) (half F : R) (weights : List R)
    (hq : ∀ j, rho (q j) ^ 2 = 0) :
    rho (filters q D half weights F) = rho F := by
  exact List.rec (Eq.refl (rho F))
    (fun a weights ih =>
      (filter_preserves_quotient rho q D half
        (filters q D half weights F) a hq).trans ih) weights

end OrientedFilterErasure

#print axioms OrientedFilterErasure.collision_maps_to_zero
#print axioms OrientedFilterErasure.filter_preserves_quotient
#print axioms OrientedFilterErasure.all_filters_preserve_quotient
