"""Check the delivered source, or replay its exact all-n baseline in pinned Lean."""
import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent
WORK=ROOT.parent.parent/'work'
parser=argparse.ArgumentParser()
parser.add_argument('--check-only',action='store_true')
parser.add_argument('--node',choices=['n73','n75','n76'],default='n73')
parser.add_argument('--environment-file',type=Path,default=WORK/'mathlib-environment.json')
parser.add_argument('--cache-dir',type=Path,default=WORK/'delivered-proof-cache')
parser.add_argument('--lean-bin',type=Path,default=Path('C:/Users/REGIS/Documents/Codex/runtimes/elan/toolchains/leanprover--lean4---v4.34.1/bin/lean.exe'))
args=parser.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
for name,digest in manifest['sha256'].items():
    if sha(ROOT/name)!=digest: raise SystemExit('Delivered file changed: '+name)
names={'n73':'ActualClosedSubsetTransfer.lean','n75':'AtomicFirstPrefix.lean','n76':'AtomicSecondPrefix.lean'}
replay=json.loads((ROOT/('verification/'+args.node+'-independent-replay.json')).read_text(encoding='utf-8'))
source=ROOT/'proofs'/names[args.node]
assert sha(source)==replay['source_sha256']
assert replay['exit_code']==0 and replay.get('baseline_verified',replay.get('atomic_lemmas_verified',False))
if args.check_only:
    print(json.dumps({'files_verified':len(manifest['sha256']),
                      'node':args.node,'recorded_exit_code':0,'audited_declarations':len(replay['audits']),
                      'current_compiler_invocations':0,'root_conjecture_verified':False}))
    raise SystemExit(0)
provenance=json.loads((ROOT/'verification/n73-dependency-provenance.json').read_text(encoding='utf-8'))
for name,item in provenance['dependencies'].items():
    assert sha(ROOT/'proofs'/name)==item['source_sha256']
    assert sha(args.cache_dir/Path(name).with_suffix('.olean'))==item['compiled_sha256']
prepared=json.loads(args.environment_file.read_text(encoding='utf-8-sig'))
env=os.environ.copy();env.update(prepared)
extra=[]
if args.node=='n76':
    baseline=json.loads((ROOT/'verification/n73-independent-replay.json').read_text(encoding='utf-8'))
    directory=WORK/'wt-n73-independent'
    assert sha(directory/'ActualClosedSubsetTransfer.lean')==baseline['source_sha256']
    assert sha(directory/'ActualClosedSubsetTransfer.olean')==baseline['compiled_sha256']
    extra.append(str(directory))
env['LEAN_PATH']=os.pathsep.join([str(ROOT/'proofs'),*extra,str(args.cache_dir),prepared['LEAN_PATH']])
outdir=WORK/'closed-state-reproduction';outdir.mkdir(parents=True,exist_ok=True)
command=[str(args.lean_bin),'-o',str(outdir/Path(names[args.node]).with_suffix('.olean')),str(source)]
try:
    p=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,timeout=600)
    code,out,err=p.returncode,p.stdout,p.stderr
except subprocess.TimeoutExpired as e:
    code,out,err=124,e.stdout or b'',e.stderr or b''
stdout=out.decode('utf-8',errors='replace');stderr=err.decode('utf-8',errors='replace')
audit={name:[a.strip() for a in body.split(',') if a.strip()]
       for name,body in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",stdout,re.S)}
valid=code==0 and set(audit)==set(replay['audits']) and all(
    set(values)<={'propext','Classical.choice','Quot.sound'} for values in audit.values())
report={'node':args.node,'command':command,'source_sha256':sha(source),'exit_code':code,
        'stdout':stdout,'stderr':stderr,'audits':audit,'baseline_verified':valid,
        'root_conjecture_verified':False}
(outdir/(args.node+'-replay.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'exit_code':code,'baseline_verified':valid,
                  'baseline_theorems':len(audit),'root_conjecture_verified':False}))
if not valid: print(stdout);print(stderr)
raise SystemExit(0 if valid else 1)
