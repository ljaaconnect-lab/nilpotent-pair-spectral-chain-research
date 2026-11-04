import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Algebra.Module.LinearMap.Basic
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Logic.Function.Basic

/-!
Projection through the SAME linear spectral program.
The projected input values must already be supplied by its scalar prefix.
A linear map in a semantic theorem is not an extra primitive scalar gate.
No compiler for the nonlinear oriented prefix is constructed here.
-/

namespace INTTProjection

open scoped BigOperators

variable {R A I : Type*} [CommSemiring R] [AddCommMonoid A] [Module R A]

/-- Projection commutes with a finite spectral sum. -/
theorem linear_readout_projection [Fintype I]
    (projection : A →ₗ[R] R) (coeff : I → R) (values : I → A) :
    projection (∑ f, coeff f • values f) =
      ∑ f, coeff f * projection (values f) := by
  simp

#print axioms linear_readout_projection

/-- An instruction references existing wires; the output address is supplied by run. -/
inductive Gate (R : Type*) where
  | add (left right : ℕ)
  | scale (coefficient : R) (source : ℕ)

def Gate.eval (g : Gate R) (state : ℕ → A) : A :=
  match g with
  | .add left right => state left + state right
  | .scale coefficient source => coefficient • state source

/-- A shared straight-line program. One fresh wire is written per instruction. -/
def run : List (Gate R) → ℕ → (ℕ → A) → (ℕ → A)
  | [], _, state => state
  | g :: rest, next, state =>
      run rest (next + 1) (Function.update state next (g.eval state))

def gates (program : List (Gate R)) : ℕ := program.length

theorem gate_projection (projection : A →ₗ[R] R) (g : Gate R) (state : ℕ → A) :
    projection (g.eval state) = g.eval (projection ∘ state) :=
  match g with
  | .add left right => map_add projection (state left) (state right)
  | .scale coefficient source => map_smul projection coefficient (state source)

theorem step_projection (projection : A →ₗ[R] R) (g : Gate R)
    (next : ℕ) (state : ℕ → A) :
    projection ∘ Function.update state next (g.eval state) =
      Function.update (projection ∘ state) next (g.eval (projection ∘ state)) :=
  (Function.comp_update projection state next (g.eval state)).trans
    (congrArg (Function.update (projection ∘ state) next)
      (gate_projection projection g state))

/-- No gate, address or reference is changed. The initial scalar state is projected. -/
theorem program_projection (projection : A →ₗ[R] R) (program : List (Gate R)) :
    ∀ (next : ℕ) (state : ℕ → A),
      projection ∘ run program next state = run program next (projection ∘ state) :=
  List.rec
    (fun _ _ => rfl)
    (fun g rest ih next state =>
      (ih (next + 1) (Function.update state next (g.eval state))).trans
        (congrArg (run rest (next + 1)) (step_projection projection g next state)))
    program

/-- Output selection is a wire lookup, with the same counted program. -/
theorem selected_output_same_program (projection : A →ₗ[R] R)
    (program : List (Gate R)) (next : ℕ) (state : ℕ → A) (output : ℕ) :
    projection (run program next state output) =
        run program next (projection ∘ state) output ∧
      gates program = program.length :=
  ⟨congrFun (program_projection projection program next state) output, rfl⟩

#print axioms gate_projection
#print axioms step_projection
#print axioms program_projection
#print axioms selected_output_same_program

/-- At the fused spectral index, the linear program returns its common amplitude. -/
theorem fused_target_readout [Fintype I] (coeff phase : I → R)
    (kernel : (∑ f, coeff f * phase f) = 1) (core : R) :
    (∑ f, coeff f * (phase f * core)) = core := by
  simpa only [Finset.sum_mul, mul_assoc, one_mul] using
    congrArg (fun total : R => total * core) kernel

#print axioms fused_target_readout

/-- The fused final bin is independent of auxiliary inputs exactly when its core is. -/
theorem fused_target_constant_iff [Fintype I] {X : Type*} (coeff phase : I → R)
    (kernel : (∑ f, coeff f * phase f) = 1) (core : X → R) (target : R) :
    (∀ x, (∑ f, coeff f * (phase f * core x)) = target) ↔
      (∀ x, core x = target) := by
  simp only [fused_target_readout coeff phase kernel]

#print axioms fused_target_constant_iff

end INTTProjection
