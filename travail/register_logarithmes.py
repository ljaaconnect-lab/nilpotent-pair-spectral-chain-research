from pathlib import Path
import html
import json

root = Path(__file__).resolve().parents[1]
catalogue = json.loads((root/'catalogue.json').read_text(encoding='utf-8'))
assert len(catalogue) == 100
entry = {
    'id': 'nov01:logarithmes-chaine',
    'campagne': 'Logarithmes formels du raccord existant et élagage triangulaire',
    'hypothese': 'Introduire log/exp dans le circuit complet et vérifier le coût scalaire après retour exact',
    'statut_archive': 'partial',
    'resultat': 'Circuit log formel depuis a,z, stabilisation après binom(k,2), 40 tables numériques, 200 jets intermédiaires, 3 tables z formel ; 3 identités de conjugaison vérifiées dans Lean',
    'enseignement': 'Log/exp de séries sont polynomiaux en leur longueur et l élagage réduit les portes ; la compilation des dérivées ne donne pas encore une borne quasi-polynomiale ou polynomiale globale.',
    'commit': None,
    'dossier': 'etudes/2026-11-01/logarithmes-chaine',
}
entry['documents'] = [p.relative_to(root).as_posix() for p in sorted((root/entry['dossier']).rglob('*'))
                      if p.is_file() and '__pycache__' not in p.parts]
catalogue.append(entry)
(root/'catalogue.json').write_text(json.dumps(catalogue, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
constitution = json.loads((root/'constitution.json').read_text(encoding='utf-8'))
constitution['tentatives'] = len(catalogue)
(root/'constitution.json').write_text(json.dumps(constitution, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
page = (root/'index.html').read_text(encoding='utf-8')
assert '100 pistes' in page
page = page.replace('100 pistes', '101 pistes')
page = page.replace('exports/projet-annihilation-raccord-initialisation-2026-11-01.zip',
                    'exports/projet-annihilation-logarithmes-2026-11-01.zip')
anchor = '<strong>Travaux les plus récents</strong>'
page = page.replace(anchor, anchor +
    '<p><a href="etudes/2026-11-01/logarithmes-chaine/LOGARITHMES_ET_COUT.md"><strong>Logarithmes formels dans la chaîne complète</strong></a>'
    '<br>Transformation exacte, élagage prouvé, comparaison de portes et conjugaison Lean. Borne quasi-polynomiale ou polynomiale non établie.</p>', 1)
details = '<details class="essai" data-search="' + html.escape(entry['id']+' '+entry['campagne'].lower()) + '"><summary><span>' + entry['id'] + '</span> ' + html.escape(entry['campagne']) + '</summary>'
details += '<p>'+html.escape(entry['resultat'])+'</p><p>'+html.escape(entry['enseignement'])+'</p><p>'
details += ' · '.join('<a href="'+name+'">'+name.rsplit('/', 1)[1]+'</a>' for name in entry['documents'])
details += '</p></details>'
page = page.replace('<p class="meta" id="count"></p>', '<p class="meta" id="count"></p>'+details, 1)
(root/'index.html').write_text(page, encoding='utf-8')
readme = (root/'README.txt').read_text(encoding='utf-8').replace('100 pistes', '101 pistes')
old = 'Dernière reprise : etudes/2026-11-01/raccord-initialisation/EXECUTION_RACCORD_EXISTANT.md.'
assert old in readme
readme = readme.replace(old,
    'Dernière reprise : etudes/2026-11-01/logarithmes-chaine/LOGARITHMES_ET_COUT.md.\n'
    'Logarithmes formels dans le raccord existant, avec retour exact et élagage.\n'
    '40 tables numériques, 200 jets intermédiaires et 3 tables z formel vérifiés.\n'
    'Trois identités de conjugaison vérifiées dans Lean.\n'
    'Borne quasi-polynomiale ou polynomiale globale non établie.\n\n'
    'Étape précédente : etudes/2026-11-01/raccord-initialisation/EXECUTION_RACCORD_EXISTANT.md.')
readme = readme.replace('  python outils/verifier_integrite.py\n',
                        '  python outils/verifier_integrite.py\n'
                        '  python outils/reproduire.py run logarithmes\n'
                        '  python outils/reproduire.py run preuves-logarithmes\n')
(root/'README.txt').write_text(readme, encoding='utf-8')
reproducer = (root/'outils/reproduire.py').read_text(encoding='utf-8')
reproducer = reproducer.replace('JOBS={\n', 'JOBS={\n'
    " 'logarithmes':('etudes/2026-11-01/logarithmes-chaine','verify_log_circuit.py'),\n"
    " 'preuves-logarithmes':('etudes/2026-11-01/logarithmes-chaine/lean','replay_lean.py'),\n", 1)
(root/'outils/reproduire.py').write_text(reproducer, encoding='utf-8')
cadre = root/'documents/CADRE_ACTUEL.md'
with cadre.open('a', encoding='utf-8') as handle:
    handle.write('\n## Introduction de logarithmes — 1 novembre 2026\n\n'
        'À la demande de l auteur, une transformation logarithmique formelle\n'
        'est appliquée au même raccord, avec normalisation en epsilon et\n'
        'retour exact avant lecture spectrale. Le coefficient d ordre k\n'
        'stabilise après binom(k,2) facteurs ; cette propriété donne un\n'
        'élagage effectivement compilé et testé. Tous les log/exp sont\n'
        'développés en portes scalaires ; a,z restent les seules données\n'
        'variables aux sorties. Cette transformation n établit pas encore\n'
        'de borne générale quasi-polynomiale ou polynomiale. Voir\n'
        'etudes/2026-11-01/logarithmes-chaine/LOGARITHMES_ET_COUT.md.\n')
print(json.dumps({'studies': len(catalogue), 'documents': len(entry['documents'])}))
