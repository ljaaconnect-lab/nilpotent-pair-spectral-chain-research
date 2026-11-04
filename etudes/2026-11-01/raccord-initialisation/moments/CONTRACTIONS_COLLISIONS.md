# Initialisation par contractions de collisions

Cette note part du produit compact et porte directement sur les observations
du lecteur. Elle établit une formule générale exacte et des circuits scalaires
aux ordres fixes. **Elle ne démontre pas une borne polynomiale uniforme pour
tous les ordres jusqu'à h = n(n−1)/2.**

Fixons une fréquence et posons x_ij = B_ij t_j, avec
t_j = omega^(f d_j). Pour un ensemble non vide S de lignes, définissons

    W_S = sum_j product_(i in S) x_ij,
    ell_i = W_{ {i} }.

Chaque W_S est donc une contraction sur une colonne commune, sans condition
de colonnes distinctes. Les phases sont déjà dans ses feuilles :
W_S(f) = sum_j omega^(f |S| d_j) product_(i in S) B_ij.

## Identité générale

Soit C_B(u) le polynôme qui pondère chaque contribution du produit compact
par u à la puissance de son nombre de collisions. Sa définition est utilisée
pour la preuve, pas comme une entrée gratuite :

    C_B(u) = sum_(j_1,...,j_n) (product_i x_(i,j_i)) u^(kappa(j)),
    kappa(j) = number of pairs a < b such that j_a = j_b.

Pour un graphe simple H sur les n lignes, posons

    w(H) = product_(S connected component of H) W_S.

Alors

    C_B(1+v) = sum_(H subset K_n) v^(number of edges H) w(H).       (1)

Preuve : pour une contribution fixée,

    (1+v)^kappa = product_(a<b) (1 + v [j_a=j_b]).

Le développement choisit un graphe H. Ses contraintes d'égalité imposent
une colonne commune dans chaque composante connexe, sans relation imposée
entre composantes. La somme sur les colonnes se factorise donc en w(H).
Ceci est une identité sur les entiers, valable après toute réduction modulo Q.

Écrivons c_e = [v^e] C_B(1+v). Pour S(r,e), nombre de Stirling de deuxième
espèce, la relation k^r = sum_e S(r,e) k^(underline e) donne

    mu_r = (L^r G_B)(t) = sum_(e=0)^min(r,h) S(r,e) e! c_e.       (2)

Les coefficients S(r,e)e! se préparent en un nombre polynomial de portes
structurelles. Le point qui reste à compiler uniformément est la contraction
globale c_e dans (1), pas cette transformation triangulaire.

## Premiers ordres, avec toutes leurs contractions

Dans les expressions suivantes, chaque terme porte le produit des ell_i
sur les lignes absentes de ses indices. Ainsi W_abc signifie
W_{ {a,b,c} } product_(i not in {a,b,c}) ell_i, et W_ab W_cd porte
le produit extérieur à {a,b,c,d}.

    mu_0 = product_i ell_i.

    mu_1 = sum_(a<b) W_ab.

    mu_2 = mu_1
           + 6 sum_(a<b<c) W_abc
           + 2 sum_(a<b<c<d) (W_ab W_cd + W_ac W_bd + W_ad W_bc).

Pour décrire mu_3 sans ambiguïté, posons A_3 = somme des W_S pour |S|=3,
A_4 = somme des W_S pour |S|=4, M_22 = somme sur les partitions d'un
sous-ensemble de quatre lignes en deux paires, M_32 = somme sur un bloc de
trois lignes et un bloc disjoint de deux, et M_222 = somme sur les partitions
d'un sous-ensemble de six lignes en trois paires. Tous incluent encore les
facteurs ell_i extérieurs. Alors

    mu_3 = mu_1 + 24 A_3 + 6 M_22 + 96 A_4 + 18 M_32 + 6 M_222.

En effet c_1=mu_1, c_2=3A_3+M_22 et
c_3=A_3+16A_4+3M_32+M_222. Les 16 arbres étiquetés sur quatre sommets
expliquent le coefficient 16. On a mu_2=c_1+2c_2 et
mu_3=c_1+6c_2+6c_3.

Ces formules sont des circuits sans division sur les amplitudes. À ordre
r fixé, la formule (1) limitée à e<=r ne touche jamais plus de 2r lignes
non isolées. Une compilation directe coûte O(n^(2r+1)) portes pour les
moments jusqu'à r. Cette borne est polynomiale pour chaque r fixé mais son
exposant dépend de r : elle ne répond pas encore au cas r<=h variable.

## Fusion exacte avec le lecteur

Le projecteur pi_n(L) lit la collision zéro. Sur la même représentation,
la lecture est donc particulièrement simple :

    (pi_n(L) G_B)(t) = C_B(0) = sum_(e=0)^h (-1)^e c_e.          (3)

Ainsi le passage par tous les mu_r n'est pas obligatoire : une contraction
partagée calculant directement la somme alternée de (3) constitue aussi un
raccord valable. L'identité supprime le besoin de matérialiser les moments,
mais n'accorde pas gratuitement le calcul des c_e ni de leur somme.

## Pourquoi le seul vecteur de moments partiels ne donne pas la mise à jour

Le lecteur ferme sous L; l'initialisation ajoute des facteurs de ligne.
Ces deux opérations ont des règles différentes. À t=(1,1), les produits
partiels F=s_1 et H=s_2 ont tous deux le vecteur (1,0,0,...). Pourtant,
après multiplication par la même nouvelle ligne ell=s_1,

    (L(F ell))(1,1) = 1,       (L(H ell))(1,1) = 0.

Une mise à jour ne recevant que ce vecteur et la nouvelle ligne ne peut
donc pas être correcte pour tous les produits partiels. Ceci ne rejette
aucune autre représentation : cela précise que la construction progressive
doit partager des contractions ouvertes, ou intégrer le lecteur autrement.

## Vérification reproductible

`verify_moment_contractions.py` vérifie (1), (2), les formules jusqu'à
mu_3 et (3) pour de petites instances, par une référence indépendante sur
les contributions du produit. Les énumérations sont celles du vérificateur,
pas un circuit général revendiqué polynomial. Le rapport enregistre les
empreintes du code et le domaine de vérification.
