from pathlib import Path
import json, os
ROOT = Path(__file__).resolve().parent
selected = {key: os.environ.get(key) for key in ['LEAN_PATH', 'LEAN_SRC_PATH', 'LEAN_SYSROOT']}
(ROOT / 'mathlib-environment.json').write_text(json.dumps(selected, indent=2))
print(json.dumps(selected))
