"""Vérification des empreintes du projet consolidé, sans dépendance externe."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
 data=json.loads((ROOT/'manifeste.json').read_text(encoding='utf-8'));errors=[]
 for name,sha in data['sha256'].items():
  p=ROOT/name
  if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=sha:errors.append(name)
 print(json.dumps({'files_checked':len(data['sha256']),'errors':errors},ensure_ascii=False,indent=2))
 sys.exit(bool(errors))
