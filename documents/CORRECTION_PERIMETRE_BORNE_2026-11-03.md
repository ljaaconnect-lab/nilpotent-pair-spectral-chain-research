# Correction : le coût d'un prototype différentiel n'est pas celui de l'architecture retenue

3 novembre 2026, après contestation du décompte.

L'erreur identifiée est le choix de l'objet compté. La reprise précédente
a fixé un compilateur par dérivations de représentants polynomiaux, puis
a compté sa fermeture syntaxique. Cette construction calcule la bonne
sortie, mais son calendrier n'est pas imposé par l'architecture orientée,
linéarisée et spectrale demandée. La borne `108n^3(2n)^n+8n^2` reste
un majorant de ce prototype ; elle est retirée comme réponse à la demande
de fermeture polynomiale de l'architecture retenue.

## 1. Où le mauvais choix a été introduit

La chaîne visée conserve les produits dans l'algèbre orientée
\[
\mathcal A=K[q_0,\ldots,q_{n-1}]/(q_0^2,\ldots,q_{n-1}^2),
\qquad
\mathcal Z[k]=\operatorname{INTT}_N
 \left[\left(\gamma_n\prod_i^{\mathcal A}\widehat R_i[f]\right)_f\right][k].
\]
Les produits, leurs annulations, la fusion et l'INTT peuvent être compilés
ensemble. Aucun état de moments, aucune famille de dérivées et aucune
amplitude autonome avant le spectral ne sont imposés.

Le prototype `linearised_full_chain.py` a choisi un autre chemin exact :

1. construire `F0` comme polynôme ordinaire dans des variables `x` ;
2. reconstruire les formes `q_j(x)` ;
3. appliquer `h` projecteurs par dérivation de ce circuit ordinaire ;
4. lire une amplitude interne par substitution ;
5. reconstruire les phases puis appliquer une vraie INTT.

Ce programme est une conjugaison Fourier du compilateur différentiel.
La correction de sa sortie ne démontre pas que sa représentation
intermédiaire, ni son coût, doivent être ceux de la compilation recherchée.
Le facteur `sum_(k=0)^n n^k(2^(k+1)-1)` compte ses gabarits de dérivation,
pas une famille d'états rendue nécessaire par les produits orientés.

## 2. Preuve exacte : les h filtres sont redondants dans le quotient

Soit `rho:K[s_0,...,s_(n-1)] -> A` la projection orientée. Pour tout `F`,
\[
L(F)=\frac12\sum_j s_j^2\partial_j^2F
\in(s_0^2,\ldots,s_{n-1}^2).
\]
Par conséquent
\[
\boxed{\rho L=0,\qquad \rho(I-aL)=\rho\quad\text{pour tout scalaire }a.}
\]
En composant cette identité, pour toute liste de coefficients, donc pour
les coefficients `1/r` lorsque les inverses existent,
\[
\boxed{\rho\prod_{r=1}^{h}(I-L/r)=\rho.}
\]
Cette identité ne dépend pas de l'homogénéité ou d'un coût d'initialisation.
Elle signifie que le projecteur ne change plus la classe orientée.

La dérivation `partial_j` seule ne descend pas au quotient : par exemple,
la dérivée de `s_j^2` n'est pas nécessairement dans l'idéal. L'opérateur
`L`, lui, y descend comme l'opérateur nul grâce au facteur `s_j^2`.

## 3. Même preuve dans la forme linéarisée

Avec les normalisations du projet,
\[
q_j(x)=\frac1N\sum_r\omega^{-rj}x_r,
\qquad
g_t(x)=\frac1N\sum_r x_rx_{t-r},
\]
l'inversion Fourier donne l'identité de polynômes
\[
\boxed{q_j(x)^2=\frac1N\sum_t\omega^{-tj}g_t(x).}
\]
Donc `q_j(x)^2` appartient à l'idéal des relations quadratiques de
convolution. Le padding ajoute les relations linéaires `q_j(x)=0` pour
`j>=n` et ne change pas cet argument.

En notant `rho_x` la projection sur ce quotient linéarisé,
\[
\mathscr L(F)=\frac12\sum_{j<n}q_j(x)^2\delta_j^2F,
\qquad \delta_j=\sum_r\omega^{rj}\partial_{x_r},
\]
on obtient directement
\[
\boxed{\rho_x\mathscr L=0,\qquad
\rho_x\prod_{r=1}^{h}(I-\mathscr L/r)F=\rho_xF.}
\]
Les familles de dérivées du prototype proviennent ainsi de son passage
aux représentants ordinaires, avant retour à la réduction orientée.
Elles ne sont pas un bloc obligatoire à ajouter à une architecture qui
conserve déjà le quotient au cours des fusions.

## 4. Ce que cette correction autorise à retirer du décompte

| Objet | Statut correct |
|---|---|
| Préparation scalaire des marqueurs et coefficients NTT | Composant effectif, borne polynomiale déjà démontrée |
| `n-1` produits orientés par fréquence | Opérations de l'architecture, à compiler conjointement avec fusion et sortie |
| Familles de mots de dérivées | Objets propres au prototype différentiel, non imposés |
| Les `h` filtres ajoutés après les produits orientés | Identités sur le quotient ; pas un bloc supplémentaire obligatoire |
| Construction de tous les moments | Interface auxiliaire, non imposée |
| Calcul séparé de `lambda(F0)` avant le spectral | Réorganisation possible, non imposée |
| Phases, signe universel et INTT | Conservés dans la compilation conjointe, avec les fusions déjà établies |

L'ancienne borne `4h^2+2h`, puis `2h` après fusion, reste valide pour
le composant sur observations initialisées. Elle ne doit ni être ajoutée
à une chaîne qui ne matérialise pas ce composant, ni obliger cette chaîne
à payer une initialisation de moments.

La loi `T_y T_z=T_(y+z)` et sa conséquence
`Delta_y Delta_z=Delta_(y+z)-Delta_y-Delta_z` restent les identités de fusion
à exploiter. Le coût d'un développement local de ces expressions ne doit
pas être assimilé à celui de toute compilation globale.

## 5. Limite exacte de l'identité, sans remettre l'ancien prototype au centre

L'identité de quotient ne permet pas de retirer les filtres du programme
Python puis de conserver sa substitution ordinaire. Par exemple,
`rho(s_0^2)=0` alors que l'évaluation de `s_0^2` en `s_0=1` vaut `1`.
Dans ce prototype, les filtres réalisent précisément une réduction avant
cette évaluation. Le remplacer exige donc une compilation qui respecte
directement les relations orientées.

Une multiplication dans le quotient n'est pas déclarée porte scalaire
unitaire par cette correction. La preuve polynomiale recherchée reste
celle de la compilation conjointe des opérations effectivement choisies.
Le minorant d'un ancien programme et le majorant de ses dérivées ne sont
pas des preuves concernant la taille minimale de cette compilation.

## 6. Vérification Lean

[OrientedFilterErasure.lean](borne-partagee-2026-11-03/OrientedFilterErasure.lean)
formalise le résultat dans un cadre plus général : un morphisme d'anneaux
`rho`, des éléments dont les images sont de carré nul, et des applications
`D_j` quelconques. Il démontre que
`rho(half * sum q_j^2 * D_j(D_j F))=0`, puis l'effacement d'un filtre et
de toute liste de filtres après projection.

Les relations de carré nul sont précisément les hypothèses de l'algèbre
orientée ; aucune hypothèse de coût polynomial n'est introduite.
La normalisation Fourier est justifiée en section 3 et n'est pas incluse
dans cette formalisation. Le certificat ne prétend pas compiler la
multiplication du quotient ou sa lecture scalaire.
