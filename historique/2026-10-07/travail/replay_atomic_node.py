"""One fresh committed replay of a new elementary proof file, with axiom audit."""
import argparse, hashlib, json, os, re, subprocess, time
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('node',choices=['n75','n76']);args=parser.parse_args()
ROOT=Path(__file__).resolve().parent;REPO=ROOT/'research';NODE=args.node
AGENT=ROOT/('wt-'+NODE);WT=ROOT/('wt-'+NODE+'-independent')
GIT=Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')
LEAN=Path('C:/Users/REGIS/Documents/Codex/runtimes/elan/toolchains/leanprover--lean4---v4.34.1/bin/lean.exe')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def git(*arguments):
    return subprocess.run([str(GIT),'-c','safe.directory='+REPO.as_posix(),'-c','core.autocrlf=false',
                           '-C',str(REPO),*arguments],capture_output=True,text=True,check=True).stdout.strip()
commit=git('rev-parse','arbor/'+NODE)
resultfile=ROOT/(NODE+'-independent-replay.json')
if WT.exists():
    assert git('-C',str(WT),'rev-parse','HEAD')==commit
    previous=json.loads(resultfile.read_text(encoding='utf-8'))
    assert previous['exit_code']!=0, 'Do not repeat a successful replay'
    attempts=len(list(ROOT.glob(NODE+'-independent-replay-attempt-*.json')))+1
    resultfile.rename(ROOT/(NODE+f'-independent-replay-attempt-{attempts:02d}.json'))
else:
    git('worktree','add','--detach',str(WT),commit)
report=json.loads((WT/(NODE+'-strict-report.json')).read_text(encoding='utf-8'))
source=WT/Path(report['source']).name;original=AGENT/Path(report['source']).name
assert source.resolve().parent==WT.resolve()
assert sha(original)==report['source_sha256']
assert source.read_bytes()==original.read_bytes(), 'Commit replay must be byte-identical'
assert not re.search(r'\b(sorry|axiom|admit|native_decide)\b',source.read_text(encoding='utf-8'))
prepared=json.loads((ROOT/'mathlib-environment.json').read_text(encoding='utf-8-sig'))
env=os.environ.copy();env.update(prepared)
cache=ROOT/'delivered-proof-cache'
old=json.loads((cache/'replay-report.json').read_text(encoding='utf-8'))
for item in old['sources']:
    assert item['exit_code']==0
    assert sha(ROOT.parent/'outputs/conjecture-1-5-suite/proofs'/item['source'])==item['source_sha256']
inherited=json.loads((ROOT/'wt-n73/n73-dependency-provenance.json').read_text(encoding='utf-8'))
for item in inherited['dependencies'].values():
    assert sha(Path(item['source_path']))==item['source_sha256']
    assert sha(Path(item['compiled_path']))==item['compiled_sha256']
if NODE=='n75':
    dep=json.loads((AGENT/'n75-dependency-build.json').read_text(encoding='utf-8'))
    assert dep['exit_code']==0
    assert sha(ROOT/'mathlib/Mathlib/LinearAlgebra/Matrix/SchurComplement.lean')==dep['source_sha256']
    assert sha(ROOT/'mathlib/.lake/build/lib/lean/Mathlib/LinearAlgebra/Matrix/SchurComplement.olean')==dep['compiled_sha256']
extra=[]
if NODE=='n76':
    baseline=json.loads((ROOT/'n73-independent-replay.json').read_text(encoding='utf-8'))
    assert baseline['baseline_verified'] and baseline['exit_code']==0
    directory=ROOT/'wt-n73-independent'
    assert sha(directory/'ActualClosedSubsetTransfer.lean')==baseline['source_sha256']
    assert sha(directory/'ActualClosedSubsetTransfer.olean')==baseline['compiled_sha256']
    extra.append(str(directory))
env['LEAN_PATH']=os.pathsep.join([str(WT),*extra,str(cache),prepared['LEAN_PATH']])
command=[str(LEAN),'-o',str(source.with_suffix('.olean')),str(source)]
started=time.monotonic()
try:
    p=subprocess.run(command,cwd=WT,env=env,capture_output=True,timeout=600)
    code,out,err=p.returncode,p.stdout,p.stderr
except subprocess.TimeoutExpired as e:
    code,out,err=124,e.stdout or b'',e.stderr or b''
stdout=out.decode('utf-8',errors='replace');stderr=err.decode('utf-8',errors='replace')
audits={name:[a.strip() for a in body.split(',') if a.strip()]
        for name,body in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",stdout,re.S)}
declarations=report.get('declarations') or [item['declaration'] for item in report['goal_statuses']]
accepted=code==0 and set(audits)==set(declarations) and all(
    set(values)<={'propext','Classical.choice','Quot.sound'} for values in audits.values())
result={'node':NODE,'commit':commit,'kind':'independent committed atomic replay',
        'source_sha256':sha(source),'raw_source_equal':True,'command':command,
        'exit_code':code,'stdout':stdout,'stderr':stderr,'audits':audits,
        'accepted_declarations':len(audits),'atomic_lemmas_verified':accepted,
        'elapsed_seconds':time.monotonic()-started,'root_conjecture_verified':False,
        'compiled_sha256':sha(source.with_suffix('.olean')) if code==0 else None}
resultfile.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:result[k] for k in ('node','exit_code','accepted_declarations','atomic_lemmas_verified','root_conjecture_verified')},indent=2))
if not accepted:print(stdout);print(stderr)
raise SystemExit(0 if accepted else 1)
