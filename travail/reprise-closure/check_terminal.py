from pathlib import Path
import hashlib,json,subprocess,sys,time
sys.stdout.reconfigure(encoding='utf-8')
root=Path(r'D:\Codex\Projets\annihilation-collision-orientee')
sys.path.insert(0,str(root/'etudes/2026-11-01/lean-operateurs'))
from lean_check import LEAN,environment
source=root/'etudes/2026-11-01/fusion-ntt/TerminalDifference.lean'
sha=hashlib.sha256(source.read_bytes()).hexdigest()
start=time.monotonic()
p=subprocess.run([str(LEAN),str(source)],cwd=source.parent,env=environment(),capture_output=True,text=True,encoding='utf-8')
report={'source':str(source),'sha256':sha,'source_changed':hashlib.sha256(source.read_bytes()).hexdigest()!=sha,'exit_code':p.returncode,'seconds':round(time.monotonic()-start,3),'stdout':p.stdout,'stderr':p.stderr}
(root/'travail/reprise-closure/terminal-check.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(p.stdout,end=''); print(p.stderr,end=''); print('EXIT',p.returncode)
