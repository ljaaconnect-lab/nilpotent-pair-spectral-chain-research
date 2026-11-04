# Projection fusionnée avant dérivation

La chaîne corrigée possède une nouvelle compilation scalaire exacte, qui
supprime chaque colonne auxiliaire immédiatement après sa première dérivée.
Depuis les entrées originales `a,z`, elle utilise **223 portes pour n=5** et
**472 pour n=6**, contre respectivement 2 858 et 20 394 dans le compilateur
direct précédent avec fusion terminale et spectrale.

La preuve d'exactitude ci-dessous vaut à tout ordre. Une étude ultérieure
établit désormais `C_Y(n)>=binom(n,n/2)>=2^(n/2)` pour `n=2^k>=4`,
dans [ce compilateur précis](taille/CROISSANCE_PROJECTION.md).
**Sa taille n'admet donc pas de borne polynomiale générale.** Ce résultat
ne concerne pas une autre compilation scalaire de la même chaîne.

## 1. Même projecteur, normalisé avant création des nœuds

On travaille sur les formes homogènes de degré `n` en `n` variables `s_j`,
sur le corps `F_Q`, avec `Q` premier et `Q>max(2,binom(n,2))`. Posons

\[
G_B(s)=\prod_{i=0}^{n-1}\sum_{j=0}^{n-1}B_{ij}s_j,
\qquad B_{ij}=(1+a_{ij}^2)z^{2^{in+j}},
\]
\[
D_j=s_j\partial_j,\qquad
L=\frac12\sum_j(D_j^2-D_j),\qquad
\pi_n(X)=\prod_{r=1}^{\binom n2}(1-X/r).
\]

Pour `s^m` de degré total `n`, on a

\[
Ls^m=\kappa(m)s^m,
\qquad \kappa(m)=\sum_j\binom{m_j}{2}.
\]

Si chaque `m_j` est positif, leur somme égale au nombre de variables impose
`m_j=1` pour tout `j`. Sinon au moins un `m_j` vaut zéro. Par conséquent

\[
\prod_jm_j=
\begin{cases}1& m=(1,\ldots,1),\\0&\text{sinon.}\end{cases}
\]

Le même indicateur est donné par `pi_n(kappa(m))` : la collision nulle
caractérise ici `(1,...,1)`, et toute collision non nulle est un entier de
`1` à `binom(n,2)`, annulé par un facteur du projecteur. Les dénominateurs
sont inversibles par l'hypothèse sur `Q`. Ainsi, sur tout cet espace,

\[
\boxed{\pi_n(L)=\prod_{j=0}^{n-1}D_j.}
\]

Cette identité normalise le projecteur de collision déjà utilisé. Elle ne
consiste pas à compter `D_j` comme une porte scalaire.

## 2. Compilation effective de chaque opération

Définir successivement

\[
H_0=G_B,\qquad
H_{j+1}=\left.\partial_jH_j\right|_{s_j=0}
\quad(0\le j<n).
\]

Sur un monôme, cette opération garde exactement les termes d'exposant `1`
en `s_j`, avec coefficient inchangé, et supprime cette variable. Les termes
d'exposant `0` sont tués par la dérivation ; ceux d'exposant supérieur à `1`
sont tués par la substitution. Par induction, `H_j` est homogène de degré
`n-j`, indépendant des `j` premières variables, et représente exactement
les monômes de `G_B` dont ces exposants valent tous `1`.

À la dernière étape, `H_n` est un scalaire `Y` et

\[
\pi_n(L)G_B(s)=Y\prod_js_j.
\]

Le programme construit d'abord `B` et `G_B` depuis `a,z`. À chaque étape,
la dérivation est développée par les règles usuelles dans le DAG partagé :

\[
\partial_j(F+G)=\partial_jF+\partial_jG,\qquad
\partial_j(FG)=(\partial_jF)G+F(\partial_jG).
\]

Puis `s_j=0` est propagé immédiatement ; les produits nuls et sommes avec
zéro disparaissent avant la dérivation suivante. Le DAG d'origine met en
cache les requêtes `(nœud, colonne)` ; aucune table de coefficients indexée
par les sous-ensembles n'est créée. Il n'utilise ni logarithme ni table de
jets. Les seules portes arithmétiques de sortie sont `+` et `*`.

Le calcul de `Y` est entièrement compilé depuis `a,z`. Aucun coefficient
cible, observation ou résultat intermédiaire équivalent n'est fourni en
entrée. Les exposants de `z` sont construits par carrés successifs et ne
sont jamais réduits modulo `Q-1` dans le circuit formel.

## 3. Raccord exact au préfixe antérieur

Pour `n>=3`, conserver les notations de la fusion terminale :

\[
h_k=\binom k2,\qquad
I=K_n\setminus\{0,h_{n-1},h_n\},\qquad
c(X)=\prod_{r\in I}(1-X/r),
\]
\[
\alpha=c(h_{n-1}),\qquad\beta=c(h_n).
\]

Dans le degré `n`, les deux plus grandes valeurs de collision correspondent
uniquement aux profils `(n-1,1)` et `(n)`. Pour vérifier l'unicité : si la
plus grande multiplicité est au plus `n-2`, la convexité de `binom(k,2)`
majore la collision, pour `n>=4`, par `binom(n-2,2)+1<h_(n-1)` ; pour `n=3`,
la seule possibilité restante est `(1,1,1)`, de collision zéro.

Les composantes de ces deux profils sont explicitement

\[
V(s)=\sum_j\left(\prod_iB_{ij}\right)s_j^n,
\]
\[
U(s)=\sum_{i,j}\left(\prod_{\ell\ne i}B_{\ell j}\right)
               s_j^{n-1}\sum_{k\ne j}B_{ik}s_k.
\]

Le même raisonnement diagonal sur les monômes établit donc

\[
\boxed{c(L)G_B(s)=Y\prod_js_j+\alpha U(s)+\beta V(s).}
\]

Cela reconstruit exactement le préfixe demandé. À `s=1`, en reprenant
`C=V(1)` et `S=U(1)+nC` du raccord terminal déjà établi,

\[
X=(c(L)G_B)(1)=Y+\alpha S+(\beta-n\alpha)C.
\]

La lecture terminale existante devient

\[
X-\alpha S+(n\alpha-\beta)C=Y.
\]

Dans la chaîne complète, les deux queues se compensent donc **avant** la
création de leurs portes. Le compilateur produit directement le fil `Y`
par la récurrence de la section 2 ; il ne construit pas un ancien préfixe
pour le simplifier après coup. La reconstruction du préfixe est une identité
de raccord, pas une entrée gratuite.

Le fichier `prefix_projection.py` construit effectivement `X` si le préfixe
lui-même est demandé. Il partage tous les `B_ij` déjà présents dans le
circuit de `Y`. Pour chaque colonne, les produits préfixes et suffixes
donnent son produit complet et ses `n` produits avec une ligne omise en au
plus `3n-5` multiplications. Les sommes de lignes et de cofacteurs coûtent
chacune `n(n-1)` additions ; la formation de `S` coûte `2n-1` portes, celle
de `C` coûte `n-1` additions. Les deux pondérations et leur addition à `Y`
coûtent au plus quatre portes. Ainsi, pour cette nouvelle réalisation,

\[
\boxed{C_X(n)\le C_Y(n)+5n^2-4n+2.}
\]

Cette borne quadratique concerne le raccord, pas `C_Y`. Les constantes
`alpha,beta` dépendent seulement de `n,Q` ; elles se calculent par les
produits affichés sur au plus `binom(n,2)` facteurs. Le spectre atteint se
construit par la récurrence des partitions entières utilisée dans le code,
avec un nombre polynomial d'opérations sur ses ensembles d'entiers bornés
par `binom(n,2)`.

Les tailles du préfixe reconstruit sont `83,175,330,630,1232` pour
`n=3,...,7`. Les surcoûts mesurés sont `34,65,107,158,219`. Le vérificateur
indépendant contrôle 16 tables numériques pour `n=3,...,6`, deux tables
avec `z` formel pour `n=3`, et la structure du circuit pour `n=7`.

## 4. Orientation et spectral inclus

Après la correction universelle du signe, la forme orientée vaut
`Y (prod_j s_j) Omega_tilde`. Aux phases `s_j=omega^(f*d_j)`, elle vaut
`Y omega^(f*sum_j d_j) Omega_tilde`. L'INTT déjà spécifiée donne donc

\[
\mathcal Z_Q[k]=
\delta_{k,\,\sum_jd_j\bmod N}\,Y\widetilde\Omega.
\]

Le programme conserve le routage à zéro porte arithmétique de la fusion
spectrale précédente. `N`, puissance de deux supérieure à `n`, et un nombre
premier `Q` tel que `N` divise `Q-1` sont des paramètres fournis ; leur
recherche n'est pas déclarée gratuite ni démontrée polynomiale ici.

## 5. Résultats et portée

Les comptes comprennent la préparation de `B` depuis `a,z` et toutes les
portes atteignables depuis la sortie finale. Les nœuds temporaires du
compilateur sont comptés séparément dans le rapport.

| n | Portes scalaires finales | Nœuds alloués à la compilation |
|---:|---:|---:|
| 1 | 3 | 9 |
| 2 | 18 | 40 |
| 3 | 49 | 116 |
| 4 | 110 | 268 |
| 5 | 223 | 627 |
| 6 | 472 | 1 366 |
| 7 | 1 013 | 2 980 |

Vérification reproductible :

```text
python etudes/2026-11-01/projection-avant-derivation/verify_direct_projection.py --write-report
python etudes/2026-11-01/projection-avant-derivation/verify_prefix_projection.py --write-report
```

Le rapport conserve les empreintes des quatre sources Python utilisées et
atteste : 28 tables numériques complètes modulo `97`, 140 lectures d'étapes
intermédiaires, 6 tables en `z` formel pour `n<=3`, et 6 reconstructions du
préfixe à des valeurs générales de `s`, pour `n=3,4,5`. Chaque taille comprend
un cas `z=0` et un cas dont une ligne d'amplitudes est nulle. Les invariants
de degré et l'absence des variables éliminées sont contrôlés à chaque étape.

Les petites énumérations de référence appartiennent exclusivement au
vérificateur. Elles ne font pas partie du compilateur ni de ses portes.

Il y a `n` étapes, mais le coût de chacune dépend de la taille du DAG
précédent. Leur nombre linéaire ne démontre donc pas une borne polynomiale
du circuit entier. Les preuves Lean antérieures de comptage restent
indépendantes : elles ne formalisent ni cette normalisation ni une borne
de taille de ce nouveau compilateur.

## 6. Ce que le décompte général établit actuellement

Traiter les `B_ij` comme les sorties déjà construites de la préparation.
Avant projection, les nombres de portes au-dessus de ces sorties sont
`M_0=n²+n-1` multiplications et `A_0=n²-n` additions. Pour une dérivation,
chaque ancienne multiplication peut rester utilisée et ajoute au plus
deux multiplications et une addition. Chaque ancienne addition peut rester
utilisée et ajoute au plus une addition. La substitution en zéro ne peut
augmenter le nombre de portes atteignables : chaque ancienne porte a une
seule image, éventuellement simplifiée ou partagée. D'où

\[
M_{j+1}\le3M_j,\qquad A_{j+1}\le2A_j+M_j.
\]

Une induction donne `M_j<=3^j M_0` et
`A_j<=2^j A_0+(3^j-2^j)M_0`. En ajoutant la préparation de `B`,

\[
C_Y(n)\le4n^2-1+2(n^2+n-1)3^n-(2n-1)2^n.
\]

Il s'agit d'une majoration générale de ce compilateur, non d'une borne
inférieure. La [preuve ultérieure propre à ce DAG](taille/CROISSANCE_PROJECTION.md)
établit séparément la borne inférieure affichée en tête de cette note.
Elle étudie les produits conservés par la projection immédiate ; elle
n'est pas un transfert de la preuve du compilateur antérieur.

Deux variantes ont également été examinées sans modifier le compilateur
reproductible ci-dessus. Former le produit initial en chaîne à gauche
réduit les comptes observés à `108,458,957,2040,4411,9606` pour
`n=4,6,7,8,9,10` ; l'identification de tous ses partages syntaxiques à tout
ordre n'est pas démontrée ici. Lire les deux dernières variables par deux
évaluations polarisées augmente les comptes ; cette variante est écartée.
Aucune de ces observations ne fournit la borne polynomiale recherchée.

## 7. Vérification Lean de l'étape de projection

`lean/Projection.lean` utilise la dérivée formelle de Mathlib et prouve,
pour tout semi-anneau de coefficients `R` et tout `p : R[X]`,

\[
p'(0)=[X^1]p,\qquad
(aX^k)'(0)=\begin{cases}a&k=1,\\0&k\ne1.\end{cases}
\]

Les autres variables peuvent être placées dans l'anneau des coefficients.
Ces théorèmes certifient donc l'identité locale employée à chaque étape.
Le replay vérifie les sources et les axiomes ; aucune preuve ne contient
`sorry`. La dépendance Mathlib manquante dans le cache est compilée depuis
sa source inchangée, avec son empreinte conservée dans le rapport.

```text
python etudes/2026-11-01/projection-avant-derivation/lean/replay_projection.py
```

La composition multivariée du compilateur, le routage spectral et sa taille
ne sont pas formalisés par ces deux lemmes. En particulier, ils ne sont pas
une preuve Lean de la borne polynomiale générale demandée.
