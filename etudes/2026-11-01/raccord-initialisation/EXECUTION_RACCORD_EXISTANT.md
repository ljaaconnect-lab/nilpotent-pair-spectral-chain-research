# Exécution du raccord existant depuis a,z

La dernière consigne de l'auteur est de conserver les objets déjà choisis
et leur raccord. Cette reprise porte donc sur l'exécution commune du
produit compact, des facteurs du lecteur et de l'INTT. La branche du
produit déformé est seulement conservée comme exploration antérieure.

**Un compilateur scalaire exécutable du raccord existant est maintenant
fourni. Sa borne de taille polynomiale générale n'est pas démontrée.**

## Chaîne conservée

\[
B_{ij}=(1+a_{ij}^{2})z^{2^{in+j}},\qquad
H_0(s)=G_B(s)=\prod_i\sum_j B_{ij}s_j,
\]

\[
H_r=H_{r-1}-\frac1rL(H_{r-1}),\quad
L=\frac12\sum_j s_j^2\partial_j^2,\quad
1\le r\le h=\binom n2,
\]

\[
\mathcal Z_Q[k]=\widetilde\Omega\,
\operatorname{INTT}_N[(H_h(t(f)))_f][k],\qquad
t_j(f)=\omega^{fd_j}.
\]

C'est exactement le raccord de `orbite-scalaire/ORBITE_ET_FERMETURE.md`,
avec la correction universelle déjà comprise dans
\(\gamma_nq_{[n]}=\widetilde\Omega\). Les paramètres admissibles
\(Q,\omega,d\) sont fournis, \(Q>\max(2,h)\), et \(\omega\) est
d'ordre exact \(N\), puissance de deux strictement supérieure à \(n\).

## Compilation effectivement réalisée

Le compilateur `spectral/reprise-globale/shared_operator_dag.py` construit
un graphe partagé de portes scalaires. Les formes de lignes sont
multipliées avec un arbre équilibré. Les sous-expressions identiques
sont réutilisées, y compris entre les fréquences après substitution.

La dérivation a lieu pendant la construction du circuit. Pour chaque
paire (nœud, variable), le compilateur mémorise le sous-circuit dérivé.
Il applique exactement la règle de somme et la règle de Leibniz aux
portes. Il élimine les zéros, les produits par un et les calculs entre
constantes. Les majorants de degré par variable permettent d'éviter les
dérivations qui sont nulles.

Chaque facteur \(I-L/r\) est ainsi traduit en portes \(+\) et
\(\times\). Après substitution des phases et compilation d'une vraie
INTT radix-2, les seules variables encore accessibles depuis les sorties
sont **a et z**. Le circuit ne demande ni moments préalablement calculés,
ni valeur terminale en entrée. Aucun opérateur différentiel ne subsiste
comme porte d'exécution.

Le décompte porte sur les portes accessibles depuis les sorties. Le
rapport conserve aussi les nœuds alloués et la taille du cache de
dérivation, pour distinguer la construction du circuit de son exécution.

## Ce que le partage prouve, et ce qu'il ne prouve pas

Le partage est effectif : une dérivée déjà construite pour un nœud est
réutilisée. La preuve de correction de la traduction se fait par
induction sur le graphe, puis sur les facteurs du lecteur.

Pour obtenir la fermeture polynomiale générale, il faut encore une borne
uniforme du nombre de nœuds créés et conservés quand \(n\) augmente.
Les comptes à petites tailles ne fournissent pas cette borne. Le fait
que chaque passe de dérivation ait un coût polynomial dans la taille
du graphe courant ne borne pas à lui seul le graphe après toutes les
passes.

Cette distinction concerne le candidat de compilation testé. Elle ne
constitue aucune impossibilité pour le raccord choisi ni pour un autre
partage de ses calculs.

L'analyse générale est consignée dans
`spectral/reprise-globale/BORNE_DEMONTREE_DU_COMPILATEUR.md`. Elle établit
\(S_0\le6n^2-2\) puis
\(S_{r+1}\le(9n+1)S_r+3n+2\), en comptant les dérivées premières
et secondes réellement partagées. La chaîne entière a donc un majorant
démontré \(NS_h+2N\log_2N+N\). Cette majoration reste exponentielle
en \(n\) ; ce n'est pas une borne inférieure ni une impossibilité
d'obtenir une autre organisation polynomiale.

## Vérification et portée Lean

`spectral/reprise-globale/verify_shared_operator_dag.py` exécute le circuit
depuis les entrées originales et compare tous les slots à une référence
indépendante. Le rapport `shared-operator-dag-validation.json` consigne
les tailles, les empreintes et les cas où z est conservé comme polynôme
formel. La référence de test n'entre pas dans le circuit.

La recompilation et l'exécution indépendantes passent sur **48 tables
numériques** jusqu'à \(n=6\), ainsi que **8 tables avec z formel**
jusqu'à \(n=4\). Les tailles complètes observées sont respectivement
8, 65, 434, 4 441, 35 131 et 242 471 portes. Ce sont les comptes du
candidat exécuté, pas une preuve d'une loi de croissance générale.

La preuve Lean de l'entrelacement des différences reste celle de
`orbite-scalaire/OrbitDifference.lean`. La nouvelle preuve
`dualite/DualReader.lean` vérifie sur de vraies occupations naturelles
la loi de collision sous addition et le passage du lecteur à travers
un monôme, ainsi que sa valeur terminale. Sa recompilation indépendante
réussit sans `sorryAx`, erreur ni avertissement. Ces lemmes ne certifient
pas une borne de complexité du compilateur.

Deux candidats auxiliaires testent d'autres partages de la même action
de L : différentiation inverse dans `dualite/ad_compilation.py`, et
coordonnées logarithmiques avec suppression des divisions dans
`moments/reprise-globale/`. Ils ne changent pas le raccord à exécuter.
