from pathlib import Path
import html
import json

root = Path(__file__).resolve().parents[1]
catalogue = json.loads((root / 'catalogue.json').read_text(encoding='utf-8'))
assert len(catalogue) == 99
entry = {
    'id': 'nov01:raccord-initialisation',
    'campagne': 'Exécution scalaire partagée du raccord existant depuis a,z',
    'hypothese': 'Compiler conjointement le produit compact et le lecteur existants, sans observations ni amplitude fournies en entrée',
    'statut_archive': 'partial',
    'resultat': 'DAG partagé de portes scalaires + et × exécutant G_B, les facteurs I-L/r et l INTT depuis a,z ; 48 tables numériques jusqu à n=6 et 8 tables avec z formel ; noyau dual vérifié dans Lean ; variantes de compilation documentées',
    'enseignement': 'Le raccord choisi est conservé et exécutable sans porte différentielle abstraite. Une borne polynomiale générale du nombre de portes reste à démontrer. Les nouvelles formulations antérieures sont conservées uniquement comme pistes auxiliaires.',
    'commit': None,
    'dossier': 'etudes/2026-11-01/raccord-initialisation',
}
entry['documents'] = [p.relative_to(root).as_posix()
                      for p in sorted((root / entry['dossier']).rglob('*'))
                      if p.is_file() and '__pycache__' not in p.parts]
catalogue.append(entry)
(root / 'catalogue.json').write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
constitution = json.loads((root / 'constitution.json').read_text(encoding='utf-8'))
constitution['tentatives'] = len(catalogue)
(root / 'constitution.json').write_text(json.dumps(constitution, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
page = (root / 'index.html').read_text(encoding='utf-8')
assert '99 pistes' in page
page = page.replace('99 pistes', '100 pistes')
page = page.replace('exports/projet-annihilation-orbite-scalaire-2026-11-01.zip',
                    'exports/projet-annihilation-raccord-initialisation-2026-11-01.zip')
anchor = '<strong>Travaux les plus récents</strong>'
page = page.replace(anchor, anchor +
    '<p><a href="etudes/2026-11-01/raccord-initialisation/EXECUTION_RACCORD_EXISTANT.md"><strong>Exécution du raccord existant depuis a,z</strong></a>'
    '<br>Circuit partagé de portes scalaires, sans observations en entrée ; 48 tables numériques et 8 tables formelles vérifiées. Borne polynomiale générale non établie.</p>', 1)
details = '<details class="essai" data-search="' + html.escape(entry['id'] + ' ' + entry['campagne'].lower()) + '"><summary><span>' + entry['id'] + '</span> ' + html.escape(entry['campagne']) + '</summary>'
details += '<p>' + html.escape(entry['resultat']) + '</p><p>' + html.escape(entry['enseignement']) + '</p><p>'
details += ' · '.join('<a href="' + name + '">' + name.rsplit('/', 1)[1] + '</a>' for name in entry['documents'])
details += '</p></details>'
page = page.replace('<p class="meta" id="count"></p>', '<p class="meta" id="count"></p>' + details, 1)
(root / 'index.html').write_text(page, encoding='utf-8')
readme = (root / 'README.txt').read_text(encoding='utf-8').replace('99 pistes', '100 pistes')
old = 'Dernière reprise : etudes/2026-11-01/orbite-scalaire/ORBITE_ET_FERMETURE.md.'
assert old in readme
readme = readme.replace(old,
    'Dernière reprise : etudes/2026-11-01/raccord-initialisation/EXECUTION_RACCORD_EXISTANT.md.\n'
    'Le raccord choisi est conservé : G_B, facteurs I-L/r et INTT.\n'
    'Un compilateur partagé les traduit en portes scalaires depuis a,z.\n'
    '48 tables numériques n<=6 et 8 tables avec z formel n<=4 passent.\n'
    'Le nombre général de portes n est pas encore borné polynomialement.\n'
    'Les nouvelles formulations explorées restent seulement auxiliaires.\n\n'
    'Étape précédente : etudes/2026-11-01/orbite-scalaire/ORBITE_ET_FERMETURE.md.')
readme = readme.replace('  python outils/verifier_integrite.py\n',
    '  python outils/verifier_integrite.py\n'
    '  python outils/reproduire.py run raccord-existant\n'
    '  python outils/reproduire.py run preuves-raccord-dual\n'
    '  python outils/reproduire.py run raccord-collisions\n'
    '  python outils/reproduire.py run raccord-dual\n'
    '  python outils/reproduire.py run raccord-contractions\n')
(root / 'README.txt').write_text(readme, encoding='utf-8')
print(json.dumps({'studies': len(catalogue), 'active': entry['dossier'], 'documents': len(entry['documents'])}))
