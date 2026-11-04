from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
document = 'documents/AUDIT_COMPILATION_GENERIQUE_2026-11-02.md'
page = (root/'index.html').read_text(encoding='utf-8')
if 'id="compilation-generique"' not in page:
    anchor = '<strong>Travaux les plus récents</strong>'
    addition = ('<p id="compilation-generique"><a href="'+document+'">'
        '<strong>Compilation générique polynomiale : outils retrouvés</strong></a><br>'
        'Compilateur n57–n59 vérifié dans Lean, initialisation et lecture comprises ; '
        'transport fusionné et dérivations. Correction ciblée de l’inventaire.</p>')
    assert anchor in page
    page = page.replace(anchor, anchor+addition, 1)
page = page.replace('exports/projet-annihilation-architecture-couts-2026-11-02.zip',
                    'exports/projet-annihilation-compilation-generique-2026-11-02.zip')
(root/'index.html').write_text(page, encoding='utf-8')
archive_script = (root/'travail/archive_architecture_couts.py').read_text(encoding='utf-8')
archive_script = archive_script.replace('exports/projet-annihilation-architecture-couts-2026-11-02.zip',
    'exports/projet-annihilation-compilation-generique-2026-11-02.zip')
(root/'travail/archive_generic_compilation.py').write_text(archive_script, encoding='utf-8')

documents = [root/document,
             root/'documents/INVENTAIRE_COUTS_2026-11-02.md',
             root/'documents/ARCHITECTURE_ET_COUTS_2026-11-02.md']
link_count = 0
for note in documents:
    for target in re.findall(r'\[[^\]\n]+\]\(([^)\s]+\.(?:md|py|lean|json|pdf|txt|html)(?:#[^)]*)?)\)', note.read_text(encoding='utf-8')):
        if not target.startswith(('http:', 'https:', '#')):
            assert (note.parent/target.split('#')[0]).resolve().is_file(), (note.name, target)
            link_count += 1
print(f'Audit connected; {link_count} local document links verified.')
