# Compilation partagée de l'action L sur le produit complet

Ce travail conserve le raccord et le lecteur déjà construits. Il compile
l'action existante L sur la source compacte, puis initialise ses observations.
Il ne propose pas une nouvelle formule de raccordement.

Le programme produit effectivement tous les moments requis jusqu'à h aux
tailles n=3 et n=4, depuis x_ij=B_ij t_j, avec uniquement des additions et
des multiplications scalaires. La construction algébrique est générale,
mais **la taille de son DAG partagé n'a pas de borne polynomiale générale
démontrée**. Les n² coordonnées ci-dessous ne constituent pas une telle borne.

## 1. Action sur le produit complet

Posons ell_i(s)=sum_j B_ij s_j et G=product_i ell_i. Dans une localisation
provisoire où les ell_i sont inversibles, introduisons

    p_ij = B_ij s_j / ell_i,
    m_j = sum_i p_ij,
    q_i = sum_j p_ij²,
    v_i = sum_j m_j p_ij,
    A = sum_(i<k) sum_j p_ij p_kj.

La dérivation Euler s_j partial_j, agissant sur une expression en p, devient
une dérivation D_j déterminée par

    D_j p_ik = p_ik (delta_jk - p_ij).

Par la règle de Leibniz,

    G^(-1) L(G F) = A F + B F,
    B = sum_j m_j D_j + (1/2) sum_j (D_j²-D_j).

La notation B pour cet opérateur est locale à cette section et ne remplace
pas la matrice des amplitudes B_ij. Le code le nomme `drift`.

Son action sur une feuille est une expression scalaire explicite :

    B(p_ik) = p_ik (m_k-p_ik+q_i-v_i).                       (1)

En effet
sum_j(D_j²-D_j)p_ik/2 = p_ik(q_i-p_ik), et
sum_j m_j D_jp_ik = p_ik(m_k-v_i).

L'action sur chaque porte est également scalaire :

    D_j(u+v) = D_ju + D_jv,
    D_j(uv)  = u D_jv + v D_ju,
    B(u+v)   = Bu+Bv,
    B(uv)    = u Bv + v Bu + sum_j (D_ju)(D_jv).            (2)

Les constantes ont dérivée et dérive nulles. Ces règles permettent une
compilation ascendante, avec partage de chaque paire (porte,j) et de chaque
valeur B(porte). Aucune porte « appliquer L » ne subsiste.

En commençant par F_0=1, le programme construit

    F_(r+1) = A F_r + B F_r,
    mu_r = G F_r.                                         (3)

Les équations (1)–(3) concernent le produit complet G. Elles ne nécessitent
pas une mise à jour par lignes ni un état indexé par colonnes déjà choisies.

## 2. Suppression des divisions, y compris aux données singulières

La localisation précédente sert à établir les règles; elle n'est pas
imposée aux entrées du circuit. Introduisons un paramètre epsilon et

    H_epsilon(s) = product_i [1+epsilon(ell_i(s)-1)],
    p_ij(epsilon) = epsilon B_ij s_j / [1+epsilon(ell_i(s)-1)].

Les mêmes identités d'Euler et de Leibniz restent exactes : chaque facteur
de H est affine en s, et sa dérivée Euler est epsilon B_ij s_j. La somme
des p_ij d'une ligne n'a pas besoin d'être égale à 1 pour les règles (1)–(3).

On travaille dans le seul anneau de jets univariés

    R[epsilon]/(epsilon^(n+1)).

Toutes les inverses ont une constante 1 et se calculent explicitement :

    (1+epsilon delta_i)^(-1)
       = sum_(k=0)^n (-delta_i)^k epsilon^k mod epsilon^(n+1),
    delta_i = ell_i(t)-1.

Le programme prépare les n² jets p_ij par puissances successives de
-delta_i, puis exécute toutes les portes du DAG dans ces jets. Enfin il
multiplie chaque F_r par H_epsilon, puis somme ses coefficients.

Justification de cette dernière étape : L^r H_epsilon est un **polynôme
en epsilon de degré au plus n**, puisque L agit seulement sur s. Ses n+1
coefficients obtenus modulo epsilon^(n+1) sont donc tous ses coefficients,
et leur somme est sa valeur en epsilon=1, c'est-à-dire L^r G.
On ne substitue pas epsilon=1 dans une fraction tronquée non corrigée.

Ainsi aucune inversion de donnée ni condition ell_i(t)!=0 n'est nécessaire.
La procédure reste correcte si une somme de ligne, ou une ligne entière,
est nulle. Les vérifications incluent explicitement ces deux situations.

## 3. Réutilisation de la relation spectrale existante

Pour éviter des actions redondantes, on prend l'ensemble effectivement
atteint des valeurs de collision :

    K_n = {sum_l binom(b_l,2) : b_l>=1, sum_l b_l=n}.

Il se prépare sans données, par une programmation dynamique sur le degré
et l'entier collision : O(n³) états et O(n⁴) transitions suffisent.
Les degrés inférieurs à n sont couverts aussi, en ajoutant des blocs de
taille 1, ce qui ne change pas la collision. Posons d=|K_n| et

    chi_n(T) = product_(k in K_n)(T-k)
             = T^d + sum_(j<d) c_j T^j.

Il suffit de compiler explicitement F_0,...,F_(d-1). Les observations
suivantes jusqu'à h utilisent la relation déjà valable pour le lecteur :

    mu_r = -sum_(j<d) c_j mu_(r-d+j),    r>=d.

Cela améliore les petits cas mais ne donne pas une borne polynomiale
pour les d premières actions. En particulier d n'est pas traité comme
une constante indépendante de n.

## 4. Coût entièrement scalaire

Soient a et m les nombres d'additions et multiplications du DAG partagé
qui produit F_0,...,F_(d-1), après suppression des portes inaccessibles.
Une addition de jets coûte n+1 portes et leur produit tronqué scolaire
coûte exactement (n+1)² portes. La préparation des jets et de H coûte
2n³+4n²+n portes dans le prototype, qui compte aussi les produits par zéro.
La lecture de chaque moment coûte (n+1)²+n portes. Le coût total est donc

    2n³+4n²+n + (n+1)a + (n+1)²m
    + d(n²+3n+1) + (h+1-d)(2d-1).                         (4)

Ce coût part des fils x_ij=B_ij t_j déjà définis dans la chaîne. La
préparation des marqueurs a,z et des phases n'est pas incluse une deuxième
fois. Une copie peut être exécutée pour chaque fréquence, puis branchée
au lecteur et à l'INTT existants.

Un passage des règles (2) utilise O(nS) portes pour un DAG de taille S,
avec partage effectif. La répétition à ordre variable n'est pas bornée
polynomialement ici : une borne directe de type (Cn)^r est seulement
une borne supérieure du compilateur, pas une fermeture générale.

## 5. Vérification et tailles mesurées

`verify_global_action.py` vérifie les observations par une référence
indépendante sur les contributions du produit. Cette énumération n'est
présente que dans le vérificateur. Le compilateur utilise les règles
scalaires (1)–(3), sans parcourir ces contributions.

| n | K_n | Moments initialisés | Portes du DAG F de base | Portes scalaires après suppression des divisions |
|---|---|---|---|---|
| 3 | 0,1,3 | mu_0,...,mu_3 | 222 | 2 495 |
| 4 | 0,1,2,3,6 | mu_0,...,mu_6 | 59 846 | 859 749 |

Ces tests sont effectués modulo 97 sur trois sortes d'entrées par taille :
matrice générique, somme de ligne nulle, ligne nulle. Ils vérifient aussi
toutes les fréquences des sources originales x_ij=(1+a_ij²)
2^(2^(in+j)) omega^(f j) pour N=4 et N=8. Le coût mesuré est identique
pour toutes les entrées d'une même taille : aucune branche ne dépend des
données. Des tests intermédiaires complètent la validation pour n=2 et
pour les actions directes jusqu'à l'ordre 3.

Le rapport `global-action-validation.json` enregistre les tailles, les
comptes et les empreintes des deux programmes. Cette vérification exécutable
ne remplace pas une preuve Lean et ne constitue pas une preuve de borne
polynomiale générale.
