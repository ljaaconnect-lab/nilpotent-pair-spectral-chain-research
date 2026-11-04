"""Build or verify the publication indexes and SHA-256 manifest (stdlib only)."""
from pathlib import Path
import argparse
import hashlib
import json
import re
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {'.git', '.lake', '__pycache__', '.venv', 'node_modules',
                 'reproducibility-results'}
EXCLUDED_TOP = {'output', 'tmp', 'exports'}
MANIFEST = 'publication/manifest.json'

def files():
    return sorted(p for p in ROOT.rglob('*') if p.is_file()
                  and not any(x in EXCLUDED_DIRS for x in p.relative_to(ROOT).parts[:-1])
                  and p.relative_to(ROOT).parts[0] not in EXCLUDED_TOP
                  and p.suffix not in {'.pyc', '.pyo', '.olean', '.ilean', '.ir', '.sig', '.private', '.server'})

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write_indexes():
    proofs=[]
    for p in files():
        if p.suffix != '.lean':
            continue
        text=p.read_text(encoding='utf-8-sig',errors='replace')
        path=p.relative_to(ROOT).as_posix()
        proofs.append({'path':path,'sha256':digest(p),
                       'imports':re.findall(r'^import\s+(.+)$',text,re.M),
                       'declared_theorems_and_lemmas':len(re.findall(r'^\s*(?:private\s+)?(?:theorem|lemma)\s+',text,re.M)),
                       'role':'historical-source' if path.startswith('historique/') else 'research-source',
                       'verification_claim':'Consult the associated report and its assumptions; indexing is not a proof check.'})
    (ROOT/'publication/proofs.json').write_text(json.dumps({'date':'2026-11-04','count':len(proofs),
        'scope':'All retained Lean sources, including historical candidates. No blanket verification claim.',
        'files':proofs},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    catalogue=json.loads((ROOT/'catalogue.json').read_text(encoding='utf-8-sig'))
    lines=['# Index des tentatives conservées','','Les 105 entrées du catalogue historique sont reproduites ci-dessous. Les statuts et scores sont ceux de leur campagne ; ils ne certifient pas la clôture scalaire générale. Voir le README pour l’état actuel.','','## Catalogue historique','','| Identifiant | Campagne | Statut archivé | Hypothèse / objet |','|---|---|---|---|']
    def cell(t):
        return str(t).replace('|','\\|').replace('\n',' ')[:230]
    for row in catalogue:
        lines.append('| '+ ' | '.join(cell(row.get(k,'')) for k in ['id','campagne','statut_archive','hypothese'])+' |')
    lines+=['','Les chemins complets, résultats et enseignements se trouvent dans [catalogue.json](../catalogue.json).','','## Notes complémentaires récentes','']
    for p in sorted((ROOT/'documents').glob('*.md')):
        rel=p.relative_to(ROOT).as_posix()
        lines.append(f'- [{p.stem}](../{rel})')
    lines+=['','## Sources Lean','','L’index exhaustif [proofs.json](proofs.json) contient chaque chemin, son empreinte et ses imports. Les sources de candidats historiques sont conservées, y compris les pistes corrigées ou non retenues.','']
    (ROOT/'publication/attempts.md').write_text('\n'.join(lines),encoding='utf-8')
    paths=files()
    records=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)}
             for p in paths if p.relative_to(ROOT).as_posix()!=MANIFEST]
    data={'date':'2026-11-04','algorithm':'sha256','manifest_excludes_itself':True,
          'current_manuscript_included':False,'file_count':len(records),
          'total_bytes':sum(r['bytes'] for r in records),
          'by_extension':dict(Counter(Path(r['path']).suffix for r in records)), 'files':records}
    (ROOT/MANIFEST).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return data

def verify():
    data=json.loads((ROOT/MANIFEST).read_text(encoding='utf-8'))
    errors=[]
    for r in data['files']:
        p=ROOT/r['path']
        if not p.is_file() or p.stat().st_size!=r['bytes'] or digest(p)!=r['sha256']:
            errors.append(r['path'])
    actual={p.relative_to(ROOT).as_posix() for p in files()}-{MANIFEST}
    expected={r['path'] for r in data['files']}
    errors+=sorted(actual^expected)
    forbidden=list((ROOT/'output').rglob('*')) if (ROOT/'output').exists() else []
    errors += [str(p.relative_to(ROOT)) for p in forbidden if p.is_file() and p.suffix in {'.tex','.pdf'}]
    summary={'status':'passed' if not errors else 'failed','files':data['file_count'],
             'lean_sources':data['by_extension'].get('.lean',0),'errors':sorted(set(errors)),
             'current_manuscript_included':False}
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return int(bool(errors))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true',help='Rebuild indexes and manifest for a new publication state')
    args=parser.parse_args()
    if args.write:
        write_indexes()
    return verify()

if __name__=='__main__':
    raise SystemExit(main())
