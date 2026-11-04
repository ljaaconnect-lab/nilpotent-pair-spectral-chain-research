# Lecture scalaire par canaux de déterminants : formule et portée

Ce candidat calcule chaque canal en portes scalaires depuis `a,z`. Il
élimine effectivement les répétitions de colonnes sans stocker les
colonnes utilisées. La correction finale obtenue est exacte aux tailles
`n=3,4`. **Le filtre proposé ne donne pas la chaîne générale : deux termes
de signes opposés deviennent indiscernables dès `n=5`.** Cette conclusion
concerne le score spectral précis décrit ici.

## 1. Entrées linéarisées et élimination dans chaque canal

Préparer `B_ij=(1+a_ij²)z^(2^(in+j))`, puis

\[
A_i[r]=\sum_{j<n}B_{ij}\omega^{rj},\qquad
K_f[i,s]=A_i[fi-s]\quad(0\le i,s<n).
\]

Prendre `N` puissance de deux strictement supérieure à
`sum_(i=0)^(n-1) i²`, `Q` premier avec `N | Q-1`, et `omega` d'ordre `N`.
Avec `V[j,s]=omega^(-js)` et `D_f[i,j]=B_ij omega^(fij)`, on a exactement

\[
K_f=D_fV,\qquad
\frac{\det K_f}{\det V}
 =\sum_{\sigma\in S_n}\operatorname{sgn}(\sigma)
   \prod_i B_{i,\sigma(i)}\,
     \omega^{f e(\sigma)},\qquad
e(\sigma)=\sum_i i\sigma(i).
\]

Les `omega^(-j)` sont distincts, donc `det V` est une constante non nulle.
Le déterminant élimine les affectations qui répètent une colonne, et
laisse un signe dépendant de la permutation. Ce signe doit être corrigé
pour retrouver la lecture orientée paire, après sa correction universelle.

## 2. Condition exacte sur le filtre de lecture

Choisir une table constante `g[0..N-1]` et

\[
\lambda_f=\frac1N\sum_k g[k]\omega^{-fk},\qquad
Y_g=\sum_f\lambda_f\frac{\det K_f}{\det V}.
\]

L'orthogonalité donne le résidu exact

\[
Y_g-Y=\sum_\sigma
 \left(g[e(\sigma)\bmod N]\operatorname{sgn}(\sigma)-1\right)
 \prod_iB_{i,\sigma(i)}.
\]

Ainsi, il suffit que toutes les permutations d'une même classe de score
aient le même signe, et de prendre ce signe pour `g`. Une telle table
existe pour `n=3,4` ; le vérificateur énumère toutes les permutations de
ces deux tailles pour certifier cette propriété des constantes.

| n | N | Scores occupés | Classes aux signes mélangés | Portes depuis a,z |
|---:|---:|---:|---:|---:|
| 3 | 8 | 4 | 0 | 1 082 |
| 4 | 16 | 11 | 0 | 6 590 |
| 5 | 32 | 21 | 3 | 32 482 |
| 6 | 64 | 36 | 26 | 137 166 |

Les décomptes concernent le programme scalaire, même lorsque sa sortie
n'est pas correcte. Une petite table `g` ne démontre pas une construction
uniforme polynomiale des constantes à tous les ordres.

## 3. Deux termes que le score ne sépare pas

Pour `n=5`, les permutations

\[
\sigma=(0,2,4,1,3),\qquad \tau=(1,0,4,3,2)
\]

ont toutes deux le score entier `25`, tandis que leurs signes sont `-1`
et `+1`. Toute valeur `g[25 mod N]` devrait donc valoir simultanément `-1`
et `+1`. Le défaut persiste pour tout module de fréquence et tout corps
de caractéristique différente de deux : augmenter `N` ne sépare pas ces
deux scores entiers égaux.

Le contre-exemple est réalisable depuis les entrées originales : modulo
`97`, prendre `z=1`, `a_ij=0` lorsque `j=tau(i)` et `a_ij=22` ailleurs.
Alors `1+22²=0 mod 97`, donc `B` est la matrice de la permutation `tau`.
Le filtre enregistré choisit `g[25]=-1` ; il retourne `96=-1 mod 97`
alors que la sortie correcte vaut `1`. Aucun oracle de coefficients n'est
requis pour cette instance.

## 4. Calcul du déterminant et coût réellement exécuté

Le programme utilise les traces des puissances et la récurrence de Newton

\[
e_0=1,\qquad
e_k=\frac1k\sum_{r=1}^k(-1)^{r-1}e_{k-r}\operatorname{Tr}(K^r),
\qquad \det K=e_n.
\]

Les inverses `1/k` sont des constantes du corps, avec `Q>n`. Il n'y a pas
de division par une donnée. La multiplication matricielle est entièrement
développée en portes scalaires `+` et `*`. Le coût par déterminant est

\[
d(n)=(n-1)n^2(2n-1)+\frac{5n^2-n}{2}.
\]

La préparation partagée, les NTT et la contraction donnent exactement

\[
4n^2-1+2nN\log_2N+N d(n)+2N-1
\]

appels de portes dans ce programme. Le routage vers
`k=sum_j d_j mod N` est ensuite le même câblage que dans la chaîne
orientée. La borne en portes est polynomiale en `n,N` ; la correction du
filtre est la condition qui échoue pour cette construction générale.

## 5. Rejeu

`python etudes/2026-11-01/linearisation-orientee-convolution/determinants/verify_determinant_channels.py`

Seize instances numériques vérifient le résidu exact, dont `z=0`.
Deux instances `n=3` conservent `z` formel, sans réduction des exposants.
Les témoins isolés à `n=5,6` sont contrôlés depuis `a,z`. Les permutations
servent seulement à certifier les constantes et à vérifier les sorties ;
elles ne sont pas parcourues lors de l'évaluation scalaire du candidat.
