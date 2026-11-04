from pathlib import Path
import html
import json
import re

root = Path(__file__).resolve().parents[1]
catalogue = json.loads((root/'catalogue.json').read_text(encoding='utf-8'))
assert len(catalogue) == 103
entry = next(item for item in catalogue if item['id'] == 'nov01:borne-chaine-generale')
entry['resultat'] = ('Borne directe recomptée S_I + 4n²−3n+2 après partage et fusion spectrale ; '
    'lecteur fusionné en 2q portes depuis les observations ; correction terminale à défaut R conservée')
entry['enseignement'] = ('Le recomptage supprime le double compte des sommes de lignes et les copies spectrales. '
    'La borne générale du préfixe reste non démontrée ; aucune reprise par jets ni double log.')
entry['documents'] = [p.relative_to(root).as_posix() for p in sorted((root/entry['dossier']).rglob('*'))
                      if p.is_file() and '__pycache__' not in p.parts]
(root/'catalogue.json').write_text(json.dumps(catalogue, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

page = (root/'index.html').read_text(encoding='utf-8')
page = page.replace('exports/projet-annihilation-borne-generale-2026-11-01.zip',
                    'exports/projet-annihilation-fusion-borne-revisee-2026-11-01.zip')
old = '<p><a href="etudes/2026-11-01/borne-chaine-generale/RESULTAT.md"><strong>Recherche de la borne générale dans le circuit direct</strong></a><br>Extension exacte de la correction terminale ; borne polynomiale de toute la chaîne non obtenue.</p>'
new = '<p><a href="etudes/2026-11-01/borne-chaine-generale/BORNE_REVISEE_APRES_FUSION.md"><strong>Borne recomptée après fusion</strong></a><br>Préfixe partagé + 4n²−3n+2 portes ; spectral fusionné. Borne polynomiale générale du préfixe non obtenue.</p>'
assert old in page
page = page.replace(old, new, 1)
details = '<details class="essai" data-search="'+html.escape(entry['id']+' '+entry['campagne'].lower())+'"><summary><span>'+entry['id']+'</span> '+html.escape(entry['campagne'])+'</summary>'
details += '<p>'+html.escape(entry['resultat'])+'</p><p>'+html.escape(entry['enseignement'])+'</p><p>'
details += ' · '.join('<a href="'+name+'">'+name.rsplit('/', 1)[1]+'</a>' for name in entry['documents'])
details += '</p></details>'
pattern = r'<details class="essai" data-search="nov01:borne-chaine-generale [^"]*">.*?</details>'
page, count = re.subn(pattern, lambda match: details, page, count=1, flags=re.S)
assert count == 1
(root/'index.html').write_text(page, encoding='utf-8')

readme = (root/'README.txt').read_text(encoding='utf-8')
anchor = 'Dernière reprise : etudes/2026-11-01/borne-chaine-generale/RESULTAT.md.\n'
assert anchor in readme
readme = readme.replace(anchor, anchor +
    'Décompte révisé : borne-chaine-generale/BORNE_REVISEE_APRES_FUSION.md.\n'
    'Préfixe direct + 4n²−3n+2 portes ; partage et routage vérifiés n=3..6.\n', 1)
(root/'README.txt').write_text(readme, encoding='utf-8')
reproducer = (root/'outils/reproduire.py').read_text(encoding='utf-8')
assert "'recompte-fusion'" not in reproducer
reproducer = reproducer.replace('JOBS={\n', 'JOBS={\n'
    " 'recompte-fusion':('etudes/2026-11-01/borne-chaine-generale','verify_fused_cost_review.py'),\n", 1)
(root/'outils/reproduire.py').write_text(reproducer, encoding='utf-8')
with (root/'documents/CADRE_ACTUEL.md').open('a', encoding='utf-8') as handle:
    handle.write('\n## Révision de la borne avec fusion — 1 novembre 2026\n\n'
        'Le décompte est repris dans le circuit direct. Les sommes de lignes\n'
        'sont déjà présentes dans son préfixe et ne sont pas recomptées.\n'
        'La correction de deux niveaux et leur lecture ajoutent au plus\n'
        '4n²−3n+2 portes au préfixe spécialisé en s=1, préparation de B incluse.\n'
        'Le routage spectral est déjà fusionné et ne crée aucune porte.\n\n'
        'L ancienne interface de lecteur bénéficie aussi de la fusion :\n'
        'tous ses facteurs et sa lecture deviennent une contraction en 2q\n'
        'portes, q=|K_n|−1, lorsque les observations sont construites. Leur\n'
        'initialisation demeure comptée ; cette interface n est pas imposée\n'
        'au circuit direct. Aucune borne polynomiale du préfixe n est déduite\n'
        'de ces seuls gains. Voir BORNE_REVISEE_APRES_FUSION.md dans la reprise.\n')
print(json.dumps({'studies': len(catalogue), 'documents': len(entry['documents'])}))
