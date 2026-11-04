from pathlib import Path
import html
import json
import re

root = Path(__file__).resolve().parents[1]
folder = 'etudes/2026-11-01/linearisation-orientee-convolution'
old_folder = 'etudes/2026-11-01/projection-avant-derivation'
catalogue = json.loads((root/'catalogue.json').read_text(encoding='utf-8'))
old = next(e for e in catalogue if e['id'] == 'nov01:projection-avant-derivation')
old['resultat'] = ('Compilation exacte : 223 et 472 portes pour n=5 et 6 ; '
    'preuve spécifique C_Y(n)>=binom(n,n/2)>=2^(n/2) pour n puissance de deux >=4')
old['enseignement'] = ('Le préfixe se reconstruit avec au plus 5n²−4n+2 portes supplémentaires. '
    'Le compilateur à projection immédiate possède néanmoins une croissance exponentielle prouvée. '
    'Lean vérifie la conséquence arithmétique conditionnelle, pas son atteignabilité. '
    'Ce résultat ne concerne pas tous les circuits scalaires possibles.')
old['documents'] = [p.relative_to(root).as_posix() for p in sorted((root/old_folder).rglob('*'))
                    if p.is_file() and '__pycache__' not in p.parts]
study_id = 'nov01:linearisation-orientee-convolution'
entry = next((e for e in catalogue if e['id'] == study_id), None)
if entry is None:
    entry = {'id': study_id}
    catalogue.append(entry)
entry.update({
    'campagne': 'Matrice et orientation linéarisées, fusion spectrale et lecteur dual',
    'hypothese': 'Transformer ensemble les coefficients et les orientations, puis fusionner toutes les fréquences avant la lecture',
    'statut_archive': 'partial',
    'resultat': 'Un seul représentant F0 construit en O(n² log(n+1)) portes ; 496, 628, 774 portes pour n=6,7,8 ; raccord exact aux translations T_y T_z=T_(y+z)',
    'enseignement': 'Relations d’annihilation par convolution et padding exact ; 24 tables fusionnées, 4 sorties en z formel et 24 différences terminales contrôlées. Le lecteur général n’est pas compilé polynomialement. Le candidat par canaux de déterminants est exact à n=3,4 mais son filtre échoue dès n=5.',
    'commit': None, 'dossier': folder,
    'documents': [p.relative_to(root).as_posix() for p in sorted((root/folder).rglob('*'))
                  if p.is_file() and '__pycache__' not in p.parts],
})
assert len(catalogue) == 105
(root/'catalogue.json').write_text(json.dumps(catalogue, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

page = (root/'index.html').read_text(encoding='utf-8').replace('104 pistes,', '105 pistes,')
page = page.replace('exports/projet-annihilation-projection-fusionnee-2026-11-01.zip',
                    'exports/projet-annihilation-matrice-linearisee-2026-11-01.zip')
recent = ('<p id="linearisation-recente"><a href="'+folder+'/FUSION_LINEARISEE.md">'
          '<strong>Matrice linéarisée et fusion de toutes les fréquences</strong></a>'
          '<br>Un représentant auxiliaire en O(n² log(n+1)) portes ; raccord exact aux différences '
          'de translations. Lecture scalaire générale encore à compiler.</p>')
if 'id="linearisation-recente"' in page:
    page = re.sub(r'<p id="linearisation-recente">.*?</p>', lambda m: recent, page, count=1, flags=re.S)
else:
    anchor = '<strong>Travaux les plus récents</strong>'
    assert anchor in page
    page = page.replace(anchor, anchor+recent, 1)
projection = ('<p id="projection-recente"><a href="'+old_folder+'/taille/CROISSANCE_PROJECTION.md">'
    '<strong>Projection immédiate : exactitude et croissance du compilateur</strong></a>'
    '<br>Preuve de C_Y(n) ≥ 2^(n/2) pour n puissance de deux ≥4, spécifique au graphe de ce compilateur. '
    'La recherche d’une autre réalisation reste ouverte.</p>')
page = re.sub(r'<p id="projection-recente">.*?</p>', lambda m: projection, page, count=1, flags=re.S)
for item in (old, entry):
    details = '<details class="essai" data-search="'+html.escape(item['id']+' '+item['campagne'].lower())+'">'
    details += '<summary><span>'+item['id']+'</span> '+html.escape(item['campagne'])+'</summary>'
    details += '<p>'+html.escape(item['resultat'])+'</p><p>'+html.escape(item['enseignement'])+'</p><p>'
    details += ' · '.join('<a href="'+name+'">'+name.rsplit('/', 1)[1]+'</a>' for name in item['documents'])
    details += '</p></details>'
    pattern = r'<details class="essai" data-search="'+re.escape(item['id'])+r' [^"]*">.*?</details>'
    if re.search(pattern, page, flags=re.S):
        page = re.sub(pattern, lambda m: details, page, count=1, flags=re.S)
    else:
        page = page.replace('<p class="meta" id="count"></p>', '<p class="meta" id="count"></p>'+details, 1)
(root/'index.html').write_text(page, encoding='utf-8')

readme = (root/'README.txt').read_text(encoding='utf-8')
readme = readme.replace('104 pistes et tentatives', '105 pistes et tentatives')
start = readme.index('PARCOURS CONSEILLÉ\n')+len('PARCOURS CONSEILLÉ\n')
end = readme.index('Étape précédente : etudes/2026-11-01/borne-chaine-generale/RESULTAT.md.', start)
readme = readme[:start]+(
    'Dernière reprise : '+folder+'/FUSION_LINEARISEE.md.\n'
    'Matrice et orientation transformées ensemble, annihilation par convolution.\n'
    'Toutes les fréquences fusionnent en un représentant auxiliaire F0.\n'
    'Préparation O(n² log(n+1)) : 496, 628, 774 portes pour n=6,7,8.\n'
    'Raccord exact à la loi T_y T_z=T_(y+z), sans table de colonnes utilisées\n'
    'dans le compilateur de préparation. Lecture scalaire générale non résolue.\n'
    'Le candidat de lecteur par déterminants réussit n=3,4, puis son filtre\n'
    'échoue dès n=5 ; preuve et témoins dans le sous-dossier determinants/.\n\n'
    'Étape précédente : '+old_folder+'/PROJECTEUR_COMPILE.md.\n'
    'Projection immédiate exacte ; préfixe reconstruit avec un surcoût quadratique.\n'
    'Une nouvelle preuve spécifique à ce compilateur établit désormais\n'
    'C_Y(n)>=binom(n,n/2)>=2^(n/2) pour n puissance de deux >=4.\n'
    'La conséquence arithmétique est vérifiée dans Lean, conditionnellement\n'
    'à la borne inférieure ; le code du compilateur n’est pas formalisé.\n'
    'Cette preuve ne s’applique pas à toutes les autres réalisations scalaires.\n\n')+readme[end:]
(root/'README.txt').write_text(readme, encoding='utf-8')

reproducer = (root/'outils/reproduire.py').read_text(encoding='utf-8')
jobs = {
    'taille-projection': (old_folder+'/taille', 'verify_block_roots.py'),
    'preuve-croissance-projection': (old_folder+'/taille/lean', 'replay_growth.py'),
    'matrice-linearisee': (folder, 'verify_linearised_inputs.py'),
    'fusion-matrice-linearisee': (folder, 'verify_fused_linearised.py'),
    'canaux-determinants': (folder+'/determinants', 'verify_determinant_channels.py'),
}
lean_replay = root/folder/'lean/replay_preparation_bound.py'
if lean_replay.exists():
    jobs['preuve-preparation-linearisee'] = (folder+'/lean', lean_replay.name)
for job, (path, script) in jobs.items():
    if repr(job)+':' not in reproducer:
        reproducer = reproducer.replace('JOBS={\n', f'JOBS={{\n {job!r}:({path!r},{script!r}),\n', 1)
(root/'outils/reproduire.py').write_text(reproducer, encoding='utf-8')

cadre_path = root/'documents/CADRE_ACTUEL.md'
cadre = cadre_path.read_text(encoding='utf-8')
marker = '## Matrice linéarisée, convolution et fusion spectrale — 1 novembre 2026'
if marker not in cadre:
    addition = ('\n'+marker+'\n\n'
        'La demande active porte sur la matrice linéarisée pour éviter la gestion\n'
        'des colonnes utilisées. Les coefficients et la base orientée sont\n'
        'transformés ensemble. Les carrés nuls deviennent des convolutions\n'
        'quadratiques nulles, avec les relations linéaires du padding.\n\n'
        'La fusion exacte des phases permet de construire un seul F0.\n'
        'Sa préparation compte O(n² log(n+1)) portes depuis a,z et les\n'
        'variables auxiliaires x. Le compilateur construit uniquement un\n'
        'représentant ; la lecture qui élimine ces variables reste à compiler.\n'
        'Le raccord aux différences de translations est prouvé à tout ordre.\n'
        'Les 24 tables numériques, 4 tables en z formel et 24 lectures par\n'
        'différences de référence passent. Aucune borne de toute la chaîne\n'
        'scalaire n’est revendiquée à partir de cette seule préparation.\n\n'
        'Une recherche de lecteur par déterminants Fourier supprime les\n'
        'répétitions sans états de colonnes, mais le score proposé ne sépare\n'
        'pas les signes à partir de n=5. Le résidu et des témoins issus de\n'
        'a,z sont conservés ; ce défaut concerne ce candidat particulier.\n\n'
        'Le compilateur précédent à projection immédiate a désormais sa\n'
        'propre preuve de croissance C_Y(n)>=2^(n/2), pour n puissance de\n'
        'deux >=4. Cette preuve ne provient pas du transfert d’une borne\n'
        'd’un autre compilateur et ne limite pas les autres circuits possibles.\n'
        'Lean vérifie la conséquence arithmétique conditionnelle de croissance ;\n'
        'l’atteignabilité des portes est une preuve écrite contrôlée sur le code.\n\n'
        'Voir ../'+folder+'/FUSION_LINEARISEE.md.\n')
    # Preserve the previous document bytes and their historical line endings.
    with cadre_path.open('ab') as output:
        output.write(addition.encode('utf-8'))

result_path = root/'etudes/2026-11-01/borne-chaine-generale/RESULTAT.md'
result = result_path.read_text(encoding='utf-8')
old_text = ('Sa borne polynomiale générale reste non démontrée. La preuve de croissance\n'
            'ci-dessous porte uniquement sur le compilateur antérieur.')
new_text = ('Mise à jour : sa [propre preuve de croissance](../projection-avant-derivation/taille/CROISSANCE_PROJECTION.md)\n'
            'établit désormais C_Y(n)>=2^(n/2) pour n puissance de deux >=4.\n'
            'La reprise active utilise la [matrice linéarisée et la fusion spectrale](../linearisation-orientee-convolution/FUSION_LINEARISEE.md).\n'
            'La preuve ci-dessous conserve sa portée sur le compilateur antérieur.')
result = result.replace(old_text, new_text)
result_path.write_bytes(result.encode('utf-8'))
print(json.dumps({'studies': len(catalogue), 'linearisation_documents': len(entry['documents']),
                  'projection_documents': len(old['documents'])}))
