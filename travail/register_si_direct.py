from pathlib import Path
import html
import json
import re

root = Path(__file__).resolve().parents[1]
catalogue = json.loads((root/'catalogue.json').read_text(encoding='utf-8'))
assert len(catalogue) == 103
entry = next(item for item in catalogue if item['id'] == 'nov01:borne-chaine-generale')
entry['resultat'] = ('Recomptage fusionné conservé ; preuve S_I(2m) >= binom(2m,m) >= 2^m '
    'pour le compilateur direct fixé ; témoins structuraux et sémantiques vérifiés, comptage combinatoire Lean')
entry['enseignement'] = ('Cette borne inférieure porte sur les nœuds du compilateur retenu, '
    'pas sur tous les circuits. La recherche polynomiale doit modifier la compilation avant création '
    'des dérivées ; aucun résultat général de polynomialité ou d impossibilité n est affirmé.')
entry['documents'] = [p.relative_to(root).as_posix() for p in sorted((root/entry['dossier']).rglob('*'))
                      if p.is_file() and '__pycache__' not in p.parts]
(root/'catalogue.json').write_text(json.dumps(catalogue, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
page = (root/'index.html').read_text(encoding='utf-8')
page = page.replace('exports/projet-annihilation-fusion-borne-revisee-2026-11-01.zip',
                    'exports/projet-annihilation-prefixe-direct-2026-11-01.zip')
old = '<p><a href="etudes/2026-11-01/borne-chaine-generale/BORNE_REVISEE_APRES_FUSION.md"><strong>Borne recomptée après fusion</strong></a><br>Préfixe partagé + 4n²−3n+2 portes ; spectral fusionné. Borne polynomiale générale du préfixe non obtenue.</p>'
new = ('<p><a href="etudes/2026-11-01/borne-chaine-generale/si-direct/CROISSANCE_DAG_DIRECT.md"><strong>Taille du préfixe du compilateur direct</strong></a>'
       '<br>Au moins binom(2m,m) portes pour n=2m dans ce compilateur précis. La recherche d une autre réalisation polynomiale reste ouverte.</p>')
assert old in page
page = page.replace(old, new, 1)
details = '<details class="essai" data-search="'+html.escape(entry['id']+' '+entry['campagne'].lower())+'"><summary><span>'+entry['id']+'</span> '+html.escape(entry['campagne'])+'</summary>'
details += '<p>'+html.escape(entry['resultat'])+'</p><p>'+html.escape(entry['enseignement'])+'</p><p>'
details += ' · '.join('<a href="'+name+'">'+name.rsplit('/', 1)[1]+'</a>' for name in entry['documents'])
details += '</p></details>'
page, count = re.subn(r'<details class="essai" data-search="nov01:borne-chaine-generale [^"]*">.*?</details>',
                     lambda match: details, page, count=1, flags=re.S)
assert count == 1
(root/'index.html').write_text(page, encoding='utf-8')
readme = (root/'README.txt').read_text(encoding='utf-8')
anchor = 'Dernière reprise : etudes/2026-11-01/borne-chaine-generale/RESULTAT.md.\n'
assert anchor in readme
readme = readme.replace(anchor, anchor +
    'Le préfixe du compilateur direct fixé possède au moins binom(2m,m) portes\n'
    'pour n=2m>=4. Preuve dans borne-chaine-generale/si-direct/.\n'
    'Ce résultat ne borne pas la taille des autres circuits possibles.\n', 1)
(root/'README.txt').write_text(readme, encoding='utf-8')
reproducer = (root/'outils/reproduire.py').read_text(encoding='utf-8')
assert "'taille-prefixe-direct'" not in reproducer
reproducer = reproducer.replace('JOBS={\n', 'JOBS={\n'
    " 'taille-prefixe-direct':('etudes/2026-11-01/borne-chaine-generale/si-direct','verify_derivative_roots.py'),\n"
    " 'preuve-comptage-direct':('etudes/2026-11-01/borne-chaine-generale/lean','replay_direct_dag_counting.py'),\n", 1)
(root/'outils/reproduire.py').write_text(reproducer, encoding='utf-8')
with (root/'documents/CADRE_ACTUEL.md').open('a', encoding='utf-8') as handle:
    handle.write('\n## Taille du préfixe défini et poursuite de la fusion — 1 novembre 2026\n\n'
        'Une preuve spécifique au compilateur direct existant établit désormais\n'
        'S_I^(1)(2m) >= binom(2m,m) >= 2^m pour m>=2. Ses premières passes\n'
        'créent des racines de dérivées distinctes qui restent atteignables\n'
        'après s=1. Cette conclusion dépend de son partage syntaxique et de\n'
        'ses règles de simplification ; elle ne concerne pas tous les circuits\n'
        'scalaires pour la même sortie. Voir si-direct/CROISSANCE_DAG_DIRECT.md\n'
        'dans l étude borne-chaine-generale.\n\n'
        'Le noyau Lean vérifie uniquement le lemme combinatoire de comptage\n'
        'et ses conséquences conditionnelles à une injection, pas le code\n'
        'Python ni le théorème complet d atteignabilité. La preuve de ce\n'
        'dernier est écrite, relue indépendamment et contrôlée sur le code.\n\n'
        'L auteur demande de poursuivre la recherche polynomiale. La cible\n'
        'active est une compilation qui fusionne avant de créer ces dérivées,\n'
        'toujours sans jets, logarithmes, moments gratuits ni amplitude\n'
        'terminale en entrée. Aucune telle borne globale n est encore obtenue.\n')
print(json.dumps({'studies': len(catalogue), 'documents': len(entry['documents'])}))
