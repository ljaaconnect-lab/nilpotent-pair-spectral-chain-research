# Existence des déformations : le critère précédent est incompatible avec la séparation dense

Résultat du 2 novembre 2026. Pour la famille de déformations linéaires
d'incidences proposée dans `APPORT_PAPIER_ETH_2026-11-02.md`, on peut
maintenant trancher la question d'existence. Le degré **effectif** de la
sortie, après toutes les annulations, satisfait

\[
\boxed{
\deg_T F\ \ge\ \frac1n\sum_{i=1}^n\deg_T\det P_i
\ \ge\ \frac1n\sum_{t=1}^{L}\sum_{i=1}^n
          \bigl(n-\operatorname{rang}P_i(t)\bigr).
}
\tag{1}
\]

Si chaque facteur est séparé en un groupe de taille au plus s et au
plus μ mesures communes, le modèle précédent impose
rank P_i(t)≤s+μ. On obtient donc

\[
\boxed{\deg_T F\ge L(n-s-\mu).}
\tag{2}
\]

Ainsi, **s+μ<n interdit deg F<L**. Cette obstruction vaut en
caractéristique zéro comme dans les corps finis. Elle porte sur le
degré réel, et renforce le calcul antérieur qui portait seulement
sur le majorant brut nR.

La borne scalaire conditionnelle précédente reste une implication
correcte. En revanche, ses hypothèses favorables ne peuvent pas être
réalisées dans cette famille dense pour toutes les tailles. Ce résultat
ne constitue pas une borne inférieure pour les circuits scalaires
généraux de la chaîne orientée et spectrale.

## Hypothèses exactes

Soit K un corps, n≥2, et P_i(T) une matrice n×n sur K[T] pour chaque
ligne i=1,...,n, avec P_i(0)=I. La ligne j de P_i est la forme de
remplacement P_ij. Les coefficients de ces matrices sont indépendants
des données a,z. Les points t_1,...,t_L sont distincts et non nuls.

La déformation étudiée est précisément

\[
F_B(T)=\sum_{x\in\{0,1\}^n}(-1)^{n-|x|}
\prod_{i=1}^n\left(\sum_{j=1}^n
B_{ij}\sum_{v=1}^n P_i(T)_{jv}x_v\right).
\tag{3}
\]

La séparation est celle du papier : pour chaque facteur, toutes ses
formes de remplacement dépendent linéairement des coordonnées d'un
même groupe et des mesures partagées. Il s'agit de la condition de
noyau sur l'espace vectoriel entier, et pas seulement d'un accord
accidentel sur quelques affectations booléennes.

On exigeait deg F_f<L pour toutes les fréquences, ou de façon équivalente
un degré inférieur à L pour toute la table INTT déformée. Une lecture
qui projette préalablement sur une seule coordonnée est une interface
différente; la preuve ci-dessous ne lui est pas transférée automatiquement.

## 1. Le tenseur exact des coefficients orientés

Dans V=(K^n)^{⊗n}, définissons

\[
\tau=\sum_{\sigma\in\mathfrak S_n}
 e_{\sigma(1)}\otimes\cdots\otimes e_{\sigma(n)}.
\]

Ses coordonnées valent un lorsque tous les indices sont distincts,
et zéro sinon. C'est le tenseur des coefficients conservés par
l'annihilation des collisions, avec la correction universelle du
signe déjà prise en compte.

La somme signée sur x de (3) annule tout monôme auquel manque une
variable. Comme le produit est homogène de degré n en x, les termes
survivants contiennent chaque variable exactement une fois. Par
conséquent, le coefficient de ∏_i B_(i,j_i) est

\[
v_{j_1,\ldots,j_n}(T)=
\sum_{\sigma\in\mathfrak S_n}\prod_i P_i(T)_{j_i,\sigma(i)}.
\]

Le tenseur de tous ces coefficients est exactement

\[
v(T)=\bigl(P_1(T)\otimes\cdots\otimes P_n(T)\bigr)\tau.
\tag{4}
\]

Il n'y a pas de transposition avec cette convention. Posons
h=max_j deg v_j(T). Puisque v(0)=τ≠0, ce degré est bien défini.

Cette écriture sert à démontrer un invariant; elle n'est pas une
représentation intermédiaire que le circuit devrait matérialiser.

## 2. Semi-stabilité du tenseur, dans toute caractéristique

On peut étendre K à sa clôture algébrique sans changer les degrés
ni les rangs. Considérons G=SL_n^n agissant sur V. Dire que τ est
semi-stable signifie que zéro n'appartient pas à l'adhérence de son
orbite sous G.

Pour n≥3, le stabilisateur de τ contient :

- (D,...,D), pour toute matrice diagonale D de déterminant un;
- (Π,...,Π), pour toute permutation paire Π des n coordonnées.

La première assertion vient de ce que chaque terme de τ utilise
toutes les coordonnées : le multiplicateur est det D=1. La seconde
vient de la permutation des termes de la somme.

Dans chaque facteur K^n, un sous-espace invariant sous tout le tore
diagonal est une somme d'axes de coordonnées, les caractères du tore
étant distincts. Le groupe des permutations paires est transitif
pour n≥3. Un sous-espace stable sous les deux actions est donc zéro
ou K^n. Cette irréductibilité vaut aussi en caractéristique positive;
elle ne fait aucune hypothèse de semi-simplicité des groupes finis.

Le résultat externe utilisé est le théorème de Kempf : si un vecteur
non nul est instable, son stabilisateur est contenu dans son
parabolique optimal. Pour un produit de groupes spéciaux linéaires,
ce parabolique est propre et impose un drapeau non trivial dans au
moins un facteur. Cela contredirait l'irréductibilité précédente.
Donc τ est semi-stable.

Les hypothèses de caractéristique et de produit de groupes sont
explicites dans [Derksen–Makam, théorème 4.1(4) et §5.1](https://www.ias.edu/sites/default/files/DerksenMa_Polystability.pdf).
Le même argument est exposé pour des tenseurs à trois facteurs dans
[Christandl–Lysikov–Zuiddam, lemme 23 et appendice A](https://arxiv.org/pdf/2012.14412);
la description des paraboliques produits donne ici les n facteurs.

Pour n=2, τ correspond à la matrice
\(\begin{pmatrix}0&1\\1&0\end{pmatrix}\).
Son déterminant est non nul dans tout corps et invariant sous
SL_2×SL_2. Cela donne directement la semi-stabilité dans ce cas.

## 3. Une borne sur le degré effectif, sans recours à la norme

La semi-stabilité assure l'existence d'un invariant homogène I de
degré D>0 tel que I(τ)≠0. La relation entre le cône nul et les
invariants est rappelée dans le théorème 2.3 et les définitions 2.2,
2.5 de Derksen–Makam. L'invariant n'est utilisé qu'à titre de preuve;
aucun algorithme de construction ni aucune borne sur D n'est supposé.

Dans une clôture algébrique de K(T), choisissons α_i tel que
α_i^n=det P_i(T). Les déterminants sont non nuls puisqu'ils valent
un en zéro. Les matrices α_i^(−1)P_i sont dans SL_n. Par homogénéité
et invariance,

\[
I(v(T))=\left(\prod_i\alpha_i\right)^D I(\tau).
\]

En élevant à la puissance n, on obtient une identité polynomiale :

\[
\boxed{
I(v(T))^n=I(\tau)^n\left(\prod_i\det P_i(T)\right)^D.
}
\tag{5}
\]

Cette forme ne demande ni de diviser D par n ni de supposer que la
caractéristique ne divise pas n. Son membre droit est non nul.
Comme I est homogène de degré D et les coordonnées de v de degré
au plus h,

\[
\deg I(v(T))\le Dh.
\]

Prendre les degrés dans (5), puis annuler l'entier positif D, donne

\[
\boxed{nh\ge\sum_i\deg\det P_i(T).}
\tag{6}
\]

C'est ici que l'on contrôle le degré **après toutes les annulations**.
Le raisonnement ne remplace jamais h par nR.

## 4. Les points séparateurs imposent des multiplicités

Fixons i et un point t de rang r=rank P_i(t). Des opérations de
lignes constantes inversibles rendent les n−r dernières lignes
nulles en t. Chaque entrée de ces lignes est divisible par T−t.
En factorisant dans le déterminant, on obtient

\[
(T-t)^{n-r}\mid\det P_i(T).
\]

Les facteurs correspondant aux points distincts sont premiers entre
eux. Puisque le déterminant est non nul,

\[
\deg\det P_i(T)\ge
\sum_{a=1}^L\bigl(n-\operatorname{rank}P_i(t_a)\bigr).
\tag{7}
\]

Les inégalités (6) et (7) prouvent (1). Au point t_a, la condition de
noyau du design place toutes les lignes de P_i(t_a) dans la somme
de l'espace des s coordonnées locales et des espaces engendrés par
les μ mesures. Sa dimension est au plus s+μ. On obtient (2).

Si les points sont 1,...,L dans F_p et p≤L, un point est déjà égal
à zéro. La condition rank P_i(t)≤s+μ<n contredit alors P_i(0)=I.
Si p>L, les points sont distincts et non nuls, et la preuve ci-dessus
s'applique. Changer de corps ne supprime donc pas l'obstruction.

## 5. Le résultat subsiste avec les entrées originales et l'INTT

Prenons les marqueurs originaux

\[
B_{ij}=(1+a_{ij}^2)z^{2^{(i-1)n+j-1}}.
\]

Dans F_B(T), le coefficient du monôme en a
\(\prod_i a_{i,j_i}^2\) provient d'un seul tuple (j_1,...,j_n).
Il est égal à v_j(T), multiplié par une puissance non nulle de z.
Cela démontre

\[
\deg_T F_{B(a,z)}=\max_j\deg_T v_j=h.
\tag{8}
\]

Il s'agit d'une identité de polynômes formels. On ne réduit aucun
exposant de z, ni les variables a, modulo des identités de fonctions
sur le corps fini.

Dans le corps de l'architecture spectrale, N est inversible et ω
est d'ordre N; la condition p=cN+1 assure cette compatibilité.
À fréquence f, chaque coefficient v_j est multiplié par la constante
non nulle ω^(fΣ_i d_(j_i)); son degré reste inchangé. L'INTT est une
matrice constante inversible. Le vecteur de coefficients de degré h
reste non nul après cette transformation. Donc

\[
\max_k\deg_T H_k=\max_f\deg_T F_f=h.
\tag{9}
\]

L'orientation et le spectral sont donc tous deux pris en compte
dans cette preuve. Aucune amplitude P_A n'est imposée en entrée.

## 6. Conséquence pour l'existence demandée

Après retrait des mesures nulles, on peut prendre Δ≥1 lorsqu'il
reste des mesures. Les conditions de coût précédentes impliquent

\[
s\le b\log_2 n,\qquad
\mu\log_2(2\Delta+1)\le h_0\log_2 n,
\]

et donc s+μ≤(b+h_0)log₂n. Pour des constantes fixes b,h_0, cela
est strictement inférieur à n lorsque n est assez grand. Par (2),

\[
\deg_T F\ge L(n-s-\mu)\ge L,
\]

en contradiction avec la condition de degré exigée dans le critère
proposé, deg F<L. Cette contradiction ne dépend même pas d'une borne
polynomiale sur L. Ajouter des points en conservant ces conditions
de séparation ne suffit pas.

**Conclusion d'existence :** il n'existe pas de famille générale de
ces matrices de remplacement indépendantes des données satisfaisant
simultanément la séparation favorable et le petit degré de toute
la table exigé dans la note précédente.

## 7. La borne est atteinte par une famille explicite

Fixons 1≤r<n. Pour des points distincts non nuls, posons

\[
\rho(T)=\prod_{a=1}^L(1-T/t_a),\qquad
P_i(T)=\operatorname{diag}
(\underbrace{\rho,\ldots,\rho}_{n-r},
 \underbrace{1,\ldots,1}_{r})\quad\text{pour tout }i.
\]

Alors P_i(0)=I, rank P_i(t_a)=r et, puisque chaque terme orienté
utilise chaque coordonnée exactement une fois,

\[
v(T)=\rho(T)^{n-r}\tau,
\qquad \deg_T v=L(n-r).
\]

La borne est donc exacte dans cette famille. Aux points de lecture,
les facteurs peuvent tous être rattachés au groupe des r dernières
variables, sans mesure partagée; les autres groupes n'ont que le
signe local. Le coût des valeurs est faible, mais ces valeurs sont
nulles et ne reconstruisent pas la sortie originale par petit degré.

## Portée et suite du projet

Cette preuve ferme **la proposition précise de la note précédente**.
Elle ne conclut pas à l'impossibilité d'un circuit scalaire polynomial
pour la sortie originale. Elle n'impose pas un calcul préalable de
P_A et ne change pas l'objectif du projet.

Elle n'exclut pas, sans argument supplémentaire :

- une projection sur le seul slot utile AVANT la reconstruction;
- des déformations non linéaires ou dépendant des données;
- une lecture exploitant une autre identité que deg F<L;
- une séparation qui ne satisfait pas la condition linéaire de noyau
  du design étudié.

Ces variantes demandent leur propre construction et leur propre
preuve de coût. Aucun résultat polynomial général n'est revendiqué
pour elles ici.

En particulier, deg F<L était une condition suffisante pour la
lecture par valeurs, pas une condition nécessaire à cette identité
pour chaque polynôme particulier. La preuve ne réfute donc pas
toutes les lectures par valeurs de polynômes de degré supérieur.

### Un cas exact où projeter le slot avant reconstruction change le degré

La réserve sur la projection n'est pas seulement formelle. Pour n=2,
N=2, d=(0,1), k*=1 et en caractéristique différente de deux, posons

\[
g(T)=3T-2T^2,\qquad
P_1(T)=\begin{pmatrix}1&0\\g(T)&1-T\end{pmatrix},\qquad
P_2(T)=\begin{pmatrix}(1-T)(1+2T)&T\\0&1\end{pmatrix}.
\]

Les deux matrices valent I en zéro. En T=1, la première utilise
uniquement x_0 et la seconde uniquement x_1 : deux groupes de taille
un, sans aucune mesure partagée. Pourtant, si
J=\(\begin{pmatrix}0&1\\1&0\end{pmatrix}\), un calcul exact donne

\[
P_1(T)J P_2(T)^\top=
\begin{pmatrix}T&1\\1&g(T)\end{pmatrix}.
\]

L'INTT place alors les deux coordonnées dans

\[
H_0(T)=T B_{00}B_{10}+g(T)B_{01}B_{11},\qquad
H_1(T)=B_{00}B_{11}+B_{01}B_{10}.
\]

La table entière a degré deux, conformément à la barrière. Le slot
utile H_1 a degré zéro. Avec L=1, H_1(0)=H_1(1); le slot H_0(0)=0
est connu par l'architecture et peut être émis directement. Au point
de calcul, les fréquences sont les deux produits de sommes de lignes
(B_00±B_01)(B_10±B_11), calculés depuis B. Aucune amplitude n'est
fournie en entrée.

Cela donne une construction positive exacte pour n=2 avec la
projection préalable. L'existence générale de cette variante n'est
pas établie, et la nouvelle preuve de non-existence pour la table
déformée entière ne doit pas lui être attribuée.

## Vérifications

Le théorème général ci-dessus est une preuve écrite, avec relectures
mathématiques indépendantes et les résultats externes identifiés.
Il n'est pas entièrement formalisé dans Lean.

Les tests `deformations-existence-2026-11-02/check_degree_barrier.py`
contrôlent 162 cas exacts sur F_5, F_7 et F_97 : 54 cas atteignant la
borne, 108 cas avec cisaillements unimodulaires, 1 080 contrôles de
rang, 540 déterminants formels et 22 302 coordonnées tensorielles.
Dans 141 cas, le degré effectif est strictement inférieur au majorant
brut tout en respectant (2). Neuf cas spectraux vérifient également
le degré maximal après INTT. Les développements exponentiels sont
uniquement des oracles de test sur de petites tailles.

Le sous-dossier `deformations-existence-2026-11-02/lean/` contient
la formalisation locale du transfert de degré à partir de (5), et
la contradiction arithmétique finale, avec rapport et script de
rejeu. Les trois théorèmes ont passé le contrôle Lean 4.34.1 sans
`sorry`, sans avertissement et sans axiome supplémentaire; le statut
exact est consigné dans `validation.json`.
La semi-stabilité de τ, le théorème de Kempf et les multiplicités
matricielles de (7) restent des preuves écrites, pas des hypothèses
dissimulées dans un certificat Lean du théorème complet.

Le script `deformations-existence-2026-11-02/single_slot_example.py`
vérifie séparément le cas n=2 de projection préalable, avec son
rapport `single-slot-validation.json`. Il ne revendique aucune
généralisation à toutes les tailles.
