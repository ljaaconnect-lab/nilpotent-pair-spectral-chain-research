# Compilation générique polynomiale : résultats déjà acquis

Audit ciblé du 2 novembre 2026, à la demande de retrouver cet outil dans
les travaux existants. **Le compilateur générique polynomial existe bien.**
L'inventaire précédent ne recensait pas suffisamment les outils déjà
construits ; la duplication des différences n'est pas notre seul compilateur.
Ce document rétablit leurs contrats exacts, sans changer l'architecture cible.

## 1. Le résultat le plus explicite : n40, n57 et n59

Le compilateur prend un circuit initial qui construit les entrées de
`M`, `u`, `v`, avec `M` de dimension `r × r`, et un entier `K`. Il produit
un circuit scalaire calculant

\[
u^\top M^K v.
\]

Les produits matriciels sont entièrement développés en portes scalaires
`+` et `×`. Les carrés successifs réutilisent les fils du résultat précédent.
La matrice n'est donc pas une porte primitive dans le décompte.

Si le circuit initial possède au plus `S` portes et si `J(K)` est le
nombre d'instructions du plan binaire, la borne est

\[
\boxed{C\le S+J(K)(2r^3-r^2)+2r^2+r-1},\qquad r\ge1.
\]

Le coût ajouté est exact pour le circuit construit :

| Bloc | Portes scalaires |
|---|---:|
| Un produit dense de deux matrices `r × r` | `2r³−r²` |
| Plan de puissance partagé | `J(K)(2r³−r²)` |
| Contraction terminale avec `u,v` | `2r²+r−1` |
| Construction initiale de `M,u,v` | Comptée une seule fois, au plus `S` |

Le théorème `binary_plan_logarithmic` établit
`J(K) <= 2 Nat.log2 K`. Pour `K>=1`, le coût est donc

\[
O\bigl(S+r^3\log(K+1)+r^2\bigr).
\]

**C'est un vrai outil de compilation générique polynomial en
`S`, `r` et la longueur binaire de `K`, avec lecture terminale comprise.**
Un grand exposant ne provoque pas ici une itération linéaire en `K`.

Pour l'exposant historique `K=n^n−1`, `n>=2`, la borne prouvée dans Lean est

\[
\boxed{C\le S+4r^3n^2+3r^2.}
\]

Le développement n59 compose effectivement le circuit initial et le
compilateur. Pour des constantes naturelles `c,d` indépendantes de `n`,
sous `1<=r<=n^d` et `S<=n^c`, il prouve

\[
\boxed{C\le n^c+4n^{3d+2}+3n^{2d}.}
\]

Ce n'est pas seulement une estimation de nombres d'opérations abstraites :
la sémantique du circuit composé et son nombre de portes sont formalisés.
Le théorème fonctionne sur tout semi-anneau ; les marqueurs formels en
`z` peuvent rester dans les entrées construites.

Sources et noms des théorèmes :

- [PowerCompiler.lean](../etudes/2026-10-07/livrables/conjecture-1-5-suite/proofs/PowerCompiler.lean) : `binary_plan_correct`, `binary_plan_logarithmic`, `central_plan_gate_bound`.
- [MatrixScalarCompiler.lean](../etudes/2026-10-07/livrables/conjecture-1-5-suite/proofs/MatrixScalarCompiler.lean) : `scalar_compiler_correct`, `scalarCircuit_gate_count`, `conditional_scalar_budget`.
- [ConditionalCriterion.lean](../etudes/2026-10-07/livrables/conjecture-1-5-suite/proofs/ConditionalCriterion.lean) : `compose_input_correct`, `polynomial_composed_budget`.
- [Compte rendu n57](../etudes/2026-10-07/livrables/conjecture-1-5-suite/verification/n57/N57_INSIGHTS.md) et [compte rendu n59](../etudes/2026-10-07/livrables/conjecture-1-5-suite/verification/n59/N59_INSIGHTS.md).

Les trois sources ont été recompilées le 2 novembre 2026 avec Lean 4.34.1,
sans modification : **trois réussites, zéro erreur, zéro avertissement**.
Les audits des 35 théorèmes n'utilisent que les axiomes standard
`propext`, `Classical.choice`, `Quot.sound` ; aucun `sorryAx`.
Le [rapport de revalidation](verification-compilation-generique-2026-11-02.json)
conserve les commandes, empreintes et sorties complètes. Cette revalidation
porte sur la construction Lean ; elle ne formalise pas l'exporteur Python.

## 2. Ce que ce théorème prend effectivement en charge

Le compilateur assure déjà la puissance partagée, sa traduction en portes
scalaires, la contraction finale et la composition avec une initialisation
explicite. Ces points ne doivent plus figurer comme outils manquants.

Son application à une expression cible utilise en revanche une identité
exacte de représentation par `uᵀM^K v` et les bornes sur `r` et `S`.
Dans `conditional_target_coefficient`, cette identité est un argument
explicite du théorème. Elle n'est ni un axiome ajouté ni une conclusion
du compilateur.

Pour le raccord actuel, il faut donc vérifier si la représentation fermée
de l'action composée et du lecteur fournit déjà ces données avec les
bonnes bornes. La loi `T_y T_z=T_(y+z)` ne constitue pas, à elle seule,
cette représentation de la composition des différences.

Cette précision fixe le domaine d'application de l'outil acquis ; elle
ne justifie pas de revenir à la duplication comme unique méthode.

La [vérification des constantes c et d](CONSTANTES_C_D_2026-11-02.md)
établit maintenant `d=2` pour le lecteur à observations et le met au
format exact `uᵀM^K v`. La borne d'initialisation `S<=n^c` de ce même
lecteur demeure à établir. Le couple `c=5,d=2` démontré pour le
générateur paramétrique concerne une autre sortie.
Ce pont matriciel représente seulement le lecteur fourni et n'est pas
une étape de la chaîne active ; l'[INTT demeure sa lecture terminale](LECTURE_INTT_ET_MOMENTS_2026-11-02.md).

## 3. Les autres outils polynomiaux retrouvés

Ces coûts concernent des interfaces différentes. Ils ne s'additionnent
pas automatiquement à celui du compilateur n57.

| Outil | Borne établie | Entrées et portée |
|---|---|---|
| Transport rationnel triangulaire générique | `2(p+1) binom(d+1,3)` portes par action | `p>=1` générateurs triangulaires de dimension `d` et un vecteur ; mise à jour de l'état |
| Fusion de `m` de ces transports | `p(m−1)` additions de paramètres, puis une action | Paramètres scalaires ; même loi d'action |
| AD inverse partagée | Au plus `4S` portes supplémentaires pour le gradient complet | Circuit scalaire courant de taille `S` |
| Dérivation directe mémoïsée | Au plus `9S` portes supplémentaires pour `(∂jF,∂j²F)` ; `9nS` pour toutes les diagonales | Circuit courant de taille `S` |
| Scalarisation du DAG aval, théorème B.11 du papier | Au plus `s+b` portes | Coordonnées initiales construites pour `s` portes ; `b` portes scalaires/module de rang un, avec additions et multiplications par un scalaire |

Le transport triangulaire donne en particulier
`n(n+1)²(n+2)/3 = O(n⁴)` pour `p=n`, `d=n+1`.
Il met à jour un état utilisable pour toute observation polynomiale
non commutative ; le coût de calcul de l'observation choisie reste à
compter. Les identités de fusion sont formalisées dans Lean ; le
décompte exact du programme de transport n'est pas formalisé dans Lean.

Pour les dérivations, la polynomialité porte sur la taille `S` du circuit
fourni à une passe. La variante directe du projecteur donne explicitement
`S_(r+1) <= (9n+1)S_r+3n+2`. Le coût local est établi ; une borne polynomiale
uniforme en `n` sur toutes les tailles intermédiaires n'en découle pas.
Les contrôles du compilateur Python ne sont pas une formalisation Lean
de son coût.

Sources :

- [Transport rationnel et coût exact](../etudes/2026-11-01/reprise-flot-rationnel/REPRISE.md).
- [AD inverse](../etudes/2026-11-01/raccord-initialisation/dualite/AD_INVERSE.md).
- [Borne du compilateur direct mémoïsé](../etudes/2026-11-01/raccord-initialisation/spectral/reprise-globale/BORNE_DEMONTREE_DU_COMPILATEUR.md).
- [Papier avec raccordement, p.44–45 et p.61](../sources/papiers/annihilation_raccord_spectral_demonstrations.pdf).

## 4. Correction apportée à l'inventaire

La récurrence `S_(r+1)<=2S_r+N+2` décrivait seulement l'implémentation
locale par duplication des différences. Elle ne recensait pas l'ensemble
des compilateurs disponibles et ne doit pas servir de conclusion sur
leur coût général.

L'état exact est : **la compilation polynomiale de plusieurs classes
de représentations est acquise, avec un compilateur générique n57–n59
dont la correction, la lecture et le coût sont vérifiés dans Lean.**
Le point à raccorder à l'architecture actuelle est une représentation
exacte appartenant à l'une de ces classes, avec ses paramètres bornés
depuis les données originales.

Cet audit ne réintroduit pas une méthode abandonnée et ne prétend pas
avoir établi ce dernier raccord. Il corrige l'inventaire des outils disponibles.
