import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WT = ROOT / 'wt-n72'
source = ROOT / 'pole_functional_candidate.py'
shutil.copyfile(source, WT/source.name)
record = {'node': 'n72', 'frozen_before_execution': True,
          'sha256': {name: hashlib.sha256((WT/name).read_bytes()).hexdigest()
                     for name in ['n72-protocol.json', source.name]}}
(WT/'n72-source-freeze.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
print(json.dumps(record))
