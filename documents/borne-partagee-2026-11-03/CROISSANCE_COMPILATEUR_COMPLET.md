# Croissance du compilateur direct partagé, INTT comprise

Date : 3 novembre 2026.

## Énoncé et périmètre

Cette note concerne exclusivement `compile_chain` et la classe `DAG` du fichier historique
[`shared_operator_dag.py`](../../etudes/2026-11-01/raccord-initialisation/spectral/reprise-globale/shared_operator_dag.py),
empreinte SHA256 `a17cbcdae56dc3338ae46d42239d2a1a99e0b169865f16fc62f5c83b31cb3b06`.
Ses règles de partage et de simplification restent inchangées. Le plafond pratique
de nœuds doit être suffisamment grand pour terminer la compilation ; il ne fait
pas partie de la définition mathématique du circuit à borner.

Soit `C_complet(n)` le nombre de portes scalaires `+` et `*` dans l'union des
sous-graphes accessibles depuis toutes les sorties finales de `compile_chain`,
préparation depuis `a,z`, toutes les `h=binom(n,2)` compositions, substitutions
de phases et véritable INTT comprises. Pour `n=2m>=4`, `Q` premier,
`Q>max(2,h)`, et les paramètres spectraux admissibles du programme,

\[
\boxed{C_{\rm complet}(2m)\ge\binom{2m}{m}\ge2^m.}
\]

Le compilateur direct fixé n'admet donc pas de majorant polynomial uniforme
en `n`. **Cette conclusion ne porte pas sur tous les circuits scalaires de la
même sortie, sur une autre représentation, ni sur une autre règle de fusion.**
Elle ne remet pas en cause l'existence de constructions exactes de
`Y=lambda(F_0)` déjà obtenues dans le projet.

La [preuve antérieure du préfixe](../../etudes/2026-11-01/borne-chaine-generale/si-direct/CROISSANCE_DAG_DIRECT.md)
établissait la présence des témoins ci-dessous avant la correction terminale.
Nous explicitons ici leur conservation jusqu'aux sorties de la vraie INTT.

## 1. Initialisation et témoins

Le programme construit, en portes scalaires,

\[
B_{ij}=(1+a_{ij}^2)z^{2^{in+j}},\quad
G(s)=\prod_{i=0}^{n-1}\sum_{j=0}^{n-1}B_{ij}s_j,
\]
\[
L=\frac12\sum_j s_j^2\partial_j^2,\quad
H_0=G,\quad H_r=H_{r-1}-\frac1r L(H_{r-1})\quad(1\le r\le h).
\]

Les puissances de `z` restent formelles et sont calculées par carrés successifs.
Pour chaque ensemble `A` de `m` colonnes, les colonnes étant traitées dans l'ordre
croissant pour fixer les appels syntaxiques, considérons la racine calculée

\[
V_A=\left(\prod_{j\in A}\partial_j^2\right)G.
\]

Ces ensembles sont uniquement des témoins externes du comptage. Le programme
ne reçoit pas cette famille en entrée et ne construit pas un tableau de
sous-ensembles ou de jets.

## 2. Les racines témoins apparaissent dans les premières compositions

Une occurrence marquée d'une racine `V` est un chemin qui la relie à la racine
courante, en traversant des additions et des multiplications dont l'autre
facteur est un monôme `c*s^beta` avec `c!=0`.

Dans `DAG.derivative`, la règle de Leibniz crée explicitement les deux branches
sur un produit. Suivre la branche qui dérive l'enfant marqué conserve l'autre
facteur. Les additions dérivent leurs deux enfants. Si la dérivée de `V` est
non nulle et non constante en `a,z`, les règles zéro/unité et le calcul entre
constantes ne peuvent supprimer cette occurrence. Le cache renvoie la même
racine déjà construite ; il ne change pas ses enfants.

Deux dérivations successives conservent ainsi une occurrence marquée de
`partial_j^2 V`. La construction de `L`, puis celle de `H_r`, ajoutent des
facteurs `s_j^2/2` et `-1/r`, dont les constantes sont non nulles puisque
`Q>max(2,h)`. Par induction, `H_k` contient le nœud de chacune des dérivées

\[
\partial_{j_k}^2\cdots\partial_{j_1}^2G
\]

pour laquelle les dérivées intermédiaires ont un terme non nul dépendant des
entrées originales. Pour `k<=m` et des colonnes distinctes, attribuer deux
lignes à chacune des colonnes déjà dérivées produit un tel terme, de coefficient
`2^k`. Les lignes restantes peuvent être attribuées à une colonne non traitée.
La caractéristique est différente de deux. Les racines `V_A` sont donc toutes
présentes dans `H_m`.

## 3. Racines distinctes et absence syntaxique de variables auxiliaires

Leur formule est

\[
V_A=2^m\sum_{\substack{\phi:\{0,\ldots,n-1\}\to A\\
|\phi^{-1}(j)|=2\;(j\in A)}}\prod_i B_{i,\phi(i)}.
\]

La partie de degré `2n` en `a` possède, pour chaque application `phi`, le
monôme de coefficient non nul

\[
2^m z^{\sum_i2^{in+\phi(i)}}\prod_i a_{i,\phi(i)}^2.
\]

Des applications distinctes donnent des monômes distincts en `a`. Le support
des colonnes est exactement `A` ; deux ensembles différents donnent donc des
polynômes différents, même après l'initialisation spécialisée depuis `a,z`.
Ils ne peuvent être portés par le même nœud. Chaque racine est une porte
arithmétique, puisqu'elle n'est ni une constante ni une variable d'entrée.

Les dérivées intermédiaires sont syntaxiquement homogènes en `s`, de degré
`n-2k`. Les additions joignent des degrés identiques, les multiplications
additionnent des degrés non négatifs et les branches nulles sont supprimées.
Au degré zéro, aucun descendant d'un `V_A` ne peut être une variable `s_j`.
Ainsi, l'absence de `s` ne dépend pas d'une annulation sémantique que le DAG
aurait omis de simplifier.

## 4. Conservation après toutes les h compositions

Chaque mise à jour ultérieure crée `H_r=H_(r-1)+(-1/r)*L(H_(r-1))` et garde
la racine précédente comme enfant. `DAG.add` ne réalise ni collecte de termes
opposés, ni factorisation distributive globale. Les racines `V_A`, non
constantes, restent donc accessibles par des occurrences marquées jusqu'à
`H_h`.

Cette étape vaut pour la liste complète `1,...,h` utilisée par `compile_chain`,
pas seulement pour un préfixe fusionné du projecteur. Même lorsque des termes
se compensent mathématiquement, cette règle de construction ne supprime pas
les branches non constantes qui les portent.

## 5. Conservation après les phases

Pour une fréquence `f`, la substitution est

\[
s_j=\omega^{f d_j}.
\]

Toutes ces valeurs sont non nulles. Les facteurs `c*s^beta` des chemins
marqués deviennent des constantes non nulles. Les raccourcis de produits
par un peuvent raccourcir un chemin mais ne suppriment pas son extrémité
`V_A`. Celle-ci, déjà indépendante de `s` dans son graphe, est réutilisée
avec le même identifiant de nœud par l'internement.

Chaque sortie de fréquence contient donc encore les `binom(n,m)` racines.
Cet argument n'exige aucune propriété particulière des labels `d_j`.

## 6. Conservation pendant la véritable INTT

Dans `DAG.intt`, un papillon construit

\[
u=e+\alpha o,\qquad v=e-\alpha o,
\]

avec `alpha` une puissance de `omega`, donc non nulle. La soustraction est
un produit par `-1` suivi d'une addition. Un chemin vers une racine non
constante dans `e` ou `o` est conservé : aucune de ces multiplications ne
porte le facteur zéro, et une addition à un terme non constant n'est pas
calculée comme une opération entre constantes. Même dans le cas où les deux
opérandes sont mathématiquement opposés, `DAG.add` ne réalise pas cette
annulation.

La permutation des entrées ne change pas les sous-graphes. À chaque niveau
des papillons, chaque entrée possède au moins un chemin vers une sortie.
L'union des racines témoins atteignables reste donc conservée jusqu'à la
normalisation par `1/N`. Celle-ci est non nulle puisque `N` divise `Q-1`.

Il reste ainsi au moins `binom(2m,m)` portes distinctes dans l'union des
sous-graphes des sorties finales. Choisir une colonne dans chacune de `m`
paires de colonnes donne `2^m` ensembles distincts de taille `m`, d'où
`binom(2m,m)>=2^m`. Cette quantité dépasse toute borne `K*(2m)^c` avec
`K,c` constants.

## 7. Vérification de la construction historique

[`verify_full_chain.py`](verify_full_chain.py) appelle directement
`compile_chain` sans modifier la classe ni ses règles. Il inspecte ensuite
les racines intermédiaires en rejouant les mêmes appels : aucune porte ne
doit être allouée par ce rejeu. Les témoins sont récupérés par lecture des
entrées déjà présentes du cache de dérivées ; leur inspection n'alloue ni
nœud ni entrée de cache.

Pour `n=4,6`, `Q=97`, il contrôle leur présence après `h`, après chacune des
substitutions de phase et dans l'union des sorties de la vraie INTT. Il
contrôle également leur distinction sémantique depuis `a,z` : avec `z=1`,
deux lignes attribuées à chaque colonne de `A`, `a_ij=0` sur les entrées
choisies et `a_ij=22` ailleurs, les valeurs des témoins sont
`2^m*delta_(A,A')`, puisque `1+22²=0 mod 97`. La sortie complète vaut alors
zéro, ce qui vérifie explicitement que la compensation finale n'efface pas
syntaxiquement les témoins. Un choix bijectif supplémentaire produit un
dans le slot utile et zéro ailleurs.

Le rapport conserve les empreintes du code historique, de la preuve
antérieure, du présent texte et du vérificateur, ainsi que les décomptes.
Ces contrôles finis corroborent la preuve ; ils ne la remplacent pas.
L'atteignabilité jusqu'à l'INTT n'est pas revendiquée comme formalisée en Lean.

Reproduction, sans modification du compilateur :

```text
python -B documents/borne-partagee-2026-11-03/verify_full_chain.py --write-report
```
