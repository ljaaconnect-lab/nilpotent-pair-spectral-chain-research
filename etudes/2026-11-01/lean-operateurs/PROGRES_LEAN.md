# Circuit d’opérateurs : correcteur quintique et certificats Lean

Travail du 1 novembre 2026. Objectif conservé : produire toute la chaîne
orientée et spectrale en portes scalaires, depuis les entrées originales.
Le prototype est maintenant exact jusqu’au degré cinq. La fermeture
polynomiale à tout ordre n’est pas démontrée.

## Nouveau circuit entier

À chaque fréquence, on garde les matrices à horloge de dimension `n+1` :

\[
A_j[f]=\omega^{fd_j}\sum_{i=0}^{n-1}
 (1+a_{ij}^2)z^{2^{in+j}}E_{i+1,i}.
\]

Les matrices ne constituent pas des portes primitives : `circuit.py`
développe chacune de leurs entrées en additions et multiplications scalaires.
Les puissances de `z` sont obtenues par carrés successifs.

Soit \(\{X,Y\}=XY+YX\). On normalise les jets par
\(H_r=2^r r!U_r\), \(S_{j,r}=2^r r!W_{j,r}\), avec
\(H_0=S_{j,0}=I\). La nouvelle récurrence est

\[
\begin{aligned}
T_{j,r}&=\{A_j,S_{j,r-1}\},\\
H_r&=\sum_jT_{j,r}
+2\binom{r-1}{3}\{C_4,H_{r-4}\}
+8\binom{r-1}{4}\{C_5,H_{r-5}\},\\
S_{j,r}&=H_r-rT_{j,r}.
\end{aligned}
\]

Un terme d’indice négatif est omis. Ici \(C_4=24R_4\), et le nouvel
opérateur est \(C_5=48R_5\). Tous les coefficients de la récurrence sont
entiers. Les seules inversions constantes nécessaires à la lecture sont
des puissances de deux et \(N\), donc disponibles modulo un premier impair
admettant la racine spectrale choisie. Les divisions par `r` et `r!`
du prototype précédent ont disparu.

La sortie de **toute** la chaîne est directement

\[
\mathcal Z[k]=\widetilde\Omega\,
 \operatorname{INTT}_N\big[(2^{-n}H_n[f]_{n,0})_f\big][k].
\]

La correction du signe universel est déjà incluse :
\(\gamma_n q_{[n]}=\widetilde\Omega\).
Ni \(P_A\), ni ses coefficients, ni une table de sous-ensembles ne sont
des entrées du circuit. La spécification attendue de la sortie est utilisée
uniquement par le vérificateur indépendant.

## Définition compacte du nouvel opérateur

Pour une partition d’égalité \(\pi\), on note

\[
M_\pi(A)=\sum_{\ell:\mathrm{blocs}(\pi)\to[n]}
 A_{\ell(\pi_1)}\cdots A_{\ell(\pi_r)}.
\]

Les étiquettes des blocs sont libres : deux blocs différents peuvent prendre
la même colonne. Un bloc singleton est remplacé directement par
\(P=\sum_jA_j\). On ne boucle donc que sur les blocs répétés.

`correcteurs.json` donne les **12 coefficients entiers de \(C_4\)** et les
**44 coefficients entiers de \(C_5\)**. Chaque partition non nulle comporte
au plus deux blocs répétés : l’évaluation de chacun de ces deux opérateurs
utilise au plus deux sommes sur les colonnes. Le correcteur quintique n’est
pas une table de sous-ensembles. La borne du prototype entier demeure
\(O(Nn^2(n+1)^3)=O(n^6)\) portes scalaires pour \(n<N\le2n\).
Cette borne est celle du prototype tronqué, dont la validité générale ne
découle pas du coût.

La dérivation des coefficients utilise le critère universel suivant :

\[
\sum_\pi \left(\prod_{B\in\pi}(-1)^{|B|-1}(|B|-1)!\right)M_\pi
 =\sum_{\text{colonnes toutes distinctes}}A_{j_1}\cdots A_{j_r}.
\]

Les égalités s’interprètent dans un anneau non commutatif : aucune
commutation artificielle des matrices à horloge n’intervient.

## Ce que Lean vérifie

`CollisionFilter.lean` établit, pour **tout ordre** `r` et toute famille de
colonnes `w`, sans hypothèse sur le nombre de colonnes :

\[
\det\big[(\mathbf1_{w_i=w_j})_{i,j}\big]
 =\begin{cases}1& w\text{ injective},\\0&\text{sinon}.\end{cases}
\]

`WeylOperators.lean` prouve dans tout anneau, sous la seule relation
\(dx=xd+1\), l’identité exacte
\((x-x^2d)^2=x^4d^2\). Elle précise pourquoi l’annihilation par le nouvel
opérateur s’applique à un état multiaffine ; la nilpotence n’est pas affirmée
sur tous les polynômes.

`PartitionCertificate.lean` vérifie dans le noyau les identités de
coefficients des récurrences aux ordres quatre et cinq, dans l’espace libre
des partitions d’égalité. Le certificat de support garantit que toutes les
partitions de ces expressions sont couvertes. Il emploie `decide`, sans
`native_decide`. Les identités portent sur des partitions formelles, sans
spécialiser les matrices ou le nombre de colonnes.
Le même fichier certifie les ordres zéro à trois et la borne de 44 termes
avec au plus deux blocs répétés pour le correcteur quintique.

`WordFilter.lean` relie le certificat quintique au filtre de mots pour un
**type arbitraire de colonnes**. Pour toutes colonnes `a,b,c,d,e`, le poids
du mot dans la forme normale de `H5` vaut `32` si les cinq colonnes sont
distinctes et zéro sinon. Ce résultat ne fixe donc pas le nombre de
colonnes disponibles. Le facteur `32=2^5` est précisément supprimé par la
lecture du circuit entier.

La génération des partitions à ordre variable reste une méthode de
**dérivation et de certification**. Elle n’est pas revendiquée comme
algorithme polynomial : le nombre de partitions augmente avec l’ordre.
La preuve Lean de ces certificats ne remplace pas une formalisation de
chaque instruction Python du compilateur scalaire.

## Vérification du compilateur

Le rapport `validation.json` consigne :

- 15 035 coefficients de mots libres contrôlés, pour 1 à 6 colonnes et
  les degrés 0 à 5 ;
- 60 tables spectrales numériques complètes, jusqu’à `n=5`, sur deux corps ;
- 10 tables complètes avec `z` formel ;
- la réparation de l’ancien contre-exemple légal : la table est maintenant
  `[0,0,131890214,0,0,0,0,0]` ;
- un témoin d’ordre six conservé pour la continuation : le mot
  `(0,0,0,0,2,5)` conserve un coefficient `-240` dans `H6`, alors qu’il doit
  être nul. Il atteint aussi le canal spectral attendu.

Ce dernier témoin interdit de qualifier le prototype de circuit général
exact. Il ne constitue pas une impossibilité des circuits recherchés.

La dérivation a été prolongée jusqu’à l’ordre huit : les nouveaux opérateurs
comportent respectivement 200, 869 et 4 138 partitions non nulles aux ordres
six, sept et huit. Ces opérateurs ne sont pas intégrés au prototype présenté.
Un essai de transport du seul correcteur quartique par insertion de `P` ou
duplication d’une position ne suffit pas au degré cinq : rang 9 contre rang
augmenté 10 (`transport.json`).

## Rejouer

Depuis ce dossier :

```powershell
python -B derive_quintic.py
python -B verifier.py --write-report
python -B replay_lean.py
```

Le compilateur installé est Lean 4.34.1. Le script de reprise emploie
l’installation locale et le cache Mathlib déjà présents, avec les produits
de compilation sur `D:` ; `lean-validation.json` donne les chemins, versions,
empreintes des sources et sorties brutes. Le petit fichier
`LocalNoncommRing.lean` est une copie sous sa licence du tactic Mathlib dont
le binaire était absent du cache local.

La prochaine construction doit remplacer la croissance de la famille des
correcteurs par une loi d’opérateurs fermée, avec preuve de correction à
tout ordre et borne polynomiale sur l’ensemble des portes scalaires.
