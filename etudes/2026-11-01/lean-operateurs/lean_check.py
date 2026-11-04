"""Run the existing Lean 4.34.1 kernel, with build products on D:."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[3]
BUILD=ROOT/'travail/lean-operateurs'
SOURCE_ENV=Path(r'C:\Users\REGIS\Documents\Codex\2026-10-07\role-context-you-are-the-lead\work\mathlib-environment.json')
LEAN=Path(r'C:\Users\REGIS\Documents\Codex\runtimes\elan\toolchains\leanprover--lean4---v4.34.1\bin\lean.exe')

def environment():
    env=os.environ.copy()
    raw=json.loads(SOURCE_ENV.read_text(encoding='utf-8'))
    for k,v in raw.items():env[k]=v.replace('\\\\','\\')
    env['LEAN_PATH']=str(BUILD/'local-cache')+';'+str(Path(__file__).resolve().parent)+';'+env['LEAN_PATH']
    return env

def run(file,output=None):
    BUILD.mkdir(parents=True,exist_ok=True)
    p=Path(file).resolve()
    cmd=[str(LEAN)]
    if output:
        out=Path(output).resolve();out.parent.mkdir(parents=True,exist_ok=True)
        cmd.extend(['-o',str(out)])
    cmd.append(str(p))
    source_sha=hashlib.sha256(p.read_bytes()).hexdigest()
    start=time.monotonic()
    result=subprocess.run(cmd,cwd=p.parent,env=environment(),capture_output=True,text=True,encoding='utf-8',errors='replace')
    report={'file':str(p),'sha256':source_sha,
            'source_changed_during_check':hashlib.sha256(p.read_bytes()).hexdigest()!=source_sha,
            'compiler':str(LEAN),'exit_code':result.returncode,'seconds':round(time.monotonic()-start,3),
            'stdout':result.stdout,'stderr':result.stderr}
    (BUILD/'last-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(result.stdout,end='');print(result.stderr,end='',file=sys.stderr)
    print(json.dumps({k:v for k,v in report.items() if k not in ['stdout','stderr']},ensure_ascii=False))
    return result.returncode

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser();parser.add_argument('file');parser.add_argument('--output')
    args=parser.parse_args();raise SystemExit(run(args.file,args.output))
