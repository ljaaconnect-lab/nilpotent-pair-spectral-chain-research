"""Register this verified study and refresh the project manifest/archive."""
from pathlib import Path
import hashlib
import html
import json
import re
import subprocess
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REL = HERE.relative_to(ROOT).as_posix()
ID = 'nov01:lean-operateurs'
ARCHIVE = 'projet-annihilation-lean-2026-11-01.zip'


def main():
    checks = json.loads((HERE/'validation.json').read_text(encoding='utf-8'))
    lean = json.loads((HERE/'lean-validation.json').read_text(encoding='utf-8'))
    assert checks['status'] == 'quintic_operator_verified' and lean['status'] == 'passed'
    for name, sha in checks['code_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == sha
    for record in lean['files']:
        assert hashlib.sha256((HERE/record['source']).read_bytes()).hexdigest() == record['sha256']
    files = ['PROGRES_LEAN.md', 'CollisionFilter.lean', 'WeylOperators.lean',
             'PartitionCertificate.lean', 'WordFilter.lean', 'circuit.py',
             'correcteurs.json', 'validation.json', 'lean-validation.json',
             'replay_lean.py', 'derive_quintic.py', 'verifier.py', 'transport.json']
    entry = {'id': ID, 'campagne': 'Circuit operateur et preuves Lean',
             'hypothese': 'Construire une fermeture des operateurs orientes et spectraux, avec certificats Lean et compilation scalaire depuis les entrees originales',
             'statut_archive': 'partial',
             'resultat': 'Correcteur quintique a 44 contractions, recurrence entiere ; preuves Lean du filtre general et des certificats jusqu au degre cinq ; 60 tables numeriques et 10 tables formelles exactes',
             'enseignement': 'Le premier echec est corrige et la chaine est exacte jusqu a n=5 ; un residu au degre six reste. La fermeture generale polynomiale n est pas prouvee.',
             'commit': None, 'dossier': REL, 'documents': [REL+'/'+x for x in files]}
    catalogue = json.loads((ROOT/'catalogue.json').read_text(encoding='utf-8'))
    catalogue = [x for x in catalogue if x['id'] != ID]+[entry]
    (ROOT/'catalogue.json').write_text(json.dumps(catalogue, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    count = len(catalogue)

    index = (ROOT/'index.html').read_text(encoding='utf-8')
    index = re.sub(r'<p>\d+ pistes,', f'<p>{count} pistes,', index, count=1)
    index = re.sub(r'href="exports/[^"]+"', f'href="exports/{ARCHIVE}"', index, count=1)
    if f'data-search="{ID} ' not in index:
        links = ' · '.join(f'<a href="{REL}/{x}">{html.escape(x)}</a>' for x in files)
        detail = (f'<details class="essai" data-search="{ID} lean quintique horloge operateur circuit certificat">'
                  f'<summary><span>{ID}</span> Correcteur quintique et preuves Lean</summary>'
                  f'<p>{html.escape(entry["resultat"])}</p><p>{html.escape(entry["enseignement"])}</p>'
                  f'<p>{links}</p></details>')
        index = index.replace('<details class="essai"', detail+'<details class="essai"', 1)
        recent = (f'<p><a href="{REL}/PROGRES_LEAN.md"><strong>Correcteur quintique, récurrence entière et preuves Lean</strong></a>'
                  '<br>Filtre général formalisé ; certificats de correction jusqu’au degré cinq ; '
                  'chaîne complète testée avec z formel. Fermeture générale encore ouverte.</p>')
        index = index.replace('<strong>Travaux les plus récents</strong>', '<strong>Travaux les plus récents</strong>'+recent, 1)
    (ROOT/'index.html').write_text(index, encoding='utf-8')

    readme = (ROOT/'README.txt').read_text(encoding='utf-8')
    readme = re.sub(r'; \d+ pistes et tentatives', f'; {count} pistes et tentatives', readme, count=1)
    begin = readme.index('Dernière reprise :')
    end = readme.index('\n1. sources/papiers/', begin)
    readme = readme[:begin]+(
        f'Dernière reprise : {REL}/PROGRES_LEAN.md.\n'
        'Correcteur quintique et récurrence entière construits en portes scalaires.\n'
        'Preuves Lean rejouées : filtre général, opérateur de création et\n'
        'certificats aux ordres quatre et cinq. Chaîne exacte jusqu’à n=5 ;\n'
        'fermeture générale non obtenue, résidu au degré six conservé.\n'
        'Les prototypes antérieurs restent dans operateurs-horloge/ et linearisation-mod-Q/.\n')+readme[end:]
    if 'python outils/reproduire.py run lean-operateurs' not in readme:
        readme = readme.replace('  python outils/reproduire.py run operateurs-horloge',
                                '  python outils/reproduire.py run lean-operateurs\n  python outils/reproduire.py run preuves-operateurs\n  python outils/reproduire.py run operateurs-horloge')
    (ROOT/'README.txt').write_text(readme, encoding='utf-8')

    constitution = json.loads((ROOT/'constitution.json').read_text(encoding='utf-8'))
    constitution.setdefault('tentatives_initiales', constitution['tentatives'])
    constitution['tentatives'] = count
    (ROOT/'constitution.json').write_text(json.dumps(constitution, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

    paths = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
                                    cwd=ROOT, text=True, encoding='utf-8').split('\0')
    names = sorted({x for x in paths if x != 'manifeste.json' and (ROOT/x).is_file()})
    manifest = {'date': '2026-11-01', 'sha256': {
        name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names}}
    (ROOT/'manifeste.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    archive = ROOT/'exports'/ARCHIVE
    archive.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name in names+['manifeste.json']:
            z.write(ROOT/name, arcname='annihilation-collision-orientee/'+name)
    print(json.dumps({'studies': count, 'manifest_files': len(names), 'archive': str(archive),
                      'archive_bytes': archive.stat().st_size}, ensure_ascii=False))


if __name__ == '__main__':
    main()
