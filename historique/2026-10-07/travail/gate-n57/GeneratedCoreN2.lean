import Std

/- Generated from checked SymPy polynomial expressions; run the strict verifier. -/
namespace GeneratedCollisionN2

theorem factorization {R : Type} [Lean.Grind.CommRing R] (a b t : R) :
    ((t + ((-1) * (t ^ 2))) * ((a * (t ^ 2)) + ((-1) * b * t))) = ((a * (t ^ 3)) + (b * (t ^ 3)) + ((-1) * a * (t ^ 4)) + ((-1) * b * (t ^ 2))) := by
  grind

def listCoeff (p : List Rat) (k : Nat) : Rat := (p[k]?).getD 0
def convolutionCoeff (p q : List Rat) (k : Nat) : Rat :=
  ((List.range (k + 1)).map
    (fun i => listCoeff p i * listCoeff q (k - i))).foldr (· + ·) 0

theorem central_convolution (a b : Rat) :
    convolutionCoeff [0, ((-1) * b), a] [0, 1, (-1)] 3 = (a + b) := by
  simp [convolutionCoeff, listCoeff, List.range_succ]
  grind

#print axioms GeneratedCollisionN2.factorization
#print axioms GeneratedCollisionN2.central_convolution
end GeneratedCollisionN2
