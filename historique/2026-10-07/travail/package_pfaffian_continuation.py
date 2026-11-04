"""Package the accepted delta, keeping generic Pfaffian claims explicitly unverified."""
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parent
out = root.parent / 'outputs/conjecture-1-5-continuation'
out.mkdir(parents=True, exist_ok=True)

def copy(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)

ledger = json.loads((root / 'research/.arbor/verified-bases.json').read_text(encoding='utf-8'))
entries = [entry for entry in ledger['entries'] if entry['node_id'] in ('n63', 'n67')]
assert {entry['node_id'] for entry in entries} == {'n63', 'n67'}
for node, filename in [('n63', 'MobiusBridge.lean'), ('n67', 'HadamardPfaffian.lean')]:
    proof = root / ('gate-' + node) / filename
    selected = [entry for entry in entries if entry['node_id'] == node]
    assert all(entry['source_sha256'] == hashlib.sha256(proof.read_bytes()).hexdigest() for entry in selected)
    copy(proof, out / 'proofs' / filename)
subset = {'entries': entries, 'accepted_declarations': len(entries),
    'count_note': 'Supporting declarations only; no conjectural axiom or proof of Conjecture 1.5.',
    'root_conjecture_verified': False}
(out / 'arbor').mkdir(exist_ok=True)
(out / 'arbor/verified-bases.json').write_text(json.dumps(subset, indent=2), encoding='utf-8')
for name in ('run.json', 'tree.json'):
    copy(root / 'research/.arbor' / name, out / 'arbor' / name)
git = Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')
git_args = [str(git), '-c', 'safe.directory=' + (root / 'research').as_posix(),
    '-C', str(root / 'research')]
subprocess.run(git_args + ['bundle', 'create', str(out / 'research.bundle'),
    'arbor/n63', 'arbor/n64', 'arbor/n65', 'arbor/n66', 'arbor/n67', 'arbor/n68'], check=True, capture_output=True)
subprocess.run(git_args + ['bundle', 'verify', str(out / 'research.bundle')],
    check=True, capture_output=True)
for source in (root / 'gate-n63').glob('n63-*'):
    if source.is_file():
        copy(source, out / 'verification/n63' / source.name)
copy(root / 'further-proof-replay.json', out / 'verification/further-proof-replay.json')
for source in (root / 'gate-n67').glob('n67-*'):
    if source.is_file():
        copy(source, out / 'verification/n67' / source.name)
    elif source.is_dir():
        for item in source.rglob('*'):
            if item.is_file():
                copy(item, out / 'verification/n67' / source.name / item.relative_to(source))
for node, directory in [('n65', 'initial-jets'), ('n66', 'synchronization'), ('n68', 'contextual-moments')]:
    for source in (root / ('wt-' + node)).iterdir():
        if source.is_file() and (source.name.startswith(node + '-') or source.name.startswith(node.upper() + '_')
                or source.name in ('initial_jets.py', 'local_basis.py', 'evaluate_local_basis.py', 'evaluate_carry_basis.py',
                    'candidate.py', 'euler_identity.py', 'euler_compiler.py', 'pfaffian_coefficients.py')
                or source.name.startswith('carry_')):
            copy(source, out / 'positive-frontier' / directory / source.name)
draft = root / 'wt-n66/LocalGadget.lean'
if draft.exists():
    copy(draft, out / 'positive-frontier/synchronization/LocalGadget.lean')
    obsolete = out / 'positive-frontier/synchronization/unverified-drafts/LocalGadget.lean'
    if obsolete.exists():
        obsolete.unlink()
for path in [root / 'pfaffian-delivered-proof-cache/replay-report.json',
             root / 'pfaffian-delivered-validation/n64-positive-test-report.json']:
    if path.exists():
        replay = json.loads(path.read_text(encoding='utf-8'))
        if 'sources' in replay:
            for record in replay['sources']:
                destination = out / 'verification' / ('delivered-' + Path(record['source']).stem + '.json')
                destination.write_text(json.dumps({'root_conjecture_verified': False, 'source': record}, indent=2),
                                       encoding='utf-8')
        else:
            copy(path, out / 'verification/delivered-pfaffian-validation.json')
for name in ('n64-positive-test-report.json', 'n64-heldout-freeze.json', 'n64-checkout-incident.json'):
    copy(root / name, out / 'verification' / name)
copy(root / 'mathlib-environment.json', out / 'verification/mathlib-environment-local.json')
for source in (root / 'gate-n64').iterdir():
    if source.is_file() and (source.name.startswith('n64-') or source.name in (
        'pfaffian_coefficients.py', 'candidate.py', 'euler_identity.py', 'euler_compiler.py',
        'evaluate_pfaffian.py', 'blueprint-pfaffian-aggregation.md', 'N64_DESIGN.md', 'N64_INSIGHTS.md')):
        copy(source, out / 'circuits/n64' / source.name)
copy(root / 'test-boundary/pfaffian-local-heldout.json', out / 'validation-boundaries/pfaffian-local-heldout.json')
copy(root.parent / 'outputs/conjecture-1-5-suite/reproduction/verify_delivered.py', out / 'reproduction/verify_delivered.py')
driver = out / 'reproduction/verify_delivered.py'
driver_source = driver.read_text(encoding='utf-8').replace('work/delivered-proof-cache',
    'work/pfaffian-delivered-proof-cache')
driver_source = driver_source.replace('args = parser.parse_args()',
    "parser.add_argument('--source', action='append', help='Replay only the named new standalone source')\nargs = parser.parse_args()")
driver_source = driver_source.replace("report = {'root_conjecture_verified':False, 'sources':[]}",
    "assert not args.source or set(args.source) <= set(files), 'Unknown source selection'\nreport = {'root_conjecture_verified':False, 'sources':[]}")
driver_source = driver_source.replace('for filename in order:\n',
    'for filename in order:\n    if args.source and filename not in args.source:\n        continue\n')
driver.write_text(driver_source, encoding='utf-8')

# Adapt only path/integrity setup in the independently exercised held-out evaluator.
validation = (root / 'validate_pfaffian_candidate.py').read_text(encoding='utf-8')
start = validation.index('root = Path(__file__).resolve().parent')
end = validation.index('sys.path.insert(0, str(gate))')
setup = '''package = Path(__file__).resolve().parent.parent
root = package.parent.parent / 'work/pfaffian-delivered-validation'
root.mkdir(parents=True, exist_ok=True)
gate = package / 'circuits/n64'
manifest = json.loads((package / 'manifest-sha256.json').read_text(encoding='utf-8'))
for relative, expected in manifest.items():
    assert hashlib.sha256((package / relative).read_bytes()).hexdigest() == expected, relative
original = json.loads((package / 'verification/n64-positive-test-report.json').read_text(encoding='utf-8'))
ref = original['commit']
source_hash = original['source_integrity']
protocol_hash = original['protocol_integrity']
dependencies = original['imported_source_integrity']
boundary = package / 'validation-boundaries/pfaffian-local-heldout.json'
freeze = json.loads((package / 'verification/n64-heldout-freeze.json').read_text(encoding='utf-8'))
assert hashlib.sha256(boundary.read_bytes()).hexdigest() == freeze['sha256']
cases = json.loads(boundary.read_text(encoding='utf-8'))['cases']
'''
validation = validation[:start] + setup + validation[end:]
(out / 'reproduction/verify_local_pfaffian.py').write_text(validation, encoding='utf-8')

status = '''[FOUND INVARIANT]
La clôture positive de Conjecture 1.5 n'a pas été obtenue.
Le nouveau résultat Lean concerne les coefficients de correction de Möbius :
c_f(S)=sum_{T subset S} (-1)^(|S|-|T|) f(T).
La reconstruction zêta et la borne des littéraux sont des obligations auxiliaires.
Pour f(T)=(-1)^inv(T), la borne obtenue contrôle la taille des constantes.

Le candidat n64 fournit une matrice fixe de taille 2n²+2 dont les Pfaffiens
principaux sur les deux ports de chaque arête sélectionnée reproduisent c(S).
Ses quatre identités locales passent 7184/7184 contrôles pour n=2,3,4,5,
puis 96/96 contrôles indépendants sur 24 nouveaux appariements n=6,7,8.
Ce dernier ensemble est maintenant publié et ne constitue plus un test inédit.
L'énoncé général Pfaffien et la sémantique générale du compilateur de traces
restent formellement non vérifiés ; ces scores ne remplacent pas Lean.

[LEAN 4 TACTICS APPLIED]
proofs/MobiusBridge.lean contient exclusivement les lemmes acceptés par Lean.
verification/further-proof-replay.json donne le rejeu du commit par le root.
Les axiomes permis sont propext, Classical.choice, Quot.sound.
Aucun sorryAx ou axiome conjectural n'est admis dans les sources acceptées.
Le fragment de preuve et les binders exacts sont conservés dans le source.

[GATE COUNT VERIFICATION]
La récurrence explicite du candidat Pfaffien est
q_0=1, q_k=(1/(2k)) sum_{i=1..k} (-1)^(i-1) tr((-JA)^i) q_{k-i}.
Chaque opération est abaissée en portes binaires + ou × sur Q ; les divisions
constantes utilisent des littéraux rationnels. Pour les ordres 2,4,6,8,10,12,
les graphes sérialisés comptent 6,139,853,2990,7772,16809 portes.
Il s'agit du coût du calcul local du Pfaffien, pas de l'extracteur complet.

La contraction globale doit conserver exactement les sous-ensembles qui
sélectionnent ensemble les deux ports de chaque arête. Le blueprint expose
cette projection supplémentaire et la moyenne de signes à compiler.
Sa simplification connue restitue la formule n15 déjà explorée.
La construction uniforme de cette projection avec un coût polynomial,
des littéraux admissibles et une preuve générale reste à fournir.
Aucun Pi(n) pour le circuit scalaire complet n'est démontré ici.
Le score de la conjecture racine reste 0 ; aucune dispreuve n'est revendiquée.
'''
status += '''
CONTINUATION POSITIVE n65/n66/n67
[FOUND INVARIANT]
Le sélecteur local COPY4 vérifie H^(tensor4) COPY4 = 2 EVEN4.
EVEN4 est la signature explicitement développée du Pfaffien à quatre modes,
avec ses six paramètres supérieurs égaux à un. L'inverse matriciel H/2
est exact. Ces trois énoncés locaux sont maintenant vérifiés par Lean.

n65 donne le spectre d'inversion borné et un initialiseur scalaire J0,J1.
Les jets J2,...,JD restent à construire : la transition compagnon seule
n'initialise pas une représentation bon marché. Les coûts n65 du rapport
sont dérivés du source, sans exécution numérique revendiquée.

n66 fournit 53/53 contrôles symboliques locaux positifs. Son développement
sépare explicitement ces résultats du score global 0/3. Le suivi auxiliaire
de parité requiert encore l'ordre des jambes et ses phases de shuffle ;
il ne fournit pas une transformation de Hadamard ordinaire des deux familles.

[LEAN 4 TACTICS APPLIED]
proofs/HadamardPfaffian.lean contient trois théorèmes par decide +kernel.
Quatre candidats locaux ont été compilés (codes 1,0,0,0), puis le root
a recompilé le commit figé avec code 0. Les trois théorèmes et la définition
gaussian4 sont audités ; celle-ci ne compte pas comme un quatrième théorème.
Les rapports de rejeu des sources livrées sont conservés dans verification.

[GATE COUNT VERIFICATION]
Le transform local de quatre jambes est compilé en 96 portes ; son inverse
ajoute 112 portes. Le résidu chiral est compilé en 18 portes.
La construction et la contraction cohérentes des familles complètes restent
des obligations séparées. Aucun coût polynomial global Pi(n) n'est acquis.

FRONTIERE CONTEXTUELLE n68
Une nouvelle réduction informelle remplace K_aa=J_lex par R^T J_n R,
R_(i,e)=delta_(i,row(e)). Si deux a-ports ont la même ligne, la contribution
du premier noyau s'annule ; sinon les deux matrices coïncident sur les
ports sélectionnés. Cette substitution préserve donc les produits de
coefficients avec tout poids de synchronisation diagonal en Q.
Avec K_bb=-C^T J_n C, les deux secteurs du second noyau ont rang au plus n.
Cette réduction contextuelle et sa fermeture scalaire ne sont pas vérifiées
dans Lean ; aucune invariance sous toutes les dérivées n'est supposée.
La documentation n68 précise les obligations de transition qui restent ouvertes.
'''
(out / 'statut.txt').write_text(status, encoding='utf-8')
readme = '''CONJECTURE 1.5 — CONTINUATION n63 à n68, 7 octobre 2026
Ce dossier est un complément de conjecture-1-5-suite ; il ne prétend pas
résoudre la conjecture. Lire statut.txt pour distinguer preuve, calcul fini,
coût local et obligation de compression générale.

Reproduction sur ce poste, avec Python, SymPy 1.14 et Mathlib/Lean 4.34.1 :
python reproduction/verify_delivered.py
python reproduction/verify_local_pfaffian.py
Les scripts écrivent leurs rapports dans work/pfaffian-delivered-*, sans
modifier les sources livrées. Les chemins de l'environnement Mathlib sont
ceux de ce poste ; un autre poste doit fournir le même environnement épinglé.
La frontière publiée vérifie uniquement des identités locales positives.
Le manifeste SHA256 contrôle les bytes effectivement livrés, y compris
leurs fins de ligne. L'incident n64 explique la normalisation Git du protocole.

Les commits des branches nommées arbor/n63 à arbor/n68 sont conservés dans
research.bundle, l'arbre Arbor et verification. Le bundle Git est vérifié.
Les scores locaux sont distincts du score de preuve racine.
Les refus de merge au score égal 1 ne sont pas des refus d'autorisation.

Méthode : adaptations locales des skills Arbor, Hilbert et lean-proof,
subagents isolés dans des worktrees Git ; pas d'exécution d'un service distant.
Référence logicielle ajoutée, record arXiv courant consulté le 7 octobre 2026 :
Kassis, Timothy; Agarwal, Vinayak; He, Yuhuan; Patel, Darshil;
Brueckner, Aubrey M. (2026). Scientific Agent Skills: A Library of Procedural
Knowledge for Research Agents. arXiv:2609.00065, record courant v2.
https://doi.org/10.48550/arXiv.2609.00065

Référence mathématique consultée pour l'interface de sommation :
Okada, Soichi. Pfaffian Formulas and Schur Q-Function Identities.
Advances in Mathematics 353 (2019), 446–470, Lemma 3.1 et Theorem 3.4.
https://doi.org/10.1016/j.aim.2019.07.006
Ces théorèmes ne fournissent pas dans ce dossier la projection synchronisée.
Les dérivations du blueprint sont explicitement marquées informelles.

Nouvelle preuve autonome : proofs/HadamardPfaffian.lean (trois théorèmes).
Pour ne vérifier que ce nouveau source inchangé depuis le rejeu du commit :
python reproduction/verify_delivered.py --source HadamardPfaffian.lean
Les lemmes Möbius déjà livrés ont leur propre rapport de compilation.
Les quatre déclarations n67 incluent la définition gaussian4 auditée ;
le total de déclarations n'est pas un total de résultats indépendants.
positive-frontier contient les constructions partielles, leurs versions,
protocoles et contraintes. Le fichier LocalGadget.lean de ce dossier est
un brouillon non compilé conservé pour le contrôle du gel des sources ;
seuls les sources dans proofs sont des preuves acceptées. Aucun objectif
racine n'est clos.
'''
(out / 'README.txt').write_text(readme, encoding='utf-8')
manifest = {p.relative_to(out).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
    for p in sorted(out.rglob('*')) if p.is_file() and p.name != 'manifest-sha256.json'}
(out / 'manifest-sha256.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
archive = out.with_suffix('.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as handle:
    for source in sorted(out.rglob('*')):
        if source.is_file():
            handle.write(source, source.relative_to(out.parent))
with zipfile.ZipFile(archive) as handle:
    assert handle.testzip() is None
    for relative, digest in manifest.items():
        assert hashlib.sha256(handle.read(out.name + '/' + relative)).hexdigest() == digest
print(json.dumps({'archive': str(archive), 'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
    'files': len(manifest) + 1, 'accepted_delta_declarations': len(entries), 'root_conjecture_verified': False}))
