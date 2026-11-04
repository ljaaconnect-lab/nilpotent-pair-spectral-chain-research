# Outils de la littérature pour compiler les produits orientés en portes scalaires

Recherche du 2 novembre 2026, sur quatre axes complémentaires : circuits
arithmétiques, algèbres nilpotentes, contractions de tenseurs, lecture duale
et apolarité. Les recherches incluent des publications de 2025 et 2026.

**Résultat : plusieurs théorèmes de compilation exactement pertinents ont
été identifiés, mais aucun des théorèmes vérifiés ne fournit à lui seul une
borne polynomiale générale en n pour notre chaîne.** Ce constat porte sur
les sources consultées, et ne constitue ni une preuve d'absence dans toute
la littérature ni une impossibilité mathématique.

Le meilleur raccord direct au produit orienté est la compilation dans
l'algèbre apolaire de Brand–Pratt. Le cadre de fermeture compacte à étudier
pour une représentation différente est celui des matchgates et des
contractions pfaffiennes. Leurs hypothèses ne sont pas déjà satisfaites par
nos facteurs généraux. Les compiler exige de fournir la représentation,
depuis a,z, et de vérifier sa fidélité à la sortie de toute la chaîne.

## 1. Spécification conservée

On travaille dans

\[
A_n=K[q_1,\ldots,q_n]/(q_1^2,\ldots,q_n^2),\qquad q_iq_j=q_jq_i.
\]

Les facteurs restent

\[
L_i[f]=\sum_j B_{ij}\omega^{fd_j}q_j,
\qquad B_{ij}=(1+a_{ij}^2)z^{2^{(i-1)n+j-1}}.
\]

Le produit orienté, le signe universel corrigé et l'INTT font partie de
la même spécification. La fonctionnelle terminale est une notation de
lecture, jamais une entrée supposée connue. Les phases et la fusion déjà
prouvée peuvent être partagées. Le degré exponentiel en z n'est pas une
taille de circuit : ses puissances se préparent par carrés successifs.
Inversement, un algorithme polynomial en ce degré dense ne devient pas
polynomial en n.

Un théorème est directement suffisant seulement s'il fournit : exactitude
sur les entrées originales ; portes scalaires binaires + et × ; coût des
préparations et de la lecture ; paramètres uniformément polynomiaux en n ;
compatibilité avec le corps de la NTT. Les constantes de corps peuvent
être des feuilles. Une division par une donnée variable n'est pas une
porte autorisée dans cette version du modèle.

## 2. Carte des résultats vérifiés

| Outil et source primaire | Garantie effectivement établie | Application à notre chaîne |
|---|---|---|
| [Brand–Pratt, *An Algorithmic Method of Partial Derivatives*, §4.1, propositions 4–5](https://arxiv.org/abs/2005.05143) | Compilation d'un circuit dans l'algèbre apolaire ; coût O(R(A_f) S) en multiplications entre quantités variables | Correspondance exacte avec A_n, mais dimension 2^n ; les opérations linéaires doivent aussi être comptées |
| [Björklund–Husfeldt–Kaski–Koivisto, *Fourier meets Möbius*, théorème 1](https://www.cs.helsinki.fi/u/mkhkoivi/publications/stoc-2007.pdf) | Convolution des sous-ensembles en O(n² 2^n) opérations d'anneau | Fusion exacte de deux états généraux ; ne donne pas poly(n) |
| [Arvind–Joglekar–Srinivasan, *Arithmetic Circuits and the Hadamard Product of Polynomials*](https://arxiv.org/abs/0907.4006) | Produit de Hadamard non commutatif : ABP × ABP de taille O(S_1 S_2), ou circuit de degré polynomial × ABP avec surcoût polynomial | Il faut un petit filtre exact ; un filtre linéaire universel des mots sans répétition a une largeur centrale au moins binom(n,floor(n/2)) |
| [Bostan–Lecerf–Schost, *Tellegen's Principle into Practice*, propositions 1–2](https://mathexp.eu/bostan/publications/BoLeSc03.pdf) | Transposition d'un programme linéaire avec coût essentiellement identique | Permet de déplacer le lecteur vers les produits ; ne réduit pas automatiquement la représentation du lecteur transporté |
| [Bravyi, *Contraction of matchgate tensor networks on non-planar graphs*, théorèmes 1 et 3](https://arxiv.org/abs/0801.2989) | Représentation quadratique en l'arité des matchgates et contraction de coût polynomial × 2^(2g), g étant le genre | Fermeture compacte réelle ; identité matchgate et réseau de petit genre restent à construire pour notre sortie |
| [Cai–Gorenstein, *Matchgates Revisited*](https://arxiv.org/abs/1303.6729) | Identités algébriques caractérisant les signatures matchgate | Donne un test précis de fermeture, plus fort que la seule nilpotence ou commutation |
| [Mahajan–Subramanya–Vinay, *A Combinatorial Algorithm for Pfaffians*, §7](https://eccc.weizmann.ac.il/report/1999/030/download/) | Calcul du Pfaffien par opérations d'anneau, sans division ; réalisation séquentielle O(S⁴) | Fournit la dernière compilation scalaire si un raccord pfaffien polynomial est explicitement construit |
| [Markov–Shi, *Simulating quantum computation by contracting tensor networks*](https://arxiv.org/abs/quant-ph/0511069) | Contraction de coût polynomial dans la taille, exponentiel dans la largeur pertinente | Suffit pour largeur logarithmique et dimension des indices bornée ; cette propriété n'est pas établie pour notre réseau dense |
| [Valiant–Skyum–Berkowitz–Rackoff, *Fast Parallel Computation of Polynomials Using Few Processors*](https://doi.org/10.1137/0212043) | Réduction de profondeur d'un circuit déjà donné ; théorème 3 de taille O(C³), profondeur O(log C log D), D degré formel | Réorganise un circuit petit déjà disponible ; ne compile pas gratuitement une multiplication dans A_n |
| [Andrews–Wigderson, *Constant-Depth Arithmetic Circuits for Linear Algebra Problems*, v2](https://arxiv.org/html/2404.10839v2) | Formules de taille polynomiale pour des problèmes univariés et matrices structurées, en caractéristique zéro ou suffisamment grande, avec conventions précises sur divisions et sélection | Utile après une réduction à une taille dense polynomiale ; le lemme 2.7 d'extraction d'un coefficient dépend du degré d, pas de log d |
| [Björklund–Kaski–Koana–Nederlof, *Kronecker Scaling of Tensors*, ICALP 2026, théorèmes 1.1–1.2](https://drops.dagstuhl.de/doi/10.4230/LIPIcs.ICALP.2026.36) | Décomposition constructive des tenseurs de tripartition équilibrée ; rang R(P_d)≤Λ^d implique circuits O(Γ^n) pour Γ>Λ | Résultat de fusion très pertinent, mais sa conclusion est exponentielle dans n et l'amélioration du taux dépend du rang ; ce n'est pas la borne polynomiale cherchée |

Les notes de branches donnent les hypothèses, conventions de taille et
liens de lecture plus précisément : [algèbres](recherche-compilation-2026-11-02/algebres.md),
[circuits](recherche-compilation-2026-11-02/circuits.md),
[tenseurs](recherche-compilation-2026-11-02/tenseurs.md).

## 3. Le raccord le plus exact : algèbre apolaire

Prenons le polynôme fixe f(x)=x_1...x_n et le circuit compact

\[
g_f(x)=\prod_{i=1}^n\sum_j B_{ij}\omega^{fd_j}x_j.
\]

Pour éviter toute ambiguïté de notation, l'indice f de g_f désigne ici la
fréquence ; le polynôme test x_1...x_n est fixe. La quantité
(∂_1...∂_n)g_f est exactement le coefficient que conserve l'annihilation
au degré n. Cette égalité identifie une interface mathématique ; elle ne
remplace pas le projet par un calcul autonome de l'amplitude et ne remet
pas en service les jets abandonnés.

Brand–Pratt travaillent en caractéristique zéro dans leur formulation
générale. Leur exemple 1 identifie explicitement

\[
\mathcal A_{x_1\cdots x_n}
=K[\partial_1,\ldots,\partial_n]/(\partial_1^2,\ldots,\partial_n^2).
\]

Pour ce monôme carré-libre, l'identification reste vraie dans tout corps :
les dérivées par sous-ensembles donnent des monômes distincts avec
coefficient un, et tous les carrés de dérivées l'annulent. Il n'y a pas
d'inversion de factorielle. C'est exactement A_n.

Leur proposition 5 donne O(R(A_f)|C|) multiplications non scalaires,
c'est-à-dire entre deux quantités variables. Elle ne compte pas à elle
seule toutes les additions et multiplications par constantes que notre
modèle veut compter. Leur proposition 4 donne R(A_f)≥dim A_f. Ici la
dimension est 2^n. L'application directe du théorème ne fournit donc
pas des paramètres polynomiaux en n.

Il s'agit d'une limite de cette application, pas d'un minorant des
circuits scalaires globaux pour la sortie.

### Conversion explicite en toutes les portes scalaires

Soit une algèbre A de dimension d munie d'une décomposition bilinéaire
explicite de rang R :

\[
(xy)_k=\sum_{\rho=1}^R c_{k\rho}
 \left(\sum_{u=1}^d a_{\rho u}x_u\right)
 \left(\sum_{v=1}^d b_{\rho v}y_v\right).
\]

Les deux familles de formes linéaires coûtent au plus 2R(2d−1) portes,
les produits R portes, la reconstruction d(2R−1) portes. D'où

\[
C_\times\le 6dR-R-d\le6dR.
\]

Un circuit dans A comportant m multiplications et a additions admet donc

\[
\boxed{C_{\rm scalaire}\le
C_{\rm préparation}+6dRm+da+C_{\rm lecture}.}
\]

C'est un véritable théorème de compilation, avec décompte de toutes les
portes. Si d,R,m,a et les coûts d'extrémité sont polynomiaux en n, la
chaîne est polynomiale. Ce décompte est notre développement élémentaire
de la construction bilinéaire ; il n'est pas présenté comme une nouvelle
borne générale de d ou de R pour A_n.

## 4. Compilation par un filtre de mots : un autre contrat exact

Un programme de branchement algébrique (ABP) représente un polynôme
non commutatif par des chemins dans un graphe en couches. Le produit
\(\prod_i\sum_j B_{ij}X_j\) possède une représentation compacte : l'ordre
des facteurs distingue les positions des lettres.

Le produit de Hadamard d'Arvind–Joglekar–Srinivasan filtre ces mots
coefficient par coefficient. Si le filtre exact possède largeur w et
des transitions constantes c_(i,u,v,j), on peut construire directement

\[
A_i[f]_{uv}=\sum_j c_{i,u,v,j}B_{ij}\omega^{fd_j}
\]

puis propager un vecteur de largeur w. Toutes les portes de préparation
des matrices et de propagation sont comptées, sans compter une matrice
comme une porte :

\[
C_f\le (2n^2+n)w^2+1
\]

après la préparation partagée de B. Avec N≤2n fréquences, une borne
conservatrice, avant de tirer parti de toutes les fusions, est

\[
C_{\rm total}\le C_B+2n[(2n^2+n)w^2+1]+C_{\rm INTT}.
\]

Ainsi w≤K n^r donnerait un exposant 3+2r pour ce bloc. Cependant,
le filtre universel des mots sans répétition a une matrice de
préfixes/suffixes contenant l'identité de taille binom(n,k) à la coupure
k. Toute représentation linéaire de ce filtre exige au moins cette
largeur. Cette interface universelle ne possède donc pas de filtre
linéaire de largeur polynomiale. Un raccord global dépendant des facteurs et
ne matérialisant pas cette interface serait un autre problème.

## 5. Fermeture compacte non linéaire : matchgates et Pfaffiens

Les signatures matchgate constituent un cas où un tenseur ayant
potentiellement 2^d coordonnées est décrit par O(d²) paramètres et où
des contractions appropriées préservent une structure calculable.
Le paramètre de compression est alors une matrice antisymétrique et
des données canoniques, pas une liste de tous les coefficients.

Bravyi donne un algorithme pour un réseau de v sommets, plongé sur une
surface orientable de genre g et muni d'une coupe planaire de m arêtes,
de coût

\[
O((v+m)^6)+O(m^3)2^{2g}.
\]

Le théorème est une garantie de contraction arithmétique, dont il faut
encore préciser les divisions si on réclame un circuit universel +,×.
On peut obtenir une garantie plus conservatrice sans divisions variables
en utilisant les gadgets planaires et la compilation des Pfaffiens.

**Contrat suffisant pour notre modèle.** Supposons qu'un générateur
en portes +,× construise depuis a,z les poids d'un graphe pondéré à S
sommets, avec un plongement de genre g indépendant des valeurs des
entrées, et une identité exacte entre son polynôme des couplages parfaits
pondérés et l'observation terminale orientée corrigée. Le graphe, son
plongement et les orientations nécessaires doivent être construits
uniformément en temps polynomial dans leur taille. Les signes de la
formule de surface et ses facteurs
1/2^g sont des constantes ; le corps doit être de caractéristique
différente de deux. Alors les 2^(2g) Pfaffiens peuvent être compilés
sans divisions variables, en

\[
\boxed{C\le C_{\rm génération}+O(2^{2g}S^4)
       +C_{\rm préparation/lecture\ restante}.}
\]

La borne O(S⁴) provient de la réalisation par opérations d'anneau de
Mahajan–Subramanya–Vinay. Elle n'utilise pas l'élimination avec divisions
par des pivots qui pourraient s'annuler.
La formule à 4^g Pfaffiens est donnée explicitement par
[Galluccio–Loebl, théorème 3.10](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v6i1r6/pdf/).
Il s'agit d'une identité polynomiale à coefficients dans Z[1/2], ce qui
permet son emploi sur le corps impair de notre architecture.

Si l'on part de signatures canoniques de M sommets et ports au total,
le théorème 3 de Bravyi les transforme en gadgets planaires de taille
S=O(M²), donnant la borne conservatrice

\[
C\le C_{\rm génération}+O(2^{2g}M^8)
       +C_{\rm préparation/lecture\ restante}.
\]

Il faut fournir les paramètres canoniques et leurs circuits, pas
supposer leur extraction gratuite depuis des tables de taille 2^d.
Des hypothèses S≤K_S n^d, g≤b log_2 n et C_génération≤K_G n^e
donneraient effectivement un exposant absolu

\[
c=\max\{e,4d+2b,2\},
\]

en supposant explicitement un coût restant au plus K_R n² : c'est le
cas de la préparation B et de l'INTT de longueur N≤2n. Si un autre raccord
ou lecteur reste à compiler, son exposant doit être ajouté au maximum.
Cette implication est prouvée ; son hypothèse de représentation de
notre instance générale n'est pas construite.

### Vérification sur nos facteurs actuels

Deux encodages ne doivent pas être confondus.

1. Dans un réseau biparti à contraintes EXACT1, les facteurs locaux sont
   des matchgates. Le réseau dense est K_(n,n), dont tout plongement
   orientable cellulaire a genre au moins (n−2)²/4 pour n≥3. En effet,
   chaque face a au moins quatre côtés, donc 2−2g=v−e+f≤v−e/2, avec
   v=2n,e=n². La contraction de petit genre ne s'applique pas à ce
   réseau naturel. Cela ne prouve pas qu'aucun autre réseau ne convient.

2. Dans le relèvement direct q_j=θ_(2j−1)θ_(2j), un facteur
   L=Σ_j b_j θ_(2j−1)θ_(2j) n'est généralement pas une signature
   matchgate. Sur quatre ports, il a T_12=b_1 et T_34=b_2, les autres
   coefficients pairs pertinents étant nuls. L'identité nécessaire

   \[
   T_\varnothing T_{1234}-T_{12}T_{34}
      +T_{13}T_{24}-T_{14}T_{23}=0
   \]

   devient −b_1b_2=0, fausse pour des poids généraux non nuls. Les phases
   spectrales non nulles et un signe universel ne rendent pas ce produit
   nul. Le relèvement pair garantit la commutation et l'annihilation,
   mais pas la fermeture matchgate.

Ce cadre offre un test de raccord concret. Il ne justifie pas de traiter
le produit orienté général comme déjà gaussien, pfaffien ou de petit genre.

## 6. Lecture transposée et résultats récents

Le principe de Tellegen transporte un lecteur λ à travers une
multiplication M_L:x↦Lx en remplaçant λ par M_L^*λ. La composition
se renverse, sans exiger la table finale complète. Mais le théorème
préserve essentiellement le coût d'un programme linéaire déjà donné.
Il ne donne pas, seul, un petit circuit pour tous les lecteurs ainsi
transportés. C'est une règle de compilation utile pour exploiter une
fermeture démontrée, pas une preuve de cette fermeture.

Le [théorème 13 de Kaski–Koivisto–Nederlof](https://arxiv.org/html/1203.4063)
extrait un coefficient d'un circuit sur l'algèbre de groupe
K[(Z/2Z)^n], en caractéristique différente de deux, avec O*(S) opérations
lorsque S borne le support de toute sa sortie avant extraction.
La garantie est probabiliste (succès au moins 1/2) : le fait que notre
table finale n'ait qu'un slot utile ne fournit ni cette borne de support
dans l'algèbre requise, ni un lecteur déterministe exact.

Le papier ICALP 2026 sur le Kronecker scaling est proche de notre question
de fusion à tout ordre. Son théorème 1.2 transforme une hypothèse de rang
R(P_d)≤Λ^d en circuits uniformes O(Γ^n), pour tout Γ>Λ. Il ne transforme
pas un exposant constant dans la dimension d'un tenseur en polynomial
dans le nombre de générateurs. On peut réutiliser sa technique de
décomposition, mais pas citer sa conclusion comme C(n)≤Kn^c.

Une prépublication de 2026 sur les matrices de zéons faiblement unitaires
a aussi été examinée. Son théorème 3.9, tel qu'écrit, possède un
contre-exemple élémentaire : le projecteur de rang un U=uu* est singulier
alors que la conclusion exigerait UΨ_1 inversible ; le graphe vide donne
Ψ_1=I. Le détail, les références exactes et la portée limitée de cette
observation figurent dans la note algèbres. Cette affirmation n'est pas
retenue comme théorème de compilation. Aucun jugement sur tous les
résultats de cette prépublication n'est déduit de ce seul point.

## 7. Ce que cette revue ajoute au projet

Le nom standard de notre algèbre est identifié, et trois contrats de
compilation avec coûts scalaires explicites sont disponibles : algèbre
de dimension d et multiplication bilinéaire de rang R ; filtre ABP de
largeur w ; contraction pfaffienne de taille S et genre g. Le troisième
illustre une représentation compacte non linéaire qui n'est pas couverte
par notre ancienne borne sur les états linéaires universels.

Pour obtenir le résultat général, il faut encore une construction
depuis a,z respectant les hypothèses de l'un de ces contrats, ou un
autre théorème réellement applicable. Les deux encodages matchgate
naturels ont été examinés et ne suffisent pas. Aucun coût d'initialisation,
filtre, changement de représentation ou lecture n'est supposé gratuit.

Cette reprise est une revue mathématique sourcée et des décomptes écrits.
Elle ne revendique aucun nouveau certificat Lean ni la résolution de la
borne polynomiale générale. Les résultats formalisés des études antérieures
gardent exactement leur portée.

Traçabilité : 25 recherches Exa réussies sur quatre axes, représentant
173 emplacements de résultats, avec doublons et résultats écartés. Ces
173 notices ne sont pas 173 articles lus intégralement. Les théorèmes
retenus ont été vérifiés dans leurs sources primaires. Les métadonnées
sont dans [recherche.json](recherche-compilation-2026-11-02/recherche.json).
