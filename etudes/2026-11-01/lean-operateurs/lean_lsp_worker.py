"""Persistent local Lean server to check one proof step at a time."""
from pathlib import Path
from queue import Queue,Empty
import json,subprocess,threading,time,sys,os
from lean_check import LEAN,BUILD,environment

sys.stdout.reconfigure(encoding='utf-8')

DIR=BUILD/'lsp';DIR.mkdir(parents=True,exist_ok=True)
HERE=Path(__file__).resolve().parent
messages=Queue()
p=subprocess.Popen([str(LEAN),'--server'],cwd=HERE,env=environment(),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
(DIR/'pid.json').write_text(json.dumps({'python':os.getpid(),'lean':p.pid}),encoding='utf-8')

def receive():
    while True:
        headers={}
        while True:
            line=p.stdout.readline()
            if not line:return
            if line in (b'\r\n',b'\n'):break
            k,v=line.decode().split(':',1);headers[k.lower()]=v.strip()
        data=p.stdout.read(int(headers['content-length']))
        messages.put(json.loads(data))
threading.Thread(target=receive,daemon=True).start()
def stderr():
    with (DIR/'stderr.log').open('ab') as out:
        while True:
            line=p.stderr.readline()
            if not line:return
            out.write(line);out.flush()
threading.Thread(target=stderr,daemon=True).start()
def send(method,params,ident=None):
    message={'jsonrpc':'2.0','method':method,'params':params}
    if ident is not None:message['id']=ident
    data=json.dumps(message).encode('utf-8')
    p.stdin.write(f'Content-Length: {len(data)}\r\n\r\n'.encode()+data);p.stdin.flush()

send('initialize',{'processId':os.getpid(),'rootUri':HERE.as_uri(),'capabilities':{'textDocument':{'publishDiagnostics':{'versionSupport':True}}},'initializationOptions':{'hasWidgets':False}},1)
while True:
    msg=messages.get()
    if msg.get('id')==1:
        (DIR/'capabilities.json').write_text(json.dumps(msg,indent=2),encoding='utf-8');break
send('initialized',{})
print('Lean LSP ready',flush=True)
opened=set();versions={};diagnostics={}
seen={x.name for x in DIR.glob('request-*.json')}
while True:
    jobs=sorted(x for x in DIR.glob('request-*.json') if x.name not in seen)
    if not jobs:
        time.sleep(.05);continue
    for request in jobs:
        seen.add(request.name);job=json.loads(request.read_text(encoding='utf-8'))
        if job.get('stop'):
            send('shutdown',None,2);send('exit',None)
            try:p.wait(timeout=5)
            except subprocess.TimeoutExpired:p.terminate()
            print('Lean LSP stopped',flush=True);raise SystemExit(0)
        path=Path(job['file']).resolve();uri=path.as_uri();text=path.read_text(encoding='utf-8')
        version=versions.get(uri,0)+1;versions[uri]=version;diagnostics[uri]=[]
        if uri not in opened:
            send('textDocument/didOpen',{'textDocument':{'uri':uri,'languageId':'lean4','version':version,'text':text}});opened.add(uri)
        else:
            send('textDocument/didChange',{'textDocument':{'uri':uri,'version':version},'contentChanges':[{'text':text}]})
        ident=1000+len(seen)
        lines=text.splitlines()
        send('textDocument/hover',{'textDocument':{'uri':uri},'position':{'line':max(0,len(lines)-1),'character':max(0,len(lines[-1])-1)}},ident)
        start=time.monotonic();hovered=False;completed=False
        while not (hovered and completed):
            msg=messages.get()
            if msg.get('method')=='textDocument/publishDiagnostics':
                params=msg['params']
                if params.get('uri')==uri and params.get('version',version)==version:diagnostics[uri]=params['diagnostics']
            if msg.get('method')=='$/lean/fileProgress':
                params=msg['params'];doc=params.get('textDocument',{})
                if doc.get('uri')==uri and doc.get('version',version)==version:
                    completed=params.get('processing')==[]
            if msg.get('id')==ident:hovered=True
        # The terminal progress notification, rather than hover alone, is
        # necessary: theorem elaboration and diagnostic reporting are async.
        barrier=ident+100000
        send('textDocument/hover',{'textDocument':{'uri':uri},'position':{'line':max(0,len(lines)-1),'character':0}},barrier)
        while True:
            msg=messages.get()
            if msg.get('method')=='textDocument/publishDiagnostics':
                params=msg['params']
                if params.get('uri')==uri and params.get('version',version)==version:diagnostics[uri]=params['diagnostics']
            if msg.get('id')==barrier:break
        # Collect diagnostics already queued immediately after the hover reply.
        time.sleep(.2)
        while True:
            try:msg=messages.get_nowait()
            except Empty:break
            if msg.get('method')=='textDocument/publishDiagnostics' and msg['params'].get('uri')==uri:
                diagnostics[uri]=msg['params']['diagnostics']
        result={'file':str(path),'version':version,'completed':completed,'seconds':round(time.monotonic()-start,3),'diagnostics':diagnostics[uri]}
        target=DIR/request.name.replace('request-','result-');temporary=target.with_suffix('.tmp')
        temporary.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');temporary.replace(target)
        print(json.dumps(result,ensure_ascii=False),flush=True)
