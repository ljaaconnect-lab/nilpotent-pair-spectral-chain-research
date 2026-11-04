from pathlib import Path
import hashlib
import json
import re

root = Path(__file__).resolve().parents[1]
document = 'documents/ARCHITECTURE_ET_COUTS_2026-11-02.md'
readme = (root/'README.txt').read_text(encoding='utf-8')
if document not in readme:
    readme = readme.replace('INVENTAIRE DES COÛTS\n',
        'SCHÉMA ET ÉTAT DES PREUVES\n'+document+'\n'
        'Architecture après fusion, coûts établis et portée des vérifications.\n'
        'Le lecteur composé est identifié comme le bloc restant à borner.\n\n'
        'INVENTAIRE DES COÛTS\n', 1)
(root/'README.txt').write_text(readme, encoding='utf-8')
page = (root/'index.html').read_text(encoding='utf-8')
page = page.replace('exports/projet-annihilation-inventaire-couts-2026-11-02.zip',
                    'exports/projet-annihilation-architecture-couts-2026-11-02.zip')
if 'id="architecture-couts"' not in page:
    anchor = '<strong>Travaux les plus récents</strong>'
    addition = ('<p id="architecture-couts"><a href="'+document+'">'
        '<strong>Schéma de l’architecture et état des coûts</strong></a><br>'
        'Préparation scalaire, branches auxiliaires et lecteur composé ; '
        'preuves algébriques, contrôles finis et portée du certificat Lean.</p>')
    assert anchor in page
    page = page.replace(anchor, anchor+addition, 1)
(root/'index.html').write_text(page, encoding='utf-8')
archive_script = (root/'travail/archive_inventaire_couts.py').read_text(encoding='utf-8')
archive_script = archive_script.replace('exports/projet-annihilation-inventaire-couts-2026-11-02.zip',
                                        'exports/projet-annihilation-architecture-couts-2026-11-02.zip')
(root/'travail/archive_architecture_couts.py').write_text(archive_script, encoding='utf-8')

# Read-only checks of the evidence and local links used by the synthesis.
note = root/document
for target in re.findall(r'^- \[[^\]]+\]\(([^)]+)\)', note.read_text(encoding='utf-8'), flags=re.M):
    if not target.startswith(('http:', 'https:', '#')):
        assert (note.parent/target).resolve().is_file(), target
report = json.loads((root/'etudes/2026-11-01/linearisation-orientee-convolution/fused-linearised-validation.json').read_text(encoding='utf-8'))
assert report['status'] == 'passed'
assert not report['complete_scalar_Z_compiled']
for path, digest in report['source_sha256'].items():
    assert hashlib.sha256((root/path).read_bytes()).hexdigest() == digest, path
assert [(c['n'], c['coefficient_scalar_gates'], c['polynomial_representative_scalar_gates'])
        for c in report['cases'] if c['n'] >= 6] == [(6,401,496), (7,517,628), (8,647,774)]
assert sum(c['numeric_oriented_tables'] for c in report['cases']) == 24
assert sum(c['formal_z_tables'] for c in report['cases']) == 4
assert sum(c['dual_translation_difference_checks'] for c in report['cases']) == 24
print('Architecture connected; evidence and document links verified.')
