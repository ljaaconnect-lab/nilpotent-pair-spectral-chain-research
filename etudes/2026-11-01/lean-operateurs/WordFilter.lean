import PartitionCertificate

set_option Elab.async false
set_option maxHeartbeats 1000000
set_option maxRecDepth 8192

namespace OrientedOperators.PartitionCertificate
universe u

def literal5 : Poly := [
  ([0, 0, 0, 0, 0], 768),
  ([0, 0, 0, 0, 1], -192),
  ([0, 0, 0, 1, 0], -192),
  ([0, 0, 0, 1, 1], -64),
  ([0, 0, 0, 1, 2], 64),
  ([0, 0, 1, 0, 0], -192),
  ([0, 0, 1, 0, 1], -64),
  ([0, 0, 1, 0, 2], 64),
  ([0, 0, 1, 1, 0], -64),
  ([0, 0, 1, 1, 1], -64),
  ([0, 0, 1, 1, 2], 32),
  ([0, 0, 1, 2, 0], 64),
  ([0, 0, 1, 2, 1], 32),
  ([0, 0, 1, 2, 2], 32),
  ([0, 0, 1, 2, 3], -32),
  ([0, 1, 0, 0, 0], -192),
  ([0, 1, 0, 0, 1], -64),
  ([0, 1, 0, 0, 2], 64),
  ([0, 1, 0, 1, 0], -64),
  ([0, 1, 0, 1, 1], -64),
  ([0, 1, 0, 1, 2], 32),
  ([0, 1, 0, 2, 0], 64),
  ([0, 1, 0, 2, 1], 32),
  ([0, 1, 0, 2, 2], 32),
  ([0, 1, 0, 2, 3], -32),
  ([0, 1, 1, 0, 0], -64),
  ([0, 1, 1, 0, 1], -64),
  ([0, 1, 1, 0, 2], 32),
  ([0, 1, 1, 1, 0], -64),
  ([0, 1, 1, 1, 1], -192),
  ([0, 1, 1, 1, 2], 64),
  ([0, 1, 1, 2, 0], 32),
  ([0, 1, 1, 2, 1], 64),
  ([0, 1, 1, 2, 2], 32),
  ([0, 1, 1, 2, 3], -32),
  ([0, 1, 2, 0, 0], 64),
  ([0, 1, 2, 0, 1], 32),
  ([0, 1, 2, 0, 2], 32),
  ([0, 1, 2, 0, 3], -32),
  ([0, 1, 2, 1, 0], 32),
  ([0, 1, 2, 1, 1], 64),
  ([0, 1, 2, 1, 2], 32),
  ([0, 1, 2, 1, 3], -32),
  ([0, 1, 2, 2, 0], 32),
  ([0, 1, 2, 2, 1], 32),
  ([0, 1, 2, 2, 2], 64),
  ([0, 1, 2, 2, 3], -32),
  ([0, 1, 2, 3, 0], -32),
  ([0, 1, 2, 3, 1], -32),
  ([0, 1, 2, 3, 2], -32),
  ([0, 1, 2, 3, 3], -32),
  ([0, 1, 2, 3, 4], 32)]

theorem literal5_identity : exact 5 = literal5 := by
  decide

def compatible {α : Type u} [DecidableEq α] (pattern : Pattern) (w : List α) : Bool :=
  (pattern.zip w).all fun a => (pattern.zip w).all fun b =>
    if a.1 = b.1 then decide (a.2 = b.2) else true

def wordWeight {α : Type u} [DecidableEq α] (w : List α) (p : Poly) : Int :=
  (p.map fun (pattern, c) => if compatible pattern w then c else 0).sum

theorem fifth_filter_on_arbitrary_columns {α : Type u} [DecidableEq α]
    (a b c d e : α) :
    wordWeight [a, b, c, d, e] (exact 5) =
      if a ≠ b ∧ a ≠ c ∧ a ≠ d ∧ a ≠ e ∧ b ≠ c ∧ b ≠ d ∧ b ≠ e ∧
        c ≠ d ∧ c ≠ e ∧ d ≠ e then 32 else 0 := by
  simp [literal5_identity, wordWeight, compatible, literal5]
  by_cases hab : a = b
  all_goals simp_all
  all_goals by_cases hac : a = c
  all_goals simp_all
  all_goals by_cases had : a = d
  all_goals simp_all
  all_goals by_cases hae : a = e
  all_goals simp_all
  all_goals grind (splits := 14)

theorem normalForm_exact5 : normalForm 5 (exact 5) = exact 5 := by
  decide

theorem quintic_word_certificate {α : Type u} [DecidableEq α]
    (a b c d e : α) :
    wordWeight [a, b, c, d, e] (normalForm 5 h5) =
      if a ≠ b ∧ a ≠ c ∧ a ≠ d ∧ a ≠ e ∧ b ≠ c ∧ b ≠ d ∧ b ≠ e ∧
        c ≠ d ∧ c ≠ e ∧ d ≠ e then 32 else 0 := by
  simpa only [order5_certificate, normalForm_exact5] using
    fifth_filter_on_arbitrary_columns a b c d e

#print axioms literal5_identity
#print axioms fifth_filter_on_arbitrary_columns
#print axioms normalForm_exact5
#print axioms quintic_word_certificate

end OrientedOperators.PartitionCertificate
