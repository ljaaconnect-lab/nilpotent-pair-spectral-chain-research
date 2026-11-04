import MatrixScalarCompiler

/-!
Closure of ordinary arithmetic circuits under extensions of a shared store.
Old wires, including coefficient and auxiliary-coordinate wires, remain in
the store. Each extension uses one existing prefix and charges only its new
block. Ring-homomorphic interpretation is a semantic theorem, not a gate.
This construction does not remove auxiliary orientation coordinates.
-/

open DenseScalar

namespace SharedStateClosure

universe u v

def extend {I J O : Type} (c : Circuit I J) (op : Circuit J O) : Circuit I (Sum J O) :=
  .comp c (.pair (.wire id) op)

theorem extend_eval {I J O : Type} {R : Type u} [Semiring R]
    (c : Circuit I J) (op : Circuit J O) (inputs : I → R) :
    (extend c op).eval inputs = Sum.elim (c.eval inputs) (op.eval (c.eval inputs)) := rfl

theorem old_wires_preserved {I J O : Type} {R : Type u} [Semiring R]
    (c : Circuit I J) (op : Circuit J O) (inputs : I → R) (j : J) :
    (extend c op).eval inputs (Sum.inl j) = c.eval inputs j := rfl

theorem new_outputs_computed {I J O : Type} {R : Type u} [Semiring R]
    (c : Circuit I J) (op : Circuit J O) (inputs : I → R) (o : O) :
    (extend c op).eval inputs (Sum.inr o) = op.eval (c.eval inputs) o := rfl

theorem extend_gates {I J O : Type} (c : Circuit I J) (op : Circuit J O) :
    (extend c op).gates = c.gates + op.gates := by
  simp [extend, Circuit.gates]

/-- The same circuit commutes with a change of coefficient semiring. -/
theorem circuit_eval_natural {R : Type u} {A : Type v} [Semiring R] [Semiring A]
    (rho : R →+* A) {I O : Type} (c : Circuit I O) :
    ∀ inputs : I → R,
      (fun o => rho (c.eval inputs o)) = c.eval (fun i => rho (inputs i)) := by
  induction c with
  | wire read => exact fun _ => rfl
  | constant bits => simp [Circuit.eval, apply_ite]
  | add left right => exact fun inputs => funext (fun _ => rho.map_add _ _)
  | mul left right => exact fun inputs => funext (fun _ => rho.map_mul _ _)
  | pair left right ih_left ih_right =>
    exact fun inputs => funext (Sum.rec
      (fun o => congrFun (ih_left inputs) o)
      (fun o => congrFun (ih_right inputs) o))
  | parallel family ih =>
    exact fun inputs => funext (fun output => congrFun (ih output.1 inputs) output.2)
  | comp first next ih_first ih_next =>
    exact fun inputs => (ih_next (first.eval inputs)).trans
      (congrArg next.eval (ih_first inputs))

/-- An arbitrary typed sequence of extensions, each retaining its previous store. -/
inductive SharedChain : Type → Type → Type 1 where
  | start (I : Type) : SharedChain I I
  | append {I J O : Type} (previous : SharedChain I J) (op : Circuit J O) :
      SharedChain I (Sum J O)

def SharedChain.compile {I J : Type} : SharedChain I J → Circuit I J
  | .start _ => .wire id
  | .append previous op => extend previous.compile op

def SharedChain.gateBudget {I J : Type} : SharedChain I J → ℕ
  | .start _ => 0
  | .append previous op => previous.gateBudget + op.gates

def SharedChain.eval {I J : Type} {R : Type u} [Semiring R] :
    SharedChain I J → (I → R) → J → R
  | .start _, inputs => inputs
  | .append previous op, inputs =>
      Sum.elim (previous.eval inputs) (op.eval (previous.eval inputs))

theorem shared_chain_eval {I J : Type} {R : Type u} [Semiring R]
    (chain : SharedChain I J) (inputs : I → R) :
    chain.compile.eval inputs = chain.eval inputs := by
  exact SharedChain.rec
    (motive := fun _ previous => previous.compile.eval inputs = previous.eval inputs)
    rfl (fun previous op ih =>
      congrArg (fun state => Sum.elim state (op.eval state)) ih) chain

theorem shared_chain_gates {I J : Type} (chain : SharedChain I J) :
    chain.compile.gates = chain.gateBudget := by
  exact SharedChain.rec
    (motive := fun _ previous => previous.compile.gates = previous.gateBudget)
    rfl (fun previous op ih => by
      simpa only [SharedChain.compile, SharedChain.gateBudget] using
        (extend_gates previous.compile op).trans
          (congrArg (fun value => value + op.gates) ih)) chain

theorem shared_chain_correct {I J : Type} {R : Type u} [Semiring R]
    (chain : SharedChain I J) (inputs : I → R) :
    chain.compile.eval inputs = chain.eval inputs ∧
      chain.compile.gates = chain.gateBudget := by
  exact ⟨shared_chain_eval chain inputs, shared_chain_gates chain⟩

end SharedStateClosure

#print axioms SharedStateClosure.extend_eval
#print axioms SharedStateClosure.old_wires_preserved
#print axioms SharedStateClosure.new_outputs_computed
#print axioms SharedStateClosure.extend_gates
#print axioms SharedStateClosure.circuit_eval_natural
#print axioms SharedStateClosure.shared_chain_eval
#print axioms SharedStateClosure.shared_chain_gates
#print axioms SharedStateClosure.shared_chain_correct
