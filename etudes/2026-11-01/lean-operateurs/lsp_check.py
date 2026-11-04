from pathlib import Path
import argparse,json,time,sys
from lean_check import BUILD

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    p=argparse.ArgumentParser();p.add_argument('file')
    p.add_argument('--wait',type=float,default=5)
    p.add_argument('--brief',action='store_true')
    args=p.parse_args()
    d=BUILD/'lsp';d.mkdir(parents=True,exist_ok=True)
    number=1+max([int(x.stem.split('-')[1]) for x in d.glob('request-*.json')],default=0)
    name=f'{number:04d}.json'
    (d/('request-'+name)).write_text(json.dumps({'file':str(Path(args.file).resolve())}),encoding='utf-8')
    result=d/('result-'+name);end=time.monotonic()+min(args.wait,50)
    data=None
    while time.monotonic()<end:
        if result.exists():
            try:data=json.loads(result.read_text(encoding='utf-8'));break
            except (json.JSONDecodeError,PermissionError):pass
        time.sleep(.03)
    if data is not None:
        print(json.dumps({'job':number,'completed':data.get('completed',False),'seconds':data['seconds'],'diagnostics':[{'line':x['range']['start']['line']+1,'severity':x['severity'],'message':x['message'][:250] if args.brief else x['message']} for x in data['diagnostics']]},ensure_ascii=False))
    else:print(json.dumps({'job':number,'status':'pending','result':str(result)}))
