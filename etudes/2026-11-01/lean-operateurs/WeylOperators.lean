import LocalNoncommRing

set_option Elab.async false

namespace OrientedOperators

variable {R : Type*} [Ring R]

/-- Exact square of the creation operator; nilpotence requires the
multiaffine invariant, rather than being an identity on every polynomial. -/
theorem creation_square (x d : R) (hdx : d * x = x * d + 1) :
    (x - x ^ 2 * d) ^ 2 = x ^ 4 * d ^ 2 := by
  have hmove (a : R) : d * (x * a) = x * (d * a) + a := by
    simpa only [mul_assoc, add_mul, one_mul] using congrArg (fun z => z * a) hdx
  noncomm_ring [hdx, hmove]

#print axioms creation_square

end OrientedOperators
