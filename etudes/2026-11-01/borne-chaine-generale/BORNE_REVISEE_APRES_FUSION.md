# Borne recomptée après fusion et partage

La réalisation étudiée est le circuit direct partagé, sans logarithme et
sans table de jets. On reprend les fusions déjà démontrées, en comptant une
seule fois les sous-circuits communs. Le resserrement principal est

\[
\boxed{C_{\mathrm{chaîne}}(n)\le S_I^{(1)}(n)+4n^2-3n+2\quad(n\ge3).}
\]

Ici `S_I^(1)` compte le préfixe direct depuis `a,z`, préparation de `B`
comprise, après substitution `s=1` et avant la correction terminale.
Le terme ajouté est polynomial et ne contient aucune réplication spectrale.
Une étude ultérieure du compilateur fixé établit
`S_I^(1)(2m) >= binom(2m,m) >= 2^m` : voir
[Croissance du DAG direct](si-direct/CROISSANCE_DAG_DIRECT.md).
Le majorant additif de cette note reste valable ; il ne rend pas
polynomial ce préfixe. La preuve de croissance ne vise pas d'autres
compilations de la même sortie.

## 1. Ce que la fusion permet de compter une seule fois

Posons `h_k=binom(k,2)`, `K_n` le spectre de collision atteint et

\[
I=K_n\setminus\{0,h_{n-1},h_n\},\qquad
c(X)=\prod_{r\in I}(1-X/r),\qquad X=(c(L)G_B)(\mathbf1).
\]

La correction existante est

\[
Y=X-aS+(na-b)C,\qquad a=c(h_{n-1}),\quad b=c(h_n),
\]

\[
p_{ij}=\prod_{\ell\ne i}B_{\ell j},\quad
R_i=\sum_jp_{ij},\quad \ell_i=\sum_jB_{ij},\quad
S=\sum_i\ell_iR_i,\quad C=\sum_j\prod_iB_{ij}.
\]

Dans le compilateur direct retenu, chaque étape conserve la racine précédente
dans `H - L(H)/r`. Après substitution `s=1`, les sommes de lignes `ell_i`
du produit initial sont donc déjà présentes et partagées. Il ne faut pas
ajouter une seconde fois leurs `n(n-1)` additions. Cette propriété concerne
ce DAG direct ; pour une autre implantation n'exposant pas ces fils, la
borne indépendante depuis `B` est donnée plus bas.

Par colonne, on construit les produits complets et tous les produits
omettant une ligne avec `n-1` multiplications de préfixes, `n-2`
multiplications de suffixes utiles et `n-2` raccords internes. Le suffixe
de toute la colonne serait redondant avec son produit complet.

| Calcul ajouté au préfixe | Majorant de portes scalaires |
|---|---:|
| Produits de colonnes et produits omettant une ligne | `n(3n-5)` |
| Sommes `R_i` | `n(n-1)` |
| Somme `C` | `n-1` |
| Produits et somme pour `S` | `2n-1` |
| Combinaison `X + (-a)S + (na-b)C` | `4` |
| **Total** | **`4n²-3n+2`** |

Les coefficients de la combinaison finale sont des constantes du circuit.
Aucune division par une donnée n'intervient : le calcul reste valable si
des entrées ou des sommes de lignes sont nulles.

Sans les sommes de lignes disponibles, on ajoute `n(n-1)` portes : le
majorant indépendant depuis `B` devient `5n²-4n+2`, inférieur à l'ancien
`5n²`. Si `F_I^(1)` compte le préfixe avec les `B` comme feuilles, alors
la préparation partagée de `B` coûte au plus `4n²-1`, d'où aussi

\[
\boxed{C_{\mathrm{chaîne}}\le F_I^{(1)}+8n^2-3n+1.}
\]

## 2. Le spectral est déjà compris dans ces bornes

Après correction, la forme homogène de degré `n` ne contient plus que le
monôme `s_0 ... s_(n-1)`. La correction universelle fixe son orientation
à `Omega_tilde`. La modulation et l'INTT se réduisent exactement à

\[
\mathcal Z_Q[k]=\delta_{k,\,\sum_jd_j\bmod N}\,Y\widetilde\Omega.
\]

Le même fil `Y` alimente le bon indice ; les autres sorties valent zéro.
Ce routage coûte zéro porte arithmétique. On ne réintroduit donc ni un
facteur `N`, ni le coût d'une INTT après la correction terminale. La table
possède toujours `N` références de sortie. `Y` est calculé depuis les
entrées originales, jamais fourni en entrée.

## 3. Révision de l'ancienne borne polynomiale du composant lecteur

L'étude `orbite-scalaire` comptait auparavant les mises à jour successives
d'un état de `h+1` observations, pour `h=binom(n,2)`. Son surcoût était

\[
N(4h^2+2h)+2N\log_2N+N.
\]

Pour comparer cette borne avec la fusion, poser `q=|K_n|-1<=h` et

\[
p_K(X)=\prod_{r\in K_n\setminus\{0\}}(1-X/r)
      =1+\sum_{j=1}^q p_jX^j.
\]

Fusionner tous les facteurs avec leur lecture revient à calculer seulement

\[
(p_K(L)G_B)(\mathbf1)=\mu_0+\sum_{j=1}^q p_j\mu_j,
\qquad \mu_j=(L^jG_B)(\mathbf1).
\]

La constante `p_0=1` évite un produit supplémentaire. Le lecteur demande
au plus `q` multiplications et `q` additions : **`2q<=n(n-1)` portes**.
L'ensemble du composant ancien devient donc quadratique, constantes
précompilées, après fusion du spectral et de la lecture.

Si `J_q(n)` désigne le coût simultané des observations **depuis `a,z`**,
préparation incluse, la borne de cette implantation est

\[
C_{\mathrm{chaîne}}\le J_q(n)+2q.
\]

Ceci est le recomptage de l'ancienne interface, pas une obligation de
matérialiser ces observations dans le circuit direct de la section 1.
Elles ne sont pas des données gratuites et cette formule ne borne pas
encore `J_q`. Le routage concerne le projecteur complet ; il ne s'applique
pas séparément à chacun des moments intermédiaires.

Les coefficients sont des constantes dépendant seulement de `n,Q`.
Si leur calcul est compté au lieu de les précompiler, les produits de
facteurs linéaires coûtent au plus `q²` opérations de corps. La borne du
composant devient `q²+2q`, toujours polynomiale. Pour le préfixe de degré
`d=|I|`, la préparation de ses coefficients et des deux poids terminaux
peut de même être majorée par `d²+4d+4`, inverses des entiers autorisés
fournis parmi les paramètres. Ces coûts ne dépendent pas de `a,z`.

## 4. Vérification sur le DAG existant

Le compilateur direct a été recompté sans modification, avec `Q=97`.
Les nombres suivants comptent seulement les portes atteignables depuis
les racines concernées. Le partage des sommes de lignes est contrôlé.

| `n` | Préfixe `S_I^(1)` | Chaîne complète | Ajout réel | Borne de l'ajout |
|---:|---:|---:|---:|---:|
| 3 | 43 | 72 | 29 | 29 |
| 4 | 316 | 362 | 46 | 54 |
| 5 | 2 776 | 2 858 | 82 | 87 |
| 6 | 20 278 | 20 394 | 116 | 128 |

Ces comptes vérifient le partage du compilateur ; la preuve générale du
majorant est le décompte de la section 1. Ils ne prouvent pas la
polynomialité de `S_I^(1)` et ne sont pas présentés comme une preuve Lean.

La borne précédente est donc réellement réduite par fusion. La partie
restant à borner est précisément le préfixe direct, sans lui attribuer
le coût d'une représentation par jets abandonnée.

Reproduction du recomptage :

```text
python outils/reproduire.py run recompte-fusion
```

Le rapport `fused-cost-review-validation.json` conserve les empreintes du
vérificateur et du compilateur historique utilisé sans modification. Des
gardes interdisent l'exécution des helpers de jets ou de logarithmes dans
cette vérification du mode direct.
