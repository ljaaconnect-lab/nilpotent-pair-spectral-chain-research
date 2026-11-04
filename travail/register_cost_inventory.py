from pathlib import Path

root = Path(__file__).resolve().parents[1]
document = 'documents/INVENTAIRE_COUTS_2026-11-02.md'
readme = (root/'README.txt').read_text(encoding='utf-8')
readme = readme.replace('Regroupement du 2026-11-01 ;', 'Regroupement du 2026-11-02 ;', 1)
if document not in readme:
    readme = readme.replace('PARCOURS CONSEILLÉ\n',
        'INVENTAIRE DES COÛTS\n'+document+'\n'
        'Chaque étape de la chaîne, les coûts locaux des opérateurs et le total\n'
        'après fusion sont distingués, sans double comptage.\n\nPARCOURS CONSEILLÉ\n', 1)
(root/'README.txt').write_text(readme, encoding='utf-8')
page = (root/'index.html').read_text(encoding='utf-8')
page = page.replace('Projet de recherche consolidé · 1 novembre 2026',
                    'Projet de recherche consolidé · 2 novembre 2026', 1)
page = page.replace('exports/projet-annihilation-matrice-linearisee-2026-11-01.zip',
                    'exports/projet-annihilation-inventaire-couts-2026-11-02.zip')
if 'id="inventaire-couts"' not in page:
    anchor = '<strong>Travaux les plus récents</strong>'
    addition = ('<p id="inventaire-couts"><a href="'+document+'">'
        '<strong>Inventaire de chaque coût de la chaîne</strong></a><br>'
        'Entrées, NTT, représentation, annihilation, translations, différences, '
        'lecture et sortie spectrale ; total avec les partages conservés.</p>')
    assert anchor in page
    page = page.replace(anchor, anchor+addition, 1)
(root/'index.html').write_text(page, encoding='utf-8')
archive_script = (root/'travail/archive_borne_generale.py').read_text(encoding='utf-8')
archive_script = archive_script.replace("manifest = {'date': '2026-11-01'",
                                        "manifest = {'date': '2026-11-02'")
archive_script = archive_script.replace('exports/projet-annihilation-matrice-linearisee-2026-11-01.zip',
                                        'exports/projet-annihilation-inventaire-couts-2026-11-02.zip')
(root/'travail/archive_inventaire_couts.py').write_text(archive_script, encoding='utf-8')
print('Inventaire relié au projet; archive datée du 2 novembre préparée.')
