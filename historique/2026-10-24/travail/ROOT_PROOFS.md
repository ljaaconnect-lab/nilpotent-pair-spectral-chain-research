# Résultats du coordinateur — portée restreinte

Ces résultats ne résolvent pas la conjecture 1.5. Ils concernent des modèles
précis de représentation et de lecture. Les constructions dépendantes des
facteurs d'entrée et les circuits scalaires généraux ne sont pas exclus.

## Codage polynomial d'un sous-ensemble individuel

Pour S inclus dans {1,...,n}, q_S(X)=produit_{j dans S}(X-j) est injectif.
Ses n+1 coefficients au plus ont chacun O(n log(n+1)) bits.
Si S et T sont disjoints, q_{S union T}=q_S q_T; un PGCD détecte
l'intersection. Ce codage et ses opérations sont polynomiaux pour un
sous-ensemble individuel. Il ne fournit pas un codage additif fidèle d'une
superposition arbitraire de sous-ensembles pondérés.

Contre-exemple admissible à la somme Q=sum_S f_S q_S, dès la première couche
et z=1 : les premières lignes (1,10,1) et (5,2,5) donnent toutes deux
Q=12X-24. Avec les deux lignes suivantes (2,1,1),(2,1,1), les permanents
valent respectivement 46 et 38. Toutes les entrées sont 1+a^2 avec a entier.
Un fusionneur et un lecteur scalaires sans division utilisant seulement Q
et les lignes suivantes échouent donc. Cela n'exclut pas un algorithme
ayant accès aux facteurs originaux ou une autre représentation.

## Nombre de mesures scalaires fixes du déterminant

Soit D_A(z)=det(B_A(z)) et P_A(z)=per(B_A(z)). Supposons une représentation
P_A(z)=sum_{l=1}^M D_A(a_l) R_l(z), où les points scalaires a_l sont
indépendants de A et de z, et les fonctions R_l sont indépendantes de A.
Alors M>=n!.

Preuve : les exposants E(sigma)=sum_i 2^(in+sigma(i)) sont distincts.
Les fonctions c_sigma(A)=produit_i(1+a_i,sigma(i)^2) sont linéairement
indépendantes, car leur monôme de degré 2n propre à sigma n'apparaît dans
aucune autre. La famille des P_A engendre donc l'espace des n! monômes
z^E(sigma). La représentation proposée est contenue dans l'espace engendré
par les M fonctions R_l, d'où la borne.

Une preuve constructive utilise seulement A=P_tau, matrice de permutation.
La matrice des coefficients est H_sigma,tau=2^|sigma intersection tau|.
Elle est le Gram des vecteurs (1_{S inclus dans sigma}) indexés par les
matchings partiels S. Les coordonnées correspondant aux matchings complets
contiennent l'identité. H est donc définie positive et de rang n!.

La même borne vaut pour M mesures linéaires scalaires fixes quelconques
suivies d'une reconstruction linéaire fixe. Elle ne s'applique pas à des
points dépendant de z, à une reconstruction non linéaire, ou à un lecteur
qui exploite aussi les facteurs originaux.

Pour la moyenne sur T racines de l'unité de B.27, la condition d'exactitude
universelle est l'injectivité des E(sigma) modulo T. La nécessité se voit
même pour A=0 : dans une classe d'alias, chaque coefficient devient
sgn(tau) sum_{sigma dans la classe}sgn(sigma). Si les deux signes sont
présents, ils ne peuvent donner simultanément 1; si un seul signe est
présent, le coefficient est la taille de la classe. Donc chaque classe
doit être un singleton. Cela ne concerne pas le paramètre spectral N
du raccordement aval B.18, qui peut rester polynomial.

## Lecture par évaluations partagées du produit auxiliaire

La polarisation de Glynn donne exactement
per(B)=2^(1-n) sum_{epsilon_1=1, epsilon_j=+-1}
       (produit_j epsilon_j) produit_i(sum_j B_ij epsilon_j).
Les états par blocs de lignes se fusionnent coordonnée par coordonnée.
Il y a cependant 2^(n-1) coordonnées.

Cette quantité est minimale dans le modèle de points partagés fixes et
de lecture linéaire : si per(B)=sum_l c_l produit_i(B_i point a_l),
la spécialisation de toutes les lignes à y donne
n! produit_j y_j=sum_l c_l(a_l point y)^n.
Le rang de Waring du monôme carré libre est 2^(n-1), sur un corps
algébriquement clos de caractéristique zéro. Source primaire :
Carlini, Catalisano, Geramita, https://arxiv.org/abs/1110.0745.
Cette application du théorème ne couvre pas des points adaptatifs.

## Vérifications et raccordement

verify_subset_representations.py / verification.json contiennent les
contrôles finis exacts des codages, fusions, filtres, rangs et contre-exemples.
Ils ne constituent pas une preuve de complexité asymptotique.
Le raccordement B.18 du PDF confirmé reste conservé : à une source scalaire
de taille Pi s'ajoute 2N log2(N)+3N-3 pour N puissance de deux, N>=2.
Aucune des bornes restreintes ci-dessus ne réfute une source scalaire
générale de taille polynomiale.
