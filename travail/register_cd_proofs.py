from pathlib import Path
import hashlib
import json
import re

root = Path(__file__).resolve().parents[1]
document = 'documents/CONSTANTES_C_D_2026-11-02.md'
page = (root/'index.html').read_text(encoding='utf-8')
if 'id="constantes-cd"' not in page:
    anchor = '<strong>Travaux les plus récents</strong>'
    addition = ('<p id="constantes-cd"><a href="'+document+'">'
        '<strong>Constantes c et d : preuves et raccord exact</strong></a><br>'
        'd=2 établi pour le lecteur à observations ; pont matriciel et six théorèmes Lean. '
        'La borne d’initialisation S≤n^c de ce lecteur reste à démontrer.</p>')
    assert anchor in page
    page = page.replace(anchor, anchor+addition, 1)
page = page.replace('exports/projet-annihilation-compilation-generique-2026-11-02.zip',
                    'exports/projet-annihilation-constantes-cd-2026-11-02.zip')
(root/'index.html').write_text(page, encoding='utf-8')

checks = '''
moment_folder = root/'documents/constantes-cd-2026-11-02/lean'
moment_report = json.loads((moment_folder/'validation.json').read_text(encoding='utf-8'))
assert moment_report['exit_code'] == 0
assert not moment_report['source_changed_during_check']
assert moment_report['stderr'] == ''
assert 'sorryAx' not in moment_report['stdout']
assert 'warning:' not in moment_report['stdout']
assert sha(moment_folder/'MomentCompilerBridge.lean') == moment_report['source_sha256']
assert sha(moment_folder/'replay.py') == moment_report['replay_sha256']

'''
archive = (root/'travail/archive_generic_compilation.py').read_text(encoding='utf-8')
archive = archive.replace('exports/projet-annihilation-compilation-generique-2026-11-02.zip',
                          'exports/projet-annihilation-constantes-cd-2026-11-02.zip')
anchor = "raw = subprocess.run(['git', 'ls-files'"
assert anchor in archive
archive = archive.replace(anchor, checks+anchor, 1)
(root/'travail/archive_cd_proofs.py').write_text(archive, encoding='utf-8')

link_count = 0
for filename in [document, 'documents/AUDIT_COMPILATION_GENERIQUE_2026-11-02.md',
                 'documents/INVENTAIRE_COUTS_2026-11-02.md']:
    note = root/filename
    for target in re.findall(r'\[[^\]\n]+\]\(([^)\s]+\.(?:md|py|lean|json|pdf|txt|html)(?:#[^)]*)?)\)', note.read_text(encoding='utf-8')):
        if not target.startswith(('http:', 'https:', '#')):
            assert (note.parent/target.split('#')[0]).resolve().is_file(), (note.name, target)
            link_count += 1
print(f'Constants proof connected; {link_count} local document links verified.')
