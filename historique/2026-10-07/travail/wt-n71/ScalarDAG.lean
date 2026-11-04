import EncodingBridge

namespace CollisionScalarDAG

open CollisionEncodingBridge

noncomputable section

/-- Signed numerator plus positive denominator in normalized rational form. -/
def naturalBits (m : Nat) : Nat := if m = 0 then 1 else Nat.log2 m + 1

def rationalBits (q : Rat) : Nat :=
  1 + naturalBits q.num.natAbs + naturalBits q.den

/-- These are the only permitted source-node labels. -/
inductive Leaf (n : Nat) where
  | marked (i j : Fin n)
  | variableZ
  | rational (q : Rat)

def Leaf.eval {n : Nat} (A : Matrix (Fin n) (Fin n) Rat) :
    Leaf n → Polynomial Rat
  | .marked i j => Polynomial.C (1 + (A i j) ^ 2)
  | .variableZ => Polynomial.X
  | .rational q => Polynomial.C q

/-- References in a gate appended at position k are strictly earlier nodes. -/
inductive Node (n k : Nat) where
  | leaf (label : Leaf n)
  | add (left right : Fin k)
  | mul (left right : Fin k)

def Node.eval {n k : Nat} (A : Matrix (Fin n) (Fin n) Rat)
    (prior : Fin k → Polynomial Rat) : Node n k → Polynomial Rat
  | .leaf label => label.eval A
  | .add left right => prior left + prior right
  | .mul left right => prior left * prior right

def Node.gates {n k : Nat} : Node n k → Nat
  | .leaf _ => 0
  | .add _ _ => 1
  | .mul _ _ => 1

def Node.literalBound {n k : Nat} (B : Nat) : Node n k → Prop
  | .leaf (.rational q) => rationalBits q ≤ B
  | _ => True

/-- A topological node sequence; earlier values can be shared by any later gate. -/
inductive Program (n : Nat) : Nat → Type where
  | nil : Program n 0
  | snoc {k : Nat} (prior : Program n k) (node : Node n k) : Program n (k + 1)

def Program.eval {n : Nat} (A : Matrix (Fin n) (Fin n) Rat) :
    {k : Nat} → Program n k → Fin k → Polynomial Rat
  | _, .nil => Fin.elim0
  | _, .snoc prior node =>
      Fin.lastCases (node.eval A (prior.eval A)) (prior.eval A)

def Program.gates {n : Nat} : {k : Nat} → Program n k → Nat
  | _, .nil => 0
  | _, .snoc prior node => prior.gates + node.gates

def Program.literalBound {n : Nat} (B : Nat) : {k : Nat} → Program n k → Prop
  | _, .nil => True
  | _, .snoc prior node => prior.literalBound B ∧ node.literalBound B

structure Circuit (n : Nat) where
  nodeCount : Nat
  program : Program n nodeCount
  output : Fin nodeCount

def Circuit.eval {n : Nat} (A : Matrix (Fin n) (Fin n) Rat)
    (c : Circuit n) : Polynomial Rat := c.program.eval A c.output

def Circuit.gates {n : Nat} (c : Circuit n) : Nat := c.program.gates

def Circuit.literalBound {n : Nat} (B : Nat) (c : Circuit n) : Prop :=
  c.program.literalBound B

def Realizes {n : Nat} (B : Nat) (A : Matrix (Fin n) (Fin n) Rat)
    (c : Circuit n) : Prop :=
  c.gates ≤ B ∧ c.literalBound B ∧ c.eval A = markedPermanent A

/-- The unconditional algebraic-circuit component is stated, not proved here.
    Uniform construction in polynomial bit time is a separate REQUIRED obligation. -/
def AlgebraicCircuitComponent : Prop :=
  ∃ Pi : Polynomial Nat, ∀ n : Nat, 1 ≤ n →
    ∀ A : Matrix (Fin n) (Fin n) Rat,
      ∃ c : Circuit n, Realizes (Pi.eval n) A c

#check CollisionScalarDAG.AlgebraicCircuitComponent
#print CollisionScalarDAG.AlgebraicCircuitComponent
#print axioms CollisionScalarDAG.rationalBits
#print axioms CollisionScalarDAG.Leaf.eval
#print axioms CollisionScalarDAG.Node.eval
#print axioms CollisionScalarDAG.Program.eval
#print axioms CollisionScalarDAG.Program.gates
#print axioms CollisionScalarDAG.Program.literalBound
#print axioms CollisionScalarDAG.Realizes
#print axioms CollisionScalarDAG.AlgebraicCircuitComponent

end
end CollisionScalarDAG
