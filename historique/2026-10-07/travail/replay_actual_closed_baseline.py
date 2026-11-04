"""Independent replay of the committed actual subset transfer; not a root proof."""
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REPO=ROOT/'research'
AGENT=ROOT/'wt-n73'
WT=ROOT/'wt-n73-independent'
COMMIT='97513bc5e9cca5e0b33d0844980d29da1121a234'
GIT=Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')
LEAN=Path('C:/Users/REGIS/Documents/Codex/runtimes/elan/toolchains/leanprover--lean4---v4.34.1/bin/lean.exe')
CACHE=ROOT/'delivered-proof-cache'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
subprocess.run([str(GIT),'-c','safe.directory='+REPO.as_posix(),'-c','core.autocrlf=false',
                '-C',str(REPO),'worktree','add','--detach',str(WT),COMMIT],check=True)
report=json.loads((WT/'n73-strict-report.json').read_text(encoding='utf-8'))
source=WT/report['source']
agent_source=AGENT/report['source']
assert sha(agent_source)==report['source_sha256']
assert source.read_bytes().replace(b'\r\n',b'\n')==agent_source.read_bytes().replace(b'\r\n',b'\n')
assert not re.search(r'\b(sorry|axiom|native_decide|admit)\b',source.read_text(encoding='utf-8'))
provenance=json.loads((WT/'n73-dependency-provenance.json').read_text(encoding='utf-8'))
for item in provenance['dependencies'].values():
    assert sha(Path(item['source_path']))==item['source_sha256']
    assert sha(Path(item['compiled_path']))==item['compiled_sha256']
prepared=json.loads((ROOT/'mathlib-environment.json').read_text(encoding='utf-8-sig'))
env=os.environ.copy();env.update(prepared)
env['LEAN_PATH']=str(WT)+os.pathsep+str(CACHE)+os.pathsep+prepared['LEAN_PATH']
command=[str(LEAN),'-o',str(WT/'ActualClosedSubsetTransfer.olean'),str(source)]
start=time.monotonic()
try:
    p=subprocess.run(command,cwd=WT,env=env,capture_output=True,timeout=600)
    code,out,err=p.returncode,p.stdout,p.stderr
except subprocess.TimeoutExpired as e:
    code,out,err=124,e.stdout or b'',e.stderr or b''
stdout=out.decode('utf-8',errors='replace');stderr=err.decode('utf-8',errors='replace')
audit={}
for declaration, body in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",stdout,re.S):
    audit[declaration]=[x.strip() for x in body.split(',') if x.strip()]
allowed={'propext','Classical.choice','Quot.sound'}
accepted=code==0 and set(audit)==set(report['declarations']) and all(set(v)<=allowed for v in audit.values())
result={
    'node':'n73','kind':'independent committed baseline replay','commit':COMMIT,
    'source':str(source),'source_sha256':sha(source),
    'executor_source_sha256':report['source_sha256'],
    'canonical_LF_source_equal':True,'raw_source_equal':sha(source)==report['source_sha256'],
    'command':command,'exit_code':code,'stdout':stdout,'stderr':stderr,
    'elapsed_seconds':time.monotonic()-start,'timeout_seconds':600,
    'audits':audit,'accepted_declarations':len(audit),'baseline_verified':accepted,
    'root_conjecture_verified':False,'state_dimension':'2^n',
    'compiled_sha256':sha(WT/'ActualClosedSubsetTransfer.olean') if code==0 else None,
}
(ROOT/'n73-independent-replay.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:result[k] for k in ['node','exit_code','accepted_declarations','baseline_verified','root_conjecture_verified','raw_source_equal']},indent=2))
if not accepted:
    print(stdout);print(stderr)
raise SystemExit(0 if accepted else 1)
