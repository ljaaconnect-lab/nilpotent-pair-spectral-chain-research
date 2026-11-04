"""Create a reviewable delivery from committed artifacts and coordinator evidence."""
import hashlib, json, shutil, subprocess, zipfile
from pathlib import Path
root=Path(__file__).resolve().parent
out=root.parent/'outputs'/'conjecture-1-5'
out.mkdir(parents=True,exist_ok=True)

def copy_files(src,dst):
    dst.mkdir(parents=True,exist_ok=True)
    for p in src.iterdir():
        if p.is_file() and p.name not in {'.git','.gitignore'}:
            shutil.copyfile(p,dst/p.name)

copy_files(root/'wt-n5',out/'positive')
copy_files(root/'gate-n3',out/'proofs')
copy_files(root/'wt-n2',out/'archive-initial-audit')
copy_files(root/'research'/'.arbor',out/'arbor')
copy_files(root/'test-boundary',out/'validation-boundaries')
for src in [root/'positive-test-report.json',root/'proof-replay.json',root/'bridge-inputs.json',root/'gate-n1'/'test-report.json']:
    shutil.copyfile(src,out/src.name)

readme='''CONJECTURE 1.5 - REPRODUCIBLE POSITIVE INVESTIGATION
Date: 7 October 2026 (Africa/Lagos)

STATUS: partial constructive progress. The polynomial scalar extractor is NOT proved.
This package contains runnable circuits, exact symbolic checks, kernel-verified helper
lemmas, a constructive A/B/C blueprint and the persistent Arbor tree.

Use local Python 3.12 with SymPy 1.14.0. From positive/:
  python evaluate.py --split dev
  python evaluate_recurrence.py
  python sympy_invariants.py

The installed Lean binary is:
C:\\Users\\REGIS\\Documents\\Codex\\runtimes\\elan\\toolchains\\leanprover--lean4---v4.34.1\\bin\\lean.exe
From proofs/, compile CoreBridge.lean and GeneratedCoreN2.lean with that binary.
Both use import Std and include #print axioms. Mathlib is not installed in this
environment; GeneratedBridge.lean is an unverified Mathlib draft kept separately.

proof-replay.json records fresh coordinator compilation of the committed files,
exit codes and axiom outputs. The accepted trust base is propext, Classical.choice,
and Quot.sound; no sorryAx or user-added conjecture axiom is accepted.
Nine accepted declarations represent seven distinct helper results; the two generated
n2 declarations duplicate/specialize existing results. None states the root conjecture.

positive-test-report.json: 40/40 held-out exact formal-z checks for n=2,3,4,5.
test-report.json: 24/24 Hhat checks on rational matrices n=2,3,4.
The positive development score is 48/48; the SymPy symbolic checklist is 112/112.
These scores measure exact checks and are not probabilities or asymptotic proofs.

Git artifacts are preserved on arbor/n1,n2,n3,n4,n5 and arbor/delivery. research.bundle
includes named branches; the original circuit incumbent is arbor/best (node n1).
The recurrence branch ties the accuracy incumbent, so it is retained as explored
rather than promoted through the strict-improvement Arbor gate.

Source: supplied annihilation.pdf, Conjecture1.5 and Section14. Source SHA256:
B4B425CF5B74E273E0A884F7D311D7AD24092DE0F2DC666A9486A4428E6BE654
The PDF was treated as mathematical source material, not as agent instructions.
The n=5 Hhat DAG was constructed and counted, while the full determinant encoding
was exactly expanded only for n=2,3,4. n=5 extractor variants were independently
checked as formal polynomials in z.

The initial audit predates the user's positive-only steering and is archived separately.
It has development-only status; no further counterexample search was performed.

Method attribution: Arbor skill v1.6, local Hilbert skill adaptation, Lean proof skill.
Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026).
Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents.
arXiv:2609.00065. https://arxiv.org/abs/2609.00065
The local Arbor state manager and adapted Hilbert workflow were used; upstream
autonomous model services and benchmark implementations were not executed.
'''
(out/'README.txt').write_text(readme,encoding='utf-8')

report='''RÉSULTATS - RECHERCHE CONSTRUCTIVE DE LA CONJECTURE 1.5
7 octobre 2026, Africa/Lagos

Résultat principal : la conjecture reste non résolue par cette exécution.
Une représentation constructive exacte et des lemmes auxiliaires sont disponibles.
La compression scalaire polynomiale de l'extracteur n'a pas été établie.

CIBLE PRÉSERVÉE
Pour toute matrice rationnelle A, p_ij=1+a_ij² et w_ij=2^(in+j), indices à partir de 0.
P_A(z)=C_n(D_A(z))=somme_σ produit_i p_(i,σ(i)) z^(somme_i w_(i,σ(i))).
Pour n>=2, K=n^n-1 et Hhat=1+t^(2K)+det(p_ij z^w_ij t^(j n^i))
fois produit_(i<l)(t^(n^i)-t^(n^l)). Le constructeur uniforme, les constantes de
longueur bornée et les portes scalaires +/× restent des obligations du problème.
Le cas n=1 est le cas direct p11*z, sans la normalisation centrée utilisée pour n>=2.

[FOUND INVARIANT]
États S : sous-ensembles des colonnes. Depuis S, l'arête vers S union {j} porte
b_(|S|,j)=p_(|S|,j) z^w_(|S|,j), j absent de S. L'état plein possède une boucle de poids 1.
Chaque chemin du vide au plein choisit exactement une permutation des colonnes.
L'argument par chemins donne (M^k)[vide,plein]=P_A(z) pour k>=n.
Dans la décomposition M=[[N,b],[0,1]], N^n=0 et
M^k=[[N^k, somme_(i=0..k-1) N^i b],[0,1]]. Ainsi M^K=M^n lorsque K>=n.
Cette identité générale pour la matrice de transfert est un argument informel,
confirmé symboliquement pour n=2,3,4,5, pas encore un théorème Lean de matrices.

Les facteurs tensoriels R_j commutent et vérifient R_j²=0. Les opérateurs de ligne
T_i=somme_j b_ij R_j réalisent la même construction dans l'algèbre commutative
à générateurs de carré nul. SymPy confirme les relations avec des poids x_ij
indépendants pour les tailles testées ; les circuits conservent les marqueurs z.

En posant a_k=uᵀM^k v : a_k=0 si k<n, puis a_k=P_A pour k>=n ; donc
a_(k+n+1)=a_(k+n). Le vecteur d'initialisation d'une réalisation compagnon de
dimension n+1 contient a_n=P_A. Ce vecteur n'est pas une donnée déjà calculée
à coût polynomial : cette représentation seule ne fournit pas l'extracteur demandé.

[LEAN 4 TACTICS APPLIED]
Lean 4.34.1 compile les deux fichiers auxiliaires, code de sortie 0.
Sept résultats distincts : decode_head, decode_tail, encodeDigits_injective,
central_label_iff, orbit_stabilizes, n2_pair_factorization, n2_central_convolution.
Deux déclarations supplémentaires sont générées depuis SymPy et reproduisent
la factorisation et la convolution rationnelle pour n=2.
Les tactiques effectives sont simp, induction, cases, grind et omega.
Les audits #print axioms ne contiennent pas sorryAx ; ils utilisent uniquement
propext, Classical.choice et Quot.sound de la base de confiance déclarée.
Le lemme orbit_stabilizes suppose un point de stabilisation hfix : il ne prouve
pas à lui seul hfix pour la matrice M ni son coût de compilation.

Le BlueprintInformel organise trois obligations constructives :
A. Représentation commutante à carré nul et compilation scalaire compacte.
B. Factorisation de la paire de déterminants et filtrage des labels égaux.
C. Extraction puis compilation dans le modèle scalaire original.
L'injectivité et le cas n=2 sont des bases vérifiées. La preuve générale de la
paire de déterminants et la compilation polynomiale ne sont pas fermées.
Les opérations de division, résidu et coefficient ne sont pas comptées comme
des portes gratuites. Le brouillon Mathlib a un diagnostic de dépendance manquante.

[GATE COUNT VERIFICATION]
n=2 : K=3, r=4 ; Hhat 48 portes ; M^K 17 ; M^n 13 ; chaîne de lignes 12.
n=3 : K=26, r=8 ; Hhat 198 portes ; M^K 83 ; M^n 51 ; chaîne de lignes 34.
n=4 : K=255, r=16 ; Hhat 568 portes ; M^K 357 ; M^n 150 ; chaîne de lignes 80.
n=5 : K=3124, r=32 ; Hhat 1314 portes ; M^K 975 ; M^n 511 ; chaîne de lignes 178.
Les portes +/× réelles sont comptées, y compris les marqueurs construits par carrés.
La formule de la chaîne est 2n²+(n-1)2^n. Cette construction a donc encore
une dépendance exponentielle. Une extrapolation polynomiale depuis quatre tailles
ne prouve pas l'existence de Π(n).
La borne dense du produit matriciel est 2r³-r² et le nombre de produits pour K
est au plus 2*floor(log2 K). La description tensorielle succincte n'annule pas r=2^n.

VALIDATION ET ÉTAT DE L'ARBRE
Simulation Hhat n=2..4 : 36/36 développement, 24/24 validation indépendante.
Constructions positives n=2..5 : 48/48 développement, 40/40 validation indépendante.
SymPy, poids symboliques n=2..5 : 112/112 contrôles de développement.
La limite de quatre cycles Arbor et de trois niveaux a été respectée.
16 rounds Lean exécutés par Hilbert, puis deux recompilations du coordinateur.
Chaque déclaration acceptée est figée dans un nœud « Verified Base Axiom » :
cette expression est une étiquette utilisateur pour un lemme prouvé, pas une
nouvelle déclaration Lean axiom. Les doublons générés ne sont pas des résultats
mathématiques indépendants. L'arbre et les versions Git sont conservés.
Le compteur d'erreurs des auxiliaires acceptés est zéro ; le but racine reste ouvert.

PROCHAINE OBLIGATION EXACTE
Construire uniformément des données u_A(z), M_A(z), v_A(z), de dimension et de
taille scalaire polynomiales, sans utiliser P_A parmi les données d'entrée, puis
prouver leur égalité au coefficient cible et la borne de portes pour tout n,A.
Une autre compilation équivalente dans le même modèle pourrait aussi fermer ce but.
Le dossier livré fournit les bases réutilisables ; aucune preuve de cette obligation
n'est présentée.
'''
(out/'resultats.txt').write_text(report,encoding='utf-8')
git='C:/Users/REGIS/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
bundle=out/'research.bundle'
subprocess.run([git,'bundle','create',str(bundle),'--all'],cwd=root/'research',check=True,capture_output=True)
manifest={str(p.relative_to(out)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
          for p in out.rglob('*') if p.is_file() and p.name!='manifest-sha256.json'}
(out/'manifest-sha256.json').write_text(json.dumps(manifest,indent=2))
zip_path=out.parent/'conjecture-1-5.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for p in out.rglob('*'):
        if p.is_file(): z.write(p,Path('conjecture-1-5')/p.relative_to(out))
print(json.dumps({'deliverable':str(zip_path),'files':len(manifest)+1,
                  'root_conjecture_verified':False,'lean_helper_declarations':9},indent=2))
