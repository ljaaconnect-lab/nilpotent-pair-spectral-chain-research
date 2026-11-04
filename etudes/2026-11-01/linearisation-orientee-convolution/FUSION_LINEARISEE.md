# Un seul produit linéarisé pour toutes les fréquences

On conserve la [transformation simultanée des coefficients et de l'orientation](FORME_LINEARISEE.md).
La fusion ci-dessous réduit encore sa préparation : on ne construit plus
les `N` produits spectraux. Un seul représentant auxiliaire suffit, avec
une préparation en `O(n² log(n+1))` portes scalaires. **La lecture générale
de ce représentant reste à compiler ; cette borne n'est pas une borne de
la chaîne scalaire entière.**

## 1. Compilation depuis les données originales

Avec `n<=N<2n`, `N` puissance de deux, `Q` premier fourni et `omega` d'ordre
`N`, les étiquettes `d_j` étant des paramètres fixés à la construction du
circuit, préparer une seule fois

\[
C_{ir}=\frac1N\operatorname{NTT}(B_{i,\bullet})[r],\qquad
F_0(x)=\prod_{i=0}^{n-1}\sum_{r=0}^{N-1}C_{ir}x_{-r}.
\]

Les entrées de `C` sont uniquement `a,z`, avec
`B_ij=(1+a_ij²)z^(2^(in+j))`. Aucune amplitude terminale, dérivée composée
ni observation de collisions n'est fournie au compilateur. Le circuit
`F_0` conserve les `x_r` comme variables auxiliaires formelles.

On travaille dans le quotient muni des relations exactes

\[
\sum_r x_r x_{t-r}=0,\qquad
\frac1N\sum_r\omega^{-rj}x_r=0\quad(n\le j<N).
\]

Il s'agit de relations par convolution, sans tableau de colonnes utilisées
dans le compilateur de la préparation.

## 2. Fusion des phases avec la lecture

Dans la base orientée, l'application `q_j -> omega^(f d_j)q_j` est un
automorphisme du quotient : elle préserve chaque carré nul et le padding.
Elle transforme `F_0` en `F_f`. Le degré `n` du quotient est de dimension
un, engendré par `q_0...q_(n-1)`. Sur ce degré, l'automorphisme agit donc
par le scalaire `omega^(f sum_j d_j)`. Par conséquent,

\[
\lambda(F_f)=\omega^{f\sum_jd_j}\lambda(F_0).
\]

Cette égalité est valable après passage au quotient et lecture. Elle ne
signifie pas que les polynômes ordinaires `F_f(x)` et la phase fois `F_0(x)`
coïncident avant réduction.

Après la correction universelle de l'orientation et l'INTT,

\[
\boxed{\mathcal Z_Q[k]
 =\delta_{k,\,\sum_jd_j\bmod N}\,\lambda(F_0)\,\widetilde\Omega.}
\]

Ainsi, la totalité du coût arithmétique restant se situe dans
`lambda(F_0)`. Le routage de cette sortie vers un indice fixé par les
étiquettes est un câblage, pas un calcul répété de `N` amplitudes.

## 3. Borne de la préparation fusionnée

| Partie | Portes scalaires au plus |
|---|---:|
| Préparation de `B` | `4n²−1` |
| `n` NTT | `2nN log_2 N` |
| Normalisation des coefficients | `nN` |
| Produit de `n` formes linéaires | `2nN−1` |

D'où

\[
C_{\mathrm{préparation}}(n)
 \le 4n^2-1+2nN\log_2N+3nN-1
 =O(n^2\log(n+1)).
\]

Une borne polynomialement écrite est `C_préparation(n)<=18n³`, pour `n>=1`,
car `N<2n` et `log_2 N=ceil(log_2 n)<=n`.
Le code compte réellement les portes atteignables de la sortie auxiliaire,
avec le partage de sous-expressions. Les paramètres de corps sont fournis.

Définir `C_lecture(n)` comme le coût complet d'un circuit en portes
scalaires recevant les fils numériques ou formels `C_ir` et produisant
`lambda(F_0)`, avec toutes les variables auxiliaires éliminées. Le
représentant `F_0` n'est pas une donnée polynomiale gratuite qu'une porte
spéciale pourrait lire. Si ce circuit est construit, le raccord donne

\[
C_{\mathrm{chaîne}}(n)
 \le 4n^2-1+2nN\log_2N+nN+C_{\mathrm{lecture}}(n).
\]

Le circuit lecteur utilise directement les coefficients : on ne recompte
donc pas la construction du représentant auxiliaire dans cette borne
conditionnelle. Cette implication ne prouve pas l'existence d'un lecteur
polynomial. Une fusion supplémentaire peut encore partager des portes
entre la préparation et la lecture.

## 4. Raccord exact aux translations fusionnables

Poser `v_i[s]=C_i,(-s)` et

\[
D_n(y)=\prod_{j<n}\sum_{s<N}\omega^{sj}y_s,
\qquad T_vD(y)=D(y+v).
\]

Le lecteur exact devient

\[
\lambda(F_0)=
 \left[\left(\prod_i\sum_s v_i[s]\partial_{y_s}\right)D_n\right](0)
 =\left[\left(\prod_i(T_{v_i}-I)\right)D_n\right](0).
\]

L'inversion Fourier donne `sum_s omega^(sj) v_i[s]=B_ij`, donc

\[
H(t)=D_n\left(\sum_i t_i v_i\right)=\prod_{j<n}\sum_{i<n}B_{ij}t_i.
\]

Pour prouver la deuxième égalité, ce `H` est homogène de degré `n`.
La différence dans chacune
des `n` variables `t_i`, suivie de l'évaluation en zéro, annule tout monôme
qui en omet une. Le seul profil de degré `n` restant est `(1,...,1)`, dont
le coefficient est aussi la dérivée mixte. L'identité tient dans le corps
considéré et ne requiert pas de division par `n!`.

Les translations réalisent sur les polynômes duaux la loi exacte
`T_y T_z=T_(y+z)` ; le raccord ci-dessus porte sur leur lecture terminale.
Cette règle
fusionne toute composition de translations seules. Le produit des
différences contient aussi les soustractions : son application scalaire
compacte à `D_n` est précisément l'étape encore non compilée avec une
borne polynomiale. Le programme ne développe pas ce produit en sous-ensembles.

## 5. Vérification

`python etudes/2026-11-01/linearisation-orientee-convolution/verify_fused_linearised.py`

Le vérificateur contrôle `n=1..8`, dont le padding, les étiquettes
irrégulières, `z=0` et une ligne d'amplitudes nulle. Il compare le circuit
fusionné à celui de toutes les fréquences, puis la chaîne orientée et la
sortie INTT à une référence externe. Il garde `z` formel jusqu'à `n=4`.
Il vérifie aussi `H(t)=prod_j sum_i B_ij t_i` à des arguments tirés au sort
et l'action terminale des `n` différences par une référence externe.
Les tables de sous-ensembles sont exclusivement des oracles de contrôle
de petites tailles et ne font pas partie du circuit de préparation.

Le fichier [LinearisedPreparationBound.lean](lean/LinearisedPreparationBound.lean)
vérifie la conséquence arithmétique

\[
n\ge1,\ N\le2n,\ \ell\le n
\quad\Longrightarrow\quad
4n^2-1+2nN\ell+3nN-1\le18n^3.
\]

La formule de comptage des portes est justifiée à la section 3 et dans le
code ; sa dérivation depuis le programme n'est pas formalisée dans Lean.
Ce certificat ne formalise pas non plus la lecture du quotient. Rejeu :

`python etudes/2026-11-01/linearisation-orientee-convolution/lean/replay_preparation_bound.py`
