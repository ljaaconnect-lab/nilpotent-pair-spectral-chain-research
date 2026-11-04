# Double logarithme formel du raccord existant

Le double logarithme admet une transformation exacte, un retour de coût
polynomial sur les coefficients déjà calculés et le même élagage que le
logarithme simple. Ces résultats ne donnent pas une borne polynomiale
pour les dérivées successives du circuit. Le présent fichier démontre
les identités et leur portée, sans traiter `log` ou `exp` comme des portes.

## 1. Domaine et normalisation

On travaille dans

\[
R=\mathbb F_Q[a,z,s_1,\ldots,s_n][\varepsilon]/(\varepsilon^{n+1}),
\qquad J=\varepsilon R,
\]

avec Q premier, Q>max(2,binom(n,2)). Les entiers de 1 à n sont donc
inversibles. Pour X dans J, log(1+X) et exp(X) sont leurs séries
tronquées ; elles sont des polynômes de degré au plus n. Aucune division
par une donnée n'est nécessaire.

La chaîne conservée est

\[
H_0=\prod_i[1+\varepsilon(\ell_i(s)-1)],\qquad
H_r=(I-L/r)H_{r-1},\qquad
L=\tfrac12\sum_j(D_j^2-D_j),\quad D_j=s_j\partial_{s_j}.
\]

Chaque H_r est dans 1+J. On définit

\[
U=\log H\in J,\qquad W=\log(1+U)\in J.
\]

Le choix `log U` ne convient pas : U a une constante nulle. Le double
logarithme normalisé ci-dessus a les inverses exacts

\[
U=\exp W-1,\qquad H=\exp(\exp W-1).
\]

## 2. Conjugaison exacte de l'opérateur

Pour une série scalaire f et W dans J, la règle de la chaîne donne

\[
L(f(W))=f'(W)LW+\tfrac12 f''(W)\Gamma(W),
\qquad \Gamma(W)=\sum_j(D_jW)^2.
\]

Cette formule utilise D_j²(f(W))=f'(W)D_j²W+f''(W)(D_jW)²
et le terme -D_j de L. Posons

\[
A(U)=LU+\tfrac12\Gamma(U),\qquad E=\exp W.
\]

Comme U=E-1,

\[
LU=E\,LW+\tfrac12 E\Gamma(W),\qquad
\Gamma(U)=E^2\Gamma(W).
\]

On obtient donc

\[
\boxed{A(\exp W-1)=E\,LW+\tfrac12(E+E^2)\Gamma(W)=E\,B(W)},
\]

où l'expression factorisée utile pour le circuit est

\[
\boxed{B(W)=LW+\tfrac12(1+E)\Gamma(W).}
\]

Un seul calcul de E peut être partagé dans ces expressions. Il n'est
pas nécessaire de former E² puis de le diviser par E.

## 3. Mise à jour du double logarithme

La mise à jour logarithmique existante est

\[
U'=U+\log(1-A(U)/r).
\]

En écrivant 1+U'=E+log(1-EB(W)/r), puis en factorisant E,

\[
\boxed{
W'=W+\log\left(1+E^{-1}\log\left(1-\frac{E B(W)}r\right)\right).
}
\]

Ici E^{-1}=exp(-W) est une série à constante 1. L'expression est
définie pour toutes les données admises, y compris une somme de ligne
nulle. Le retour vérifie exactement

\[
\exp(\exp W'-1)=(I-L/r)\exp(\exp W-1).
\]

Pour un bloc de facteurs P(L)=prod_{r dans bloc}(I-L/r), la fusion
algébrique correspondante est

\[
R_P=\frac{P(L)H}{H}\in1+J,\qquad
W_P=W+\log(1+E^{-1}\log R_P).
\]

Cette identité permet de partager le changement de coordonnées autour
d'un bloc. Elle ne construit pas le numérateur P(L)H à coût polynomial :
ce calcul reste à fournir. Le quotient par H est seulement l'inverse
d'une série de constante 1 et peut être calculé en O(n²) portes à partir
de ses coefficients disponibles.

## 4. Transport de l'élagage et simplification tardive

On a deg_s([epsilon^k]H_r)<=k. L agit sur s^m par la valeur
kappa(m)=sum_j binom(m_j,2), comprise entre 0 et binom(k,2) si
|m|<=k. Après les facteurs 1 à binom(k,2), le coefficient d'ordre k
est dans le noyau de L et ne change plus.

Le coefficient d'ordre k de W dépend seulement des coefficients
d'ordre au plus k de H. Il se stabilise donc lui aussi après
binom(k,2) facteurs. Au facteur r, soit

\[
m_r=\min\{k:\binom{k}{2}\ge r\}.
\]

On a v_epsilon(A(U))>=m_r, puis v_epsilon(B(W))>=m_r, car E est une
unité. Si 2m_r>n, tous les carrés du correctif sont nuls dans R :

\[
\log(1-EB/r)=-EB/r,
\qquad \log(1-E^{-1}EB/r)=-B/r.
\]

Ainsi la mise à jour se réduit exactement à

\[
\boxed{W'=W-B(W)/r\quad\text{si }2m_r>n.}
\]

Cela supprime les deux logarithmes de cette étape. Les coefficients de
LW et Gamma(W), nécessaires à B(W), doivent toujours être calculés.
Le nombre total de mises à jour actives de coefficients est conservé :
sum_{k=2}^n binom(k,2)=binom(n+1,3). Il ne constitue pas à lui seul
un décompte des portes de dérivation.

## 5. Coût des changements de coordonnées

Écrivons U=sum_{k=1}^n u_k epsilon^k et W=sum_{k=1}^n w_k epsilon^k.
L'identité (1+U)W'=U', où la dérivation porte ici sur epsilon,
donne la récurrence triangulaire

\[
w_k=u_k-\frac1k\sum_{i=1}^{k-1}i w_i u_{k-i}.
\]

Dans l'autre sens, pour E=exp W=sum e_k epsilon^k,

\[
e_0=1,\qquad e_k=\frac1k\sum_{i=1}^{k}i w_i e_{k-i},\qquad u_k=e_k\ (k>0).
\]

Chacune de ces récurrences demande au plus 4n² portes scalaires
(une multiplication par une constante est comptée). Le majorant est
volontairement simple. Les deux exponentielles du retour H=exp(exp W-1)
demandent donc au plus 8n² portes quand les n coefficients de W sont
disponibles. La lecture epsilon=1 ajoute au plus n additions.

Par conséquent, pour le calcul de *tous les coefficients* à une phase
spectrale fixée, les trois représentations H, U et W ont des tailles de
circuit équivalentes à un surcoût O(n²) près. L'équivalence vaut aussi
pour leurs coefficients symboliques en s. Elle n'exige pas de stocker
un développement en monômes de s.

Cette équivalence laisse possible une découverte de partages plus
efficaces dans les coordonnées W. Elle montre précisément ce que le
double logarithme ne fournit pas à lui seul : il transforme les
coefficients par une application triangulaire inversible, sans borne
nouvelle sur les circuits qui doivent les produire et les dériver.

Avec la méthode de dérivation partagée déjà disponible, on conserve
un majorant de la forme

\[
S_r\le(9n+1)S_{r-1}+C n^3
\]

pour une constante absolue C : les dérivées premières et secondes
coûtent au plus 9n fois le DAG de départ, et les convolutions de séries
ainsi que les changements de coordonnées ajoutent O(n³). Ce calcul
donne encore 2^{O(n² log n)} ; il ne donne ni une minoration ni une
impossibilité d'amélioration.

## 6. Quelle transformation scalaire supprime le terme quadratique ?

On peut répondre exactement à cette question restreinte. Prenons une
coordonnée V avec U=psi(V), psi(0)=0, psi'(0)=1. Alors

\[
A(psi(V))=psi'(V)LV+
\tfrac12[psi''(V)+psi'(V)^2]\Gamma(V).
\]

Le coefficient quadratique s'annule identiquement si et seulement si

\[
psi''+psi'^2=0.
\]

En posant F=exp psi, cela équivaut à F''=0. Les deux conditions
initiales donnent F(V)=1+V, donc

\[
psi(V)=\log(1+V),\qquad V=\exp U-1=H-1.
\]

La normalisation qui supprime ce terme revient donc exactement à la
coordonnée linéaire initiale H-1. Dans le double logarithme étudié,
psi(W)=exp W-1 et psi''+psi'^2=exp W+exp(2W) : les deux contributions
s'additionnent. Cette classification concerne uniquement les
changements scalaires point par point ; elle ne dit rien d'une fusion
plus riche entre opérateurs, données et fréquences.

## 7. Vérification indépendante exécutée

Un calcul indépendant sur dictionnaires de polynômes en
(epsilon,s_1,s_2), modulo 97 et epsilon^6, a vérifié :

- la conjugaison A(exp W-1)=exp(W)B(W) ;
- l'inversion log(1+exp W-1)=W ;
- la mise à jour double logarithme ;
- le retour au facteur original (I-L/r)H.

Les six entrées symboliques utilisées sont, pour c=1,...,6,

\[
W_c=\varepsilon(cs_1+(c+1)s_2)
+\varepsilon^2(2cs_1^2+3s_1s_2)
+\varepsilon^3(c+2)s_1s_2^2+5\varepsilon^4s_1^3s_2.
\]

Les cinq facteurs testés sont r dans {1,2,3,7,10}, soit 30 mises à
jour complètes. Les quatre identités passent pour chaque cas. Cette
vérification exacte finie est distincte des preuves générales données
ci-dessus et ne certifie aucune borne asymptotique. Aucun énoncé de ce
fichier n'est présenté comme vérifié par Lean.
