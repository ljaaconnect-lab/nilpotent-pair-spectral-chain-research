from pathlib import Path
import html
import json

root = Path(__file__).resolve().parents[1]
catalogue = json.loads((root/'catalogue.json').read_text(encoding='utf-8'))
assert len(catalogue) == 101
entry = {
    'id': 'nov01:fusion-double-log',
    'campagne': 'Fusion du spectral et de deux niveaux terminaux avec la lecture, double logarithme',
    'hypothese': 'Réduire le circuit scalaire complet par fusions conjointes et changement logarithmique répété',
    'statut_archive': 'partial',
    'resultat': 'Routage spectral exact, réduction au spectre atteint et fusion terminale en au plus 5n² portes ; trois variantes exécutées ; 120 tables numériques, 192 jets et 9 tables z formel ; 4 identités Lean',
    'enseignement': 'Les fusions réduisent le circuit direct à 2858 portes pour n=5, contre 35645 avec les mêmes paramètres avant fusion. Le double log testé reste plus coûteux. La borne polynomiale du préfixe différentiel reste non démontrée.',
    'commit': None,
    'dossier': 'etudes/2026-11-01/fusion-double-log',
}
entry['documents'] = [p.relative_to(root).as_posix() for p in sorted((root/entry['dossier']).rglob('*'))
                      if p.is_file() and '__pycache__' not in p.parts]
catalogue.append(entry)
(root/'catalogue.json').write_text(json.dumps(catalogue, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
constitution = json.loads((root/'constitution.json').read_text(encoding='utf-8'))
constitution['tentatives'] = len(catalogue)
(root/'constitution.json').write_text(json.dumps(constitution, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
page = (root/'index.html').read_text(encoding='utf-8')
assert '101 pistes' in page
page = page.replace('101 pistes', '102 pistes')
page = page.replace('exports/projet-annihilation-logarithmes-2026-11-01.zip',
                    'exports/projet-annihilation-fusion-double-log-2026-11-01.zip')
anchor = '<strong>Travaux les plus récents</strong>'
page = page.replace(anchor, anchor +
    '<p><a href="etudes/2026-11-01/fusion-double-log/RESULTAT_FUSIONS.md"><strong>Fusions de l architecture et double logarithme</strong></a>'
    '<br>Lecture terminale fusionnée en au plus 5n² portes et routage spectral exact. Circuit direct réduit ; borne globale encore non démontrée.</p>', 1)
details = '<details class="essai" data-search="'+html.escape(entry['id']+' '+entry['campagne'].lower())+'"><summary><span>'+entry['id']+'</span> '+html.escape(entry['campagne'])+'</summary>'
details += '<p>'+html.escape(entry['resultat'])+'</p><p>'+html.escape(entry['enseignement'])+'</p><p>'
details += ' · '.join('<a href="'+name+'">'+name.rsplit('/', 1)[1]+'</a>' for name in entry['documents'])
details += '</p></details>'
page = page.replace('<p class="meta" id="count"></p>', '<p class="meta" id="count"></p>'+details, 1)
(root/'index.html').write_text(page, encoding='utf-8')
readme = (root/'README.txt').read_text(encoding='utf-8').replace('101 pistes', '102 pistes')
old = 'Dernière reprise : etudes/2026-11-01/logarithmes-chaine/LOGARITHMES_ET_COUT.md.'
assert old in readme
readme = readme.replace(old,
    'Dernière reprise : etudes/2026-11-01/fusion-double-log/RESULTAT_FUSIONS.md.\n'
    'Fusion du spectral, des facteurs inutiles et de deux niveaux avec la lecture.\n'
    'Correction terminale démontrée en au plus 5n² portes ; double log exécuté.\n'
    '120 tables numériques, 192 jets et 9 tables z formel ; 4 identités Lean.\n'
    'Borne polynomiale générale du préfixe différentiel non démontrée.\n\n'
    'Étape précédente : etudes/2026-11-01/logarithmes-chaine/LOGARITHMES_ET_COUT.md.')
readme = readme.replace('  python outils/verifier_integrite.py\n',
    '  python outils/verifier_integrite.py\n'
    '  python outils/reproduire.py run fusion-double-log\n'
    '  python outils/reproduire.py run preuves-double-log\n')
(root/'README.txt').write_text(readme, encoding='utf-8')
reproducer = (root/'outils/reproduire.py').read_text(encoding='utf-8')
reproducer = reproducer.replace('JOBS={\n', 'JOBS={\n'
    " 'fusion-double-log':('etudes/2026-11-01/fusion-double-log','verify_fused_circuit.py'),\n"
    " 'preuves-double-log':('etudes/2026-11-01/fusion-double-log/lean','replay_lean.py'),\n", 1)
(root/'outils/reproduire.py').write_text(reproducer, encoding='utf-8')
with (root/'documents/CADRE_ACTUEL.md').open('a', encoding='utf-8') as handle:
    handle.write('\n## Fusions conjointes et double logarithme — 1 novembre 2026\n\n'
        'La chaîne est simplifiée globalement par le support terminal unique :\n'
        'un routage remplace les copies par fréquence et l INTT. Le projecteur\n'
        'est réduit aux collisions effectivement atteintes. Ses deux derniers\n'
        'niveaux se fusionnent avec la lecture, en au plus 5n² portes depuis B,\n'
        'sans dérivées ni divisions par les données. Une variante homogène\n'
        'permet log et double log formels, avec retour exact ; le second log\n'
        'ne fournit pas de gain supplémentaire dans les tests. Ces fusions\n'
        'n imposent aucune amplitude en entrée. La borne polynomiale générale\n'
        'du préfixe différentiel reste à démontrer. Voir\n'
        'etudes/2026-11-01/fusion-double-log/RESULTAT_FUSIONS.md.\n')
print(json.dumps({'studies': len(catalogue), 'documents': len(entry['documents'])}))
