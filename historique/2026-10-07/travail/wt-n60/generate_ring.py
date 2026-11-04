"""Create the explicitly separate generic-ring variant; compile it independently."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
rat = (ROOT / "GeneralPairing.lean").read_text(encoding="utf-8")
ring = rat.replace("GeneralCollisionPairing", "GeneralCollisionPairingRing")
ring = ring.replace("Rat", "R")
ring = ring.replace("SparsePolynomial", "SparsePolynomial R")
ring = ring.replace("abbrev SparsePolynomial R :=", "abbrev SparsePolynomial (R : Type) :=")
ring = ring.replace("abbrev SparsePolynomial (R : Type) := List (Nat × R)",
                    """abbrev SparsePolynomial (R : Type) := List (Nat × R)

variable {R : Type} [Lean.Grind.CommRing R]

-- These are derived law instances, not additional hypotheses or axioms.
local instance : Std.LawfulLeftIdentity (α := R) (· + ·) (0 : R) where
  left_id a := (Lean.Grind.Semiring.add_comm 0 a).trans (Lean.Grind.Semiring.add_zero a)

local instance : Std.Associative (α := R) (· + ·) where
  assoc a b c := Lean.Grind.Semiring.add_assoc a b c
""")
(ROOT / "GeneralPairingRing.lean").write_text(ring, encoding="utf-8")
manifest = {"node": "n17", "variant": "generic Lean.Grind.CommRing R",
            "source": "GeneralPairingRing.lean", "sha256": hashlib.sha256((ROOT / "GeneralPairingRing.lean").read_bytes()).hexdigest(),
            "root_conjecture_verified": False, "verified": False}
(ROOT / "n17-ring-generation.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(json.dumps(manifest, indent=2))
