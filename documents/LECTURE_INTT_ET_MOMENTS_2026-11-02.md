# Lecture finale par INTT : rôle des moments et du pont matriciel

Clarification du 2 novembre 2026, après le rappel de l'auteur.
**L'INTT reste la lecture terminale de l'architecture. Le passage par
les moments et la matrice M=e_0 p^T ne sont pas des étapes obligatoires.**

## 1. La chaîne à compiler reste celle du papier

Avec les entrées orientées naturelles,

\[
\widehat R_i[f]=\sum_j B_{ij}q_j\omega^{fd_j},\qquad
\mathcal Z[k]=\operatorname{INTT}_N
 \left[\left(\gamma_n\prod_i\widehat R_i[f]\right)_f\right][k].
\]

La correction du signe est incluse dans `gamma_n`. Une compilation
globale peut fusionner les opérations orientées, les phases, leurs
annulations et les papillons de l'INTT. Elle n'a pas à construire une
amplitude finale ou une liste de moments avant d'exécuter le spectral.

L'identité après fusion déjà établie est

\[
\mathcal Z[k]=\delta_{k,k_*}\lambda(F_0)\widetilde\Omega.
\]

Elle autorise le partage entre toutes les fréquences et le routage
terminal. Elle ne prescrit pas de calculer `lambda(F_0)` comme une source
scalaire autonome avant le spectral : c'est aussi une spécification de
la sortie du calcul conjoint.

## 2. Pourquoi la matrice M avait été introduite

Le théorème n57–n59 porte sur un circuit de la forme `u^T M^K v`.
Pour vérifier son application au lecteur de la variante par moments,
le document précédent a choisi

\[
v=\mu,\quad u=e_0,\quad M=e_0p^T,\quad p_0=1.
\]

L'identité `M^2=M` démontre simplement que cette puissance répète le
même lecteur linéaire :

\[
u^TM^Kv=p^T\mu\quad(K\ge1).
\]

**Cette matrice ne représente pas la production des entrées du lecteur.**
Elle n'apporte aucune nouvelle fusion de la chaîne et aucun gain de
calcul par rapport à la contraction directe. Elle n'est donc pas ajoutée
au circuit à construire. Les lemmes Lean restent vrais comme preuve
de compatibilité entre deux écritures d'un lecteur fourni.

La borne `d=2` ainsi obtenue porte sur cette représentation auxiliaire.
Elle ne fournit pas, par elle-même, une représentation polynomiale de
toutes les opérations orientées avant l'INTT.

## 3. Coût de l'INTT et coût de la compilation conjointe

Sur `N` fils scalaires, l'INTT radix deux possède déjà un circuit d'au
plus `2N log_2 N+N` portes dans la convention du projet. Ce résultat
est acquis. Après la fusion spectrale particulière démontrée dans le
projet, son routage terminal ne crée même plus de porte arithmétique
supplémentaire.

Les fils orientés `prod_i Rhat_i[f]` désignent toutefois des valeurs
dans l'algèbre orientée. Un produit dans cette algèbre ne se compte pas
automatiquement comme une multiplication scalaire. La preuve générale
doit borner le graphe scalaire du calcul conjoint jusqu'aux sorties
de l'INTT, avec les annulations et partages effectivement exploités.

Ce travail n'impose ni le développement en sous-ensembles, ni un état
de moments, ni la construction préalable de chaque fréquence séparée.
Le coût polynomial des papillons est connu ; une borne polynomiale
générale de cette compilation conjointe n'est pas encore établie dans
les travaux relus.

## 4. Résultat de l'audit de I_mu

`I_mu(n)` est le coût d'initialisation de la variante qui matérialise
`mu_j=(L^jG_B)(1)` pour tous `j<=h`. L'audit n'a retrouvé aucune preuve
uniforme `I_mu(n)<=K n^c` pour des constantes indépendantes de `n`.

Les résultats positifs retrouvés sont :

- `mu_0,mu_1` se construisent en `O(n³)` portes.
- Jusqu'à un ordre `r` fixé, les contractions donnent `O(n^(2r+1))` ;
  l'exposant dépend de l'ordre.
- Le compilateur partagé initialise réellement les observations, mais
  son compte dépend d'une taille de DAG intermédiaire non bornée
  polynomialement en général.
- Une autre représentation rationnelle possède bien une initialisation
  et une fusion polynomiales ; son lecteur testé ne conserve pas
  l'annihilation exacte générale. Cette borne n'est pas celle de `I_mu`.

**Une borne polynomiale de I_mu serait suffisante pour cette variante ;
elle n'est pas une obligation imposée à toute compilation de l'architecture.**
L'audit n'a pas produit de nouvelle démonstration de cette borne.

Sources :

- [Cadre de la chaîne complète](CADRE_ACTUEL.md).
- [Fusion exacte de toutes les fréquences](../etudes/2026-11-01/linearisation-orientee-convolution/FUSION_LINEARISEE.md).
- [Circuit conjoint existant, sans moments en entrée](../etudes/2026-11-01/raccord-initialisation/EXECUTION_RACCORD_EXISTANT.md).
- [Initialisation par contractions](../etudes/2026-11-01/raccord-initialisation/moments/CONTRACTIONS_COLLISIONS.md).
- [Initialisation par action partagée](../etudes/2026-11-01/raccord-initialisation/moments/reprise-globale/COMPILATION_ACTION_EXISTANTE.md).
- [Portée de l'invariant rationnel](../etudes/2026-11-01/raccord-initialisation/moments/ADDENDUM_CONTRACTIONS.md).
