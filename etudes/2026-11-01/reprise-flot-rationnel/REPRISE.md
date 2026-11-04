# Reprise : fusion rationnelle et compilation des transports

La démonstration générale de fermeture polynomiale de la chaîne \(\mathcal Z\)
**n'est pas obtenue**. Cette reprise établit une fermeture exacte d'une famille
de transports, avec un coût scalaire polynomial de leur action et de leur
fusion. L'opération qui sélectionne les insertions distinctes reste à compiler.
Elle n'est ni une hypothèse de la preuve Lean ni une porte gratuite du code.

## 1. Remplacer le développement des dérivées par un transport

On conserve l'algèbre libre en générateurs \(X_j\), les dérivations
\(\delta_j(X_k)=X_jX_k\), et les insertions complètes
\(\mathcal I_jF=\delta_jF+FX_j\) de l'étude précédente. Pour des paramètres
centraux \(y_j\), poser

\[
Y=\sum_j y_jX_j,\qquad R_y=(1-Y)^{-1},\qquad
\phi_y(X_k)=R_yX_k,\qquad T_yF=\phi_y(F)R_y.
\]

Ces expressions sont d'abord définies dans l'algèbre des séries formelles en
\(y\) à coefficients non commutatifs. L'inverse a un terme constant égal à
1 et désigne la série géométrique. Aucune division par une factorielle n'est
nécessaire; la formulation vaut en toute caractéristique.

**Loi de fusion à tout ordre :**

\[
\boxed{\phi_y\phi_z=\phi_{y+z},\qquad T_yT_z=T_{y+z}.}
\]

Preuve. Écrire \(Z=\sum_jz_jX_j\). La substitution donne
\(\phi_y(R_z)=(1-R_yZ)^{-1}\). Or

\[
1-R_yZ=R_y(1-Y-Z),\qquad
(1-R_yZ)^{-1}R_y=(1-Y-Z)^{-1}=R_{y+z}.
\]

Ainsi \(\phi_y\phi_z(X_k)=R_{y+z}X_k\), ce qui prouve la première identité
sur tous les polynômes, puis coefficient par coefficient sur les séries.
La seconde suit de
\(T_yT_zF=\phi_y\phi_z(F)\phi_y(R_z)R_y\).

Le coefficient linéaire en \(y_j\) de \(\phi_y\) est \(\delta_j\), et celui de
\(T_y\) est donc \(\mathcal I_j\). En décomposant \(y\) en ses coordonnées et
en appliquant la fusion,

\[
\boxed{[y_0\cdots y_{n-1}]\,T_y(1)
 =\mathcal I_{n-1}\cdots\mathcal I_0(1).}
\]

Il s'agit d'un coefficient carré-libre, donc sans facteur \(n!\).
Cette identité relie le transport à l'annihilation exacte des répétitions;
elle ne remplace pas le coefficient par une simple évaluation de paramètres.

## 2. État de taille polynomiale et action scalaire explicite

Évaluer les générateurs sur \(r\) matrices \(A_j\), strictement triangulaires
inférieures de taille \(d\). Pour l'observation \(uF(A)v\), le transport est

\[
\boxed{A'_j=R_y(A)A_j,\qquad v'=R_y(A)v,\qquad u'=u.}
\]

Le même état représente donc l'observation transportée de **chaque**
polynôme non commutatif \(F\). La famille est stable : tous les \(A'_j\)
restent strictement triangulaires inférieurs. Elle contient
\(r\binom d2+d\) scalaires si \(u\) est fixé.
Évaluer ensuite un \(F\) arbitraire conserve son coût propre; cette assertion
ne fournit pas une évaluation gratuite des polynômes représentés par \(F\).

Si \(Y=\sum_jy_jA_j\), on a \(Y^d=0\), d'où
\(R_y=I+Y+\cdots+Y^{d-1}\). Il n'y a aucune inversion scalaire dépendant des
données. Le code utilise la récurrence triangulaire

\[
R_{ii}=1,\qquad R_{ik}=\sum_{h=k}^{i-1}Y_{ih}R_{hk}\quad(k<i).
\]

Puis
\[
(A'_j)_{ik}=(A_j)_{ik}+\sum_{k<h<i}R_{ih}(A_j)_{hk},\qquad
v'_i=v_i+\sum_{k<i}R_{ik}v_k.
\]

Toutes les opérations du fichier `transport.py` sont des additions ou des
multiplications scalaires ordinaires. Pour \(r\ge1\), leur compte est :

| Opération | Nombre de portes |
|---|---:|
| Construction de \(Y\) | \((2r-1)\binom d2\) |
| Résolvante triangulaire \(R\) | \(2\binom{d+1}3-\binom d2\) |
| Transport des \(r\) générateurs | \(2r\binom d3\) |
| Transport de \(v\) | \(2\binom d2\) |
| Total | \(\boxed{2(r+1)\binom{d+1}3}\) |

Le compte conserve même la multiplication initiale par 1 dans chaque entrée
de la résolvante; il correspond exactement aux portes émises. L'identité
de Pascal donne la dernière ligne. Pour les horloges \(r=n,d=n+1\), c'est
\(n(n+1)^2(n+2)/3\) portes, à tout \(n\).

Fusionner \(\ell\) transports ne demande que \(r(\ell-1)\) additions de
paramètres, suivies d'un seul transport. Pour le prouver, après \(y\) puis
\(z\), la nouvelle résolvante est \(S=(I-R_yZ)^{-1}\); l'identité
\(SR_y=R_{y+z}\) transporte simultanément tous les générateurs et le vecteur.

Les paramètres \(y_j\) sont ici des **scalaires**. Les remplacer par des
éléments carrés-nuls transformerait les portes du code en opérations dans
une algèbre agrandie. Le compte scalaire ci-dessus ne s'appliquerait plus
automatiquement à cette autre interprétation.

## 3. Raccord exact à l'orientation et au spectral

Pour chaque fréquence \(f\), prendre les générateurs d'origine

\[
A_j[f]=\omega^{fd_j}\sum_{i=0}^{n-1}
(1+a_{ij}^2)z^{2^{in+j}}E_{i+1,i},\quad u=e_n^T,\quad v=e_0.
\]

La préparation des amplitudes et marqueurs reste scalaire et polynomiale.
Les phases appartiennent aux générateurs **avant** les transports. Puisque
les matrices initiales n'ont qu'une sous-diagonale,

\[
G_f(y)=e_n^TR_y(A[f])e_0
 =\prod_{i=0}^{n-1}\left(\sum_j y_j B_{ij}\omega^{fd_j}\right).
\]

Cette dernière égalité donne aussi un circuit scalaire plus court pour ce
seul générateur. Le transport présente en plus une loi de composition pour
les observateurs de tout \(F\); il n'est pas annoncé comme une amélioration
du coût de construction du produit de lignes.

La relation exacte avec la sortie corrigée est

\[
\boxed{\mathcal Z[k]=\widetilde\Omega\,
[y_0\cdots y_{n-1}]\operatorname{INTT}_N[(G_f(y))_f][k].}
\]

Le coefficient sélectionne les colonnes distinctes. Le signe universel
est déjà corrigé par \(\gamma_nq_{[n]}=\widetilde\Omega\).
Extraction et INTT commutent par linéarité, mais cette commutation ne
fournit pas un algorithme scalaire pour l'extraction. Aucun \(P_A\) n'est
une entrée du circuit ou des identités.

**Exemple qui empêche de conclure trop tôt.** À \(n=3\), avec \(a_{ij}=0\),
\(d=(0,1,2)\), \(N=4\), poser simplement \(y=(1,1,1)\) conserve au canal
cible \(k=3\) le terme collisionnel \(z^{146}\) : il utilise trois fois la
colonne 1 et porte la même phase que les permutations. La vraie sortie de
ce canal est

\[
z^{84}+z^{98}+z^{140}+z^{161}+z^{266}+z^{273}.
\]

La fusion rationnelle est donc un résultat positif sur les transports,
mais sa lecture par évaluation ne constitue pas la chaîne demandée.

## 4. Vérification et portée exacte

`ResolventFusion.lean` contient huit théorèmes sur le noyau algébrique non
commutatif de la fusion et le transport de l'observateur. Il prouve aussi,
pour \(R_d(Y)=\sum_{k<d}Y^k\), les deux identités télescopiques
\(R_d(Y)(1-Y)=(1-Y)R_d(Y)=1-Y^d\), puis
\[
R_d(R_d(Y)Z)R_d(Y)=R_d(Y+Z)
\]
sous les trois hypothèses \(Y^d=0\), \((R_d(Y)Z)^d=0\), \((Y+Z)^d=0\).
Elles sont satisfaites pour les matrices triangulaires considérées. Ce
dernier théorème ne suppose donc aucun inverse comme opération primitive.
Le rapport
`resolvent-lean-validation.json` enregistre les déclarations effectivement
compilées, les axiomes utilisés et l'empreinte du source. Les preuves sont
sans `sorry` et sans axiome supplémentaire.

Le calcul des coûts, l'extension aux substitutions de séries et le raccord
NTT sont démontrés ci-dessus; ils ne sont pas présentés comme entièrement
formalisés dans Lean. `verify_transport.py` vérifie 256 fusions de circuits
contre une implémentation indépendante par somme géométrique, aux dimensions
2 à 9, sur les corps à 2, 3, 17 et 998244353 éléments. Ces tests portent sur
les transports, pas sur un compilateur final de \(\mathcal Z\).

Les autres branches de cette reprise ont examiné les modes de rang fixé,
Frobenius, les symétriseurs de groupe et les projecteurs différentiels de
signe. Aucune n'a fourni la loi scalaire générale manquante. Le projecteur
par nombre de collisions et les corrections par dérivations croisées
avaient déjà été étudiés dans le projet; ils ne sont pas comptés comme
des résultats nouveaux de cette reprise.

Le travail restant porte sur l'action scalaire d'une sélection telle que
\([y_0\cdots y_{n-1}]\), ou sur un autre opérateur dont **la sortie**, et non
seulement le générateur paramétrique, coïncide avec \(\mathcal Z\). La fermeture
polynomiale de cette opération n'est ni démontrée ni supposée ici.

```powershell
python -B verify_transport.py
python -B replay_lean.py
```
