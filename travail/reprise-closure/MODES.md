# Reprise : fusion par occupations de modes

Cette note est une construction conditionnelle complète. Elle ne prouve pas
la fermeture polynomiale générale du contrat.

Soit K un anneau commutatif et supposons que les **poids marqués complets**
admettent une factorisation fournie et calculable B=UV^T, avec U,V de taille
n×r. Il faut inclure dans cette condition les marqueurs z, et compter le
coût de construction de U,V. Le rang de A avant marquage ne suffit pas.

Pour chaque fréquence f, on forme deux polynômes en r variables :

    F(x)   = product_i (sum_l U[i,l] x_l),
    G_f(x) = product_j (omega^(f d_j) sum_l V[j,l] x_l).

Pour alpha=(alpha_0,...,alpha_{r-1}), |alpha|=n, poser
alpha! = product_l alpha_l!. Alors la fusion terminale est

    H[f] = sum_{|alpha|=n} alpha! coeff(F,alpha) coeff(G_f,alpha).

**Identité générale.** H[f] est exactement la somme des amplitudes de tous
les chemins bijectifs, phases spectrales incluses. Aucun P_A n'est fourni
en entrée. Après correction universelle, Z[k]=Omega_tilde INTT(H)[k].

Preuve : un terme de F choisit un mode pour chaque ligne ; un terme de G_f
choisit un mode pour chaque colonne. Deux choix peuvent être raccordés si
et seulement si leurs nombres d'occurrences alpha coïncident. Il existe
exactement product_l alpha_l! bijections raccordant les objets de même
mode. Réordonner la somme par bijection sigma donne, pour chaque sigma,
product_i sum_l U[i,l]V[sigma(i),l] = product_i B[i,sigma(i)]. La phase est
omega^(f sum_j d_j), commune à tous les raccords. La preuve est intégrale,
donc valable en toute caractéristique sans divisions.

Le couplage est aussi le couplage différentiel F(partial)G_f évalué en zéro.
La loi locale de fusion est <x_l F,G>=<F,partial_l G>. C'est une cible Lean
utile, mais cette note n'est pas une preuve Lean.

## Coût de fermeture

Au degré t, il existe D_t=binomial(t+r-1,r-1) occupations. Une multiplication
par une forme linéaire utilise au plus r D_t produits et (r-1)D_t additions.
Une chaîne de n facteurs coûte donc au plus

    (2r-1)(binomial(n+r,r)-1)

portes scalaires. Deux chaînes et la contraction finale coûtent au plus

    2(2r-1)(binomial(n+r,r)-1) + 3D_n - 1,

hors préparation des constantes factorielles (O(n+rD_n), ou précompilation
uniforme). Le résultat à chaque fréquence suivi de l'INTT a un coût
O(N r binomial(n+r,r) + N log N), plus la préparation des facteurs.
Les phases peuvent aussi être partagées grâce à l'identité de phase commune.
Pour r fixé, ce circuit est polynomial en n à tout ordre. Son état ne
mémorise aucun sous-ensemble de colonnes, seulement r nombres d'occupation.

La représentation ne clôt pas le cas général : r=n donne une dimension
binomial(2n-1,n-1), exponentielle. Ce n'est pas un opérateur gratuit.

## Pourquoi le rang des données non marquées ne suffit pas

Prenons toutes les données a_ij=0. Les poids p_ij valent 1 (rang un), tandis
que la matrice marquée vaut M_ij=z^(2^(in+j)). Son déterminant est

    sum_sigma sign(sigma) z^(sum_i 2^(in+sigma(i))).

Deux permutations distinctes utilisent des ensembles distincts d'adresses
binaires. Les exposants de z sont donc distincts. Aucun monôme du déterminant
ne s'annule : son coefficient est +1 ou -1, non nul même en caractéristique
deux. Le déterminant est non nul dans K[z] pour tout corps K, donc le rang
sur K(z) est n. La modulation spectrale des colonnes ne change pas ce rang.

Il faudrait une nouvelle compression exploitant les adresses et la lecture
terminale ensemble ; remplacer le rang des poids marqués par le rang des
poids avant marquage serait une hypothèse fausse.

## Référence vérifiée

La famille algorithmique de rang fixé est connue : Arvind, Chatterjee,
Datta, Mukhopadhyay, *Univariate Ideal Membership Parameterized by Rank,
Degree, and Number of Generators*, FSTTCS 2018, fournit un algorithme
n^{O(r)} pour le permanent de rang r sur tout corps.
https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.FSTTCS.2018.7

La présente note adapte explicitement le couplage aux phases, au marquage
et au comptage des portes du contrat ; elle ne revendique pas la nouveauté
de l'algorithme de rang fixé ni une résolution générale.
