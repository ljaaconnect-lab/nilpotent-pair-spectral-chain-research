from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import subprocess
import zipfile

root = Path(__file__).resolve().parents[1]
study = root/'etudes/2026-11-01/borne-chaine-generale'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

report = json.loads((study/'terminal-fusion-validation.json').read_text(encoding='utf-8'))
assert report['status'] == 'passed'
assert not report['scope']['general_polynomial_closure']
assert not report['scope']['general_quasipolynomial_closure']
assert not report['scope']['lean_verified']
assert (report['binomial_basis_profiles'], report['weighted_tail_instances'],
        report['whole_chain_raccords']) == (97, 30, 10)
for name, digest in report['source_sha256'].items():
    assert sha(study/name) == digest, name
assert not (study/'FUSION_SPECTRALE_GENERALE.md').exists()
cost = json.loads((study/'fused-cost-review-validation.json').read_text(encoding='utf-8'))
assert cost['status'] == 'pass'
assert not cost['scope']['general_polynomial_closure']
assert not cost['scope']['jets_or_logarithms_executed']
for source in [cost['source']] + cost['dependencies']:
    assert sha(root/source['path']) == source['sha256'], source['path']
assert [case['full_gates'] for case in cost['cases']] == [72, 362, 2858, 20394]
for case in cost['cases']:
    n = case['n']
    assert case['row_sum_roots_reachable_before_correction'] == n
    assert case['added_gates'] <= 4*n*n - 3*n + 2

direct = json.loads((study/'si-direct/derivative-roots-validation.json').read_text(encoding='utf-8'))
assert sha(root/direct['compiler']) == direct['compiler_sha256']
assert sha(root/direct['fused_compiler_source']) == direct['fused_compiler_sha256']
assert sha(study/'si-direct/verify_derivative_roots.py') == direct['verifier_sha256']
assert sha(study/'si-direct'/direct['proof_note']) == direct['proof_note_sha256']
assert all(case['pass'] for case in direct['cases'])
counting = json.loads((study/'lean/direct-dag-counting-lean-validation.json').read_text(encoding='utf-8'))
assert counting['status'] == 'passed' and not counting['compiler_formalized']
assert sha(study/'lean'/counting['source']) == counting['sha256']
assert sha(study/'lean/replay_direct_dag_counting.py') == counting['replay_sha256']

projection_folder = root/'etudes/2026-11-01/projection-avant-derivation'
projection = json.loads((projection_folder/'direct-projection-validation.json').read_text(encoding='utf-8'))
prefix_report = json.loads((projection_folder/'prefix-projection-validation.json').read_text(encoding='utf-8'))
assert [case['complete_chain_scalar_gates'] for case in projection['cases']] == [3,18,49,110,223,472,1013]
assert [case['prefix_gates'] for case in prefix_report['cases']] == [83,175,330,630,1232]
assert not projection['general_polynomial_closure']
assert not prefix_report['general_polynomial_prefix_bound']
for validation in (projection, prefix_report):
    assert validation['status'] == 'passed'
    for name, digest in validation['source_sha256'].items():
        assert sha(root/name) == digest, name
projection_lean = json.loads((projection_folder/'lean/projection-lean-validation.json').read_text(encoding='utf-8'))
assert projection_lean['status'] == 'passed' and not projection_lean['general_polynomial_closure']
assert sha(projection_folder/'lean'/projection_lean['source']) == projection_lean['sha256']
assert sha(projection_folder/'lean/replay_projection.py') == projection_lean['replay_sha256']

block_roots = json.loads((projection_folder/'taille/block-roots-validation.json').read_text(encoding='utf-8'))
assert block_roots['status'] == 'passed'
assert not block_roots['general_reachability_proof_formalized_in_lean']
assert [case['roots_per_family'] for case in block_roots['cases']] == [6, 70]
for name, digest in block_roots['source_sha256'].items():
    assert sha(root/name) == digest, name
growth_folder = projection_folder/'taille/lean'
growth = json.loads((growth_folder/'growth-lean-validation.json').read_text(encoding='utf-8'))
assert growth['status'] == 'passed' and not growth['compiler_reachability_formalized']
assert not growth['general_scalar_circuit_impossibility']
assert sha(growth_folder/growth['source']) == growth['sha256']
assert sha(growth_folder/'replay_growth.py') == growth['replay_sha256']

linear_folder = root/'etudes/2026-11-01/linearisation-orientee-convolution'
linear = json.loads((linear_folder/'linearised-inputs-validation.json').read_text(encoding='utf-8'))
fused = json.loads((linear_folder/'fused-linearised-validation.json').read_text(encoding='utf-8'))
for validation in (linear, fused):
    assert validation['status'] == 'passed'
    assert not validation['complete_scalar_Z_compiled']
    assert not validation['general_polynomial_quotient_reader_established']
    for name, digest in validation['source_sha256'].items():
        assert sha(root/name) == digest, name
assert [case['polynomial_representative_scalar_gates'] for case in fused['cases']] == [4,32,100,162,378,496,628,774]
assert sum(case['dual_translation_difference_checks'] for case in fused['cases']) == 24
determinants = json.loads((linear_folder/'determinants/determinant-channels-validation.json').read_text(encoding='utf-8'))
assert determinants['status'] == 'identities_verified'
assert not determinants['general_full_chain_correctness']
assert not determinants['general_impossibility_claim']
assert [case['mixed_orientation_classes'] for case in determinants['cases']] == [0,0,3,26]
for name, digest in determinants['source_sha256'].items():
    assert sha(root/name) == digest, name
preparation_lean = json.loads((linear_folder/'lean/preparation-bound-lean-validation.json').read_text(encoding='utf-8'))
assert preparation_lean['status'] == 'passed' and preparation_lean['single_frequency_preparation_only']
assert not preparation_lean['complete_scalar_chain_polynomial_bound']
assert not preparation_lean['gate_count_derivation_formalized']
assert sha(linear_folder/'lean'/preparation_lean['source']) == preparation_lean['sha256']
assert sha(linear_folder/'lean/replay_preparation_bound.py') == preparation_lean['replay_sha256']


moment_folder = root/'documents/constantes-cd-2026-11-02/lean'
moment_report = json.loads((moment_folder/'validation.json').read_text(encoding='utf-8'))
assert moment_report['exit_code'] == 0
assert not moment_report['source_changed_during_check']
assert moment_report['stderr'] == ''
assert 'sorryAx' not in moment_report['stdout']
assert 'warning:' not in moment_report['stdout']
assert sha(moment_folder/'MomentCompilerBridge.lean') == moment_report['source_sha256']
assert sha(moment_folder/'replay.py') == moment_report['replay_sha256']

products = root/'documents/produits-orientes-2026-11-02'
rank_report = json.loads((products/'rank-validation.json').read_text(encoding='utf-8'))
assert rank_report['status'] == 'PASS'
assert not rank_report['general_original_input_compiler']
assert rank_report['factorisation_required']
assert rank_report['instances_checked'] == 96
assert rank_report['frequency_checks'] == rank_report['intt_output_checks'] == 432
assert sha(products/'rank_factorisation.py') == rank_report['source_sha256']
pairing_report = json.loads((products/'lean/validation.json').read_text(encoding='utf-8'))
assert pairing_report['exit_code'] == 0
assert not pairing_report['source_changed_during_check']
assert 'sorryAx' not in pairing_report['stdout']
assert 'warning:' not in pairing_report['stdout']
assert pairing_report['stderr'] == ''
assert sha(products/'lean/PairingCompression.lean') == pairing_report['source_sha256']
assert sha(products/'lean/replay.py') == pairing_report['replay_sha256']

raw = subprocess.run(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
                     cwd=root, capture_output=True, check=True).stdout
files = sorted(set(x.decode('utf-8') for x in raw.split(b'\0') if x))
files.remove('manifeste.json')
manifest = {'date': '2026-11-02', 'sha256': {name: sha(root/name) for name in files}}
(root/'manifeste.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
archive = root/'exports/projet-annihilation-produits-orientes-2026-11-02.zip'
prefix = 'projet-annihilation-collision-orientee/'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as output:
    for name in files+['manifeste.json']:
        output.write(root/name, prefix+name)
with zipfile.ZipFile(archive) as incoming:
    assert set(incoming.namelist()) == {prefix+name for name in files+['manifeste.json']}
    for name, digest in manifest['sha256'].items():
        assert hashlib.sha256(incoming.read(prefix+name)).hexdigest() == digest, name
    assert incoming.read(prefix+'manifeste.json') == (root/'manifeste.json').read_bytes()

class Index(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.details = [], 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'details' and attrs.get('class') == 'essai':
            self.details += 1
        if tag == 'a':
            link = attrs.get('href', '')
            if link and not link.startswith(('#', 'http:', 'https:')):
                self.links.append(link.split('#')[0])
index = Index()
index.feed((root/'index.html').read_text(encoding='utf-8'))
assert index.details == len(json.loads((root/'catalogue.json').read_text(encoding='utf-8'))) == 105
assert not [name for name in index.links if not (root/name).exists()]
print(json.dumps({'files': len(files), 'study_count': index.details,
                  'archive': str(archive), 'archive_bytes': archive.stat().st_size,
                  'archive_sha256': sha(archive)}, indent=2))
