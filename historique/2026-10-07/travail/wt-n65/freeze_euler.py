"""Freeze source hashes before a candidate's first compiler validation."""
import hashlib
import json
from pathlib import Path
from datetime import datetime,timezone

root = Path(__file__).resolve().parent
names = ["n61-protocol.json","euler_identity.py","validate_euler_identity.py",
         "euler_compiler.py","evaluate_euler.py","candidate.py","N61_DESIGN.md"]
result = {"frozen_at_utc":datetime.now(timezone.utc).isoformat(),
          "artifact_version":"n61-euler-cofactor-v1",
          "source_hashes":{name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in names},
          "held_out_access":False,"compiler_validation_already_run":False}
path = root/"n61-source-freeze-v1.json"
if path.exists():
    raise SystemExit("Refusing to overwrite prior freeze")
path.write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
