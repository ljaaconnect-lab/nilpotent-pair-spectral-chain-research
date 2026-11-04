from pathlib import Path
import html
import json
import re

root = Path(__file__).resolve().parents[1]
folder = 'etudes/2026-11-01/projection-avant-derivation'
study_id = 'nov01:projection-avant-derivation'
catalogue = json.loads((root/'catalogue.json').read_text(encoding='utf-8'))
entry = next((e for e in catalogue if e['id'] == study_id), None)
if entry is None:
    entry = {'id': study_id}
    catalogue.append(entry)
entry.update({
    'campagne': 'Projection immédiate et fusion avant les dérivations suivantes',
    'hypothese': 'Normaliser le même projecteur homogène et supprimer chaque variable traitée avant de poursuivre',
    'statut_archive': 'partial',
    'resultat': 'Compilation scalaire exacte depuis a,z : 223 et 472 portes pour n=5 et 6 ; préfixe reconstruit en 330 et 630 portes ; deux identités locales de projection vérifiées dans Lean',
    'enseignement': 'Le raccord au préfixe coûte au plus 5n²−4n+2 portes supplémentaires. Les deux queues se compensent avant compilation de la chaîne complète. Exactitude générale établie ; taille polynomiale générale non démontrée.',
    'commit': None,
    'dossier': folder,
    'documents': [p.relative_to(root).as_posix() for p in sorted((root/folder).rglob('*'))
                  if p.is_file() and '__pycache__' not in p.parts],
})
assert len(catalogue) == 104
(root/'catalogue.json').write_text(json.dumps(catalogue, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
page = (root/'index.html').read_text(encoding='utf-8')
page = page.replace('103 pistes,', '104 pistes,')
page = page.replace('exports/projet-annihilation-prefixe-direct-2026-11-01.zip',
                    'exports/projet-annihilation-projection-fusionnee-2026-11-01.zip')
recent = ('<p id="projection-recente"><a href="'+folder+'/PROJECTEUR_COMPILE.md">'
          '<strong>Projection fusionnée avant les dérivations suivantes</strong></a>'
          '<br>Chaîne exacte depuis a,z : 223 portes pour n=5, 472 pour n=6. '
          'Préfixe reconstruit avec un surcoût quadratique ; borne polynomiale générale non démontrée.</p>')
if 'id="projection-recente"' in page:
    page = re.sub(r'<p id="projection-recente">.*?</p>', lambda m: recent, page, count=1, flags=re.S)
else:
    anchor = '<strong>Travaux les plus récents</strong>'
    assert anchor in page
    page = page.replace(anchor, anchor+recent, 1)
details = '<details class="essai" data-search="'+html.escape(entry['id']+' '+entry['campagne'].lower())+'"><summary><span>'+entry['id']+'</span> '+html.escape(entry['campagne'])+'</summary>'
details += '<p>'+html.escape(entry['resultat'])+'</p><p>'+html.escape(entry['enseignement'])+'</p><p>'
details += ' · '.join('<a href="'+name+'">'+name.rsplit('/', 1)[1]+'</a>' for name in entry['documents'])
details += '</p></details>'
pattern = r'<details class="essai" data-search="nov01:projection-avant-derivation [^"]*">.*?</details>'
if re.search(pattern, page, flags=re.S):
    page = re.sub(pattern, lambda m: details, page, count=1, flags=re.S)
else:
    page = page.replace('<p class="meta" id="count"></p>', '<p class="meta" id="count"></p>'+details, 1)
(root/'index.html').write_text(page, encoding='utf-8')
readme = (root/'README.txt').read_text(encoding='utf-8')
readme = readme.replace('103 pistes et tentatives', '104 pistes et tentatives')
anchor = 'Dernière reprise : etudes/2026-11-01/borne-chaine-generale/RESULTAT.md.'
if anchor in readme:
    readme = readme.replace(anchor,
        'Dernière reprise : '+folder+'/PROJECTEUR_COMPILE.md.\n'
        'Projection immédiate exacte, puis routage spectral : 223 portes pour n=5,\n'
        '472 pour n=6 ; préfixe reconstruit en 330 et 630 portes.\n'
        'Raccord au préfixe en au plus 5n²−4n+2 portes supplémentaires.\n'
        'La borne polynomiale générale de cette nouvelle compilation reste ouverte.\n\n'
        'Étape précédente : etudes/2026-11-01/borne-chaine-generale/RESULTAT.md.', 1)
(root/'README.txt').write_text(readme, encoding='utf-8')
reproducer = (root/'outils/reproduire.py').read_text(encoding='utf-8')
jobs = {
    'projection-immediate': (folder, 'verify_direct_projection.py'),
    'prefixe-projete': (folder, 'verify_prefix_projection.py'),
}
if (root/folder/'lean/replay_projection.py').exists():
    jobs['preuve-projection'] = (folder+'/lean', 'replay_projection.py')
for job, (path, script) in jobs.items():
    if repr(job)+':' not in reproducer:
        reproducer = reproducer.replace('JOBS={\n', f'JOBS={{\n {job!r}:({path!r},{script!r}),\n', 1)
(root/'outils/reproduire.py').write_text(reproducer, encoding='utf-8')
cadre = (root/'documents/CADRE_ACTUEL.md').read_text(encoding='utf-8')
marker = '## Projection immédiate et nouvelle réalisation du préfixe — 1 novembre 2026'
if marker not in cadre:
    cadre += ('\n'+marker+'\n\n'
        'Sur les homogènes de degré n en n variables, le projecteur existant\n'
        'pi_n(L) égale le produit des s_j partial_j. La lecture se compile\n'
        'par H_(j+1)=(partial_j H_j)|s_j=0, en supprimant chaque variable\n'
        'avant la dérivation suivante. Entrées originales a,z seulement.\n\n'
        'Le circuit a été exécuté : 223 et 472 portes pour n=5 et n=6.\n'
        'La reconstruction effective du préfixe X=Y+alpha S+(beta−n alpha)C\n'
        'coûte au plus 5n²−4n+2 portes supplémentaires. La chaîne complète\n'
        'annule ces deux queues avant création de leurs portes ; la correction\n'
        'orientée et le routage spectral restent ceux déjà établis.\n\n'
        'Cette nouvelle compilation possède une preuve générale d exactitude,\n'
        'mais aucune borne polynomiale générale de taille. La borne inférieure\n'
        'du compilateur antérieur ne lui est pas transférée. Voir\n'
        '../'+folder+'/PROJECTEUR_COMPILE.md et ses scripts de reproduction.\n')
(root/'documents/CADRE_ACTUEL.md').write_text(cadre, encoding='utf-8')
result_path = root/'etudes/2026-11-01/borne-chaine-generale/RESULTAT.md'
result = result_path.read_text(encoding='utf-8')
if 'projection-avant-derivation/PROJECTEUR_COMPILE.md' not in result:
    first, rest = result.split('\n', 1)
    result = first+'\n\nSuite constructive : une [nouvelle compilation du même projecteur](../projection-avant-derivation/PROJECTEUR_COMPILE.md)\n'
    result += 'fusionne avant les dérivations suivantes. Elle produit la chaîne complète\n'
    result += 'en 472 portes pour n=6 et reconstruit le même préfixe en 630 portes.\n'
    result += 'Sa borne polynomiale générale reste non démontrée. La preuve de croissance\n'
    result += 'ci-dessous porte uniquement sur le compilateur antérieur.\n'+rest
    result_path.write_text(result, encoding='utf-8')
print(json.dumps({'studies': len(catalogue), 'new_documents': len(entry['documents'])}))
