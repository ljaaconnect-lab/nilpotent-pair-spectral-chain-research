# Constantes c et d : démonstrations et raccord au compilateur

**Portée précisée après le rappel de l'auteur :** cette note étudie la
variante par moments. La matrice `M=e_0p^T` est une reformulation de son
lecteur fourni, sans gain de calcul ; elle n'est pas une étape ajoutée
à la chaîne. L'INTT reste la lecture finale, et une compilation conjointe
peut éviter les moments. Voir la [clarification de l'architecture](LECTURE_INTT_ET_MOMENTS_2026-11-02.md).

Travail du 2 novembre 2026, après l'audit de n57–n59. La dimension du
lecteur à observations admet **d=2**. La borne **S<=n^c** pour construire
ses observations depuis les données originales reste à démontrer.
La chaîne complète n'a donc pas encore de borne polynomiale générale.

Le résultat positif ci-dessous met le lecteur existant exactement au
format du compilateur retrouvé. Il n'ajoute pas une amplitude finale
comme entrée et ne change pas l'opérateur de lecture.

## 1. Ce que doivent désigner les deux constantes

Dans le critère n59, `r` est la dimension de la matrice donnée au
compilateur, et `S` le coût du circuit construisant ses entrées `M,u,v`
depuis les données autorisées. Les hypothèses sont simultanément

\[
r\le n^d,\qquad S\le n^c,\qquad
u^\top M^{n^n-1}v=Y,
\]

où `Y` désigne la coordonnée de la sortie orientée après correction du
signe universel. Les trois garanties doivent porter sur la même
représentation. Le symbole `Y` n'est pas une entrée du circuit.

La préparation d'un polynôme générateur avec des variables auxiliaires
et la préparation des valeurs nécessaires à son lecteur sont deux
constructions différentes ; leurs tailles ne peuvent pas être identifiées.

## 2. Démonstration de d=2 pour le lecteur exact

Reprendre les objets déjà établis dans le raccord :

\[
h=\binom n2,\quad
G_B(s)=\prod_i\sum_j B_{ij}s_j,\quad
L=\frac12\sum_j s_j^2\partial_{s_j}^2,
\quad \mu_j=(L^jG_B)(1,\ldots,1).
\]

On travaille dans le même corps fourni que précédemment, avec
`Q>max(2,h)` et les paramètres spectraux admissibles. Écrire

\[
\pi_n(X)=\prod_{a=1}^{h}(1-X/a)
       =\sum_{j=0}^{h}p_jX^j.
\]

Le terme constant vaut `p_0=1`. Le raccord du projecteur donne exactement

\[
Y=\sum_{j=0}^{h}p_j\mu_j.
\]

La dimension requise pour ce vecteur est

\[
r=h+1=1+\frac{n(n-1)}2\le n^2\qquad(n\ge1),
\]

car `2n²−2r=n²+n−2=(n−1)(n+2)>=0`. On peut donc fixer
**d=2 indépendamment de n**.

Pour vérifier que cette dimension est bien compatible avec n57, et pas
seulement celle d'une liste d'observations, poser

\[
u=e_0,\quad v=(\mu_0,\ldots,\mu_h)^\top,\quad M=e_0p^\top.
\]

Seule la première ligne de `M` est non nulle. Puisque `p^T e_0=1`,

\[
M^2=e_0(p^Te_0)p^T=M.
\]

Ainsi, pour tout entier `K>=1`,

\[
\boxed{u^TM^Kv=p^Tv=Y.}
\]

En particulier, `K=n^n−1` convient pour `n>=2`. La loi de lecture est
celle du projecteur déjà établi ; la matrice sert uniquement à la mettre
au format exact du compilateur n57–n59.

Après la fusion spectrale déjà démontrée, le routage donne
`Z[k]=delta_(k,k*) Y Omega_tilde`. Il n'y a pas à reconstruire toutes les
fréquences pour utiliser ce raccord. Pour `n=1`, la lecture est directement
`B_00` et peut être traitée séparément.

## 3. Ce que devient exactement la constante c

Noter `I_mu(n)` le nombre de portes nécessaires pour construire ensemble
`mu_0,...,mu_h` depuis `a,z`, en comptant les portes partagées une seule
fois. La préparation des `B_ij` est incluse dans `I_mu`.

Les entrées de `M` dépendent uniquement de `n,Q`. Si ces constantes
structurelles sont fournies dans le modèle de circuit, alors les autres
entrées sont obtenues par câblage et **S<=I_mu(n)**.

Si leur génération arithmétique est comptée, les coefficients de `pi_n`
s'obtiennent par multiplication successive par `1−X/a`. Au stade `a`,
la mise à jour emploie au plus `2a−1` portes, les constantes signées
`−1/a` étant fournies. Les coefficients intérieurs demandent chacun
un produit et une addition, le dernier seulement un produit ; le terme
constant reste `1`. La somme vaut `h²`. Ainsi

\[
S\le I_\mu(n)+h^2.
\]

Ce terme supplémentaire est polynomial et connu. **Dans cette variante,
le terme sans borne polynomiale générale démontrée est I_mu(n).** Le circuit de `G_B` en
`6n²−2` portes ne construit pas à lui seul toutes ces valeurs.

Avec `d=2`, le compilateur n57 fournit désormais la borne explicite

\[
\boxed{C\le I_\mu(n)+h^2+4n^8+3n^4.}
\]

La matrice choisie est de rang au plus un ; exploiter directement le
lecteur existant améliore ce majorant. Comme `p_0=1`, il suffit de `h`
produits et `h` additions. On obtient même

\[
\boxed{C_{\mathrm{chaîne}}\le I_\mu(n)+h^2+2h.}
\]

Le terme `h²` disparaît si les coefficients structurels du lecteur sont
fournis. Dans ces formules, l'annihilation et le routage spectral ne sont
pas comptés une seconde fois.

Si l'on démontrait `I_mu(n)<=n^e`, alors, pour `n>=2`, on pourrait fixer
`c=max(e,4)+1`, puisque
`I_mu+h²<=2n^max(e,4)<=n^(max(e,4)+1)`.
Cette implication ne fournit pas encore l'exposant `e`.

## 4. Pourquoi un couple c,d déjà disponible ne suffit pas

Il existe bien un couple explicite **c=5,d=2** pour le générateur compact.
Cette vérification précise la portée des objets polynomiaux choisis.

Poser

\[
\ell_i=\sum_j y_jB_{ij}\omega^{fd_j}.
\]

Construire une matrice de taille `n+1` avec `ell_i` en case `(i+1,i)`,
un `1` en case `(n,n)` et zéro ailleurs. Prendre `u=e_n`, `v=e_0`.
Pour `K>=n`, le seul chemin possible avance de `0` à `n` puis reste
dans l'état final ; par conséquent

\[
u^TM^Kv=\prod_i\ell_i=G_f(y).
\]

En traitant les phases comme constantes structurelles fournies,
la préparation de ses entrées coûte au plus

\[
S\le(4n^2-1)+n^2+n^2+n(n-1)
 =7n^2-n-1\le n^5\qquad(n\ge2),
\]

car `n³>=8>7`. De plus, `n+1<=n²`. Cela démontre le couple annoncé,
avec toutes les opérations matricielles ultérieures compilées en portes
scalaires par n57.
À fréquence zéro, les phases valent toutes `1` : le coût descend à
`6n²−n−1`, et le même couple convient sans génération de phases.

Mais ce circuit produit `G_f(y)`. Le vecteur initial du lecteur de la
section 2 est `(mu_0,...,mu_h)` ; ce n'est pas celui de ce générateur.
Par exemple, pour les données légales `n=2`, `a=0`, `z=1`, à fréquence
zéro, `G_B(1,1)=4`, tandis que `mu_0−mu_1=4−2=2` est la sortie filtrée.
Leur identification remplacerait la lecture par une autre valeur.

Pour mémoire, l'ancienne représentation exacte sur tous les sous-ensembles
permet aussi une préparation de matrice utilisant seulement les fils
`B_ij`, `0`, `1` : `S<=4n²−1<=n⁴` pour `n>=2`. On y dispose de `c=4`,
mais de `r=2^n`. Ce rappel identifie un résultat historique ; il ne
réintroduit pas cette représentation comme solution recherchée.

## 5. État des preuves

Le fichier [MomentCompilerBridge.lean](constantes-cd-2026-11-02/lean/MomentCompilerBridge.lean)
contient six théorèmes qui ont passé Lean 4.34.1, sans `sorry`, erreur ni
avertissement. Il vérifie la borne de dimension, l'idempotence, la puissance
et la contraction, ainsi que les inégalités arithmétiques
`4n²−1<=n⁴` et `7n²−n−1<=n⁵`. Ces deux dernières prennent les formules
de décompte comme expressions arithmétiques ; elles ne formalisent pas
les programmes qui les émettent.

Les vecteurs `p,mu` sont arbitraires dans le lemme de contraction. Le lien
avec `pi_n(L)G_B` utilise le raccord algébrique existant présenté à la
section 2 ; ce fichier Lean ne formalise pas le projecteur différentiel
ni un circuit d'initialisation des moments.

Le [rapport de validation](constantes-cd-2026-11-02/lean/validation.json)
conserve les sorties et empreintes. Le [script de rejeu](constantes-cd-2026-11-02/lean/replay.py)
utilise l'environnement Lean déjà installé et place ses fichiers compilés
dans le dossier de travail du projet. Les seuls axiomes employés sont
`propext`, `Classical.choice` et `Quot.sound`.

- `d=2` pour l'état du lecteur : démonstration ci-dessus.
- Mise au format `u^TM^Kv` de sa contraction : identité exacte ci-dessus.
- `c=5,d=2` pour le générateur compact : démonstration de coût ci-dessus,
  avec une sortie différente de la lecture complète.
- `c` pour l'initialisation du lecteur exact depuis `a,z` : non établi.
- Borne polynomiale générale de toute la chaîne : non établie.

Sources relues :

- [Critère formel n59](../etudes/2026-10-07/livrables/conjecture-1-5-suite/proofs/ConditionalCriterion.lean).
- [Dimension, observations et lecteur existants](../etudes/2026-11-01/orbite-scalaire/ORBITE_ET_FERMETURE.md).
- [Compilateur de l'action sur le produit complet](../etudes/2026-11-01/raccord-initialisation/moments/reprise-globale/COMPILATION_ACTION_EXISTANTE.md).
- [Borne du compilateur différentiel partagé](../etudes/2026-11-01/raccord-initialisation/spectral/reprise-globale/BORNE_DEMONTREE_DU_COMPILATEUR.md).
- [Fusion du spectral et lecture de la forme linéarisée](../etudes/2026-11-01/linearisation-orientee-convolution/FUSION_LINEARISEE.md).
- [État exact historique et dimension](../etudes/2026-10-07/livrables/conjecture-1-5-closed-state/proofs/ActualClosedSubsetTransfer.lean).
