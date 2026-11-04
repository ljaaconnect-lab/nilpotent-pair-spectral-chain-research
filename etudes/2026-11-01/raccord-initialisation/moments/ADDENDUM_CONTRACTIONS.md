# Essai d'un invariant rationnel avec le spectre conservé

L'exploration demande une représentation différente de la liste des W_S.
Le candidat ci-dessous a une fusion scalaire polynomiale effective. Sa
lecture finale ne passe pas les vérifications générales : **il n'est pas
retenu comme solution du raccord demandé**. La conclusion porte sur cette
représentation et sur les lecteurs spécifiés ici.

## État proposé et coût de fusion

Choisissons n constantes distinctes lambda_j et posons

    D(u) = product_j (u-lambda_j),
    g_j(u) = D(u)/(u-lambda_j).

La division écrite est exacte et structurelle : g_j est simplement le
produit des n−1 autres facteurs constants. À chaque fréquence f,

    H_i(u,f) = sum_j B_ij omega^(f d_j) g_j(u),
    P_k(u,f) = product_(i<k) H_i(u,f).

La mise à jour P_(k+1)=P_k H_k conserve un polynôme de degré au plus
k(n−1). Le dénominateur structurel D(u)^k permet d'interpréter cet état
comme le produit de fractions simples

    R_k(u,f) = product_(i<k) sum_j B_ij omega^(f d_j)/(u-lambda_j).

L'état comporte O(N n²) coefficients de corps, donc O(n³) si N=O(n).
La préparation des H_i coûte O(N n³) portes et la multiplication scolaire
de tous les facteurs coûte O(N n⁴) portes. Il n'y a ni développement
par sous-ensembles ni opération sur une algèbre de dimension exponentielle.

La tentative est que les pôles enregistrent les répétitions de colonnes,
puis qu'un lecteur commun aux polynômes de sortie élimine ces répétitions.

## Les fréquences doivent être traitées ensemble

La lecture d'une fréquence isolée à partir du seul R_n est insuffisante.
Pour lambda=(0,1,2), noter r_j=1/(u-j). L'identité

    r_0 r_1 r_2 = (1/2) r_1² (r_0+r_2)

identifie le produit utilisant une fois chaque colonne avec un produit
dont deux lignes sont forcées dans la colonne 1. Le lecteur orienté devrait
pourtant donner respectivement 1 et 0. Tout lecteur dépendant seulement
de cette fraction rationnelle à cette fréquence échoue, même s'il est
non linéaire.

Cette identité possède aussi une réalisation dans les feuilles originales
modulo 17, à z=1 et à la fréquence 0. Pour le premier produit, prendre
a_ii=0 et a_ij=4 hors diagonale. Pour le second, prendre les lignes de A
(4,0,4), (4,0,4), (5,4,5). On obtient les lignes de B
(0,1,0), (0,1,0), (9,0,9), et 9=1/2 modulo 17.

Le vérificateur produit en outre deux exemples denses modulo 97, en
regroupant différemment les mêmes racines des numérateurs de lignes :
pour n=3, les fractions sont identiques mais les lectures valent 44 et 20;
pour n=4, elles valent 18 et 79. Les matrices figurent dans le rapport.

**Ces exemples par fréquence ne rejettent pas un lecteur qui utilise
simultanément toutes les fréquences.** Les phases peuvent distinguer les
deux entrées. Le test suivant conserve explicitement cette information.

## Test exact avec l'INTT intégrée

Prenons d_j=j, N la première puissance de deux strictement supérieure à n,
et Q=97. Pour une occupation m=(m_0,...,m_(n−1)), de somme n, la contribution
après multiplication est portée par

    p_m(u) = product_j (u-lambda_j)^(n-m_j),
    slot(m) = sum_j j m_j mod N.

L'occupation sans collision est m=(1,...,1), au slot n(n−1)/2 modulo N.
Un lecteur linéaire des coefficients, après l'INTT, existe exactement si
p_(1,...,1) n'appartient pas à l'espace engendré par les p_m des occupations
avec collision dans ce même slot. C'est une équivalence de simple algèbre
linéaire; elle inclut toutes les amplitudes du produit et conserve la phase.

Le vérificateur calcule ces rangs exactement dans F_97, pour deux choix
de pôles : lambda_j=j et lambda_j=(j+1)². Résultats :

| n | N | Occupations avec collision dans le slot | Coordonnées polynomiales | Lecteur linéaire possible, pour chacun des deux choix de pôles |
|---|---|---|---|---|
| 2 | 4 | 0 | 3 | oui |
| 3 | 4 | 1 | 7 | oui |
| 4 | 8 | 4 | 13 | oui |
| 5 | 8 | 15 | 21 | non |
| 6 | 8 | 55 | 31 | non |
| 7 | 8 | 211 | 43 | non |

Le spectre rend donc cette lecture possible aux petites tailles où la
lecture d'une fréquence isolée échoue. Le passage n=5 montre que cette
réparation ne suffit pas pour cette famille de substitutions rationnelles
et pour un lecteur linéaire. Il n'établit pas d'impossibilité pour un lecteur
non linéaire utilisant toutes les fréquences, des pôles différents ou une
autre représentation.

## Portée

Ce candidat donne effectivement une initialisation et une fusion de taille
polynomiale depuis le produit compact. Il ne conserve pas, avec le lecteur
testé, l'information nécessaire à l'annihilation exacte des collisions.
La voie n'est donc pas annoncée comme un raccord complet. Le résultat
positif reste la preuve de coût de la fusion et la vérification que le
spectre doit être inclus dans tout test de la lecture.

Exécution : `python -B verify_rational_contractions.py`.
Le rapport `rational-contractions-validation.json` contient les deux
contre-exemples denses, les douze tests de rang et l'empreinte du code.
