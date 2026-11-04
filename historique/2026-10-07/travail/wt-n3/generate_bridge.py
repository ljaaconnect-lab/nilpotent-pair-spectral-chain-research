"""Generate a small Lean bridge from exact, checked SymPy identities.

Generation and symbolic checks are not Lean verification. Run verify_bridge.py
separately. The complexity conjecture is deliberately not a Lean declaration.
"""
import hashlib
import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parent
alpha, beta, t = sp.symbols("alpha beta t")
factored = (alpha * t**2 - beta * t) * (t - t**2)
expanded = sp.expand(factored)
central = sp.Poly(1 + t**6 + expanded, t).coeff_monomial(t**3)
assert sp.expand(expanded - (-alpha * t**4 + (alpha + beta) * t**3 - beta * t**2)) == 0
assert sp.expand(central - alpha - beta) == 0

# Use only single-tactic candidates. Compiler unavailability does not justify
# extending a tactic script or claiming any tactic has succeeded.
source = """import Mathlib

/- Generated from exact SymPy n = 2 checks. This file is an UNVERIFIED
   candidate until the strict compiler and axiom checks have succeeded.
   It makes no asymptotic arithmetic circuit assertion. -/

namespace CollisionBridge

theorem n2_pair_factorization {R : Type*} [CommRing R] (a b t : R) :
    (a * t ^ 2 - b * t) * (t - t ^ 2) =
      -b * t ^ 2 + (a + b) * t ^ 3 - a * t ^ 4 := by
  ring

theorem n2_central_coeff (a b : ℚ) :
    ((1 : Polynomial ℚ) - Polynomial.C b * Polynomial.X ^ 2 +
      Polynomial.C (a + b) * Polynomial.X ^ 3 -
      Polynomial.C a * Polynomial.X ^ 4 + Polynomial.X ^ 6).coeff 3 =
      a + b := by
  simp

#print axioms CollisionBridge.n2_pair_factorization
#print axioms CollisionBridge.n2_central_coeff

end CollisionBridge
"""
path = ROOT / "GeneratedBridge.lean"
path.write_text(source, encoding="utf-8")

def lean_expression(expr):
    """Tiny total translator for the validated commutative polynomial terms."""
    if expr in (alpha, beta, t):
        return {alpha: "a", beta: "b", t: "t"}[expr]
    if expr.is_Integer:
        return str(expr) if expr >= 0 else f"({expr})"
    if expr.is_Add:
        return "(" + " + ".join(lean_expression(arg) for arg in expr.args) + ")"
    if expr.is_Mul:
        return "(" + " * ".join(lean_expression(arg) for arg in expr.args) + ")"
    if expr.is_Pow and expr.exp.is_Integer and expr.exp >= 0:
        return f"({lean_expression(expr.base)} ^ {expr.exp})"
    raise ValueError(f"Unsupported Lean translation term: {expr!r}")

first = sp.Poly(alpha*t**2-beta*t, t)
second = sp.Poly(t-t**2, t)
first_list = "[" + ", ".join(lean_expression(first.coeff_monomial(t**i)) for i in range(3)) + "]"
second_list = "[" + ", ".join(lean_expression(second.coeff_monomial(t**i)) for i in range(3)) + "]"
core_generated = f"""import Std

/- Generated from checked SymPy polynomial expressions; run the strict verifier. -/
namespace GeneratedCollisionN2

theorem factorization {{R : Type}} [Lean.Grind.CommRing R] (a b t : R) :
    {lean_expression(factored)} = {lean_expression(expanded)} := by
  grind

def listCoeff (p : List Rat) (k : Nat) : Rat := (p[k]?).getD 0
def convolutionCoeff (p q : List Rat) (k : Nat) : Rat :=
  ((List.range (k + 1)).map
    (fun i => listCoeff p i * listCoeff q (k - i))).foldr (· + ·) 0

theorem central_convolution (a b : Rat) :
    convolutionCoeff {first_list} {second_list} 3 = {lean_expression(central)} := by
  simp [convolutionCoeff, listCoeff, List.range_succ]
  grind

#print axioms GeneratedCollisionN2.factorization
#print axioms GeneratedCollisionN2.central_convolution
end GeneratedCollisionN2
"""
(ROOT / "GeneratedCoreN2.lean").write_text(core_generated, encoding="utf-8")

core_helpers = ["decode_head", "decode_tail", "encodeDigits_injective",
                "central_label_iff", "orbit_stabilizes", "n2_pair_factorization",
                "n2_central_convolution"]
sources = {
    "GeneratedBridge.lean": {
        "sha256": hashlib.sha256(source.encode()).hexdigest(),
        "theorems": ["CollisionBridge.n2_pair_factorization", "CollisionBridge.n2_central_coeff"],
        "scope": "Mathlib draft, dependency unavailable",
    },
    "GeneratedCoreN2.lean": {
        "sha256": hashlib.sha256(core_generated.encode()).hexdigest(),
        "theorems": ["GeneratedCollisionN2.factorization", "GeneratedCollisionN2.central_convolution"],
        "scope": "Generated n2 factorization and rational list-coefficient convolution",
    },
    "CoreBridge.lean": {
        "sha256": hashlib.sha256((ROOT / "CoreBridge.lean").read_text(encoding="utf-8").encode()).hexdigest(),
        "theorems": ["CollisionCoreBridge." + name for name in core_helpers],
        "scope": "Core algebraic helper lemmas, no root circuit-complexity assertion",
    },
}
report = {
    "generator": "SymPy-to-Lean single-tactic bridge",
    "sympy_version": sp.__version__,
    "validated_n": 2,
    "H_factorized": str(factored),
    "H_expanded": str(expanded),
    "Hhat_expanded": str(1 + t**6 + expanded),
    "K": 3,
    "central": str(central),
    "symbolic_checks_passed": 2,
    "theorems": ["CollisionBridge.n2_pair_factorization", "CollisionBridge.n2_central_coeff"],
    "generated_source_sha256": hashlib.sha256(source.encode()).hexdigest(),
    "sources": sources,
    "lean_verified": False,
    "root_conjecture_verified": False,
    "scope": "Finite n=2 identity generation; no general proof or complexity bound.",
}
(ROOT / "generation-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
