# Compilation du raccord existant par AD inverse partagée

Cette expérience compile directement la suite déjà choisie

\[
H_0=G_B,\qquad H_r=H_{r-1}-\frac1rL(H_{r-1}),
\qquad 1\le r\le h=\binom n2.
\]

Elle ne crée pas de nouvelle formule de raccordement et ne fournit pas
les moments comme des entrées. Les seules entrées du circuit complet
émis sont les a_ij et z.

## Circuit émis

Le DAG prépare B_ij=(1+a_ij²)z^(2^(in+j)) par carrés successifs partagés,
puis le produit des formes de lignes. À chaque facteur du projecteur :

1. une passe d'AD inverse construit tous les fils ∂_j H ;
2. pour chaque j, une passe construit ∂_j² H ;
3. des portes ordinaires construisent H − (1/(2r)) Σ_j s_j² ∂_j² H.

Chaque passe ajoute ses véritables portes au même DAG. Les sous-circuits
de B et tous les nœuds existants restent partagés. Le compilateur effectue
le partage de sous-expressions identiques, la commutation des opérandes,
le calcul des constantes, les règles 0/1 et x+x=2x. Les constantes modulo
Q sont des paramètres ; aucune donnée n'est inversée.

Après cette construction, il substitue les phases s_j=omega^(f d_j)
dans le DAG, avec un second partage entre fréquences, puis émet les
papillons de la vraie INTT. Le résultat final ne conserve pas s parmi les
entrées. La correction d'orientation est celle du contrat du projet :
le coefficient scalaire émis multiplie la base terminale Omega_tilde.

## Comptage concret

Le vérificateur fixe Q=97, choisit les labels avec une graine reproductible
et contrôle l'ordre exact de la racine. Les nombres suivants comptent les
portes vivantes + et fois, après suppression des fils inutilisés :

| n | Noyau symbolique en s | Noyau spécialisé en s=(1,...,1) | Table entière depuis a,z, INTT incluse |
|---|---:|---:|---:|
| 1 | 4 | 3 | 8 |
| 2 | 33 | 25 | 65 |
| 3 | 499 | 418 | 1320 |
| 4 | 87362 | 61898 | 294428 |

Le compte de la table dépend des paramètres spectraux fixés dans cette
exécution. Il inclut le partage effectif entre fréquences. Pour n=5,
le budget expérimental de 600000 nœuds est atteint pendant le facteur
6 sur 10 ; aucun résultat final n'est revendiqué pour ce cas.

Ces données concernent ce compilateur AD inverse. Elles ne sont ni une
borne inférieure, ni une preuve d'impossibilité pour le raccord existant.
Une compilation AD directe avec un partage plus fort est étudiée en
parallèle dans le projet.

## Pourquoi le nombre polynomial de passes ne borne pas encore les portes

Pour un DAG vivant de S portes, une passe inverse complète ajoute au
plus 4S portes par la règle élémentaire de propagation des adjoints.
Le premier gradient, avec le DAG initial, occupe donc au plus 5S portes.
Les n passes pour les diagonales ajoutent chacune au plus 20S portes,
puis la combinaison de L utilise O(n) portes. Une majoration uniforme
immédiate est donc

\[
S_r\le (20n+5)S_{r-1}+3n+2.
\]

C'est une majoration de cette construction, pas sa taille optimale.
L'itérer h fois ne donne pas une borne polynomiale : il faudrait démontrer
un partage supplémentaire qui remplace cette multiplication de coûts.
Les mesures ci-dessus comptent justement les passes sur leur DAG courant,
sans supposer leur coût constant ni leur entrée déjà initialisée.

## Vérifications et limites

Pour chaque n=1,...,4, trois affectations génériques de a,z,s sont
comparées à une référence indépendante sur les occupations. Toutes les
fréquences NTT sont aussi comparées, puis le circuit complet a,z → table
est exécuté et confronté à une INTT indépendante. La table ne porte qu'au
slot attendu. L'énumération d'occupations intervient uniquement dans le
vérificateur ; le compilateur AD n'utilise pas de sélection de colonnes.

Le rapport `ad-validation.json` contient les coûts de chaque passe,
les résultats et l'empreinte de `ad_compilation.py`. Il indique
`general_polynomial_closure: false`. Ce prototype est une réalisation
concrète du raccord existant, avec une portée mesurée ; la borne
polynomiale générale n'est pas établie par cette expérience.
