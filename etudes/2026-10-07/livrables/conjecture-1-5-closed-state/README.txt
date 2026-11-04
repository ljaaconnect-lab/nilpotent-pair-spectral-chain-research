La famille effective par sous-ensembles est prouvée dans
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
dans search/. La fenêtre formelle actuelle compte 19 invocations réelles, détaillées dans search/run.json, et la fenêtre précédente 19 reste conservée.
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
