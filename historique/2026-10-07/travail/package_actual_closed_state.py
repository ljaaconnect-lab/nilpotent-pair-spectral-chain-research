"""Deliver exact proofs and reproducible code; do not claim polynomial closure."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT.parent/'outputs/conjecture-1-5-closed-state'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def copy(source,target):
    target=OUT/target;target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,target)

replay=json.loads((ROOT/'n73-independent-replay.json').read_text(encoding='utf-8'))
assert replay['exit_code']==0 and replay['baseline_verified']
for old_folder in ['conjecture-1-5-suite','conjecture-1-5-continuation']:
    for source in (ROOT.parent/'outputs'/old_folder/'proofs').glob('*.lean'):
        copy(source,Path('proofs')/source.name)
source=ROOT/'wt-n73/ActualClosedSubsetTransfer.lean'
assert sha(source)==replay['source_sha256']
copy(source,'proofs/ActualClosedSubsetTransfer.lean')
copy(ROOT/'wt-n71/ScalarDAG.lean','definitions/ScalarDAG.lean')
atomic=[]
for node in ['n75','n76']:
    r=json.loads((ROOT/(node+'-independent-replay.json')).read_text(encoding='utf-8'))
    assert r['exit_code']==0 and r['atomic_lemmas_verified']
    strict=json.loads((ROOT/('wt-'+node)/(node+'-strict-report.json')).read_text(encoding='utf-8'))
    source=ROOT/('wt-'+node)/Path(strict['source']).name
    assert sha(source)==r['source_sha256']
    copy(source,Path('proofs')/source.name)
    copy(ROOT/(node+'-independent-replay.json'),Path('verification')/(node+'-independent-replay.json'))
    for attempt in ROOT.glob(node+'-independent-replay-attempt-*.json'):
        copy(attempt,Path('verification')/attempt.name)
    declarations=strict.get('declarations') or [item['declaration'] for item in strict['goal_statuses']]
    atomic.append({'node':node,'source':source.name,'declarations':declarations})
for node in ['n71','n73','n75','n76']:
    wt=ROOT/('wt-'+node)
    for source in wt.glob(node+'-*.json'):
        copy(source,Path('verification')/source.name)
    for source in (wt/(node+'-compiler-rounds')).glob('*'):
        copy(source,Path('verification')/(node+'-compiler-rounds')/source.name)
    if node=='n76':
        for pattern in ['n76-round-*.txt','AtomicSecondPrefix.round*.lean','run_atomic.py']:
            for source in wt.glob(pattern):copy(source,Path('verification/n76-rounds')/source.name)
copy(ROOT/'n73-independent-replay.json','verification/n73-independent-replay.json')
copy(ROOT/'verify_closed_state_delivery.py','verify_closed_state.py')
copy(ROOT/'leap-global-search.json','search/leap-global-search.json')
for name in ['run.json','tree.json','verified-bases.json']:
    copy(ROOT/'research/.arbor'/name,Path('search')/name)
for node in ['n69','n70','n72','n74','n75','n76','n77']:
    wt=ROOT/('wt-'+node)
    for pattern in [node+'-*.json','N'+node[1:]+'*.md',node+'-*.md']:
        for source in wt.glob(pattern): copy(source,Path('frontier')/node/source.name)
for name in ['pole_functional_candidate.py']:
    copy(ROOT/'wt-n72'/name,Path('frontier/n72')/name)
for name in ['candidate.py','pfaffian_coefficients.py','n69_interfaces.py','compile_n69_references.py',
             'n69-protocol.json','n69-candidates.json','n69-source-freeze.json']:
    copy(ROOT/'wt-n69'/name,Path('reference/wt-n69')/name)
for source in (ROOT/'wt-n69').glob('n69-*.json'):
    copy(source,Path('reference/wt-n69')/source.name)
for name in ['validate_jet_reference.py','n69-reference-validation-freeze.json','n69-reference-validation-report.json']:
    copy(ROOT/name,Path('reference')/name)
copy(ROOT/'atomic_decomposition.txt','atomic-decomposition.txt')
copy(ROOT/'direct_raccord.txt','direct-raccord.txt')
for pattern in ['atomic_prefix_circuit.py','atomic-prefix-circuit-*.json','prefix?-n?-*.json']:
    for source in ROOT.glob(pattern):copy(source,Path('local-circuits')/source.name)
for source in (ROOT/'wt-n77').glob('*.py'):
    if source.name.startswith('direct_') or source.name=='evaluate_direct_corrected.py':
        copy(source,Path('direct-raccord')/source.name)
for source in (ROOT/'wt-n77').glob('n77-*.json'):
    copy(source,Path('direct-raccord')/source.name)
for name in ['N77_BLUEPRINT.md','ActualClosedSubsetTransfer.lean']:
    copy(ROOT/'wt-n77'/name,Path('direct-raccord')/name)
copy(ROOT/'validate_direct_polynomial.py','direct-raccord/validate_direct_polynomial.py')
for source in (ROOT/'direct-polynomial-validation').glob('*.json'):
    copy(source,Path('direct-raccord')/source.name)
git=Path('C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe')
repo=ROOT/'research'
bundle=OUT/'search/nodes.bundle'
subprocess.run([str(git),'-c','safe.directory='+repo.as_posix(),'-C',str(repo),
                'bundle','create',str(bundle),*[f'arbor/n{n}' for n in range(69,78)]],check=True)
verified_bundle=subprocess.run([str(git),'-c','safe.directory='+repo.as_posix(),'-C',str(repo),
                               'bundle','verify',str(bundle)],capture_output=True,text=True,check=True)
(OUT/'verification/git-bundle-verification.txt').write_text(verified_bundle.stdout+verified_bundle.stderr,encoding='utf-8')

README='''La famille effective par sous-ensembles est prouvée dans
proofs/ActualClosedSubsetTransfer.lean. Sa dimension est exactement 2^n.
La conjecture 1.5 demeure non résolue : aucune borne de circuit Pi(n), ni
construction uniforme polynomiale de son extracteur, n'est démontrée.

Les données initiales sont explicites : F0(U)=1 si U est vide, 0 sinon.
La mise à jour F(k+1)(U)=somme j dans U de b(k,j)Fk(U.erase j) contient
uniquement additions et multiplications. L'invariant coefficient_invariant
est prouvé pour tous n,k,U,b. terminal_matrix identifie la sortie avec la
somme sur les permutations ; marked_target couvre tout n,A, et marked_central
le vrai coefficient central du document pour n>=2. Aucun coefficient ni
terminal inconnu n'est une donnée initiale de la récurrence.

Les 18 théorèmes du nouveau fichier ont passé le compilateur Lean 4.34.1.
Le commit 97513bc5e9cca5e0b33d0844980d29da1121a234 a été recompilé dans
un worktree indépendant : exit 0, 18 audits acceptés, source byte-identique.
La base de confiance est propext, Classical.choice, Quot.sound. Les anciennes
dépendances sont les sources déjà vérifiées et inchangées du dossier suite.
definitions/ScalarDAG.lean définit seulement la composante existentielle exacte
des circuits ; ses huit définitions auditées ne constituent aucun théorème
de résolution. L'uniformité opérationnelle reste une obligation requise.

Le code de référence des jets est séparé dans reference/. Il conserve 2^n
coordonnées. Ses portes génériques mesurées pour n=2,3,4,5 sont 48,228,832,2640,
et marquées 55,245,863,2689. Tous les nœuds sont +/*, avec constants -1,0,1
et seulement les entrées prescrites p et z. Le supplément de développement
gelé a passé 108/108 contrôles exacts sur 36 cas identité/Vandermonde/cycle
et z=-1,0,1. Ce supplément ne modifie pas le score racine. La nouvelle frontière
réservée de l'extracteur demeure intacte ; le replay formel de référence a été
exécuté séparément. Les formules des frontières n69,n70,n72,n74 restent informelles
sauf les fichiers explicitement placés dans proofs/.

Depuis la reprise : n69 secteurs contextuels et fusion du premier préfixe ;
n70 transport des bases et réponse diagonale non initialisée ; n72 synthèse
positive de trois encodages rationnels ; n73 vraie fermeture globale de
référence ; n74 transfert adapté au suffixe réel. Les cycles sont consignés
dans search/. La fenêtre formelle actuelle compte 7 invocations (2 n71,
4 n73, 1 replay indépendant), et la fenêtre précédente 19 reste conservée.
Un score local ou une définition compilée ne prouve pas la conjecture.

Reproduction locale : python verify_closed_state.py --check-only vérifie
les empreintes sans lancer Lean. python verify_closed_state.py relance
le nouveau fichier avec les chemins Lean/Mathlib et le cache déjà préparés
dans le workspace ; chaque invocation réelle sera nouvelle et comptable.
Les options --lean-bin, --environment-file et --cache-dir permettent de
désigner explicitement le même environnement. Aucun téléchargement n'est lancé.
Le résultat et l'olean de reproduction sont écrits dans work/, hors des livrables.
python reference/validate_jet_reference.py rejoue le supplément exact gelé.

Attributions des méthodes utilisées, vérifiées sur leurs notices arXiv :

- Kassis, T., Agarwal, V., He, Y., Patel, D., et Brueckner, A. M. (2026).
  Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents.
  https://doi.org/10.48550/arXiv.2609.00065
- Kung, P.-N., et al. (2026). LEAP: Supercharging LLMs for Formal Mathematics
  with Agentic Frameworks. https://doi.org/10.48550/arXiv.2606.03303

Arbor et Hilbert sont ici appliqués par coordination locale et compilation réelle.
Le graphe LEAP est une adaptation locale ; aucun benchmark ni agent original
non publié n'a été exécuté ou reproduit.
'''
run=json.loads((ROOT/'research/.arbor/run.json').read_text(encoding='utf-8'))
formal_count=run['current_formal_window']['actual_total_compiler_invocations']
README=README.replace('n69,n70,n72,n74 restent informelles','n69,n70,n72,n74 restent informelles')
README=README.replace('La fenêtre formelle actuelle compte 7 invocations (2 n71,\n4 n73, 1 replay indépendant),',
    'La fenêtre formelle actuelle compte '+str(formal_count)+' invocations réelles, détaillées dans search/run.json,')
README += '''

Recentrage demandé : la cible active est le circuit scalaire du polynôme
complet PA=CnDA. L'extraction centrale est une reformulation historique
équivalente et ne fait pas partie des obligations supplémentaires de cette
voie directe. n77 raccorde directement les marques et les états du baseline
jusqu'à PA ; la taille du raccord de référence reste exponentielle.
Le lien avec la définition diagonale Cn est établi dans le document ;
la cible Lean présente est markedPermanent. La formalisation directe de cet
opérateur et son identité n'est pas revendiquée comme déjà compilée.
Le circuit direct complet a également été validé comme polynôme en z,
sans spécialisation numérique de z, pour quatre matrices rationnelles
supplémentaires. Toutes les sorties complètes (2,6,24,120 monômes) et les
comptes de portes (12,34,80,178) ont été vérifiés. Ce contrôle fini ne
constitue pas une preuve de taille polynomiale pour tout n.

Nouvelle décomposition élémentaire : atomic-decomposition.txt expose A1..A6
et B1..B4, ainsi que le problème de compression encore ouvert. Les nouveaux
fichiers AtomicFirstPrefix.lean et AtomicSecondPrefix.lean ont été vérifiés
par des replays indépendants de leur commit exact, exit0, axiomes standard.
La normalisation du premier mineur est une hypothèse algébrique locale,
et aucun des deux fichiers ne postule une fusion générale.

local-circuits/atomic_prefix_circuit.py construit de vrais DAG +/* pour
une requête J de profondeur1 ou2, avec ou sans les marques p,z. Les 2160
contrôles exacts ont passé. Initialiser les trois sommes de profondeur2
coûte 4n-3 portes ; une requête ajoute au plus 3|J|+7 portes. Faire cela
pour tous les 2^n sous-ensembles ne constitue pas une compression polynomiale.
Les validations et coûts exacts sont dans atomic-prefix-circuit-report.json.
La reproduction --node n75 ou --node n76 sélectionne une seule nouvelle
preuve pour compilation ; --check-only valide les empreintes sans Lean.
python direct-raccord/validate_direct_polynomial.py --source
direct-raccord/direct_corrected_circuit.py --out-dir <dossier-de-travail>
rejoue le contrôle symbolique complet, sans extraction de coefficient.
'''
(OUT/'README.txt').write_text(README,encoding='utf-8')
status={'root_conjecture_verified':False,'polynomial_closed_state_family_verified':False,
        'actual_closed_baseline_verified':True,'state_dimension':'2^n',
        'baseline_source':'proofs/ActualClosedSubsetTransfer.lean','new_baseline_theorems':18,
        'independent_replay_exit_code':0,'reference_positive_checks':'108/108 development only',
        'formal_invocations_current_window':formal_count,'prior_window_preserved':19,
        'atomic_proof_files':atomic,'local_circuit_development_checks':'2160/2160',
        'local_circuit_scope':'Fixed prefix depth1 or2, one explicit subset J',
        'direct_complete_polynomial_checks':'4/4 symbolic whole-polynomial cases',
        'direct_development_cases':'36/36 exact Fraction cases',
        'new_root_extractor_heldout_boundary_opened':False,
        'independent_baseline_replay_boundary_run':True,
        'active_target':'Whole corrected polynomial PA=CnDA; direct scalar circuit',
        'coefficient_extraction_strategy':'Archived equivalent formulation, not an additional obligation',
        'direct_Cn_semantic_bridge_formally_verified':False,
        'open_obligation':'Construct initialized polynomial-size scalar updates connected to the complete corrected polynomial, with admissible literal bits and uniform polynomial bit-time compilation.'}
(OUT/'status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
files={p.relative_to(OUT).as_posix():sha(p) for p in sorted(OUT.rglob('*'))
       if p.is_file() and p.name!='manifest.json'}
(OUT/'manifest.json').write_text(json.dumps({'sha256':files},indent=2),encoding='utf-8')
print(json.dumps({'output':str(OUT),'files':len(files),'root_conjecture_verified':False}))
