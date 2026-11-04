# Inventaire des coûts de toute la chaîne — 2 novembre 2026

L'inventaire porte sur l'architecture actuelle : coefficients et orientation
linéarisés ensemble, un seul représentant `F_0`, puis annihilation et
lecture, signe universel corrigé et sortie spectrale fusionnée.

On compte les portes scalaires binaires `+` et `×` dans `F_Q`. Une
soustraction coûte au plus deux portes : multiplication par `−1` et
addition. Les fils, constantes et permutations de fils sont gratuits dans
ce modèle. Les majorants peuvent être réduits par le partage et les
simplifications du compilateur.

Paramètres : `n>=1`, `N=2^ell`, `n<=N<2n`, `Q` premier fourni supérieur
à `max(2,binom(n,2))`, `N | Q−1`, racine fournie `omega` d'ordre `N`.
Les étiquettes `d_j` sont fixées à la construction du circuit. Les données
variables sont les `n²` valeurs `a_ij` et `z`. Les exposants de `z` restent
formels ; on ne les réduit pas modulo `Q−1`.

## 1. Entrées et préparation partagée des amplitudes

\[
B_{ij}=(1+a_{ij}^2)z^{2^{in+j}}.
\]

| Élément individuel | Portes au plus | Justification |
|---|---:|---|
| Lire `a_ij,z` | `0` | `n²+1` fils d'entrée |
| Toutes les marques `z^(2^k)`, `0<=k<n²` | `n²−1` | Carrés successifs à partir du fil `z` |
| Tous les carrés `a_ij²` | `n²` | Un produit par entrée |
| Tous les `1+a_ij²` | `n²` | Une addition par entrée |
| Toutes les amplitudes marquées `B_ij` | `n²` supplémentaires | Un produit avec la marque par entrée |
| **Préparation totale de `B`** | **`4n²−1`** | Chaque étape partagée une seule fois |

La grandeur des exposants n'impose donc pas leur nombre de multiplications
naïf. Cette observation concerne le nombre de portes du circuit formel.

## 2. Linéarisation et représentant compact

\[
C_{ir}=\frac1N\sum_{j<n}B_{ij}\omega^{rj},\qquad
F_0(x)=\prod_{i<n}\sum_{r<N}C_{ir}x_{-r}.
\]

| Élément individuel | Portes au plus | Domaine de la sortie |
|---|---:|---|
| Padding par zéros jusqu'à `N` | `0` | Fils constants |
| Une NTT de longueur `N` | `2N ell` | `N ell/2` papillons à quatre portes |
| NTT des `n` lignes | `2nN ell` | Coefficients scalaires depuis `a,z` |
| Normalisation par `1/N` | `nN` | Multiplication par une constante |
| Réindexation `v_i[s]=C_i,(-s)` | `0` | Permutation de fils |
| Produits `C_ir x_-r` des `n` formes | `nN` | Variables auxiliaires formelles `x` |
| Additions dans ces `n` formes | `n(N−1)` | Représentants ordinaires |
| Produit des `n` formes | `n−1` | Représentant ordinaire `F_0(x)` |

Le coût des coefficients seuls est

\[
\boxed{C_{\mathrm{coeff}}
 \le 4n^2-1+2nN\ell+nN.}
\]

Le représentant ajoute `2nN−1` portes, d'où

\[
\boxed{C_{F_0}
 \le4n^2-2+2nN\ell+3nN
 =O(n^2\log(n+1)).}
\]

Ces portes calculent un polynôme en variables auxiliaires ; elles ne
comprennent pas la lecture orientée de ce polynôme. Le changement de base
`x_r=sum_j omega^(rj)q_j` fixe l'interprétation de ces variables. On ne
recompte pas une transformée supplémentaire des symboles de base comme
un calcul sur les données.

## 3. Relations d'annihilation et padding orienté

Les relations du quotient sont

\[
g_t(x)=\frac1N\sum_r x_rx_{t-r}=0,\qquad
q_j(x)=\frac1N\sum_r\omega^{-rj}x_r=0\quad(n\le j<N).
\]

Il existe une façon polynomiale de **calculer les polynômes définissant
ces relations**, à des coordonnées auxiliaires données :

| Élément | Portes au plus |
|---|---:|
| Tous les `q_j(x)` par INTT | `2N ell+N` |
| Tous les carrés `q_j(x)²` | `N` |
| Tous les `g_t(x)=NTT(q(x)²)[t]` | `2N ell` |
| **Total, avec les coordonnées du padding déjà disponibles** | **`4N ell+2N`** |

Ce compte ne représente pas la réduction de `F_0` dans le quotient.
Évaluer les relations et appliquer leur effet à un produit arbitraire
sont deux opérations distinctes. Dans le circuit cible, leur effet est
pris en compte par la lecture `lambda(F_0)` ; ce tableau n'est pas un
bloc supplémentaire nécessaire à ajouter au total.

## 4. Coût individuel du dual, des translations et des différences

Définir

\[
D_n(y)=\prod_{j<n}\sum_{s<N}\omega^{sj}y_s,
\quad T_vP(y)=P(y+v),\quad\Delta_v=T_v-I.
\]

Pour un circuit `P` de `S` portes, les coordonnées de ses paramètres
`v` étant déjà disponibles :

| Opération individuelle | Portes au plus | Ce qui est compté |
|---|---:|---|
| Une évaluation de `D_n(y)` | `E_D=2N ell+n−1` | Une NTT de `y`, puis produit des `n` premières sorties |
| Une translation `T_vP(y)` | `S+N` | `N` additions pour l'argument, puis une évaluation |
| Une différence `Delta_vP(y)` | `2S+N+2` | Les deux évaluations, puis la soustraction |
| Fusion de deux déplacements `u,v` | `N` | Addition de leurs coordonnées |
| Fusion de `m` translations seules | `(m−1)N` | Construction de `sum_i v_i` |
| Action de ces translations sur `P`, en zéro | `(m−1)N+S` | Une seule évaluation après fusion |
| Action en un `y` variable | `mN+S` | Ajout de `y` au déplacement total |

À zéro, `D_n(0)=0`, donc une seule différence de `D_n` ne requiert
qu'une évaluation de `D_n(v)`. Pour les directions réellement préparées,
l'inversion Fourier donne de plus

\[
\sum_s\omega^{sj}v_i[s]=B_{ij},\qquad
(\Delta_{v_i}D_n)(0)=\prod_{j<n}B_{ij}.
\]

Cette dernière quantité coûte **`n−1` multiplications supplémentaires**
si l'on réutilise les amplitudes `B` déjà construites. Les `n` premières
différences prises séparément en zéro coûtent donc au plus `n(n−1)`
multiplications. Leurs valeurs séparées ne sont pas la valeur de leur
composition sur `D_n`.

Le raccord exact de la chaîne est

\[
Y=\lambda(F_0)=
 \left[\prod_{i<n}\Delta_{v_i}\,D_n\right](0).
\]

Noter `C_lecture(n)` le coût d'un circuit scalaire qui reçoit les
coefficients préparés `C_ir` et produit ce `Y`, en éliminant les variables
auxiliaires. **Un majorant polynomial général de ce coût n'est pas établi.**
L'application composée, l'annihilation qu'elle réalise et son évaluation
terminale appartiennent à ce même coût. On ne les ajoute pas trois fois.

La règle `T_u T_v=T_(u+v)` donne pour les différences

\[
\Delta_u\Delta_v=\Delta_{u+v}-\Delta_u-\Delta_v.
\]

Le coût local `2S+N+2` dépend de la taille `S` du circuit courant. Une
compilation générique par duplication vérifie
`S_(r+1)<=2S_r+N+2`, et donc

\[
S_m\le2^mE_D+(2^m-1)(N+2).
\]

C'est un majorant de cette compilation par duplication, et non une borne
inférieure sur toutes les compilations possibles. Les tableaux ci-dessus
ne permettent pas de remplacer `S_r` par `E_D` à chaque étape.

**Complément après relecture des travaux : des compilateurs génériques
polynomiaux sont déjà acquis.** Le compilateur n57–n59 de `uᵀM^K v`
coûte au plus `S+J(K)(2r³−r²)+2r²+r−1`, avec `J(K)<=2 log2 K`
pour `K>=1`, construction initiale et lecture comprises. Pour `K=n^n−1`,
Lean prouve `S+4r³n²+3r²`, puis `n^c+4n^(3d+2)+3n^(2d)` si
`r<=n^d` et `S<=n^c` (`r>=1`, `n>=2`). La représentation exacte
de l'action à compiler et les bornes sur `r,S` sont les hypothèses
d'application ; le compilateur ne les construit pas pour une cible arbitraire.

Le [raccord au lecteur d'observations](CONSTANTES_C_D_2026-11-02.md)
fixe `d=2` pour cette représentation auxiliaire du lecteur fourni.
Il ne représente pas les produits orientés ni la construction des
observations. Les moments et ce pont matriciel ne sont pas des étapes
imposées à la chaîne ; voir la [clarification INTT](LECTURE_INTT_ET_MOMENTS_2026-11-02.md).

Le transport rationnel triangulaire coûte `2(p+1) binom(d+1,3)` portes
pour `p>=1` générateurs de dimension `d`.
L'AD inverse ajoute au plus `4S` portes pour le gradient ; la dérivation
directe mémoïsée ajoute au plus `9nS` pour toutes les diagonales secondes.
Ces garanties, leurs interfaces et leur portée sont rétablies dans
l'[audit ciblé de la compilation générique](AUDIT_COMPILATION_GENERIQUE_2026-11-02.md).

## 5. Signe, modulation et lecture spectrale

\[
\gamma_n=(-1)^{n(n-1)/2},\quad
\gamma_nq_0\cdots q_{n-1}=\widetilde\Omega,\quad
k_* = \sum_jd_j\bmod N.
\]

| Élément | Calcul explicite séparé | Après la fusion établie |
|---|---:|---:|
| Signe universel | Au plus `1` multiplication par une constante | `0`, absorbé dans la normalisation orientée de sortie |
| Phases `omega^(f sum d_j)Y` | Au plus `N` multiplications | `0` |
| INTT de ces `N` valeurs | Au plus `2N ell+N` | `0` |
| Table de sortie | `N` références | `N` références, zéro porte arithmétique |

La fusion utilise exactement

\[
\mathcal Z_Q[k]=\delta_{k,k_*}\,Y\widetilde\Omega.
\]

Les phases et l'INTT sont donc comprises dans le routage. L'indice `k_*`
est fixé par les étiquettes à la construction du circuit.

## 6. Total sans double comptage

Pour une réalisation du lecteur recevant directement les `C_ir`,

\[
\boxed{
C_{\mathrm{chaîne}}(n)
\le \underbrace{4n^2-1}_{a,z\longmapsto B}
 +\underbrace{2nN\ell+nN}_{B\longmapsto C}
 +\underbrace{C_{\mathrm{lecture}}(n)}_{C\longmapsto Y}
.}
\]

La somme n'inclut pas une seconde construction de `F_0`, de `D_n`, de
ses traductions, ou des relations du quotient : ces écritures décrivent
le travail du lecteur. Toute fusion supplémentaire avec les fils `B`
peut encore réduire le coût de cette réalisation.

Le sous-total connu `C_coeff` est `O(n² log(n+1))`. La borne
`C_F0<=18n³` a une vérification arithmétique Lean, sous les hypothèses
`n>=1`, `N<=2n`, `ell<=n`. Lean ne formalise dans ce certificat ni la
dérivation du compte depuis le programme, ni le coût général du lecteur.

## 7. Paramètres et autres écritures du même coût

La recherche du premier `Q` et de sa racine, le coût binaire des opérations
modulaires, et un éventuel relèvement en caractéristique zéro ne font pas
partie des bornes en portes de corps affichées. La sortie concernée est
la réduction modulo `Q` de la sortie formelle du papier. La table du spectre
de collision ou les coefficients d'un projecteur restent des paramètres
de la variante qui les utilise ; ils ne sont pas requis par la préparation
linéarisée ci-dessus.

Pour rattacher cet inventaire aux variantes historiques sans additionner
leurs coûts à ceux de l'architecture actuelle :

| Variante | Identité de coût vérifiée | Partie non fournie gratuitement |
|---|---|---|
| Préfixe `X=(c(L)G_B)(1)` suivi de la correction de deux niveaux, `n>=3` | `C_chaîne<=S_I^(1)+4n²−3n+2` | Le préfixe `S_I^(1)` inclut la préparation de `B` |
| Même correction sans les sommes de lignes partagées, `n>=3` | Au plus `5n²−4n+2` depuis `B` et `X` | Calcul de `X` |
| Lecteur sur `q+1` observations `mu_0,...,mu_q` | `2q` portes, avec `q<=binom(n,2)` | Construction simultanée des `mu_j` depuis `a,z` |
| Préparation des coefficients de ce dernier lecteur | Au plus `q²` opérations, inverses des entiers fournis | Coût fixe dépendant de `n,Q` si non précompilé |

La taille des compilateurs directs historiques est étudiée séparément.
Leurs coûts ne sont pas des bornes inférieures pour une future réalisation
du lecteur de la forme linéarisée.

## Sources internes

- [Compilation des produits orientés : construction à rang fixé et portée des états linéaires](COMPILATION_PRODUITS_ORIENTES_2026-11-02.md). La borne générale reste non établie.

- [Forme linéarisée et relations orientées](../etudes/2026-11-01/linearisation-orientee-convolution/FORME_LINEARISEE.md)
- [Fusion spectrale, lecteur dual et preuve de comptage](../etudes/2026-11-01/linearisation-orientee-convolution/FUSION_LINEARISEE.md)
- [Compilateur de la préparation fusionnée](../etudes/2026-11-01/linearisation-orientee-convolution/fused_linearised.py)
- [Certificat arithmétique Lean](../etudes/2026-11-01/linearisation-orientee-convolution/lean/LinearisedPreparationBound.lean)
- [Ancien décompte après fusion](../etudes/2026-11-01/borne-chaine-generale/BORNE_REVISEE_APRES_FUSION.md)
