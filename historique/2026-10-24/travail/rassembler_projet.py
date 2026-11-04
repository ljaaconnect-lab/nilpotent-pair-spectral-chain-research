"""Consolidation non destructive des recherches et de leur provenance."""
from pathlib import Path
from html import escape
from collections import Counter
import hashlib
import json
import os
import shutil
import subprocess
import zipfile

BASE=Path(__file__).resolve().parents[1]
OLD=Path(r'C:\Users\REGIS\Documents\Codex\2026-10-07\role-context-you-are-the-lead')
OUT=Path(r'D:\Codex\Projets\annihilation-collision-orientee')
DATE='2026-11-01'
SKIP={'.git','.lake','__pycache__','node_modules','mathlib','mathlib-cache',
      'dependency-downloads','git-runtime','delivered-proof-cache','pfaffian-delivered-proof-cache'}
SKIP_EXT={'.pyc','.olean','.ilean','.o'}
origins=[]


def write(path,text):
    p=OUT/path
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(text,encoding='utf-8')


def dump(path,value):
    write(path,json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def copy_one(source,destination):
    target=OUT/destination
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,target)
    origins.append({'source':str(source),'destination':target.relative_to(OUT).as_posix(),
                    'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                    'bytes':target.stat().st_size})


def copy_tree(source,destination):
    for folder,dirs,files in os.walk(source):
        dirs[:]=[d for d in dirs if d not in SKIP and not (Path(folder)/d).is_symlink()]
        for name in sorted(files):
            p=Path(folder)/name
            if p.name in SKIP or p.suffix in SKIP_EXT or p.is_symlink():
                continue
            copy_one(p,Path(destination)/p.relative_to(source))


def extract(source,destination):
    dest=OUT/destination
    dest.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(source) as z:
        for item in z.infolist():
            target=(dest/item.filename).resolve()
            if not target.is_relative_to(dest.resolve()):
                raise ValueError('Archive hors du dossier cible : '+item.filename)
        z.extractall(dest)


def bundle(repo,destination):
    target=OUT/destination
    target.parent.mkdir(parents=True,exist_ok=True)
    command=['git','-c','safe.directory='+repo.as_posix(),'-C',str(repo),
             'bundle','create',str(target),'--all']
    subprocess.run(command,check=True,capture_output=True)


def messages_text(source):
    d=json.loads(source.read_text(encoding='utf-8'))
    text=[d['thread']['title'],'Export des messages publics\n']
    for turn in d['turns']:
        for msg in turn['messages']:
            label='UTILISATEUR' if msg['role']=='user' else 'ASSISTANT'
            text.extend([label+((' / '+msg['phase']) if msg.get('phase') else ''),msg['text'],''])
    return '\n'.join(text)


def build():
    OUT.mkdir(parents=True,exist_ok=False)
    (OUT/'travail').mkdir()
    # Dossiers livrés, puis instantanés de chaque essai, y compris non committés.
    copy_tree(OLD/'outputs','etudes/2026-10-07/livrables')
    copy_tree(OLD/'work','historique/2026-10-07/travail')
    copy_tree(BASE/'work','historique/2026-10-24/travail')
    for name in ['recherche_pa_2026-10-24.zip','chaine_orientee_spectrale_2026-10-24.zip']:
        copy_one(BASE/'outputs'/name,Path('archives')/name)
    extract(BASE/'outputs'/'recherche_pa_2026-10-24.zip','etudes/2026-10-24/source-scalaire')
    extract(BASE/'outputs'/'chaine_orientee_spectrale_2026-10-24.zip','etudes/2026-10-24/chaine-complete')
    copy_one(BASE/'outputs'/'construction_exacte_chaine.txt','documents/construction_exacte_chaine.txt')
    copy_one(BASE/'work'/'CHAIN_CONTRACT_20261024.md','documents/CADRE_ACTUEL.md')
    copy_one(BASE/'work'/'raccord-spectral.txt','sources/textes/raccord-spectral.txt')
    copy_one(OLD/'work'/'annihilation.txt','sources/textes/annihilation-historique.txt')
    papers=[]
    for p in sorted(Path(r'C:\Users\REGIS\Downloads').glob('*annihilation*.pdf')):
        copy_one(p,Path('sources/papiers')/p.name)
        papers.append({'nom':p.name,'chemin':'sources/papiers/'+p.name,
                       'reference_confirmee':p.name=='annihilation_raccord_spectral_demonstrations.pdf',
                       'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    dump('sources/papiers.json',papers)
    for source,name in [(BASE/'work'/'conversation_publique.json','conversation-principale'),
                        (BASE/'work'/'conversation_analyse_conjecture.json','analyse-de-conjecture')]:
        copy_one(source,Path('historique/conversations')/(name+'.json'))
        write(Path('historique/conversations')/(name+'.txt'),messages_text(source))
    for repo,label in [(OLD/'work/research','recherches-2026-10-07'),
                       (BASE/'work/scalar-search','source-scalaire-2026-10-24'),
                       (BASE/'work/chain-search','chaine-complete-2026-10-24')]:
        bundle(repo,Path('historique/git')/(label+'.bundle'))

    campaigns=[('oct07','Explorations et formalisation Lean',OLD/'work/research/.arbor/tree.json',
                'historique/2026-10-07/travail',{}),
               ('oct24-source','Recherche de source scalaire',BASE/'work/scalar-search/.arbor/tree.json',
                'historique/2026-10-24/travail',
                {'n1':'gate-projector','n2':'wt-nonlinear','n3':'wt-lifting','n4':'wt-projector',
                 'n5':'wt-nonlinear','n6':'wt-lifting'}),
               ('oct24-chaine','Chaîne complète orientation et spectral',BASE/'work/chain-search/.arbor/tree.json',
                'historique/2026-10-24/travail',
                {'n1':'wt-chain-phase','n2':'wt-chain-gaussian','n3':'wt-chain-normalization',
                 'n4':'wt-chain-phase','n5':'wt-chain-gaussian','n6':'wt-chain-normalization','n7':'wt-chain-phase'})]
    catalogue=[]
    for prefix,label,path,base,mapping in campaigns:
        tree=json.loads(path.read_text(encoding='utf-8'))
        for node_id,node in tree['nodes'].items():
            if node_id==tree['root']:
                continue
            folder=Path(base)/mapping.get(node_id,'wt-'+node_id)
            if not (OUT/folder).exists():
                folder=Path(base)/('research' if prefix=='oct07' else 'scalar-search')
            docs=[p.relative_to(OUT).as_posix() for p in sorted((OUT/folder).iterdir())
                  if p.is_file() and p.suffix.lower() in {'.md','.txt','.lean'}]
            catalogue.append({'id':prefix+':'+node_id,'campagne':label,
                              'hypothese':node['hypothesis'],'statut_archive':node['status'],
                              'resultat':node.get('metadata',{}).get('result',''),
                              'enseignement':node.get('insight',''),
                              'commit':node.get('metadata',{}).get('branch_ref'),
                              'dossier':folder.as_posix(),'documents':docs,
                              'dev_score':node.get('metadata',{}).get('dev_score'),
                              'test_score':node.get('metadata',{}).get('test_score')})
    dump('catalogue.json',catalogue)
    dump('provenance.json',{'date_regroupement':DATE,'sources_originales_modifiees':False,
                          'originaux':origins,'exclusions':sorted(SKIP|SKIP_EXT),
                          'motif_exclusions':'Dépendances et caches reconstruisibles ; sources, rapports, instantanés et historiques Git conservés.'})
    write('requirements.txt','sympy==1.14.0\nnumpy==2.3.5\nscipy==1.17.0\nortools==9.14.6206\n')
    write('.gitignore','__pycache__/\n*.pyc\n.venv/\n.lake/\ntravail/\n')
    write('README.txt',README.format(date=DATE,count=len(catalogue),papers=len(papers)))
    write('outils/reproduire.py',RUNNER)
    write('outils/verifier_integrite.py',VERIFY)
    write('index.html',make_html(catalogue,papers))
    dump('constitution.json',{'date':DATE,'tentatives':len(catalogue),'papiers':len(papers),
                             'fichiers_copies':len(origins),'octets_copies':sum(i['bytes'] for i in origins),
                             'resolution_polynomiale_generale_obtenue':False})
    print(json.dumps({'projet':str(OUT),'tentatives':len(catalogue),'papiers':len(papers),
                      'copies':len(origins)},ensure_ascii=False))


README='''ANNIHILATION PAR COLLISION ORIENTÉE — PROJET CONSOLIDÉ
Regroupement du {date} ; {count} pistes et tentatives recensées ; {papers} versions de papiers retrouvées.

OUVRIR index.html pour naviguer et rechercher dans les essais.
Ce dossier est un projet local autonome, prêt à ouvrir comme dossier/projet dans Codex.

CADRE ACTUEL
Construire la chaîne entière en portes scalaires polynomiales depuis les
entrées originales, orientation et spectral ensemble, sans imposer P_A en
entrée. Le cadre corrigé est documents/CADRE_ACTUEL.md. Les formulations
antérieures centrées sur une source P_A sont conservées comme historique.

La résolution polynomiale générale n'est pas obtenue dans ces travaux.
Les preuves partielles, contre-exemples et scores restent attachés à leurs
hypothèses. « merged » dans les arbres signifie référence expérimentale
retenue, et ne signifie pas conjecture résolue. Les scores de campagnes
différentes ne sont pas directement comparables.

PARCOURS CONSEILLÉ
1. sources/papiers/annihilation_raccord_spectral_demonstrations.pdf : papier confirmé.
2. documents/CADRE_ACTUEL.md : compréhension corrigée et objectif intégral.
3. documents/construction_exacte_chaine.txt : construction exacte actuelle et coût exponentiel.
4. etudes/2026-10-24/chaine-complete/ : noyaux gaussiens, polarisation,
   phases, corrections Schur–Good/Bass et réductions spectrales.
5. etudes/2026-10-24/source-scalaire/ : essais précédant le recentrage.
6. etudes/2026-10-07/livrables/ : formalisation Lean, convolutions,
   raccords, jets, préfixes, suffixes et états fermés.
7. catalogue.json / index.html : toutes les hypothèses, résultats et commits.

HISTORIQUE COMPLET
historique/ contient les instantanés des espaces de travail, les cas
non retenus, les rapports, les arbres et les messages publics disponibles
des deux conversations pertinentes. Les appels internes et le raisonnement
de l'assistant sont exclus de l'export des conversations.
Les versions des papiers sont conservées avec leurs noms et SHA256 ; leur
présence dans ce dossier n'affirme pas qu'elles ont toutes été relues ou
validées pendant ce regroupement.

historique/git/ conserve trois bundles Git autonomes. Pour explorer un
ancien état, cloner le bundle dans un nouveau dossier puis choisir le commit.
Les fichiers de travail non committés sont aussi conservés dans les
instantanés, indépendamment de ces bundles. Les originaux n'ont pas été déplacés.

VÉRIFICATION
  python outils/verifier_integrite.py
  python outils/reproduire.py list
  python outils/reproduire.py smoke
Les deux tests smoke rejouent des circuits exacts de la chaîne complète.
Ils ne prouvent pas une borne polynomiale.

Les quatre dépendances Python expérimentales sont consignées dans
requirements.txt. Les vérificateurs de base utilisent la bibliothèque
standard ; les expériences symboliques, numériques et CP-SAT utilisent
respectivement SymPy, NumPy/SciPy et OR-Tools.

LEAN
Les sources .lean, lean-toolchain, manifestes Lake et rapports de compilation
historiques sont conservés. Les bibliothèques Mathlib, exécutables et caches
compilés ne sont pas dupliqués. Rejouer une compilation Lean exige l'outil
et les dépendances indiqués dans les README et scripts de chaque livraison.
Le regroupement n'a pas relancé les milliers de compilations/essais anciens.

POUR REPRENDRE
Travailler dans travail/ ou sur une nouvelle branche Git. Garder les essais
historiques intacts, noter le cadre, les entrées, la fusion, le lecteur et
le coût total de chaque nouvelle représentation. Aucune impossibilité
générale n'est déduite des modèles restreints qui ont échoué.
'''

RUNNER='''"""Commandes de reproduction depuis le dossier consolidé."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JOBS={
 'reference':('etudes/2026-10-24/chaine-complete/reference','evaluate_dev.py'),
 'gaussian':('etudes/2026-10-24/chaine-complete/gaussian','evaluate_dev.py'),
 'phases':('etudes/2026-10-24/chaine-complete/phases_spectral','verify_phase_chain.py'),
 'cycles':('etudes/2026-10-24/chaine-complete/normalization','verify_trace_correction.py'),
 'residu6':('etudes/2026-10-24/chaine-complete/normalization','verify_residue6.py'),
 'hardcore':('etudes/2026-10-24/chaine-complete/phases_spectral','verify_spectral_hardcore.py')}
def run(name):
 folder,script=JOBS[name]
 p=subprocess.run([sys.executable,'-X','utf8',script],cwd=ROOT/folder,text=True,encoding='utf-8',capture_output=True)
 print(p.stdout,end='')
 if p.returncode:
  print(p.stderr,file=sys.stderr);raise SystemExit(p.returncode)
 return json.loads(p.stdout) if name in ('reference','gaussian') else {'exit_code':0}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('commande',choices=['list','run','smoke']);p.add_argument('essai',nargs='?',choices=list(JOBS));a=p.parse_args()
 if a.commande=='list':
  for k,(folder,script) in JOBS.items():print(k,':',folder+'/'+script)
 elif a.commande=='run':
  if not a.essai:p.error('préciser un essai')
  run(a.essai)
 else:
  results={name:run(name) for name in ['reference','gaussian']}
  assert results['reference']['score']==1912 and results['gaussian']['score']==3670
  print(json.dumps({'relocation_verified':True,'general_polynomial_proof':False},indent=2))
'''

VERIFY='''"""Vérification des empreintes du projet consolidé, sans dépendance externe."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
 data=json.loads((ROOT/'manifeste.json').read_text(encoding='utf-8'));errors=[]
 for name,sha in data['sha256'].items():
  p=ROOT/name
  if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=sha:errors.append(name)
 print(json.dumps({'files_checked':len(data['sha256']),'errors':errors},ensure_ascii=False,indent=2))
 sys.exit(bool(errors))
'''


def make_html(catalogue,papers):
    nodes=[]
    for item in catalogue:
        docs=' · '.join('<a href="'+escape(p,quote=True)+'">'+escape(Path(p).name)+'</a>' for p in item['documents'])
        hay=escape(' '.join(str(item.get(k,'')) for k in ['id','campagne','hypothese','resultat','enseignement']).lower(),quote=True)
        nodes.append('<details class="essai" data-search="'+hay+'"><summary><span>'+escape(item['id'])+'</span> '+escape(item['hypothese'])+'</summary>'
                     '<p class="meta">'+escape(item['campagne'])+' · statut archivé : '+escape(item['statut_archive'])+'</p>'
                     '<p>'+escape(item['resultat'] or 'Voir les notes et l’arbre archivés.')+'</p>'
                     '<p>'+escape(item['enseignement'])+'</p><p class="meta">Commit : '+escape(str(item['commit']))+'</p><p>'+docs+'</p></details>')
    paperlinks=''.join('<li><a href="'+escape(p['chemin'])+'">'+escape(p['nom'])+'</a>'+(' — référence confirmée' if p['reference_confirmee'] else '')+'</li>' for p in papers)
    return '''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Annihilation par collision orientée</title>
<style>body{font:16px/1.6 system-ui,sans-serif;color:#20242b;background:#fafaf8;max-width:1120px;margin:45px auto;padding:0 24px}h1{font-size:30px;line-height:1.2}h2{font-size:22px;margin-top:40px}a{color:#244f72}nav{display:flex;gap:22px;flex-wrap:wrap;border-bottom:1px solid #cbd0d4;padding:12px 0}.cadre{border-left:3px solid #244f72;padding-left:18px;max-width:900px}.meta{font-size:13px;color:#5d6267}.chemins{display:grid;grid-template-columns:1fr 1fr;gap:12px 40px}input{font:inherit;width:100%;box-sizing:border-box;padding:10px;border:1px solid #aeb5bc;background:white;margin:12px 0}details{border-top:1px solid #d4d7da;padding:12px 0}summary{cursor:pointer}summary span{font:13px ui-monospace,monospace;margin-right:8px;color:#5d6267}pre{overflow:auto;background:#f0f1ed;padding:15px}.essai[hidden]{display:none}@media(max-width:700px){.chemins{grid-template-columns:1fr}h1{font-size:25px}}</style>
<header><p class="meta">Projet de recherche consolidé · 1 novembre 2026</p><h1>Annihilation par collision orientée</h1>
<p>'''+str(len(catalogue))+''' pistes, les sources, les circuits, les preuves Lean et les vérifications réunis dans un dossier autonome.</p></header>
<nav><a href="#cadre">Cadre</a><a href="#parcours">Parcours</a><a href="#essais">Tentatives</a><a href="#papiers">Papiers</a><a href="#reproduire">Reproduire</a><a href="README.txt">Guide complet</a></nav>
<section id="cadre"><h2>Objectif et état conservé</h2><div class="cadre"><p>Construire toute la chaîne en portes scalaires polynomiales, orientation et spectral ensemble, depuis les entrées originales, sans imposer P_A en entrée.</p><p>La résolution polynomiale générale n'est pas obtenue. Les constructions exactes, preuves partielles et échecs restent attachés à leurs hypothèses. Un score local ou un statut « merged » n'est pas une preuve de la conjecture.</p></div><a href="documents/CADRE_ACTUEL.md">Lire le cadre corrigé</a></section>
<section id="parcours"><h2>Parcours de lecture</h2><div class="chemins"><div><strong>Travaux les plus récents</strong><p><a href="documents/construction_exacte_chaine.txt">Construction exacte de la chaîne complète</a><br><a href="etudes/2026-10-24/chaine-complete/LIRE.txt">Synthèse des recherches conjointes</a><br><a href="etudes/2026-10-24/chaine-complete/gaussian/REGULAR_COMPLETION.md">Noyaux et polarisation gaussienne</a><br><a href="etudes/2026-10-24/chaine-complete/normalization/NONBACKTRACKING_RESEARCH.md">Schur–Good, Bass et cycles</a></p></div><div><strong>Formalisation et historique</strong><p><a href="etudes/2026-10-07/livrables/conjecture-1-5-closed-state/README.txt">État fermé, Lean et raccords</a><br><a href="etudes/2026-10-24/source-scalaire/LIRE_D_ABORD.md">Première recherche du 24 octobre</a><br><a href="historique/conversations/conversation-principale.txt">Conversation principale</a><br><a href="historique/conversations/analyse-de-conjecture.txt">Piste stochastique et convolution</a></p></div></div></section>
<section id="essais"><h2>Tentatives et résultats consignés</h2><p>Les identifiants distinguent les trois campagnes. Les instantanés historiques sont conservés ; les hypothèses sont reprises dans leur langue originale.</p><label for="search">Rechercher une méthode, un identifiant ou un résultat</label><input id="search" type="search" placeholder="Ex. Pfaffian, Fourier, Newton, collision, n77…"><p class="meta" id="count"></p>'''+''.join(nodes)+'''</section>
<section id="papiers"><h2>Versions des papiers</h2><p>La référence confirmée reste le papier de raccordement de 63 pages. Les autres versions sont conservées comme sources, sans nouvelle validation de leurs affirmations pendant ce regroupement.</p><ul>'''+paperlinks+'''</ul></section>
<section id="reproduire"><h2>Vérifier et reprendre</h2><pre>python outils/verifier_integrite.py
python outils/reproduire.py list
python outils/reproduire.py smoke</pre><p><a href="catalogue.json">Catalogue structuré</a> · <a href="provenance.json">Origine de chaque copie</a> · <a href="manifeste.json">Empreintes du projet</a> · <a href="requirements.txt">Dépendances Python</a></p><p>Les trois historiques Git sont dans historique/git/. Les caches Mathlib et exécutables sont reconstruisibles et ne sont pas dupliqués ; les sources et rapports Lean sont conservés. Les originaux restent à leur emplacement.</p></section>
<script>const input=document.getElementById('search'),rows=[...document.querySelectorAll('.essai')],count=document.getElementById('count');function update(){const q=input.value.toLocaleLowerCase().trim();let n=0;for(const r of rows){r.hidden=q&&!r.dataset.search.includes(q);if(!r.hidden)n++;}count.textContent=n+' / '+rows.length+' pistes affichées';}input.addEventListener('input',update);update();</script></html>'''


if __name__=='__main__':build()
