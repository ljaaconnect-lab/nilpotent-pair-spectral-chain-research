from pathlib import Path
import html
import json

root = Path(__file__).resolve().parents[1]
catalogue = json.loads((root/'catalogue.json').read_text(encoding='utf-8'))
assert len(catalogue) == 98
entry = {
    'id': 'nov01:orbite-scalaire',
    'campagne': 'Orbite scalaire et fermeture des observations de collisions',
    'hypothese': 'Conserver les objets polynomiaux du raccord et fusionner le projecteur global sur les observations de l orbite scalaire',
    'statut_archive': 'partial',
    'resultat': 'Entrelacement exact de toutes les différences vérifié dans Lean ; état de h+1 observations, h=n(n-1)/2, fusion en h(4h+2) portes et lecture par fil ; variante NTT du projecteur partagée entre toutes les fréquences ; validations des composants et du raccord aux entrées originales',
    'enseignement': 'La fusion et la lecture de cet état sont polynomiales une fois les observations disponibles. Leur initialisation simultanée depuis a,z reste à construire ; le coût des jets ne constitue pas une borne imposée à cette architecture.',
    'commit': None,
    'dossier': 'etudes/2026-11-01/orbite-scalaire',
}
folder = root/entry['dossier']
entry['documents'] = [p.relative_to(root).as_posix() for p in sorted(folder.iterdir()) if p.is_file()]
catalogue.append(entry)
(root/'catalogue.json').write_text(json.dumps(catalogue, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
constitution = json.loads((root/'constitution.json').read_text(encoding='utf-8'))
constitution['tentatives'] = len(catalogue)
(root/'constitution.json').write_text(json.dumps(constitution, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
page = (root/'index.html').read_text(encoding='utf-8')
assert '98 pistes' in page
page = page.replace('98 pistes', '99 pistes')
page = page.replace('exports/projet-annihilation-schur-jet-2026-11-01.zip',
                    'exports/projet-annihilation-orbite-scalaire-2026-11-01.zip')
anchor = '<strong>Travaux les plus récents</strong>'
page = page.replace(anchor, anchor+
    '<p><a href="etudes/2026-11-01/orbite-scalaire/ORBITE_ET_FERMETURE.md"><strong>Objets choisis : orbite scalaire et observations de collisions</strong></a>'
    '<br>Fusion et lecture polynomiales sur h+1 observations ; entrelacement vérifié dans Lean. Initialisation depuis les données encore à construire.</p>', 1)
details = '<details class="essai" data-search="'+html.escape(entry['id']+' '+entry['campagne'].lower())+'"><summary><span>'+entry['id']+'</span> '+html.escape(entry['campagne'])+'</summary>'
details += '<p>'+html.escape(entry['resultat'])+'</p><p>'+html.escape(entry['enseignement'])+'</p><p>'
details += ' · '.join('<a href="'+name+'">'+name.rsplit('/', 1)[1]+'</a>' for name in entry['documents'])
details += '</p></details>'
page = page.replace('<p class="meta" id="count"></p>', '<p class="meta" id="count"></p>'+details, 1)
(root/'index.html').write_text(page, encoding='utf-8')
readme = (root/'README.txt').read_text(encoding='utf-8').replace('98 pistes', '99 pistes')
old = 'Dernière reprise : etudes/2026-11-01/fermeture-adaptative/ETAT_DIRECT.md.'
assert old in readme
readme = readme.replace(old,
    'Dernière reprise : etudes/2026-11-01/orbite-scalaire/ORBITE_ET_FERMETURE.md.\n'
    'Retour aux objets polynomiaux choisis : l orbite scalaire G_B porte\n'
    'les transports et leurs différences, avec entrelacement vérifié dans Lean.\n'
    'Le projecteur global ferme sur h+1 observations, h=n(n-1)/2, en\n'
    'h(4h+2) portes ; la lecture est un fil. Cette borne concerne le composant\n'
    'une fois les observations disponibles : leur construction simultanée\n'
    'depuis a,z reste à obtenir pour résoudre la chaîne générale.\n\n'
    'Une variante applique la NTT aux coefficients du projecteur, les partage\n'
    'entre toutes les fréquences, puis lit les observations avant l INTT finale.\n'
    'La preuve et le compte sont dans LINEARISATION_PROJECTEUR.md.\n\n'
    'Candidat auxiliaire : etudes/2026-11-01/fermeture-adaptative/ETAT_DIRECT.md.')
readme = readme.replace('  python outils/verifier_integrite.py\n',
    '  python outils/verifier_integrite.py\n'
    '  python outils/reproduire.py run orbite-scalaire\n'
    '  python outils/reproduire.py run projecteur-ntt\n'
    '  python outils/reproduire.py run observateur-collisions\n'
    '  python outils/reproduire.py run preuves-orbite\n')
(root/'README.txt').write_text(readme, encoding='utf-8')
print(json.dumps({'studies': len(catalogue), 'active': entry['dossier']}))
