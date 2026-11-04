# Réanalyse dans le quotient de convolution

**Périmètre corrigé :** la récurrence R des sections 5 et 6 est un essai
de compilation, dont les groupes de lignes ne sont pas imposés par
l'architecture retenue. Ses G, s_k et W ne doivent pas entrer dans le coût
de cette architecture. Voir l'[inventaire corrigé](INVENTAIRE_COMPLET_2026-11-03.md)
et les [mesures séparées du prototype](INVENTAIRE_PROTOTYPE_R_2026-11-03.md).

3 novembre 2026. On reprend exactement les coordonnées linéarisées,
les relations de convolution, le padding et la fusion des fréquences.
L'identité de fusion est valable dans le quotient entier, avant sa
lecture scalaire. Le contre-exemple de la tentative précédente portait
sur la suppression des directions individuelles ; il ne réfutait pas
cette identité ni la compilation conjointe demandée.

Cette réanalyse donne une normalisation scalaire effective à deux lignes,
une règle expérimentale de réduction exacte à tout ordre par convolutions
et un compilateur scalaire de cette règle, fusionné avec la préparation.
Ce candidat ne remplace pas l'architecture retenue. **La borne
polynomiale générale sur les portes du même circuit reste non démontrée.**

## 1. Les relations définissent exactement l'algèbre orientée

Soit \(R=\mathbb F_Q[\{a_{ij}\},z]\), avec \(Q\) premier fourni,
\(N\mid Q-1\), \(\omega\) d'ordre \(N\) et \(n\le N\).
Le compilateur actuel choisit \(N\) puissance de deux strictement
supérieure à \(n\). Tous les indices Fourier sont pris modulo \(N\).
Poser

\[
q_j(x)=\frac1N\sum_r\omega^{-rj}x_r,
\qquad g_t(x)=\frac1N\sum_r x_rx_{t-r}.
\]

L'inversion Fourier et l'orthogonalité donnent, comme identités de
polynômes ordinaires après changement de variables,

\[
x_r=\sum_j\omega^{rj}q_j,
\qquad g_t=\sum_j\omega^{tj}q_j^2,
\qquad q_j^2=\frac1N\sum_t\omega^{-tj}g_t.
\]

Par conséquent, l'idéal engendré par les \(g_t\) et les relations de
padding \(q_j(x)=0\), \(j\ge n\), devient exactement

\[
(q_0^2,\ldots,q_{n-1}^2,q_n,\ldots,q_{N-1}).
\]

Ainsi le quotient utilisé dans la formule de l'auteur est bien

\[
\mathcal A\simeq R[q_0,\ldots,q_{n-1}]/(q_0^2,\ldots,q_{n-1}^2).
\]

Cette égalité d'idéaux prend en compte le padding : on ne conserve pas
\(N\) générateurs actifs lorsque \(n<N\).

## 2. La fusion vaut avant toute extraction de coefficient

On a exactement

\[
\sum_r C_{ifr}x_{-r}=\sum_{j<n}B_{ij}\omega^{fd_j}q_j.
\]

L'automorphisme \(q_j\mapsto\omega^{fd_j}q_j\) préserve les carrés nuls.
Le degré \(n\) du quotient est libre de rang un sur \(R\), engendré par
\(q_{[n]}=q_0\cdots q_{n-1}\) : tout monôme de degré \(n\) qui répète
un indice est nul, et le seul monôme restant utilise chaque générateur.
L'automorphisme agit sur ce degré par \(\omega^{fD_*}\), où
\(D_*=\sum_jd_j\). Donc, directement dans \(\mathcal A\),

\[
\boxed{[F_f]=\omega^{fD_*}[F_0].}
\]

La linéarité de l'INTT et l'orthogonalité donnent alors

\[
\boxed{\mathcal Z[k]=\delta_{k,D_*\bmod N}\,\gamma_n[F_0].}
\]

Le spectral est entièrement inclus dans cette identité. Il n'y a pas
\(N\) produits indépendants à normaliser ni une autre lecture spectrale
à ajouter ensuite au budget global.

## 3. Un générateur terminal compact

Puisque \(x_0=\sum_{j<n}q_j\), développer sa puissance donne

\[
\boxed{x_0^n=n!\,q_{[n]}.}
\]

Les termes contenant un carré sont nuls et les \(n!\) ordres distincts
du produit des \(n\) générateurs donnent le même monôme. Comme
\(Q>N\ge n\), le scalaire \(n!\) est inversible. On peut donc choisir
\(x_0^n/n!\) comme générateur terminal, représenté par un circuit compact.

Cette identité ne permet pas de diviser par \(x_0\), qui est nilpotent.
Elle fixe le label terminal ; elle ne calcule pas gratuitement le
coefficient d'un produit arbitraire dans ce label.

## 4. Normalisation construite à deux lignes

Pour \(n=2,N=4\), les relations donnent

\[
x_0=q_0+q_1,\qquad x_2=q_0-q_1,
\qquad x_0x_2=0,\qquad x_2^2=-x_0^2,
\qquad x_0^2=2q_0q_1.
\]

Écrire \(C_{ir}=C_{i,0,r}\). Les formes de lignes s'expriment par
\(x_0,x_2\), et leur produit a pour coefficient dans \(q_0q_1\)

\[
b=\frac{N^2}{2}
\left(C_{00}C_{10}-C_{0,2}C_{1,2}\right).
\]

La fusion de cette réduction avec les fils de préparation donne

\[
\boxed{b=B_{00}B_{11}+B_{01}B_{10}.}
\]

Il s'agit de deux multiplications et une addition sur des fils déjà
construits. Aucune amplitude n'est ajoutée aux entrées. Le signe est
compté une seule fois : \(\gamma_2q_0q_1=\widetilde\Omega\), donc la
table scalaire normalisée est l'INTT de
\((\omega^{fD_*}b)_f\).

Le programme joint construit ces racines dans le même DAG que les
coefficients \(C\). Pour les paramètres testés, la réalisation passant
par les \(C\) utilise 50 portes avec la vraie INTT. Après fusion avec la
préparation, elle en utilise 38 :

\[
|T_2\cap P_2|=15,\qquad J_2=23,\qquad C(\Gamma_2)=38.
\]

Les 23 portes comprennent le cœur de trois portes et les phases/INTT.
Les seules variables atteignables depuis les sorties sont les quatre
\(a_{ij}\) et \(z\). Ce résultat concerne la taille deux ; ces valeurs
ne sont pas extrapolées à une borne pour tout \(n\).

## 5. Une réduction générale exprimée par convolutions

Voici une tentative de normalisation intrinsèque de ce même quotient.
La différentiation sert à en démontrer la règle ; les opérations de la
règle ci-dessous sont des convolutions et des opérations scalaires.
Elle n'est pas imposée comme l'unique compilation possible.

Sur \(R[q_0,\ldots,q_{N-1}]\), définir

\[
\Lambda=\sum_{j<n}(\partial_{q_j}-q_j\partial_{q_j}^2).
\]

Cet opérateur préserve l'idéal. En effet,

\[
(\partial_{q_j}-q_j\partial_{q_j}^2)(q_j^2H)
=-3q_j^2\partial_{q_j}H-q_j^3\partial_{q_j}^2H.
\]

Les autres termes conservent le facteur \(q_j^2\), et les variables de
padding ne sont pas dérivées. Sur un monôme sans carré,
\(\Lambda(q_S)=\sum_{j\in S}q_{S\setminus\{j\}}\).
Ainsi, pour tout \(F\) homogène de degré \(n\),

\[
[F]=bq_{[n]}\quad\Longrightarrow\quad
\boxed{\Lambda^nF=n!b.}
\]

L'égalité finale est une égalité de polynômes ordinaires : après \(n\)
réductions, le degré en variables auxiliaires est zéro, et l'idéal ne
contient aucune constante non nulle. Il ne reste donc pas de lecture
du quotient à appliquer à ce résultat.

Pour exprimer l'action dans la base demandée, poser
\(\ell(c)=\sum_r c_rx_{-r}\), avec
\(c_r=N^{-1}\sum_jb_j\omega^{rj}\) et \(b_j=0\) pour \(j\ge n\).
La convolution cyclique vérifie

\[
(c*c')_r=\sum_s c_sc'_{r-s}
=\frac1N\sum_jb_jb'_j\omega^{rj}.
\]

Il n'y a aucun facteur \(N\) supplémentaire. Le produit \(bb'\)
conserve le padding. La règle exacte est

\[
\boxed{\begin{aligned}
\Lambda\prod_{i=1}^{k}\ell(c_i)
={}&\sum_i(Nc_i[0])\prod_{u\ne i}\ell(c_u)\\
&-2\sum_{i<j}\ell(c_i*c_j)
               \prod_{u\ne i,j}\ell(c_u).
\end{aligned}}
\]

Elle résulte de la règle du produit : chaque dérivée seconde choisit
deux formes distinctes, dans deux ordres. Chaque terme a \(k-1\)
formes restantes. L'action est prolongée linéairement aux sommes
obtenues, avec les coefficients scalaires conservés sur le même DAG.

En posant \(R(\varnothing)=1\), la contraction complète peut s'écrire
sans dérivation primitive :

\[
\begin{aligned}
R(c_1,\ldots,c_k)
={}&\sum_i(Nc_i[0])R(c_1,\ldots,\widehat c_i,\ldots,c_k)\\
&-2\sum_{i<j}R(c_i*c_j,(c_u)_{u\ne i,j}).
\end{aligned}
\]

Une induction sur \(k\) prouve
\(R(c_1,\ldots,c_k)=\Lambda^k\prod_i\ell(c_i)\) : le cas vide vaut un ;
la règle du produit réduit chaque terme à \(k-1\) formes et ses
coefficients scalaires ne sont pas dérivés. L'hypothèse d'induction
s'applique donc à chaque appel de la récurrence.
Alors \(R(c_1,\ldots,c_n)/n!\) est le coefficient normalisé de
\(F_0\). La relation de fusion spectrale se conserve puisque \(\Lambda\)
préserve l'idéal. Cette contraction, les phases et l'INTT appartiennent
toutes au budget \(J_n\) déjà fixé.

## 6. Compilation expérimentale sur un même DAG

[Le compilateur joint](reanalyse-quotient-2026-11-03/compiler_joint_convolution.py)
émet les portes de cette récurrence dans le DAG natif, puis multiplie par
la constante structurelle \((n!)^{-1}\), applique les phases communes et
la véritable INTT. Ses sorties dépendent uniquement de \(a_{ij},z\).
Il ne prend ni coefficient terminal ni résultat de lecture comme entrée.
Ses seules opérations arithmétiques sont des additions et multiplications
scalaires ; il n'appelle aucun opérateur de dérivation ou de lecture du
quotient comme porte primitive.

La correction générale du compilateur suit la même induction : le fil
du cas vide vaut un ; chaque autre fil utilise les racines des appels
plus petits et les opérations de la récurrence. Les identités de
convolution certifient le pool de vecteurs, et leur commutativité et
associativité justifient la réutilisation canonique. La division par
\(n!\) donne donc \(b\), avec \([F_0]=bq_{[n]}\). Enfin, en prenant
\(\widetilde\Omega=\gamma_nq_{[n]}\), les phases et l'INTT donnent
\(\Gamma_n(a,z)_k\widetilde\Omega=\mathcal Z[k]\).
Cette correction vaut à tout ordre sous les hypothèses de la section 1 ;
elle ne dépend pas des tailles finies utilisées pour les contrôles.

Les convolutions sont indexées par les collections de facteurs de lignes
qu'elles fusionnent. Un ordre canonique assure qu'un même groupe réutilise
les mêmes fils quels que soient l'ordre et le parenthésage des fusions.
Les états de la récurrence sont également partagés. Ces collections sont
des métadonnées de compilation ; elles ne codent pas des colonnes occupées.

Une seconde variante fusionne encore ces opérations avec la préparation.
Pour un groupe de facteurs de lignes \(I\), poser

\[
b_I[j]=\prod_{i\in I}B_{ij},\qquad
c_I=\mathop{*}_{i\in I}c_i.
\]

L'identité de convolution démontrée plus haut donne

\[
c_I[r]=\frac1N\sum_{j<n}b_I[j]\omega^{rj},
\qquad \boxed{Nc_I[0]=\sum_{j<n}b_I[j].}
\]

La récurrence ne lit que cette dernière quantité pour chaque groupe.
Elle peut donc réutiliser directement les produits et sommes des fils
\(B\), sans construire les transformées intermédiaires. Le compilateur
applique effectivement cette fusion ; les nœuds devenus inutiles ne
sont pas comptés dans les ancêtres des sorties.

Mesures pour \(Q=97\), \(N=2^{\lfloor\log_2n\rfloor+1}\) et les étiquettes
consignées dans le rapport :

| n | Convolution directe, INTT incluse | Fusion avec préparation, INTT incluse | Préparation utile \(\lvert T\cap P\rvert\) de la variante fusionnée | \(J_n\) de la variante fusionnée |
|---:|---:|---:|---:|---:|
| 1 | 11 | 9 | 3 | 6 |
| 2 | 72 | 45 | 17 | 28 |
| 3 | 185 | 113 | 35 | 78 |
| 4 | 1 058 | 399 | 63 | 336 |
| 5 | 3 043 | 1 521 | 99 | 1 422 |
| 6 | 10 623 | 7 374 | 143 | 7 231 |

La normalisation spécifique à deux lignes de la section 4 utilise une
simplification supplémentaire, d'où ses 38 portes au lieu des 45 de
cette récurrence générique. Dans la partition du DAG, une somme réutilisée
depuis la préparation appartient à \(T\cap P\) : ce compte peut donc
dépasser le coût des seuls \(B\), comme à \(n=2\).

On peut prouver le majorant suivant pour **ce compilateur particulier**,
avec \(\ell=\log_2N\) :

\[
\boxed{C_{\rm candidat}(n)\le
(4n^2-1)+2n\,2^n+3n^2(n+1)^n
+(2N\ell+3N-3)+1.}
\]

La préparation des \(B\) coûte au plus \(4n^2-1\). Il existe au plus
\(2^n-1\) groupes non vides de facteurs de lignes ; chaque groupe requiert
au plus \(n\) multiplications pour son vecteur \(b_I\) et \(n-1\) additions
pour sa somme. Un état est une partition d'une partie des facteurs de
lignes : on l'encode de façon injective en attribuant à chaque ligne zéro
si elle est absente, et un plus le plus petit indice de son bloc sinon.
Il y a donc au plus \((n+1)^n\) états. Un état à \(k\) blocs émet au plus
\(2k+\binom{k}{2}\le3n^2\) portes en dehors du pool déjà partagé.
Enfin, la division par \(n!\) coûte au plus une multiplication et les
phases avec l'INTT au plus \(2N\ell+3N-3\) portes.

Ce majorant prend en compte le partage associatif et la fusion avec la
préparation. Il n'est pas polynomial et ne démontre ni une borne inférieure
ni l'impossibilité d'une meilleure compilation de l'architecture.

## 7. Portée de la tentative de clôture

Chaque convolution individuelle et chaque retrait de forme ont un coût
scalaire polynomial. La règle produit toutefois une somme de produits,
puis doit agir sur cette somme. L'associativité de la convolution permet
des partages, mais ne démontre pas à elle seule une borne sur toutes les
portes distinctes nécessaires après les \(n\) réductions.

Le problème restant est toujours

\[
\boxed{J_n=|T_n\setminus P_n|\le\kappa n^e}
\]

pour une même famille de circuits exacts. Aucun coût de lecteur n'est
reporté après ce terme. La règle générale est exacte ; la clôture
polynomiale de son coût global n'est pas déduite de son nombre d'étapes.

## 8. Vérifications

[Le vérificateur positif](reanalyse-quotient-2026-11-03/verify_quotient_reanalysis.py)
et son [rapport](reanalyse-quotient-2026-11-03/quotient-reanalysis-validation.json)
contrôlent 48 instances, 360 égalités de fréquences dans le quotient
entier et cinq cas où \(z\) reste formel. Ils vérifient les convolutions,
le padding, la fusion, le générateur terminal et les deux réalisations
scalaires de taille deux. Les dictionnaires de référence du quotient
servent au contrôle et ne sont pas des entrées du compilateur.

Ces contrôles finis ne remplacent pas les preuves algébriques générales
ci-dessus et ne démontrent pas une borne de coût pour tout \(n\).

[Le vérificateur du compilateur général](reanalyse-quotient-2026-11-03/verify_joint_convolution.py)
et son [rapport](reanalyse-quotient-2026-11-03/joint-convolution-validation.json)
couvrent les deux variantes jusqu'à \(n=6\), ainsi que d'autres corps :
18 compilations, 72 instances numériques et 12 tables avec \(z\) formel.
Tous les vecteurs fusionnés sont contrôlés indépendamment ; tous les
états intermédiaires le sont jusqu'à \(n=3\). Les oracles du quotient
restent confinés au vérificateur. Un rejeu indépendant a comparé les
résultats et les comptes au rapport, hors durées d'exécution.

[La preuve Lean](reanalyse-quotient-2026-11-03/Fourier4Normalization.lean)
établit huit théorèmes pour \(n=2,N=4\), directement à partir des quatre
convolutions et des deux relations de padding. L'algèbre ambiante est un
anneau commutatif arbitraire, autorisant les nilpotents. Le coefficient
est calculé par un circuit scalaire explicite de trois portes, puis
raccordé à cette algèbre par `algebraMap`.
Le [rejeu](reanalyse-quotient-2026-11-03/replay_fourier4_normalization.py)
et le [rapport Lean](reanalyse-quotient-2026-11-03/fourier4-lean-validation.json)
confirment la compilation sous Lean 4.34.1, sans placeholder, axiome ajouté,
erreur ou avertissement. Aucun auxiliaire nilpotent n'est inversé.
**La preuve générale de la section 5 est une preuve écrite ; ces huit
théorèmes Lean ne formalisent pas sa généralisation ni sa complexité.**

Reproduire depuis la racine du projet :

```powershell
python -B documents/reanalyse-quotient-2026-11-03/verify_quotient_reanalysis.py
python -B documents/reanalyse-quotient-2026-11-03/verify_joint_convolution.py --max-n 6
python -B documents/reanalyse-quotient-2026-11-03/replay_fourier4_normalization.py
```
