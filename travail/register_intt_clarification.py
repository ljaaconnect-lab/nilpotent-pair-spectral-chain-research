from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
document = 'documents/LECTURE_INTT_ET_MOMENTS_2026-11-02.md'
page = (root/'index.html').read_text(encoding='utf-8')
if 'id="lecture-intt"' not in page:
    anchor = '<strong>Travaux les plus récents</strong>'
    addition = ('<p id="lecture-intt"><a href="'+document+'">'
        '<strong>INTT : lecture finale et compilation conjointe</strong></a><br>'
        'La variante par moments et sa matrice de lecture ne sont pas imposées à la chaîne. '
        'Clarification du raccord et résultat de l’audit d’initialisation.</p>')
    assert anchor in page
    page = page.replace(anchor, anchor+addition, 1)
page = page.replace('exports/projet-annihilation-constantes-cd-2026-11-02.zip',
                    'exports/projet-annihilation-lecture-intt-2026-11-02.zip')
(root/'index.html').write_text(page, encoding='utf-8')
archive = (root/'travail/archive_cd_proofs.py').read_text(encoding='utf-8')
archive = archive.replace('exports/projet-annihilation-constantes-cd-2026-11-02.zip',
                          'exports/projet-annihilation-lecture-intt-2026-11-02.zip')
(root/'travail/archive_intt_clarification.py').write_text(archive, encoding='utf-8')
link_count = 0
for filename in [document, 'documents/CONSTANTES_C_D_2026-11-02.md',
                 'documents/AUDIT_COMPILATION_GENERIQUE_2026-11-02.md']:
    note = root/filename
    for target in re.findall(r'\[[^\]\n]+\]\(([^)\s]+\.(?:md|py|lean|json|pdf|txt|html)(?:#[^)]*)?)\)', note.read_text(encoding='utf-8')):
        if not target.startswith(('http:', 'https:', '#')):
            assert (note.parent/target.split('#')[0]).resolve().is_file(), (note.name, target)
            link_count += 1
print(f'INTT clarification connected; {link_count} local document links verified.')
