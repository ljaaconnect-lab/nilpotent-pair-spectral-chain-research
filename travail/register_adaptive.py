from pathlib import Path
import html
import json

root = Path(__file__).resolve().parents[1]
catalogue = json.loads((root/'catalogue.json').read_text(encoding='utf-8'))
previous_count = len(catalogue)
assert previous_count == 96
entries = [
    {
        'id': 'nov01:lecture-interrompue',
        'campagne': 'Recherche de fermeture de la lecture',
        'hypothese': 'Étudier la lecture par une transformation de circuits et des états comprimés',
        'statut_archive': 'interrupted_by_user',
        'resultat': 'Transformateur de jets vérifié sur 72 circuits et 33 tables ; noyau algébrique Lean ; deux familles restreintes testées',
        'enseignement': 'Direction interrompue à la demande de l auteur ; la recherche active revient à la construction directe de la chaîne orientée et spectrale. Aucune fermeture polynomiale obtenue.',
        'commit': None,
        'dossier': 'etudes/2026-11-01/fermeture-lecture',
    },
    {
        'id': 'nov01:schur-jet',
        'campagne': 'Construction directe de la chaîne orientée et spectrale',
        'hypothese': 'Fermer ensemble les éliminations orientées, leur état résiduel et leur lecteur avec des jets et un résolvant commun',
        'statut_archive': 'partial',
        'resultat': 'Élimination exacte sans division à tout ordre ; noyau Lean ; 14 tables numériques et 5 tables avec z formel ; fusion résiduel/lecteur vérifiée',
        'enseignement': 'Le coût scalaire actuel du cœur vaut 4*3^(n-1)-3*2^n+n+1. La fusion de plusieurs directions de jets avec lecture scalaire polynomiale reste à construire.',
        'commit': None,
        'dossier': 'etudes/2026-11-01/fermeture-adaptative',
    },
]
for entry in entries:
    assert not any(old['id'] == entry['id'] for old in catalogue)
    folder = root/entry['dossier']
    entry['documents'] = [p.relative_to(root).as_posix() for p in sorted(folder.iterdir()) if p.is_file()]
    catalogue.append(entry)
(root/'catalogue.json').write_text(json.dumps(catalogue, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
constitution = json.loads((root/'constitution.json').read_text(encoding='utf-8'))
constitution['tentatives'] = len(catalogue)
(root/'constitution.json').write_text(json.dumps(constitution, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
page = (root/'index.html').read_text(encoding='utf-8')
assert '96 pistes' in page
page = page.replace('96 pistes', '98 pistes')
page = page.replace('exports/projet-annihilation-fusion-ntt-2026-11-01.zip',
                    'exports/projet-annihilation-schur-jet-2026-11-01.zip')
anchor = '<strong>Travaux les plus récents</strong>'
page = page.replace(anchor, anchor+
    '<p><a href="etudes/2026-11-01/fermeture-adaptative/ETAT_DIRECT.md"><strong>État direct : élimination orientée et fusion Schur/jet</strong></a>'
    '<br>Chaîne complète depuis a,z ; noyau Lean et tests jusqu’à n=7. Le coût scalaire reste exponentiel.</p>', 1)
for entry in entries:
    details = '<details class="essai" data-search="'+html.escape(entry['id']+' '+entry['campagne'].lower())+'"><summary><span>'+entry['id']+'</span> '+html.escape(entry['campagne'])+'</summary>'
    details += '<p>'+html.escape(entry['resultat'])+'</p><p>'+html.escape(entry['enseignement'])+'</p><p>'
    details += ' · '.join('<a href="'+name+'">'+name.rsplit('/', 1)[1]+'</a>' for name in entry['documents'])
    details += '</p></details>'
    page = page.replace('<p class="meta" id="count"></p>', '<p class="meta" id="count"></p>'+details, 1)
(root/'index.html').write_text(page, encoding='utf-8')
readme = (root/'README.txt').read_text(encoding='utf-8').replace('96 pistes', '98 pistes')
old = 'Dernière reprise : etudes/2026-11-01/fusion-ntt/RACCORD_NTT.md.'
assert old in readme
readme = readme.replace(old,
    'Dernière reprise : etudes/2026-11-01/fermeture-adaptative/ETAT_DIRECT.md.\n'
    'Construction directe par élimination orientée sans division ; les phases\n'
    'précèdent les éliminations et une véritable INTT termine la chaîne.\n'
    'Le noyau algébrique est vérifié dans Lean ; 14 tables numériques et\n'
    '5 tables avec z formel passent. État résiduel et lecteur se regroupent\n'
    'dans un même résolvant. Le coût scalaire actuel demeure exponentiel.\n'
    'La direction de réduction de lecture a été interrompue à la demande\n'
    'de l auteur et reste uniquement dans l historique des études.\n\n'
    'Étape précédente : etudes/2026-11-01/fusion-ntt/RACCORD_NTT.md.')
readme = readme.replace('  python outils/verifier_integrite.py\n',
    '  python outils/verifier_integrite.py\n'
    '  python outils/reproduire.py run schur-jet\n'
    '  python outils/reproduire.py run preuves-schur-jet\n'
    '  python outils/reproduire.py run resolvant-partage\n')
(root/'README.txt').write_text(readme, encoding='utf-8')
print(json.dumps({'studies': len(catalogue), 'active': entries[-1]['dossier']}))
