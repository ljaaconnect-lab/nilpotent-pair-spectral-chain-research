from pathlib import Path

root = Path(__file__).resolve().parents[1]
page = (root / 'index.html').read_text(encoding='utf-8')
anchor = '<strong>Travaux les plus récents</strong>'
addition = ('<p id="produits-orientes"><a href="documents/COMPILATION_PRODUITS_ORIENTES_2026-11-02.md">'
            '<strong>Produits orientés : compilation scalaire et rang factorisé</strong></a><br>'
            'Circuit exact polynomial à rang fixé, 96 cas vérifiés et partage spectral. '
            'Portée des représentations linéaires ; borne générale toujours non démontrée.</p>')
assert anchor in page
if 'id="produits-orientes"' not in page:
    page = page.replace(anchor, anchor + addition, 1)
page = page.replace('exports/projet-annihilation-lecture-intt-2026-11-02.zip',
                    'exports/projet-annihilation-produits-orientes-2026-11-02.zip')
(root / 'index.html').write_text(page, encoding='utf-8')
archive = (root / 'travail/archive_intt_clarification.py').read_text(encoding='utf-8')
archive = archive.replace('exports/projet-annihilation-lecture-intt-2026-11-02.zip',
                          'exports/projet-annihilation-produits-orientes-2026-11-02.zip')
anchor = "raw = subprocess.run(['git', 'ls-files'"
assert anchor in archive
checks = '''products = root/'documents/produits-orientes-2026-11-02'
rank_report = json.loads((products/'rank-validation.json').read_text(encoding='utf-8'))
assert rank_report['status'] == 'PASS'
assert not rank_report['general_original_input_compiler']
assert rank_report['factorisation_required']
assert rank_report['instances_checked'] == 96
assert rank_report['frequency_checks'] == rank_report['intt_output_checks'] == 432
assert sha(products/'rank_factorisation.py') == rank_report['source_sha256']
pairing_report = json.loads((products/'lean/validation.json').read_text(encoding='utf-8'))
assert pairing_report['exit_code'] == 0
assert 'sorryAx' not in pairing_report['stdout']
assert 'warning:' not in pairing_report['stdout']
assert pairing_report['stderr'] == ''
assert sha(products/'lean/PairingCompression.lean') == pairing_report['source_sha256']

'''
archive = archive.replace(anchor, checks + anchor, 1)
(root / 'travail/archive_oriented_products.py').write_text(archive, encoding='utf-8')
print('Navigation updated; archive verifier prepared.')
