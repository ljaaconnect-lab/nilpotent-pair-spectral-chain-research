from pathlib import Path
import html
import json

root = Path(__file__).resolve().parents[1]
catalogue = json.loads((root/'catalogue.json').read_text(encoding='utf-8'))
assert len(catalogue) == 102
entry = {
    'id': 'nov01:borne-chaine-generale',
    'campagne': 'Recherche de la borne générale dans le circuit direct, sans double log ni jets globaux',
    'hypothese': 'Fusionner le lecteur et sa lecture pour borner toute la chaîne en portes scalaires',
    'statut_archive': 'partial',
    'resultat': 'Correction terminale exacte à défaut R, O(n³) pour R=2 ; préfixe direct conservé',
    'enseignement': 'Le bloc terminal est polynomial pour R fixé. Le préfixe restant ne dispose toujours pas de borne polynomiale uniforme ; la résolution générale n est pas obtenue.',
    'commit': None,
    'dossier': 'etudes/2026-11-01/borne-chaine-generale',
}
entry['documents'] = [p.relative_to(root).as_posix() for p in sorted((root/entry['dossier']).rglob('*'))
                      if p.is_file() and '__pycache__' not in p.parts]
catalogue.append(entry)
(root/'catalogue.json').write_text(json.dumps(catalogue, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
constitution = json.loads((root/'constitution.json').read_text(encoding='utf-8'))
assert not constitution['resolution_polynomiale_generale_obtenue']
constitution['tentatives'] = len(catalogue)
(root/'constitution.json').write_text(json.dumps(constitution, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
page = (root/'index.html').read_text(encoding='utf-8')
assert '102 pistes' in page
page = page.replace('102 pistes', '103 pistes')
page = page.replace('exports/projet-annihilation-fusion-double-log-2026-11-01.zip',
                    'exports/projet-annihilation-borne-generale-2026-11-01.zip')
anchor = '<strong>Travaux les plus récents</strong>'
page = page.replace(anchor, anchor +
    '<p><a href="etudes/2026-11-01/borne-chaine-generale/RESULTAT.md"><strong>Recherche de la borne générale dans le circuit direct</strong></a>'
    '<br>Extension exacte de la correction terminale ; borne polynomiale de toute la chaîne non obtenue.</p>', 1)
details = '<details class="essai" data-search="'+html.escape(entry['id']+' '+entry['campagne'].lower())+'"><summary><span>'+entry['id']+'</span> '+html.escape(entry['campagne'])+'</summary>'
details += '<p>'+html.escape(entry['resultat'])+'</p><p>'+html.escape(entry['enseignement'])+'</p><p>'
details += ' · '.join('<a href="'+name+'">'+name.rsplit('/', 1)[1]+'</a>' for name in entry['documents'])
details += '</p></details>'
page = page.replace('<p class="meta" id="count"></p>', '<p class="meta" id="count"></p>'+details, 1)
(root/'index.html').write_text(page, encoding='utf-8')
readme = (root/'README.txt').read_text(encoding='utf-8').replace('102 pistes', '103 pistes')
old = 'Dernière reprise : etudes/2026-11-01/fusion-double-log/RESULTAT_FUSIONS.md.'
assert old in readme
readme = readme.replace(old,
    'Dernière reprise : etudes/2026-11-01/borne-chaine-generale/RESULTAT.md.\n'
    'Double logarithme et réalisation globale par jets écartés.\n'
    'Correction terminale exacte à tout défaut R<n/2,\n'
    'polynomiale pour R fixé ; O(n³) pour R=2. Le préfixe reste à borner.\n'
    'La borne polynomiale de toute la chaîne n est pas obtenue.\n\n'
    'Étape précédente : etudes/2026-11-01/fusion-double-log/RESULTAT_FUSIONS.md.')
(root/'README.txt').write_text(readme, encoding='utf-8')
reproducer = (root/'outils/reproduire.py').read_text(encoding='utf-8')
assert "'fusion-terminale-generale'" not in reproducer
reproducer = reproducer.replace('JOBS={\n', 'JOBS={\n'
    " 'fusion-terminale-generale':('etudes/2026-11-01/borne-chaine-generale','verify_terminal_fusion.py'),\n", 1)
(root/'outils/reproduire.py').write_text(reproducer, encoding='utf-8')
with (root/'documents/CADRE_ACTUEL.md').open('a', encoding='utf-8') as handle:
    handle.write('\n## Circuit direct sans double logarithme ni jets globaux — 1 novembre 2026\n\n'
        'Dernière consigne : laisser le double logarithme et établir la borne\n'
        'polynomiale de toute la chaîne. Les études logarithmiques sont désormais\n'
        'conservées comme historique. L auteur précise aussi de ne pas reprendre\n'
        'la réalisation par jets auparavant écartée. Cette voie est exclue de\n'
        'la recherche active. Les fusions spectrale et terminale restent\n'
        'valides dans le circuit direct.\n\n'
        'La correction terminale est étendue à tout défaut R<n/2, avec une borne\n'
        'polynomiale pour R fixé et une spécialisation O(n³) pour R=2. Cette\n'
        'borne laisse présent le préfixe différentiel ; aucune borne polynomiale\n'
        'uniforme de ce préfixe n a été obtenue. La correction locale travaille\n'
        'sur des petits produits marqués de degré borné par R ; elle ne\n'
        'développe pas le préfixe en jets et ne résout pas son coût général.\n'
        'Voir etudes/2026-11-01/borne-chaine-generale/RESULTAT.md.\n')
print(json.dumps({'studies': len(catalogue), 'documents': len(entry['documents'])}))
