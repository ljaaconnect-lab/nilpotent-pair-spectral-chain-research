"""Package committed constructive research and independently accepted proofs."""
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / 'outputs' / 'conjecture-1-5-suite'
OUT.mkdir(parents=True, exist_ok=True)
GIT = Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')
REPO = ROOT / 'research'

def copy(src, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)

variants = {
    'encoding-and-subset': ('gate-n1', ['candidate.py', 'evaluate.py', 'README.md', 'dev-report.json']),
    'transfer': ('gate-n4', ['candidate.py', 'recurrence.py', 'evaluate_recurrence.py', 'dev-recurrence.json']),
    'half-character': ('gate-n15', ['candidate.py', 'half_character.py', 'validate_half_character.py', 'n15-dev-report.json', 'N15_DESIGN.md', 'N15_INSIGHTS.md']),
    'reciprocal': ('gate-n16', ['rational_recurrence.py', 'evaluate_rational_dev.py', 'dev-rational.json', 'RATIONAL_PROPOSAL.md']),
    'occupation': ('gate-n18', ['candidate.py', 'occupation_gram.py', 'evaluate_occupation_gram.py', 'n18-dev-report.json', 'N18_DESIGN.md', 'N18_INSIGHTS.md']),
    'mixed-jets': ('gate-n19', ['candidate.py', 'rational_recurrence.py', 'mixed_derivative.py', 'evaluate_mixed_dev.py', 'dev-mixed.json', 'MIXED_DERIVATIVE_PROPOSAL.md']),
    'direct-projector': ('gate-n61', ['candidate.py', 'euler_compiler.py', 'euler_identity.py',
                                    'evaluate_euler.py', 'validate_euler_identity.py',
                                    'N61_DESIGN.md', 'N61_INSIGHTS.md', 'n61-protocol.json', 'n61-dev-report.json']),
}
for variant, (folder, filenames) in variants.items():
    for filename in filenames:
        src = ROOT / folder / filename
        if not src.exists():
            raise FileNotFoundError(src)
        copy(src, OUT / 'circuits' / variant / filename)

ledger = json.loads((REPO / '.arbor/verified-bases.json').read_text(encoding='utf-8'))
proof_sources = {}
for entry in ledger['entries']:
    filename = entry['source']
    digest = entry['source_sha256']
    if filename in proof_sources:
        assert proof_sources[filename] == digest
        continue
    gates = [ROOT / ('gate-' + entry['node_id'])]
    gates += sorted(ROOT.glob('gate-n*'))
    match = next((g / filename for g in gates if (g / filename).exists()
                  and hashlib.sha256((g / filename).read_bytes()).hexdigest() == digest), None)
    assert match is not None, (filename, digest)
    copy(match, OUT / 'proofs' / filename)
    proof_sources[filename] = digest

for filename in ['tree.json', 'run.json', 'verified-bases.json']:
    copy(REPO / '.arbor' / filename, OUT / 'arbor' / filename)
reports = [
    'proof-replay.json', 'general-pairing-replay.json', 'label-bridge-replay.json',
    'continuation-proof-replay.json', 'positive-test-report.json', 'extended-positive-test-report.json',
    'dependency-bootstrap.json', 'mathlib-smoke-report.json', 'targeted-cache-report.json',
]
for name in reports:
    copy(ROOT / name, OUT / 'verification' / name)
if (ROOT / 'further-proof-replay.json').exists():
    copy(ROOT / 'further-proof-replay.json', OUT / 'verification/further-proof-replay.json')
if (ROOT / 'matrix-compiler-test-report.json').exists():
    copy(ROOT / 'matrix-compiler-test-report.json', OUT / 'verification/matrix-compiler-test-report.json')
if (ROOT / 'n5-full-hhat-test-report.json').exists():
    copy(ROOT / 'n5-full-hhat-test-report.json', OUT / 'verification/n5-full-hhat-test-report.json')
if (ROOT / 'constructive-frontier-audit.txt').exists():
    copy(ROOT / 'constructive-frontier-audit.txt', OUT / 'verification/constructive-frontier-audit.txt')
for name in ['projector-candidate-test-report.json', 'n61-checkout-incident.json']:
    if (ROOT/name).exists():
        copy(ROOT/name,OUT/'verification'/name)
packaged_replay = ROOT/'delivered-proof-cache/replay-report.json'
if packaged_replay.exists():
    pr = json.loads(packaged_replay.read_text(encoding='utf-8'))
    replayed_sources = {s['source']:s for s in pr['sources']}
    if set(replayed_sources) == set(proof_sources) and all(
            s['exit_code'] == 0 and s['source_sha256'] == proof_sources[name]
            for name,s in replayed_sources.items()):
        assert all(set(values) <= {'propext','Classical.choice','Quot.sound'}
                   for s in pr['sources'] for values in s['axiom_audit'].values())
        copy(packaged_replay,OUT/'verification/delivered-proof-replay.json')
        summary = {'all_delivered_sources_recompiled':True,'source_count':len(proof_sources),
                   'accepted_ledger_declarations':ledger['accepted_declarations'],
                   'all_exit_codes_zero':True,'unexpected_axioms':[],
                   'root_conjecture_verified':False,
                   'scope':'Actual delivered source files checked by their packaged replay driver; auxiliary results only.'}
        (OUT/'verification/delivery-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
for name in ['projector-candidate-test-report.json','n5-full-hhat-test-report.json']:
    if (ROOT/'delivered-validation'/name).exists():
        copy(ROOT/'delivered-validation'/name,OUT/'verification'/'packaged-reproduction'/name)
for name in ['simulation.json', 'positive-simulation.json']:
    copy(ROOT / 'test-boundary' / name, OUT / 'validation-boundaries' / name)
copy(ROOT/'test-boundary/matrix-power-heldout.json', OUT/'validation-boundaries/matrix-power-heldout.json')
copy(ROOT/'test-boundary/projector-positive-holdout.json', OUT/'validation-boundaries/projector-positive-holdout.json')
for folder, filenames in {
    'gate-n39': ['rank-one-report.json', 'rank-one-obligations.json', 'RANK_ONE_BLUEPRINT.md'],
    'gate-n40': ['n40-dev-report.json', 'n40-obligations.json', 'N40_INSIGHTS.md', 'power_plan.py', 'power-dag-examples.json'],
    'gate-n54': ['n54-strict-report.json', 'n54-leaf-result.json', 'n54-blueprint-informel.md'],
}.items():
    for name in filenames:
        copy(ROOT / folder / name, OUT / 'verification' / folder.replace('gate-', '') / name)
for folder in ['gate-n55', 'gate-n56', 'gate-n57', 'gate-n58', 'gate-n59', 'gate-n60', 'gate-n61', 'gate-n62']:
    p = ROOT / folder
    if p.exists():
        for src in p.iterdir():
            if src.is_file() and (src.name.lower().startswith(folder.replace('gate-', '') + '-')
                                 or src.name.upper().startswith(folder.replace('gate-', '').upper() + '_')
                                 or src.name in ['dense_compiler.py', 'evaluate_dense.py', 'power_plan.py',
                                                 'orientation-report.json', 'orientation-obligations.json',
                                                 'ORIENTATION_BLUEPRINT.md',
                                                 'reverse-report.json', 'reverse-obligations.json',
                                                 'REVERSE_VANDERMONDE_BLUEPRINT.md']):
                if src.suffix != '.olean':
                    copy(src, OUT / 'verification' / folder.replace('gate-', '') / src.name)
        if (p/'scalar-dags').exists():
            for src in (p/'scalar-dags').glob('*.json'):
                copy(src, OUT/'verification'/folder.replace('gate-', '')/'scalar-dags'/src.name)

count = ledger['accepted_declarations']
readme = f'''CONJECTURE 1.5 — SUITE DE LA RECHERCHE CONSTRUCTIVE
7 octobre 2026, Africa/Lagos

STATUT : la conjecture n'est pas démontrée par ces artifacts.
La représentation du coefficient central et des briques de compilation sont
formalisées ; aucun extracteur scalaire polynomial général n'est revendiqué.

Ce dossier remplace le bilan technique ancien de outputs/conjecture-1-5.
Mathlib v4.34.1 est maintenant installé et ses imports ciblés sont vérifiés.
Lean 4.34.1 :
C:\\Users\\REGIS\\Documents\\Codex\\runtimes\\elan\\toolchains\\leanprover--lean4---v4.34.1\\bin\\lean.exe
Rejouer les sources acceptées : python reproduction/verify_delivered.py
Le script utilise verification/mathlib-environment-local.json, et écrit ses
fichiers intermédiaires dans work/delivered-proof-cache. Les paths de ce JSON
correspondent à ce poste ; un autre poste doit disposer du même Mathlib épinglé.

proofs/ contient exclusivement les sources acceptées et recompilées par le
coordinateur depuis des commits figés. Le registre compte {count} déclarations,
avec des spécialisations et reformulations ; ce nombre ne compte pas autant
de découvertes indépendantes. Aucun sorryAx ni axiome conjectural n'est admis.
La base de confiance explicitement auditée est propext, Classical.choice,
Quot.sound. Les rapports de compilation donnent commandes, hashes et sorties.

circuits/ contient les variantes exécutables Python, avec Fraction/SymPy 1.14.
Les scores portent sur les frontières fixées, pas sur une preuve asymptotique.
La frontière étendue a réussi 48/48 vérifications indépendantes en z formel,
sur huit matrices rationnelles n=2,3,4,5 et six variantes d'extraction.
La nouvelle correction directe par projecteurs a réussi 24/24 contrôles dev
et 32/32 contrôles indépendants sur huit nouvelles matrices rationnelles.
Rejouer ce dernier candidat, avec les données maintenant publiées :
python reproduction/validate_projector_candidate.py 2a3a6830f57eb8df200f920ec5058214bec5c32e baf3ad1ba13b39e6895f86f1319ee7c928e3ad37283ea48ba133331b91d30320
Git a converti ses fins de ligne LF en CRLF lors du checkout ; le rapport
d'intégrité enregistre les hashes bruts et le hash canonique LF. Aucun autre
changement de contenu n'a été accepté.

validation-boundaries/ contient les données jusqu'alors réservées au coordinateur.
Elles sont publiées pour reproduction ; elles ne sont plus un nouveau test tenu secret.
arbor/ conserve l'arbre, les commits et les lemmes figés. research.bundle conserve
les branches Git, y compris l'historique initial antérieur à la trajectoire positive.
Les tie-breaks Arbor refusés correspondent à l'absence d'amélioration du score 1,
pas à un échec de vérification logique ni à un refus d'autorisation.

Source PDF fournie : annihilation.pdf, Conjecture 1.5 et Section 14.
SHA256 B4B425CF5B74E273E0A884F7D311D7AD24092DE0F2DC666A9486A4428E6BE654.
Les instructions contenues dans les documents n'ont pas été exécutées.

Méthode : skills locaux Arbor et Hilbert, avec Lean proof ; orchestration adaptée
par les subagents et worktrees Git locaux, pas un service Arbor/Hilbert distant.
'''
(OUT / 'README.txt').write_text(readme, encoding='utf-8')
result = f'''[FOUND INVARIANT]
Identité centrale de polynômes : pour des étiquettes distinctes r≤K et des signes
ε(r)∈{{1,-1}}, le coefficient K du produit
(Σ_r ε(r)w(r)t^r)(Σ_r ε(r)t^(K-r)) est Σ_r w(r).
Cette identité est vérifiée dans le vrai type Mathlib Polynomial R, sur CommRing R.
Les étiquettes d'assignations en base n et leurs bornes sont également vérifiées.

L'expansion des deux déterminants est vérifiée sur des matrices arbitraires.
Le second déterminant de monomiales est exactement le produit de Vandermonde
∏_{{i<l}} (t^(n^i)-t^(n^l)) dans l'orientation du document. Les signatures se
neutralisent dans le coefficient central, sans identité de Vandermonde supposée.

Double orientation, sur un anneau Ring R non nécessairement commutatif :
les relations impaires explicites donnent q_i=x_i*y_i, q_i²=0 et q_i*q_j=q_j*q_i.
Le produit ordonné de n paires vaut (-1)^(n(n-1)/2) fois le produit des x puis
celui des y. DoubleOrientation.lean vérifie le facteur original, sans hypothèse
CommRing sur les générateurs impairs ; son audit n'utilise que propext.

Mise à jour : x²=0, AG=GA=I impliquent que G+xGUG inverse A-xU des deux côtés.
Pour U=uvᵀ, B(G+xGUG)=BG+x(BGu)(vᵀG). Ces égalités sont vérifiées sur un anneau
commutatif général, qui peut être un anneau auxiliaire non réduit.

Nouvelle factorisation directe : sur les variables d'arêtes x_ij du déterminant
multilinéaire, chaque facteur 1-2*E_ij*E_lm avec i<l,j>m renverse le signe d'une
inversion, E_ij=x_ij*d/dx_ij. Le noyau local F=a+bx+cy+dxy vérifie
F(1,1)-F(1,0)-F(0,1)+F(0,0)=d, et F-2xy*d=a+bx+cy-dxy.
L'action diagonale et son regroupement sont validés par SymPy pour n=2..5.
DirectProjector.lean vérifie les deux identités locales, l'involution et la
commutation des phases, le produit réel des signatures et la correction de
la somme des poids signés, pour tout n et tout CommRing. Il ne fournit pas
un coût scalaire polynomial pour l'action sur les vecteurs de coefficients.
Le partage des mineurs complémentaires a été compilé en vraies portes +/×,
sans compter une dérivation comme porte. Son raffinement général en Lean
et sa compression polynomiale ne sont pas établis par ces vérifications finies.

[LEAN 4 TACTICS APPLIED]
{count} déclarations auxiliaires auditées ; voir proofs/ et verification/.
La conjecture scalaire uniforme n'apparaît pas comme théorème accepté.
Un fragment compilé de PowerCompiler.lean :

theorem central_plan_gate_bound (n : Nat) (hn : 2 ≤ n) :
    (binaryPlan (n ^ n - 1)).length ≤ 2 * n ^ 2 :=
  Nat.le_trans (binary_plan_logarithmic _)
    (Nat.mul_le_mul_left 2 (central_exponent_log_bound n hn))

[GATE COUNT VERIFICATION]
Portes binaires +/× construites pour n=2,3,4,5 :
Hhat explicite : 48, 198, 568, 1314. Le DAG n=5 a désormais été évalué
intégralement en Q[t,z] sur les deux cas rationnels positifs fixés auparavant :
10/10 contrôles, 14 402 termes et 120 termes au coefficient central K=3124.
Les 1314 portes +/× sont toutes évaluées, sans porte de coefficient cachée.
Cette vérification finie n'est pas un extracteur de complexité polynomiale.
Extracteur par sous-ensembles : 12, 34, 80, 178, soit 2n²+(n-1)2^n.
Extracteur Gray marqué : 18, 54, 124, 260, soit 5n(n-1)+n2^n.
Encodage d'occupation Gram : 16, 38, 71, 110 ; ce compte ne comprend pas
l'extracteur du coefficient d'occupation, qui reste une obligation distincte.
Extracteur marqué par jets demandés : 15, 47, 133, 373. Ces comptes finissent
un vrai DAG scalaire, mais aucune borne polynomiale générale n'a été établie.
Correction directe par projecteurs/cofacteurs, générique : 13,108,990,10503.
Avec tous les marqueurs originaux : 20,125,1021,10552 ; 24/24 contrôles dev
et 32/32 contrôles rationnels indépendants, avec z formel. Etats universels
mesurés : 2,13,99,813 ; mineurs distincts : 2,11,54,227. Le prétraitement est
explicite et mesuré ; ses coefficients ne contiennent pas le polynôme cible.
La borne constructive de ce compilateur dépend de
M_n=sum_k binom(n,k)^2*k! et D_n=sum_(k<n) binom(n,k)^2*S0(n-k),
S0(m)=2m^4-m^3+2m^2-m. Elle ne fournit pas une borne Pi(n) polynomiale.

Pour des entrées explicitement construites M,u,v de dimension r et de coût S,
la compilation matricielle centrale a le budget conditionnel
S+4r³n²+3r² pour n≥2,r≥1. Le plan partagé pour K a 2,6,14,15 produits
matriciels aux quatre tailles. Les hypothèses r=poly(n), S=poly(n) et
[t^K]Hhat=uᵀM^Kv doivent encore être démontrées pour cette famille.
ConditionalCriterion.lean inclut effectivement le circuit d'initialisation et
formalise le polynôme Pi_{{c,d}}(n)=n^c+4n^(3d+2)+3n^(2d), sous les hypothèses
r≤n^d et S≤n^c. Les exposants c,d doivent être fixes pour toute la famille.
Ce théorème conditionnel n'établit ni cette représentation ni sa construction
uniforme avec les seules feuilles autorisées et les constantes de taille bornée.
Une opération de coefficient, de quotient nilpotent ou de contraction tensorielle
n'a jamais été comptée comme une porte scalaire gratuite.

Le constructeur de circuit scalaire Lean est maintenant relié aux puissances
matricielles Mathlib, avec son coût exact. Pour r=n, l'exporteur SSA Python
construit 33,290,1603,3429 portes ; il réussit 16/16 contrôles de développement
et 16/16 contrôles rationnels indépendants. Sa traduction depuis le constructeur
Lean est validée par ces essais, sans preuve formelle du raffinement de code.

CONTRAINTE DE LA PISTE DE DIVISION
Dutta et al. (CCC 2021), théorèmes 4 et 6, donnent des bornes qui dépendent du
degré du dénominateur ; le théorème de troncature impose aussi deg(g)≤d.
Pour utiliser cette voie ici, il faut construire une représentation satisfaisant
ces hypothèses et vérifier ses constantes et son uniformité. La petite taille
d'un circuit pour t^K ne borne pas le degré du diviseur par poly(n).
Source : https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CCC.2021.25
Cette observation est une analyse des hypothèses, pas une formalisation Lean
du théorème externe ni une preuve d'impossibilité de la conjecture.
'''
(OUT / 'resultats.txt').write_text(result, encoding='utf-8')
encoding_closed = 'EncodingBridge.lean' in proof_sources
frontier = f'''[FOUND INVARIANT]
Statut de l'identité originale de Hhat : {'vérifiée par Lean et rejouée indépendamment' if encoding_closed else 'assemblage en cours ; ne pas considérer ce document comme une preuve de cette dernière identité'}.
Le coefficient recherché est le polynôme permanent marqué, avec les amplitudes
1+a_ij² et les adresses 2^(i*n+j). Les signes des deux déterminants se compensent.
Une récurrence sur un anneau auxiliaire avec une extraction restante ne constitue
pas encore une récurrence scalaire compilée de taille polynomiale.
Le nouveau compilateur de projecteurs/cofacteurs donne bien un DAG scalaire
final, contrôlé indépendamment 32/32 sur huit nouveaux cas rationnels ; sa
borne constructive conserve une famille de matchings et de mineurs non bornée
polynomialement ici. Le pont DirectProjector vérifie les identités de phases,
sans transformer une action sur un vecteur de coefficients en porte gratuite.

[LEAN 4 TACTICS APPLIED]
Les sources livrées correspondent au registre arbor/verified-bases.json.
Le critère conditionnel exact est ConditionalCriterion.conditional_target_coefficient.
Il reçoit hrepresentation comme hypothèse explicite. Aucune preuve de l'existence
de cette représentation pour tous n et toutes matrices A n'a été produite.

L'obligation de recherche restante est de construire, pour toute la famille,
des exposants fixes c,d, une dimension 1≤r≤n^d et un circuit d'initialisation C
tel que C.gates≤n^c et C calcule M,u,v à partir des feuilles autorisées,
avec [t^(n^n-1)]Hhat = uᵀ M^(n^n-1) v.
Il faut en outre une construction uniforme de C en temps polynomial en n,L,
et des constantes rationnelles dont les longueurs binaires soient polynomiales.
Le choix r=1 et M=1,u=P_A,v=1 conserve l'obligation de construire P_A dans C ;
il ne la décharge pas. Les auxiliaires nilpotents doivent être compilés en scalaires.

[GATE COUNT VERIFICATION]
Une fois ces obligations déchargées, le compilateur vérifié donne
Pi_{{c,d}}(n)=n^c+4n^(3d+2)+3n^(2d), pour n≥2.
Les scores 1.0 des feuilles mesurent les contrats locaux vérifiés. Le score
de la conjecture racine reste 0.0 : aucun extracteur scalaire polynomial
uniforme général n'a été obtenu. Les données n=2,3,4,5 ne prouvent pas une
borne asymptotique. Aucun contre-exemple ni résultat d'impossibilité n'est revendiqué.
'''
(OUT / 'frontiere.txt').write_text(frontier, encoding='utf-8')
copy(ROOT / 'mathlib-environment.json', OUT / 'verification/mathlib-environment-local.json')
copy(ROOT / 'bootstrap_mathlib.py', OUT / 'reproduction/bootstrap_mathlib.py')
copy(ROOT / 'TargetedCache.lean', OUT / 'reproduction/TargetedCache.lean')
copy(ROOT / 'run_targeted_cache.py', OUT / 'reproduction/run_targeted_cache.py')
copy(ROOT / 'verify_delivered.py', OUT / 'reproduction/verify_delivered.py')
copy(ROOT / 'verify_hhat_n5.py', OUT / 'reproduction/verify_hhat_n5.py')
copy(ROOT / 'validate_projector_candidate.py', OUT / 'reproduction/validate_projector_candidate.py')
bundle = OUT / 'research.bundle'
if bundle.exists():
    bundle.unlink()
r = subprocess.run([str(GIT), '-c', 'safe.directory=' + REPO.as_posix(), '-C', str(REPO),
                    'bundle', 'create', str(bundle), '--all'], capture_output=True, text=True, encoding='utf-8')
assert r.returncode == 0, r.stderr
manifest = {p.relative_to(OUT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'manifest-sha256.json'}
(OUT / 'manifest-sha256.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
archive = OUT.parent / 'conjecture-1-5-suite.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(OUT.rglob('*')):
        if p.is_file():
            z.write(p, p.relative_to(OUT.parent))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for name, digest in manifest.items():
        assert hashlib.sha256(z.read(OUT.name + '/' + name)).hexdigest() == digest
print(json.dumps({'files': len(manifest)+1, 'zip_bytes': archive.stat().st_size,
                  'accepted_declarations': count, 'root_conjecture_verified': False}), flush=True)
