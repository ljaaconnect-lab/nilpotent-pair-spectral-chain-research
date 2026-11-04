# Linéarisation simultanée des coefficients et de l'orientation

Suite : la [fusion des fréquences et de la lecture](FUSION_LINEARISEE.md)
réduit cette préparation à un seul représentant, en `O(n² log(n+1))`
portes scalaires, et donne son raccord exact aux différences de translations.

Cette construction adapte la NTT aux termes orientés eux-mêmes. Le
programme compile réellement, en portes scalaires `+` et `*`, les
coefficients transformés depuis les données originales `a,z`, puis les
produits de formes linéaires dans une nouvelle base auxiliaire.

La taille de cette préparation est polynomiale. **Les sorties construites
restent des représentants polynomiaux dans les variables auxiliaires : la
réduction orientée suivie de la lecture scalaire n'est pas compilée avec
une borne polynomiale par cette étude.** Les contrôles dans l'algèbre
orientée appartiennent au vérificateur, et ne sont pas des portes gratuites.

## 1. Paramètres et changement de base exact

Prendre `N` puissance de deux avec `n<=N<2n` et un nombre premier fourni
`Q>max(2,binom(n,2))` tel que `N` divise `Q-1`. La racine fournie `omega`
a exactement l'ordre `N`. Le code accepte aussi un `N` plus grand ; sa
borne est alors exprimée en `n,N`.

Les orientations paires commutent et satisfont `q_j^2=0`. Compléter par
`q_j=0` pour `n<=j<N`, et définir

\[
x_r=\widehat q_r=\sum_{j=0}^{N-1}\omega^{rj}q_j,
\qquad
q_j=\frac1N\sum_{r=0}^{N-1}\omega^{-rj}x_r.
\]

L'orthogonalité des caractères prouve l'inversion, puisque `N` est
inversible dans `F_Q`. La base orientée et les coefficients de la matrice
sont donc transformés ensemble.

## 2. Les annulations deviennent des relations de convolution

Pour `t` modulo `N`, poser

\[
g_t(x)=\frac1N\sum_{r=0}^{N-1}x_r x_{t-r}.
\]

En substituant la définition de `x`,

\[
g_t=\frac1N\sum_{r,j,k}\omega^{r(j-k)+tk}q_jq_k
    =\sum_j\omega^{tj}q_j^2=0.
\]

La transformation inverse rend ces `N` relations équivalentes aux carrés
nuls. Si `N>n`, il faut aussi conserver les relations linéaires

\[
\frac1N\sum_r\omega^{-rj}x_r=0\qquad(n\le j<N).
\]

Omettre ces relations introduirait `N` orientations indépendantes au lieu
des `n` orientations du problème. Elles font partie de la définition du
quotient, pas d'une approximation numérique.

Si `X(T)=sum_r x_r T^r`, les relations quadratiques s'écrivent également

\[
X(T)^2=0\pmod{T^N-1}.
\]

Cette écriture compacte spécifie une algèbre ; elle ne prouve pas qu'une
multiplication ou une lecture quelconque dans cette algèbre coûte un
nombre polynomial de portes scalaires.

## 3. La matrice linéarisée réellement compilée

Les entrées restent

\[
B_{ij}=(1+a_{ij}^2)z^{2^{in+j}}.
\]

Pour chaque fréquence spectrale `f`, les étiquettes `d_j` peuvent être
arbitraires. On compile par NTT radix deux

\[
C_{ifr}=\frac1N\sum_{j=0}^{n-1}
 B_{ij}\omega^{f d_j+rj}.
\]

La ligne orientée transformée est exactement

\[
\widehat R_i[f]=\sum_j B_{ij}q_j\omega^{fd_j}
              =\sum_{r=0}^{N-1} C_{ifr}x_{-r}.
\]

En effet, remplacer `x_-r` et sommer sur `r` annule les termes dont les
indices de colonne diffèrent, et conserve précisément les termes affichés.
Le polynôme représentatif produit par le programme est

\[
F_f(x)=\prod_{i=0}^{n-1}\left(\sum_r C_{ifr}x_{-r}\right).
\]

Dans le quotient défini à la section 2, ce représentant est le produit
orienté voulu. Pour les seules étiquettes naturelles `d_j=j`, on peut
réécrire la même formule avec `Bhat_i[r]=NTT(B_i)[r]` :

\[
\widehat R_i[f]=\frac1N\sum_r\widehat B_i[r]x_{f-r}.
\]

Cette dernière formule avec un simple décalage n'est pas appliquée aux
étiquettes générales. Le code utilise la modulation `omega^(f*d_j)`
avant chaque NTT et couvre donc les deux cas.

## 4. Borne de la partie effectivement compilée

Un papillon de la NTT utilise au plus quatre portes binaires : une
multiplication par le facteur de phase, deux additions et une
multiplication par `-1`. Une transformation de longueur `N` demande donc
au plus `2N log_2 N` portes. Le partage et les constantes particulières
peuvent réduire ce compte.

| Partie | Majorant de portes scalaires |
|---|---:|
| Préparation partagée de `B` depuis `a,z` | `4n²-1` |
| Modulations des `nN` lignes transformées | `n²N` |
| `nN` NTT radix deux | `2nN² log_2 N` |
| Normalisation par `1/N` | `nN²` |
| Les `N` produits de `n` formes linéaires | `N(2nN-1)` |

Ainsi, tous les représentants `F_f`, avec leur préparation, ont un circuit
scalaire de taille au plus

\[
4n^2-1+n^2N+2nN^2\log_2N+3nN^2-N.
\]

Avec `N<2n`, cette borne est `O(n^3 log(n+1))`. Le sous-circuit de tous les
`C_ifr` a uniquement `a,z` pour données. Les représentants `F_f` ont aussi
les `N` indéterminées auxiliaires `x_r` ; ils n'ont pas encore été réduits
au scalaire final. Les sorties `C` sont indexées par `i,f,r`, en nombre
`nN²`, donc également polynomial.

Les paramètres de corps et de phase sont fournis. Leur recherche n'est
pas comprise dans cette borne en portes de corps. Les puissances de `z`
sont construites par carrés successifs, sans réduire leurs exposants
modulo `Q-1` dans le circuit formel.

## 5. Lecteur terminal exact dans la base linéarisée

Soit `lambda` le coefficient de `q_0...q_(n-1)` dans le quotient, et
introduisons seulement pour décrire son action le polynôme dual

\[
\mathcal D_n(y)=\prod_{j=0}^{n-1}
                  \left(\sum_{r=0}^{N-1}\omega^{rj}y_r\right).
\]

Pour tout représentant homogène `F(x)` de degré `n`,

\[
\boxed{\lambda(F)=F(\partial_{y_0},\ldots,\partial_{y_{N-1}})
                       \mathcal D_n(y)\big|_{y=0}.}
\]

Sur le monôme `x^alpha`, les deux membres valent `prod_r alpha_r!` fois
le coefficient de `y^alpha` dans `D_n`. Ce coefficient énumère exactement
les choix d'un facteur Fourier pour chacune des `n` orientations. Cela
prouve l'identité par linéarité. Elle tient compte du padding puisque le
produit définissant `D_n` ne comporte que les `n` orientations actives.

Pour `N=n`, `D_n` est aussi le déterminant de la matrice circulante de
première colonne `y`. De même,

\[
\det\left(\frac{\partial g_t}{\partial x_r}\right)
 =\left(\frac2N\right)^N\det(\operatorname{Circ}(x))
 =2^N q_0\cdots q_{N-1}.
\]

Ces expressions donnent un lecteur et un élément terminal compacts. Elles
ne donnent pas gratuitement le coût de l'application de l'opérateur
différentiel `F(partial)` à `D_n`. Cette application générale n'est pas
présentée comme une porte scalaire ni comme une lecture déjà polynomiale.

## 6. Orientation corrigée et sortie spectrale

Dans le quotient, le degré `n` est porté par `q_0...q_(n-1)`. En notant
`Y=lambda(F_0)`, les étiquettes de toutes les orientations présentes sont
utilisées une fois, donc

\[
\lambda(F_f)=\omega^{f\sum_jd_j}Y.
\]

Après la correction universelle du signe de l'orientation, l'INTT donne

\[
\mathcal Z_Q[k]=\delta_{k,\,\sum_jd_j\bmod N}\,Y\widetilde\Omega.
\]

Ce raccord est exact. Le nouveau programme fournit les représentants
`F_f` et leurs coefficients ; il ne fournit pas encore un circuit scalaire
polynomial produisant `Y` depuis ces représentants.

## 7. Vérification reproductible

```text
python etudes/2026-11-01/linearisation-orientee-convolution/verify_linearised_inputs.py
```

Le vérificateur compare la NTT compilée à la formule directe pour `n=3,4,5,6`
modulo `97`, avec les étiquettes naturelles, nulles et irrégulières. Il
contrôle aussi les représentants comme polynômes ordinaires évalués en
`x`, puis les identités de convolution, le padding, le lecteur dual et
la chaîne orientée entière dans une petite algèbre de référence. Les cas
`z=0` et ligne d'amplitudes nulle sont inclus. Pour `n=3`, des contrôles
gardent `z` formel dans les coefficients et dans la sortie orientée.

Les tables de monômes et de sous-ensembles appartiennent exclusivement à
ce vérificateur de petites tailles. Elles ne sont pas utilisées par
`linearised_inputs.py`. Le rapport distingue explicitement la préparation
polynomiale prouvée et la fermeture polynomiale de la lecture non établie.
