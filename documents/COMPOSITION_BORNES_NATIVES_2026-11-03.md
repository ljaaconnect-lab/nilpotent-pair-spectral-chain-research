# Composition des bornes de l'architecture native

Travail du 3 novembre 2026. Question : les bornes polynomiales déjà démontrées
pour les éléments choisis s'appliquent-elles ensemble, jusqu'aux sorties
scalaires de l'INTT ?

**Résultat du raccord :** elles donnent une borne polynomiale générale pour
le circuit orienté entier, et pour un circuit partagé de représentants
linéarisés de toutes ses sorties. Elles ne donnent pas encore la borne
générale du circuit à sorties scalaires et à seules entrées originales
`a,z`. Le point précis est une différence de représentation entre les
théorèmes disponibles, explicitée ci-dessous. Aucune croissance
exponentielle n'est déduite de ce constat.

Le [compilateur de la composition](composition-native-2026-11-03/compose_native_representatives.py)
réalise effectivement ce raccord, signe universel, partage spectral et
véritable INTT compris. Il conserve les variables auxiliaires d'orientation.

## 1. Architecture et conventions communes

Les indices de lignes et de colonnes vont de `0` à `n-1`. Le corps
`K=F_Q`, son premier `Q` et une racine `omega` d'ordre exact `N` sont
fournis, avec `N | Q-1`. Choisir la plus petite puissance de deux strictement
supérieure à `n`, donc

\[
n<N\le 2n,\qquad \ell=\log_2N\le n,\qquad n\ge1.
\]

Les étiquettes `d_j` sont fixées à la construction du circuit. Les
constantes et les fils partagés suivent les conventions du papier.
`Q>binom(n,2)` n'est pas une hypothèse de cette chaîne native.

Poser

\[
B_{ij}=(1+a_{ij}^{2})z^{2^{in+j}},\qquad
\gamma_n=(-1)^{n(n-1)/2},\qquad
\varepsilon_n=\begin{cases}1&n\equiv2,3\pmod4,\\0&\text{sinon.}\end{cases}
\]

La sous-algèbre orientée est

\[
\mathcal A=K[a,z][q_0,\ldots,q_{n-1}]/(q_j^2),
\quad q_iq_j=q_jq_i,
\quad q_0\cdots q_{n-1}=\gamma_n\widetilde\Omega.
\]

La chaîne choisie reste exactement

\[
R_i[t]=\sum_{j:d_j=t\bmod N}B_{ij}q_j,
\quad \widehat R_i[f]=\sum_{j<n}B_{ij}q_j\omega^{fd_j},
\]
\[
\mathcal Z[k]=\operatorname{INTT}_N
 \left[\left(\gamma_n\prod_{i<n}\widehat R_i[f]\right)_{f<N}\right][k].
\]

L'expression scalaire terminale n'est ni une feuille ajoutée, ni un calcul
préalable imposé. Les opérations dans `K[a,z]` signifient des portes
arithmétiques construites depuis les entrées `a,z`, et non des polynômes
arbitraires fournis gratuitement.

## 2. La règle de composition déjà acquise

Si un circuit partagé de taille `S` produit les fils consommés par un
second circuit de taille `T`, leur raccord utilise au plus `S+T` portes.
La réutilisation d'un fil ne recopie pas son sous-circuit. La composition
d'un nombre polynomial de blocs de coût polynomial reste donc polynomiale,
**lorsque leurs formats d'entrée et de sortie coïncident**.

Plus précisément, si l'on raccorde `m(n)<=A n^b` blocs, chacun ajoutant
au plus `K n^c` portes dans une représentation commune, leur coût ajouté
est au plus `AK n^(b+c)`. Les constantes et exposants doivent être
uniformes en `n` ; les préfixes partagés sont comptés une seule fois.

Cette règle figure déjà dans
[MatrixScalarCompiler.lean](../etudes/2026-10-07/livrables/conjecture-1-5-suite/proofs/MatrixScalarCompiler.lean) :
`Circuit.comp` évalue la composition et `Circuit.gates` additionne les
tailles. Le théorème `compose_input_correct` de
[ConditionalCriterion.lean](../etudes/2026-10-07/livrables/conjecture-1-5-suite/proofs/ConditionalCriterion.lean)
en donne conjointement la sémantique et le compte. Le
[rejeu Lean existant](verification-compilation-generique-2026-11-02.json)
est passé.

Le même anneau `R` est utilisé de part et d'autre de cette composition.
Une instanciation dans l'algèbre orientée compte ses opérations ; une
instanciation sur les scalaires compte des portes scalaires. Ce théorème
ne change pas à lui seul la représentation de ses fils.

## 3. Premier raccord complet : circuit orienté natif

La proposition 13.8 et les raccords spectraux du papier donnent, en
partant des `a_ij`,

\[
\boxed{C_{\rm orienté}(n,N)
 \le6n^2+n-2+\varepsilon_n+\mathcal B(N)},
\qquad \mathcal B(N)=2N\ell+3N-3.
\]

Le préfixe orienté est construit une seule fois. Les phases communes
permettent son partage entre toutes les fréquences. Les hypothèses sur
`N` donnent

\[
C_{\rm orienté}\le10n^2+7n-4\le17n^2.
\]

Avec `D_*=sum_j d_j` et `k_*=D_* mod N`, l'identité spectrale exacte est

\[
\mathcal Z[k]=\delta_{k,k_*}\gamma_n\prod_{i<n}\sum_{j<n}B_{ij}q_j.
\]

Après cette fusion du spectral en routage, le compte descend à

\[
\boxed{C_{\rm orienté,fusionné}\le6n^2+n-2+\varepsilon_n\le7n^2.}
\]

Il s'agit d'une borne générale pour toute la chaîne dans son algèbre.
Les produits d'éléments orientés y comptent comme opérations de cette
algèbre ; le papier n'affirme pas qu'ils sont chacun une porte du corps `K`.

## 4. Deuxième raccord complet : représentants linéarisés

On reprend la
[forme linéarisée et sa fusion](../etudes/2026-11-01/linearisation-orientee-convolution/FUSION_LINEARISEE.md),
avec la même préparation partagée :

\[
C_{ir}=N^{-1}\sum_{j<n}B_{ij}\omega^{rj},\qquad
F_0(x)=\prod_{i<n}\sum_{r<N}C_{ir}x_{-r}.
\]

L'indice `-r` se lit modulo `N`. Pour préciser la représentation, poser

\[
q_j(x)=N^{-1}\sum_{r<N}\omega^{-rj}x_r.
\]

Le quotient linéarisé impose

\[
\sum_{r<N}x_rx_{t-r}=0\quad(t<N),\qquad
q_j(x)=0\quad(n\le j<N).
\]

Ces relations sont exactement la transformée des carrés nuls et du
padding. Noter `rho_x` l'interprétation dans l'algèbre orientée, définie
par `x_r -> sum_{j<n} omega^(rj) q_j`. L'inversion Fourier donne

\[
\rho_x(F_0)=\prod_{i<n}\sum_{j<n}B_{ij}q_j=:F_A.
\]

L'automorphisme de phase `q_j -> omega^(f d_j)q_j` agit au degré `n` par
la phase unique `omega^(fD_*)`. On peut donc construire les représentants
de toutes les fréquences à partir du seul `F_0` :

\[
\widetilde W_f(x)=\gamma_n\omega^{fD_*}F_0(x),
\qquad
\widetilde Z_k(x)=\operatorname{INTT}_N(\widetilde W)_k.
\]

L'orthogonalité Fourier prouve alors, comme identité de polynômes,

\[
\boxed{\widetilde Z_k(x)=\gamma_n\delta_{k,k_*}F_0(x)},
\qquad
\boxed{\rho_x(\widetilde Z_k)=\mathcal Z[k].}
\]

Cette dernière égalité prouve le raccord de bout en bout. La phase commune
représente les produits natifs après passage au quotient ; elle ne
prétend pas égaler leur développement ordinaire avant quotient.
Le signe universel est appliqué une seule fois.

### Comptage sans double facturation

| Élément raccordé | Sortie produite | Portes supplémentaires au plus |
|---|---|---:|
| Marqueurs et amplitudes depuis `a,z` | `B_ij` scalaires | `4n²−1` |
| `n` NTT et normalisation | `C_ir` scalaires | `2nN ell+nN` |
| Produit partagé de formes linéaires | `F_0(x)` | `2nN−1` |
| Signe universel | `gamma_n F_0(x)` | `epsilon_n` |
| Phases partagées et vraie INTT | table `Ztilde_k(x)` | `B(N)=2N ell+3N−3` |

Les deux premières lignes produisent bien des fils scalaires depuis
`a,z`. Les suivantes restent des polynômes avec les variables auxiliaires
`x_r`, représentés par des portes ordinaires.

En notant

\[
P(n,N)=4n^2-2+2nN\ell+3nN\le18n^3,
\]

on obtient pour **l'ensemble des sorties**

\[
\boxed{C_{\rm représentants,INTT}
 \le P(n,N)+\varepsilon_n+\mathcal B(N)\le29n^3.}
\]

La fusion finale permet aussi

\[
\boxed{C_{\rm représentants,fusionné}
 \le P(n,N)+\varepsilon_n\le18n^3+1.}
\]

Les constantes cubiques sont des majorants commodes ; le compte explicite
est `O(n² log(n+1))`. Il ne comporte aucun facteur supplémentaire `N`
devant le coût de `F_0` et ne compte aucun filtre différentiel.
Le nombre d'enregistrements de portes est polynomial, avec les constantes
de corps fournies comme dans le papier. La construction est polynomiale
en `n` et dans la taille d'encodage de ces paramètres : les marqueurs
sont obtenus par carrés successifs, les NTT par papillons et les produits
par raccord de fils, sans développement en monômes.

## 5. Le point exact que les bornes ne couvrent pas encore

Le théorème B.11 du papier compile un DAG aval de module de rang un en
`s+b` portes scalaires. Son invariant est `U=u Omega_tilde`, **avec le fil
scalaire `u` effectivement construit**. Il traite les portes

\[
U+V,\qquad rU\quad(r\text{ scalaire}).
\]

Pour `n>=2`, une multiplication native qui atteint le degré terminal est
par exemple

\[
\mathcal A_{n-1}\times\mathcal A_1\longrightarrow\mathcal A_n.
\]

Ses deux entrées sont orientées. Elle ne relève pas du contrat `rU`,
même si sa sortie appartient au module terminal de dimension un.
Les deux constructions disponibles fournissent soit ce fil orienté,
soit un représentant `F_0(x)` ; elles ne fournissent pas encore le fil
scalaire exigé par cette application de B.11. C'est explicitement la
distinction de la remarque B.13 et de la discussion après B.15, pages
45 et 47 du papier.

Le cas `n=1` est entièrement scalaire : la coordonnée `B_00` est déjà un
fil de la préparation. La réserve concerne la borne uniforme en `n`.

La forme linéarisée ne supprime pas cette différence de format :
`rho_x(Ztilde_k)=Z[k]` est une identité de représentation, et non une
porte scalaire gratuite nommée `rho_x`. Une évaluation arbitraire des
variables `x` ne réalise pas la lecture de la coordonnée orientée.

**Cela n'impose pas un lecteur séparé avant l'INTT.** Un compilateur
global peut mêler produits orientés, linéarisation, fusion et lecture
terminale. Pour conclure par les bornes individuelles actuelles, il faut
que l'un de leurs théorèmes couvre ce même format de sortie. Cette
garantie générale n'a pas été retrouvée dans les résultats relus.

## 6. Place des autres outils déjà établis

- La fusion `T_y T_z=T_(y+z)` couvre exactement les translations seules.
  Le raccord déjà établi
  `[(prod_i (T_(v_i)-I)) D_n](0)=lambda(F_0)` porte sur leurs différences
  et leur observation. La loi de translation ne constitue pas à elle
  seule un compilateur scalaire de cette observation composée. Aucun
  développement par sous-ensembles n'est ajouté ici.
- Le compilateur générique n57–n59 est bien polynomial pour des entrées
  matricielles scalaires construites et une dimension polynomialement
  bornée. L'identité de sortie, le coût d'initialisation et la dimension
  doivent concerner la même représentation. Son instanciation pour le
  générateur auxiliaire conserve ces auxiliaires ; elle ne peut être
  substituée à une instanciation qui lirait déjà la sortie terminale.
- Les `h` filtres de l'essai différentiel sont redondants après projection
  dans le quotient, comme démontré dans la
  [correction de périmètre](CORRECTION_PERIMETRE_BORNE_2026-11-03.md).
  Ils ne sont ni remis dans le circuit natif ni ajoutés à son coût.

## 7. Vérifications et portée

Le [rapport d'exécution](composition-native-2026-11-03/native-composition-validation.json)
contrôle 20 configurations, `n=1..8`, dans les corps `Q=97` et `Q=17` :
80 instances numériques et 8 tables gardant `z` formel. Les références
calculent directement les produits orientés par fréquence puis une DFT
inverse indépendante. Les étiquettes irrégulières, `z=0`, une ligne
d'amplitudes nulle et le padding sont couverts. Les tables de référence
sont uniquement dans le vérificateur.

Les appels différentiels sont bloqués. Une vraie INTT est exécutée dans
chaque compilation ; les sorties sont également comparées au routage
fusionné. En particulier, `n=7,8` passent avec `Q=17`, sans la condition
inutile `Q>binom(n,2)`.

Exemples de comptes réellement atteignables, étiquettes irrégulières :

| n | N | Q | Avec vraie INTT | Après fusion en routage |
|---:|---:|---:|---:|---:|
| 3 | 4 | 97 | 121 | 101 |
| 6 | 8 | 97 | 553 | 497 |
| 7 | 8 | 17 | 685 | 629 |
| 8 | 16 | 17 | 1494 | 1350 |

Ce sont des portes en `a,z,x`. Le rapport indique explicitement
`quotient_representatives_complete=true` et
`complete_scalar_a_z_only=false`.

Le certificat
[NativeCompositionBounds.lean](composition-native-2026-11-03/NativeCompositionBounds.lean)
vérifie cinq conséquences arithmétiques : `17n²`, `7n²`, `18n³`,
`18n³+1` et `29n³`, sous les hypothèses numériques indiquées.
Le [rejeu Lean](composition-native-2026-11-03/native-bounds-lean-validation.json)
est passé, sans `sorry` ni axiome ajouté. La justification des formules
de comptage depuis le programme reste externe à ce certificat ; celui-ci
ne formalise ni la compilation complète ni l'élimination des auxiliaires.

Les contrôles finis vérifient l'implémentation. La démonstration générale
du raccord des représentants est celle de la section 4 ; elle n'est pas
une formalisation Lean de la suppression des auxiliaires.

## Sources principales

- [Papier de raccordement](../sources/papiers/annihilation_raccord_spectral_demonstrations.pdf),
  proposition 13.8, théorème B.11, remarque B.13, discussion après B.15,
  théorème B.18 et section B.11.
- [Fusion linéarisée](../etudes/2026-11-01/linearisation-orientee-convolution/FUSION_LINEARISEE.md),
  préparation des coefficients, partage spectral et identité de translation.
- [Audit du compilateur générique](AUDIT_COMPILATION_GENERIQUE_2026-11-02.md)
  et [clarification de l'INTT](LECTURE_INTT_ET_MOMENTS_2026-11-02.md).

La conclusion précise du raccord est donc acquise : **toute la chaîne
admet un circuit orienté polynomial et des représentants linéarisés
partagés de taille polynomiale. La borne générale de sa compilation
en sorties scalaires depuis `a,z` reste à établir.**
