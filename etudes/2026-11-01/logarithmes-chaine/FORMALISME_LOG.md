# Logarithmes formels du raccord existant

Cette note introduit des logarithmes dans le circuit lui-même, et non
seulement dans son majorant de taille. Elle conserve exactement la source
`G_B`, les facteurs `I-L/r` et l'INTT. Les identités ci-dessous donnent une
compilation scalaire exacte; elles ne démontrent pas une taille générale
polynomiale ou quasi-polynomiale.

## 1. Un logarithme défini pour toutes les données

On travaille sur un corps de caractéristique Q avec les paramètres déjà
admissibles : Q est premier, Q>max(2,h), h=n(n-1)/2. Les entiers 1,...,n
sont alors inversibles. En effet, h>=n pour n>=3 et les deux petits cas
sont couverts par Q>2. Les dénominateurs du logarithme et de l'exponentielle
tronqués n'ajoutent donc pas de restriction effective au cadre actuel.

Posons ell_i(s)=sum_j B_ij s_j et delta_i=ell_i-1. La normalisation

    H_0(epsilon,s) = product_i (1+epsilon delta_i(s))

a une constante en epsilon égale à 1, même si une ligne ou une somme de
ligne est nulle. Dans R=F_Q[s][epsilon]/(epsilon^(n+1)), on peut définir

    U_0 = log H_0
        = sum_i sum_(k=1)^n (-1)^(k+1) epsilon^k delta_i^k / k.

Il ne s'agit ni d'un logarithme réel, ni d'un logarithme discret, ni d'une
nouvelle porte gratuite : chaque somme et chaque puissance est un circuit
fini d'additions et de multiplications. Avec partage des puissances de
delta_i et la préparation B_ij=(1+a_ij^2)z^(2^(in+j)), un majorant simple
de préparation est 9n^2 portes.

La source originale est H_0(1,s)=G_B(s). Le paramètre epsilon sert seulement
à autoriser une transformation algébrique sans division par les données.

## 2. Conjugaison exacte de L

Écrivons D_j=s_j partial_j et

    L = (1/2) sum_j (D_j^2-D_j).

Pour U de constante en epsilon nulle, et F quelconque dans R, les règles
de dérivation du produit donnent

    exp(-U) L(exp(U) F)
      = L F + sum_j (D_j U)(D_j F) + A(U) F,

    A(U) = L U + (1/2) sum_j (D_j U)^2.                  (1)

Preuve : D_j exp(U)=exp(U)D_j U. Une seconde dérivation donne
D_j^2 exp(U)=exp(U)((D_j U)^2+D_j^2 U). L'application de
D_j^2-D_j au produit exp(U)F donne ensuite (1), terme par terme.
Ces identités restent exactes après troncature, puisque les dérivations
agissent sur s et conservent le degré en epsilon.

En particulier, le lecteur existant s'exprime exactement par

    U_r = U_(r-1) + log(1-A(U_(r-1))/r),  1<=r<=h.       (2)

En effet, si H_(r-1)=exp(U_(r-1)), alors

    (I-L/r)H_(r-1)
      = exp(U_(r-1))(1-A(U_(r-1))/r)
      = exp(U_r).

Le terme constant en epsilon de chaque H_r reste 1; chaque logarithme de
(2) est donc défini. Son terme d'ordre 1 reste celui de U_0, une fonction
affine de s. Ainsi A(U_r) commence à epsilon^2. Le développement direct
du logarithme correctif nécessite au plus floor(n/2) puissances de A.

## 3. Évaluation scalaire des logarithmes et de l'exponentielle

On peut faire mieux qu'une suite de produits de séries pour calculer log.
Si v_0=0 et c=log(1+v), la relation (1+v)c'=v', où la dérivation porte
ici sur epsilon, donne

    c_0 = 0,
    c_k = v_k - (1/k) sum_(i=1)^(k-1) i c_i v_(k-i).     (3)

Elle utilise O(n^2) portes scalaires pour les coefficients jusqu'à n.
Dans (2), v=-A(U)/r et v_1=0; les termes nuls peuvent être omis.

La lecture finale utilise aussi une récurrence quadratique. Pour E=exp U,

    E_0 = 1,
    E_k = (1/k) sum_(i=1)^k i U_i E_(k-i).               (4)

L'identité exp(U_h)=H_h dans l'anneau tronqué fournit tous les coefficients
de H_h : l'opérateur L n'agit pas sur epsilon et H_0 a degré au plus n
en epsilon. Par conséquent

    sum_(k=0)^n E_k(s) = H_h(1,s) = pi_n(L)G_B(s).       (5)

On substitue ensuite s_j=omega^(f d_j) et on applique l'INTT existante.
La correction universelle reste incluse dans le facteur Omega_tilde.

La justification de (5) utilise le degré de H_h. On ne substitue pas
epsilon=1 dans un logarithme tronqué en prétendant que cette substitution
est un morphisme de l'anneau quotient : une telle substitution n'est pas
définie comme morphisme lorsque epsilon^(n+1)=0.

## 4. Stabilisation triangulaire réellement démontrée

Pour tout k<=n, le coefficient [epsilon^k]H_0 est de degré au plus k en s.
Sur un monôme s^m de degré au plus k, L a la valeur propre

    kappa(m) = sum_j binom(m_j,2),
    0 <= kappa(m) <= h_k = binom(k,2).

Les facteurs 1-L/r, r=1,...,h_k, annulent donc toutes les valeurs propres
positives de ce coefficient. Une fois r>=h_k,

    [epsilon^k]H_r = [epsilon^k]H_(h_k).

Le coefficient [epsilon^k]log H dépend uniquement des coefficients de H
jusqu'à k. Tous ces derniers ont stabilisé avant h_k. On en déduit

    [epsilon^k]U_r = [epsilon^k]U_(h_k)  pour r>=h_k.     (6)

Au facteur r, les coefficients U_k tels que r>h_k peuvent donc être
conservés sans nouvelle mise à jour. Le facteur r=h_k doit encore être
exécuté. Le nombre total de couples (facteur,coefficient) actifs est

    sum_(k=2)^n h_k = binom(n+1,3).

On peut également mettre directement A(U_(r-1))_k à zéro lorsque r>h_k.
En effet, à ce stade tous les coefficients de L H_(r-1) jusqu'au degré
k en epsilon sont nuls. Or A(U_(r-1))=H_(r-1)^(-1)L H_(r-1), et
l'inverse a une constante égale à 1 et aucune puissance négative. Le
produit a donc lui aussi ses coefficients d'ordres <=k nuls. Il s'agit
d'une identité avant toute évaluation des données, et non d'un test de
nullité effectué à partir d'une instance numérique.

C'est une amélioration exacte du nombre de mises à jour. Elle ne borne pas
encore le coût des circuits qui produisent leurs dérivées.

## 5. Le coût restant après introduction des logarithmes

Soit S la taille du DAG partagé produisant tous les coefficients U_k(s).
Pour une variable s_j, une traduction partagée des dérivées premières et
secondes ajoute au plus 9S portes; les n variables coûtent donc au plus
9nS. Les produits de séries dans A(U), exécutés coefficient par coefficient,
coûtent O(n^3) portes, et (3) coûte O(n^2). Il en résulte un majorant de
passe

    S_r <= (9n+1) S_(r-1) + C(n+1)^3                     (7)

pour une constante absolue C. Les économies de (6) peuvent réduire ce
compte mais ne justifient pas de remplacer le coefficient de S par 1.
En itérant (7), la borne obtenue reste de type n^(O(n^2)). Le logarithme
a rendu le produit initial additif et a donné des lectures et corrections
de séries quadratiques; il n'a pas supprimé le coût des dérivations
successives de leurs coefficients dépendant de s.

En particulier, conserver seulement les n valeurs U_k(t) ne ferme pas
(1) : il faut aussi les dérivées de ces coefficients au point t. Conserver
leur gradient et leur diagonale hessienne permet une passe; leur prochaine
mise à jour fait intervenir des dérivées d'ordres supérieurs. Ce constat
porte sur cette interface locale, pas sur l'impossibilité d'un autre partage.

Une représentation par tous les jets de polynômes de degré au plus n
autour de t donne bien un majorant fini. Elle a binom(2n,n) coordonnées
pour H. Dans ces coordonnées, chaque application de L utilise O(n)
termes par coordonnée. La préparation du produit, les h applications du
lecteur et les N=O(n) fréquences donnent donc un majorant
poly(n) binom(2n,n)=2^(O(n)) pour un compilateur auxiliaire. Ce gain sur
le majorant très lâche n^(O(n^2)) vient du degré borné et d'une table de
jets; il ne vient pas du logarithme et n'est pas une fermeture polynomiale.
La table n'est pas imposée comme représentation recherchée.

## 6. Vérification indépendante des identités

Une exécution indépendante avec Sympy 1.14.0 sur les rationnels a vérifié
exactement les identités (2), (3) et (4), facteur par facteur, pour n=1,...,4.
Pour chaque taille, trois matrices entières ont été utilisées : une matrice
générique, une matrice avec une ligne nulle, et, pour n>1, une matrice dont
la première ligne a une somme nulle. Les coefficients ont été développés
comme polynômes en s et comparés exactement.

Résultat : 12 cas, 30 comparaisons exp(U_r)=H_r, aucune différence.
Cette vérification ne compte aucune porte, ne formalise pas la complexité
dans Lean et ne remplace pas les preuves algébriques ci-dessus. Le circuit
exécutable et son décompte sont traités séparément par l'intégration.
