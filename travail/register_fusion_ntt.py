from pathlib import Path
import html
import json

root = Path(__file__).resolve().parents[1]
folder = 'etudes/2026-11-01/fusion-ntt'
catalogue = json.loads((root/'catalogue.json').read_text(encoding='utf-8'))
entry = {
    'id': 'nov01:fusion-ntt',
    'campagne': 'Raccord spectral et fusion des transports',
    'hypothese': 'Adapter la NTT modulo Q aux différences de transports pour annihiler les répétitions au degré terminal sans sélection finale de colonnes',
    'statut_archive': 'partial',
    'resultat': 'Identité exacte à tout ordre ; lemmes généraux Fourier et coefficient terminal vérifiés dans Lean ; 30 tables Z formelles, 564 égalités NTT/transport et 156 identités de mots vérifiées',
    'enseignement': 'Les facteurs spectraux sont T_(omega^(f*d_j)e_j)-I. La troncature impose une seule insertion par facteur ; la compilation scalaire polynomiale de leur action composée reste à construire.',
    'commit': None,
    'dossier': folder,
    'documents': [folder+'/'+name for name in (
        'RACCORD_NTT.md', 'FusionFourier.lean', 'TerminalDifference.lean',
        'verify_bridge.py', 'bridge-validation.json', 'replay_lean.py',
        'lean-validation.json')]
}
assert all(item['id'] != entry['id'] for item in catalogue)
assert all((root/name).is_file() for name in entry['documents'])
catalogue.append(entry)
(root/'catalogue.json').write_text(
    json.dumps(catalogue, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
constitution = json.loads((root/'constitution.json').read_text(encoding='utf-8'))
constitution['tentatives'] = len(catalogue)
(root/'constitution.json').write_text(
    json.dumps(constitution, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
page = (root/'index.html').read_text(encoding='utf-8')
assert '95 pistes' in page
page = page.replace('95 pistes', '96 pistes')
page = page.replace('exports/projet-annihilation-transport-2026-11-01.zip',
                    'exports/projet-annihilation-fusion-ntt-2026-11-01.zip')
anchor = '<strong>Travaux les plus récents</strong>'
assert anchor in page
page = page.replace(anchor, anchor+'<p><a href="'+folder+
    '/RACCORD_NTT.md"><strong>NTT et différences de transports : raccord exact</strong></a>'
    '<br>Annihilation des répétitions au degré terminal ; lemmes généraux dans Lean et '
    '30 tables Z avec z formel. Le coût scalaire de la composition reste à borner.</p>', 1)
details = '<details class="essai" data-search="nov01:fusion-ntt ntt modulo q fourier fusion transports différences terminal lean"><summary><span>'+entry['id']+'</span> NTT et différences de transports</summary>'
details += '<p>'+html.escape(entry['resultat'])+'</p><p>'+html.escape(entry['enseignement'])+'</p><p>'
details += ' · '.join('<a href="'+name+'">'+name.rsplit('/', 1)[1]+'</a>'
                      for name in entry['documents'])
details += '</p></details>'
anchor = '<p class="meta" id="count"></p>'
assert anchor in page
page = page.replace(anchor, anchor+details, 1)
(root/'index.html').write_text(page, encoding='utf-8')
print(json.dumps({'tentatives': len(catalogue), 'new_study': folder}))
