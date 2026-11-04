from pathlib import Path
import html
import json

root = Path(__file__).resolve().parents[1]
folder = 'etudes/2026-11-01/reprise-flot-rationnel'
catalogue = json.loads((root/'catalogue.json').read_text(encoding='utf-8'))
entry = {
    'id':'nov01:transport-rationnel',
    'campagne':'Reprise de la fermeture générale',
    'hypothese':'Fermer les insertions par un transport rationnel de l observation, puis compiler toute son action en portes scalaires',
    'statut_archive':'partial',
    'resultat':'Fusion rationnelle exacte a tout ordre, noyau algebraique verifie dans Lean ; transport triangulaire en 2(r+1) binom(d+1,3) portes ; 256 tests de fusion passent',
    'enseignement':'La fermeture polynomiale obtenue concerne les transports parametriques. La selection des colonnes distinctes reste a compiler ; aucune resolution generale de la chaine Z n est acquise.',
    'commit':None,
    'dossier':folder,
    'documents':[folder+'/'+name for name in ('REPRISE.md','ResolventFusion.lean',
        'transport.py','verify_transport.py','transport-validation.json',
        'replay_lean.py','resolvent-lean-validation.json')]
}
assert all(item['id'] != entry['id'] for item in catalogue)
catalogue.append(entry)
(root/'catalogue.json').write_text(json.dumps(catalogue,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
constitution = json.loads((root/'constitution.json').read_text(encoding='utf-8'))
constitution['tentatives'] = len(catalogue)
(root/'constitution.json').write_text(json.dumps(constitution,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
page = (root/'index.html').read_text(encoding='utf-8')
assert '94 pistes' in page
page = page.replace('94 pistes','95 pistes')
page = page.replace('exports/projet-annihilation-insertion-2026-11-01.zip',
                    'exports/projet-annihilation-transport-2026-11-01.zip')
anchor = '<strong>Travaux les plus récents</strong>'
assert anchor in page
page = page.replace(anchor,anchor+'<p><a href="'+folder+'/REPRISE.md"><strong>Reprise : fusion rationnelle et transports scalaires</strong></a><br>Fusion générale formalisée dans Lean ; transport de coût O(n⁴). La sélection des colonnes distinctes reste à compiler.</p>',1)
details = '<details class="essai" data-search="nov01:transport-rationnel reprise fusion rationnelle lean scalaire fermeture transport"><summary><span>'+entry['id']+'</span> Fusion rationnelle : action scalaire et limite de la lecture</summary>'
details += '<p>'+html.escape(entry['resultat'])+'</p><p>'+html.escape(entry['enseignement'])+'</p><p>'
details += ' · '.join('<a href="'+name+'">'+name.rsplit('/',1)[1]+'</a>' for name in entry['documents'])
details += '</p></details>'
anchor = '<p class="meta" id="count"></p>'
assert anchor in page
page = page.replace(anchor,anchor+details,1)
(root/'index.html').write_text(page,encoding='utf-8')
print(json.dumps({'tentatives':len(catalogue),'new_study':folder}))
