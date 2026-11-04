"""Replay the general insertion and clock-contraction proofs independently."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,time

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'lean-operateurs'))
from lean_check import LEAN,environment


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write-report',action='store_true')
    args=p.parse_args()
    records=[]
    for name in ('ClockContraction.lean','Insertion.lean'):
        file=HERE/name
        before=hashlib.sha256(file.read_bytes()).hexdigest()
        start=time.monotonic()
        result=subprocess.run([str(LEAN),str(file)],cwd=HERE,env=environment(),
                              capture_output=True,text=True,encoding='utf-8')
        record={'source':name,'sha256':before,'source_changed_during_check':
                before!=hashlib.sha256(file.read_bytes()).hexdigest(),
                'exit_code':result.returncode,'seconds':round(time.monotonic()-start,3),
                'stdout':result.stdout,'stderr':result.stderr}
        records.append(record)
        print(json.dumps({k:v for k,v in record.items() if k not in ('stdout','stderr')}),flush=True)
    passed=all(x['exit_code']==0 and not x['source_changed_during_check'] and
               'sorryAx' not in x['stdout']+x['stderr'] and 'warning:' not in x['stdout']+x['stderr']
               for x in records)
    version=subprocess.run([str(LEAN),'--version'],capture_output=True,text=True).stdout.strip()
    report={'date':'2026-11-01','status':'passed' if passed else 'failed',
            'compiler':str(LEAN),'version':version,'independent_cli_replay':True,
            'general_polynomial_solution':False,'files':records}
    if args.write_report:
        (HERE/'lean-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status']}))
    return 0 if passed else 1


if __name__=='__main__':raise SystemExit(main())
