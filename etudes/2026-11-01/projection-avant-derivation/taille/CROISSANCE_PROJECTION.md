# Taille du compilateur à projection immédiate

## Énoncé et portée exacte

Soit `C_Y(n)` le nombre de portes scalaires `+` et `*` atteignables dans
la sortie de **`direct_projection.py` avec la classe historique `DAG`**.
La préparation depuis les entrées `a,z` est comprise. Pour `n=2^k>=4`,
`m=n/2`, et tous les paramètres admissibles du projet,

\[
\boxed{C_Y(2m)\ge {2m\choose m}\ge 2^m.}
\]

Ainsi, pour ce compilateur précis, il n'existe pas de constantes `K,c`
indépendantes de `n` donnant `C_Y(n)<=K*n^c` à toutes les tailles.
La sous-suite des puissances de deux suffit à cette conclusion.

Ce résultat est une propriété de son graphe effectivement construit.
**Il ne constitue aucune borne inférieure pour tous les circuits
scalaires calculant la même sortie.** Il ne s'applique pas automatiquement
à une autre compilation, à une collecte algébrique ou à une autre fusion.

Les règles concernées sont celles du code : partage des nœuds identiques,
commutation des deux enfants pour leur internement, suppression des
produits par zéro ou un, des sommes avec zéro et calcul des opérations
entre constantes. Il n'y a pas de factorisation distributive globale.

## 1. Le produit initial possède deux blocs de même taille

On travaille dans `F_Q[a,z,s]`, avec `Q` premier et
`Q>max(2,binom(n,2))`, et

\[
B_{ij}=(1+a_{ij}^2)z^{2^{in+j}},\qquad
G=\prod_{i=0}^{n-1}\sum_{j=0}^{n-1}B_{ij}s_j.
\]

Pour une puissance de deux `n`, le produit équilibré utilisé par `DAG`
possède à sa racine deux facteurs de `m` lignes chacun. Notons leurs
ensembles de lignes `R` et `R'`, et leurs racines effectives `U,V` :

\[
G=UV,\quad
U=\prod_{i\in R}\sum_jB_{ij}s_j,\quad
V=\prod_{i\in R'}\sum_jB_{ij}s_j,
\quad |R|=|R'|=m.
\]

Le tri syntaxique des deux enfants peut échanger `U` et `V`, sans modifier
l'argument. Les deux ensembles de lignes sont disjoints et couvrent
toutes les lignes.

Posons `P_j(F)=F|_(s_j=0)` et `E_j(F)=P_j(partial_j F)`. Le compilateur
construit successivement `H_0=UV` puis `H_(t+1)=E_t(H_t)`.

## 2. Un invariant sur des produits réellement atteignables

Écrivons `J_t={0,...,t-1}`. Pour `A` inclus dans `J_t`, définir les
**nœuds produits par les opérations du compilateur**

\[
U_{A,t}=\left(\prod_{j\in J_t\setminus A}P_j\right)
         \left(\prod_{j\in A}E_j\right)U,
\qquad
V_{J_t\setminus A,t}=\left(\prod_{j\in A}P_j\right)
         \left(\prod_{j\in J_t\setminus A}E_j\right)V.
\]

Les opérations sont exécutées dans l'ordre croissant des colonnes ; cette
convention fixe les appels syntaxiques, pas seulement leurs polynômes.
Une affectation partielle `A` est admissible si

\[
|A|\le m,\qquad t-|A|\le m.
\]

**Invariant.** Pour chaque affectation admissible, le nœud de produit

\[
U_{A,t}\,V_{J_t\setminus A,t}
\]

est atteignable depuis `H_t` par un chemin dont tous les nœuds précédant
ce produit sont des additions. Ce produit a réellement les deux racines
indiquées pour enfants ; il ne s'agit pas seulement d'un terme dans une
expansion mathématique.

La preuve est une induction. À `t=0`, le produit est la racine `UV` et le
chemin est vide. À l'étape suivante, les additions du chemin sont dérivées
en additions puis spécialisées en additions, avec suppression éventuelle
d'un enfant nul. Sur le produit marqué, le code de Leibniz, suivi de la
substitution, construit littéralement les deux branches

\[
E_t(FG)=(E_tF)(P_tG)+(P_tF)(E_tG).
\]

La première branche attribue la nouvelle colonne au bloc `U`, la seconde
au bloc `V`. Elles donnent précisément les nouveaux produits de
l'invariant lorsque l'affectation correspondante est admissible.

Voici pourquoi les simplifications locales n'effacent pas une branche
admissible. Dans `U_{A,t}`, affecter des lignes distinctes aux colonnes
de `A`, puis affecter les lignes restantes à des colonnes encore non
traitées, donne un monôme non nul. Une telle affectation existe : pour
`t<n`, il reste une colonne, et pour `t=n`, l'admissibilité force
`|A|=m`, donc il ne reste aucune ligne à affecter. L'extraction a
coefficient un sur ce monôme. Le même argument vaut pour le bloc `V`.
Chaque facteur possède un monôme de degré `2m` en les variables `a` de
son propre bloc. Les deux facteurs sont donc non nuls et non constants,
avant comme après la substitution de cette étape. Leur produit ne peut
être supprimé par les règles zéro/unité ou par le calcul entre constantes.

L'élagage par degré est valide : les degrés stockés sont des majorants
des degrés en chaque variable ; une dérivée non nulle d'une branche
admissible ne peut être élaguée par un majorant nul. Un appel mémorisé
renvoie la même racine déjà construite. L'internement peut partager un
produit ou échanger ses enfants, mais il conserve leurs arêtes. Ces
mécanismes ne modifient donc pas l'invariant.

## 3. La lecture finale conserve une famille de racines distinctes

À `t=n=2m`, les affectations admissibles sont exactement les ensembles
`A` de `m` colonnes. Leurs deux facteurs sont des scalaires en `s` :

\[
U_A=\sum_{\phi:R\overset\sim\longrightarrow A}
              \prod_{i\in R}B_{i,\phi(i)},\qquad
V_{A^c}=\sum_{\psi:R'\overset\sim\longrightarrow A^c}
              \prod_{i\in R'}B_{i,\psi(i)}.
\]

L'indépendance vis-à-vis de `s` est également syntaxique. À chaque
opération, les nœuds non nuls restent homogènes en `s` : une dérivée
diminue le degré de un, une substitution zéro conserve le degré des
branches survivantes, une addition joint des degrés égaux et un produit
additionne des degrés non négatifs. À degré final zéro, aucun descendant
ne peut donc être une variable `s_j` de degré un. Les constantes en `a,z`
ont ici degré zéro en `s`.

D'après l'invariant, chaque produit effectif `U_A*V_(A^c)` est encore
atteignable depuis la sortie finale, par des additions. Ses deux facteurs
sont non constants et non nuls après toutes les substitutions. En
particulier, chaque racine `U_A` est atteignable. L'argument ne repose pas
sur la seule indépendance sémantique de `U_A` vis-à-vis de `s` : il établit
aussi le chemin qui le conserve et la non-nullité de l'autre facteur.

Après remplacement de `B`, la partie de degré `2m` en `a` de `U_A` est

\[
\sum_{\phi:R\overset\sim\longrightarrow A}
 z^{\sum_{i\in R}2^{in+\phi(i)}}\prod_{i\in R}a_{i,\phi(i)}^2.
\]

Chaque bijection produit un monôme différent, de coefficient un. Son
support de colonnes est exactement `A`. Des ensembles `A` différents
donnent donc des polynômes distincts, même avec la préparation spécialisée
depuis `a,z`. Les exposants de `z` restent formels ; aucune réduction
modulo `Q-1` n'intervient.

Deux polynômes distincts ne peuvent être portés par le même nœud. Comme
`m>=2`, une racine `U_A`, qui possède un terme de degré `2m` en `a`, n'est
ni une constante ni une variable d'entrée : c'est une porte `+` ou `*`.
Il y a donc au moins `binom(2m,m)` portes distinctes dans la sortie.

Enfin, en répartissant les `2m` colonnes en `m` paires puis en choisissant
une colonne de chaque paire, on obtient `2^m` ensembles distincts de
cardinal `m`. D'où la borne annoncée. L'exponentielle `2^(n/2)` dépasse
toute borne `K*n^c` le long des puissances de deux.

## 4. Contrôles indépendants et limites

`verify_block_roots.py` compile d'abord la sortie complète, sans ajouter
de représentation par sous-ensembles au calcul. Ensuite seulement, il
interroge les racines du bloc gauche, du bloc droit et leurs produits.
Chaque interrogation doit allouer **zéro nœud**, et toutes les racines
doivent déjà appartenir au graphe final. Il vérifie en outre les chemins
constitués uniquement d'additions vers les produits marqués.

Pour `n=4,8` et `Q=97`, il contrôle respectivement `6` et `70` racines par
famille. Les tests sémantiques utilisent les entrées originales : `z=1`,
une amplitude `a_ij=0` par ligne dans une colonne choisie, et `a_ij=22`
ailleurs. Puisque `22^2=-1 modulo 97`, le produit devient celui d'une
affectation fixée des lignes aux colonnes. En attribuant les colonnes de
`A` au premier bloc et celles de son complément au second, les valeurs
des familles `U_S`, `V_(S^c)` et `U_S*V_(S^c)` forment chacune la matrice
identité : `36` puis `4 900` entrées sont vérifiées dans chaque famille.
Le calcul final doit aussi donner un.

Les empreintes du compilateur, de la classe `DAG`, de ce texte et du
vérificateur sont contrôlées au début et à la fin. Ces contrôles finis
corroborent le mécanisme de la preuve ; ils ne remplacent pas son argument
général. La preuve de présence des racines dans ce compilateur n'est pas
présentée comme intégralement formalisée dans Lean.

Le fichier `lean/ProjectionGrowth.lean` vérifie séparément que, pour tous
entiers naturels `K,c`, il existe `k>=2` avec
`K*(2^k)^c < 2^(2^(k-1))`. Il exclut ensuite une majoration polynomiale
uniforme d'une fonction de coût lorsque la borne inférieure précédente
est donnée comme hypothèse explicite. Cette croissance arithmétique est
formalisée ; l'atteignabilité des portes demeure la preuve des sections
1–3, contrôlée sur le code et relue indépendamment.

Reproduction depuis la racine du projet :

```text
python etudes/2026-11-01/projection-avant-derivation/taille/verify_block_roots.py
python etudes/2026-11-01/projection-avant-derivation/taille/lean/replay_growth.py
```

Les ensembles utilisés par ce vérificateur sont des témoins externes
pour compter des nœuds déjà construits. Ils ne sont pas des entrées du
circuit et ne sont pas une table de jets réintroduite dans l'architecture.
