# Insertion complète : identité générale et coût scalaire

**La fermeture polynomiale générale demandée n’est pas démontrée.**
La présente construction remplace cependant les correcteurs tronqués par
une loi exacte à tout ordre, avec une compilation explicite de son action
en portes scalaires. Le coût de cette compilation conserve un majorant
exponentiel. Aucun opérateur n’est assimilé à une porte scalaire gratuite.

## 1. L’opérateur et la preuve à tout ordre

Soit \(K\langle X_0,\ldots,X_{n-1}\rangle\) l’algèbre associative libre.
On définit la dérivation \(\delta_j\) par

\[
\delta_j(1)=0,\qquad \delta_j(X_k)=X_jX_k,\qquad
\delta_j(FG)=\delta_j(F)G+F\delta_j(G).
\]

Le nouvel opérateur est

\[
\boxed{\mathcal I_j(F)=\delta_j(F)+FX_j.}
\]

Sur un mot, il insère \(X_j\) à **toutes** les positions :

\[
\mathcal I_j(X_{i_1}\cdots X_{i_r})=
 \sum_{p=0}^{r}X_{i_1}\cdots X_{i_p}X_jX_{i_{p+1}}\cdots X_{i_r}.
\]

**Théorème.** Pour tous \(i,j\), à tout degré,
\(\mathcal I_i\mathcal I_j=\mathcal I_j\mathcal I_i\).

**Preuve.** Notons \(L_x\) l’ajout de la lettre \(x\) à gauche.
La définition donne
\(\mathcal I_aL_x=L_aL_x+L_x\mathcal I_a\).
En développant \(\mathcal I_a\mathcal I_bL_x\) puis
\(\mathcal I_b\mathcal I_aL_x\), les quatre termes de bord sont les
mêmes, à permutation de la somme près. Leur différence est donc
\(L_x(\mathcal I_a\mathcal I_b-\mathcal I_b\mathcal I_a)\).
Sur le mot vide, les deux insertions donnent les mêmes deux mots, avec
leurs multiplicités. L’induction sur la longueur prouve le résultat.

Cette induction, son extension aux polynômes à coefficients naturels,
l’identité \(\mathcal I_j=\delta_j+R_{X_j}\) et la règle du produit pour
\(\delta_j\) sont vérifiées dans `Insertion.lean`.

**Corollaire exact, sans troncature en ordre :**

\[
\boxed{F_n=\mathcal I_{n-1}\cdots\mathcal I_0(1)
 =\sum_{\sigma\in S_n}X_{\sigma(0)}\cdots X_{\sigma(n-1)}.}
\]

En effet, insérer une lettre nouvelle dans toutes les positions d’un mot
qui ne la contient pas donne chaque permutation une fois : sa position
permet de retrouver de façon unique le mot précédent. L’induction construit
donc tous les mots bijectifs avec coefficient un, sans mot ayant une colonne
répétée. Ce corollaire et le raccord ci-dessous sont démontrés ici sur le
plan mathématique ; le compilateur Python n’est pas intégralement formalisé
dans Lean.

## 2. Raccord à toute la chaîne orientée et spectrale

À chaque fréquence, on évalue les générateurs sur les horloges

\[
X_j\longmapsto A_j[f]=\omega^{fd_j}\sum_{i=0}^{n-1}
 (1+a_{ij}^2)z^{2^{in+j}}E_{i+1,i}.
\]

Dans un produit de longueur \(n\), l’entrée \((n,0)\) force les lignes
successives de l’horloge. Les permutations des générateurs donnent donc
exactement les affectations bijectives de colonnes aux lignes. Leur phase
est \(\omega^{f\sum_jd_j}\), et leurs amplitudes et marqueurs sont ceux du
papier, sans carré supplémentaire des poids.

La sortie complète est

\[
\boxed{\mathcal Z[k]=\widetilde\Omega\,
 \operatorname{INTT}_N\big[(\operatorname{ev}_f(F_n)_{n,0})_f\big][k].}
\]

La correction universelle est incluse par
\(\gamma_n q_{[n]}=\widetilde\Omega\).
L’orthogonalité des caractères concentre la sortie au canal
\(\sum_jd_j\bmod N\). Il n’existe aucune entrée \(P_A\) dans le circuit.
Les phases figurent dans les générateurs évalués, avant les fusions.

On peut aussi utiliser Newton dans l’algèbre commutative engendrée par les
\(\mathcal I_j\) :

\[
V_0=1,\qquad rV_r=\sum_{k=1}^r(-1)^{k-1}
 \sum_j\mathcal I_j^k(V_{r-k}).
\]

Cette identité découle de la dérivée formelle de
\(\prod_j(1+t\mathcal I_j)\). Pour \(r=n\), \(V_n=F_n\).
Le code `insertion_circuit.py` implémente aussi cette récurrence, mais
`circuit.py` retient la succession directe, beaucoup plus petite dans les
essais. Aucune de ces deux traductions n’apporte la borne polynomiale.

## 3. Compilation scalaire effective

La dérivation agit sur chaque nœud d’un DAG non commutatif par les règles
explicites ci-dessus. Les dérivées déjà construites sont partagées par
mémoïsation. Les nœuds créés et ceux réellement utilisés sont comptés
séparément. Aucune liste de colonnes déjà utilisées n’est un état du circuit.

Pour une expression homogène de degré \(r\), son évaluation sur les horloges
est stockée dans la bande
\(x_s=X_{s+r,s}\), \(0\le s\le n-r\). Les bandes se multiplient par

\[
(xy)_s=x_{s+b}y_s\quad
 \text{si les degrés de }x,y\text{ sont }a,b.
\]

Chaque addition, produit ou multiplication par une constante sur ces bandes
devient au plus \(n+1\) portes scalaires. Les marqueurs sont construits par
\(n^2-1\) carrés successifs ; les poids sont préparés depuis les entrées
originales \(a_{ij}\). L’INTT est compilée par papillons scalaires.

**Borne actuellement justifiée.** Si \(S_r\) est le nombre de nœuds déjà
créés avant une insertion, la construction d’une dérivée crée au plus trois
nœuds par ancien nœud, puis l’insertion ajoute au plus deux nœuds. Ainsi
\(S_{r+1}\le4S_r+2\), avec \(S_0=n+2\).
Cela fournit le majorant explicite
\(S_n\le(n+3)4^n\), et un majorant
\(O(Nn(n+3)4^n+n^2+N\log N)\) pour les portes scalaires.
Cette estimation **ne prouve pas** qu’une meilleure implantation générale
est impossible ; elle ne donne pas la fermeture polynomiale demandée.

Le rapport `validation.json` donne les tailles réellement émises :

| n | nœuds opérateurs utilisés | portes scalaires de toute la chaîne |
|---:|---:|---:|
| 4 | 55 | 932 |
| 5 | 175 | 3 212 |
| 6 | 549 | 11 332 |
| 7 | 1 701 | 39 677 |
| 8 | 5 219 | 272 376 |

Ces valeurs correspondent aux étiquettes spectrales du rapport. Les
constantes de phase peuvent modifier légèrement les comptes. Il y a
16 tables numériques vérifiées jusqu’à `n=8`, et 5 tables avec `z` formel
jusqu’à `n=5`. La référence par permutations est utilisée exclusivement
pour les tests ; le compilateur ne l’appelle pas.

## 4. Autre identité générale obtenue

Pour une partition \(\pi:P\to B\) des positions d’un chemin d’horloge,

\[
\sum_{f:B\to J}\prod_{p\in P}a_{p,f(\pi(p))}
 =\prod_{b\in B}\sum_{j\in J}\prod_{p:\pi(p)=b}a_{p,j}.
\]

Cette égalité est prouvée pour tous ensembles finis dans
`ClockContraction.lean`. Pour une partition en blocs non vides, avec
\(r\ge1\) positions et \(q\ge1\) colonnes, le membre droit se calcule avec
\(qr-1\) additions et multiplications : les produits internes coûtent
\(q(r-|B|)\), les sommes \(|B|(q-1)\), et le produit final \(|B|-1\).
Le nombre de blocs répétés n’impose donc pas, à lui seul, autant de boucles
imbriquées sur les colonnes.

En particulier, une famille avec \(m\) colonnes formelles répétées deux fois
dans le même ordre se contracte par
\(\prod_{i=0}^{m-1}\sum_j a_{i,j}a_{m+i,j}\), à tout ordre.
L’évaluation d’un diagramme est désormais polynomiale ; la sommation ou la
compression de tous les diagrammes nécessaires reste à établir.

## 5. Portée de la livraison

Les six lemmes généraux des deux fichiers Lean sont compilés sans `sorry`
ni axiome ajouté. `lean-validation.json` conserve les sorties du compilateur
et les empreintes exactes. Le corollaire de permutations, Newton, le raccord
à la chaîne et le majorant de coût sont des démonstrations mathématiques
exposées ci-dessus, avec un compilateur testé séparément.

L’assertion encore manquante est une **borne polynomiale uniforme du coût
scalaire de l’action et de la fusion**. Elle n’est ni supposée dans une
preuve Lean, ni déduite des vérifications à des ordres finis. Il ne s’agit
donc pas de la démonstration générale de fermeture polynomiale demandée.

```powershell
python -B verifier.py --write-report
python -B replay_lean.py --write-report
```
