"""Validation et livraison du projet consolidé."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
import hashlib,json,os,subprocess,sys,zipfile

ROOT=Path(__file__).resolve().parents[1]
ZIPNAME='projet-annihilation-complet-2026-11-01.zip'


def main():
    assert (ROOT/'constitution.json').is_file(), 'Consolidation non terminée'
    (ROOT/'validation').mkdir(exist_ok=True)
    (ROOT/'exports').mkdir(exist_ok=True)
    (ROOT/'.gitignore').write_text('__pycache__/\n*.pyc\n.venv/\n.lake/\n/travail/\n/exports/\n',encoding='utf-8')
    readme=ROOT/'README.txt'
    readme.write_text(readme.read_text(encoding='utf-8')+'\nSTOCKAGE\nLe projet complet est stocké sur D:\\Codex\\Projets\\annihilation-collision-orientee.\nUn accès par jonction est fourni depuis le dossier outputs de la conversation.\nLes originaux de recherche restent à leurs emplacements précédents.\n',encoding='utf-8')
    index=ROOT/'index.html'
    index.write_text(index.read_text(encoding='utf-8').replace('<a href="README.txt">Guide complet</a>',
                    '<a href="README.txt">Guide complet</a><a href="exports/'+ZIPNAME+'">Archive complète</a>'),encoding='utf-8')

    checks={}
    for name,score in [('reference',1912),('gaussian',3670)]:
        folder=ROOT/'etudes/2026-10-24/chaine-complete'/name
        result=subprocess.run([sys.executable,'-X','utf8','evaluate_dev.py'],cwd=folder,
                              capture_output=True,text=True,encoding='utf-8')
        assert result.returncode==0,(name,result.stderr)
        data=json.loads(result.stdout)
        assert data['score']==score
        checks[name]=data
    primary=ROOT/'sources/papiers/annihilation_raccord_spectral_demonstrations.pdf'
    assert hashlib.sha256(primary.read_bytes()).hexdigest()=='ed1f05cd132305ec98ec4f195ae395123cc4ae68e1a137ac4a78898f4d5199f4'
    # Correspondance byte à byte des copies et des fichiers sources.
    provenance=json.loads((ROOT/'provenance.json').read_text(encoding='utf-8'))
    for entry in provenance['originaux']:
        copied=ROOT/entry['destination']
        assert copied.is_file() and hashlib.sha256(copied.read_bytes()).hexdigest()==entry['sha256'],entry['destination']
    report={'date':'2026-11-01','copies_source_verifiees':len(provenance['originaux']),
            'pistes':len(json.loads((ROOT/'catalogue.json').read_text(encoding='utf-8'))),
            'reference_pdf_sha256_verifie':True,'reproduction_depuis_nouveaux_chemins':checks,
            'lean_recompile_pendant_regroupement':False,'resolution_polynomiale_generale_obtenue':False}
    (ROOT/'validation/regroupement.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')

    files=[]
    for folder,dirs,names in os.walk(ROOT):
        dirs[:]=[d for d in dirs if d not in {'.git','__pycache__'}
                 and not (Path(folder)==ROOT and d in {'travail','exports'})]
        for name in names:
            p=Path(folder)/name
            if p.suffix=='.pyc' or p==ROOT/'manifeste.json':continue
            files.append(p)
    manifest={'date':'2026-11-01','sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                                         for p in sorted(files)}}
    (ROOT/'manifeste.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    result=subprocess.run([sys.executable,'-X','utf8','outils/verifier_integrite.py'],cwd=ROOT,
                          capture_output=True,text=True,encoding='utf-8')
    assert result.returncode==0,result.stdout+result.stderr

    def git(*args):
        r=subprocess.run(['git','-C',str(ROOT),*args],capture_output=True,text=True,encoding='utf-8')
        assert r.returncode==0,r.stderr
        return r.stdout.strip()
    git('init','-b','main')
    git('config','core.autocrlf','false')
    paths=list(manifest['sha256'])+['manifeste.json']
    pathspec=ROOT/'travail/commit-paths.bin'
    pathspec.write_bytes(b'\0'.join((':(literal)'+name).encode('utf-8') for name in paths)+b'\0')
    git('add','-f','--pathspec-from-file='+str(pathspec),'--pathspec-file-nul')
    git('-c','user.name=Codex','-c','user.email=codex@local.invalid','commit','-m',
        'Rassembler les recherches sur annihilation par collision orientee')
    commit=git('rev-parse','HEAD')

    destination=ROOT/'exports'/ZIPNAME
    with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name in paths:z.write(ROOT/name,'projet-annihilation-collision-orientee/'+name)
    with zipfile.ZipFile(destination) as z:assert z.testzip() is None
    class Links(HTMLParser):
        def __init__(self):super().__init__();self.items=[]
        def handle_starttag(self,tag,attrs):
            if tag=='a':
                value=dict(attrs).get('href','')
                if value and not value.startswith(('#','http:','https:')):self.items.append(unquote(value.split('#')[0]))
    links=Links();links.feed(index.read_text(encoding='utf-8'))
    missing=[p for p in links.items if not (ROOT/p).exists()]
    assert not missing,missing
    print(json.dumps({'projet':str(ROOT),'tentatives':report['pistes'],'fichiers_manifestes':len(files),
                      'copies_verifiees':report['copies_source_verifiees'],'liens_verifies':len(links.items),
                      'smoke_tests':{k:v['score'] for k,v in checks.items()},'commit':commit,
                      'archive':str(destination),'archive_octets':destination.stat().st_size},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
