# Littérature : algèbres de zeons et compilation en portes scalaires

Date : 2026-11-02. Branche de recherche déléguée « algèbres ».

## Résultat de cette branche

Le nom exact de notre algèbre est **algèbre de zeons** :
\[
A_n=K[q_1,\ldots,q_n]/(q_1^2,\ldots,q_n^2).
\]
La correspondance est littérale : générateurs commutatifs, carré nul, base \(q_S\), produit nul en cas de collision. Le lemme 14 de Brand–Dell–Husfeldt, *Extensor-Coding*, donne précisément cette identification et une compilation des opérations en \(2^n\operatorname{poly}(n)\) opérations du corps. Le théorème 1 de Björklund–Husfeldt–Kaski–Koivisto donne la borne explicite \(O(n^2 2^n)\) pour chaque multiplication générale.

Ces outils sont des compilateurs exacts et adaptés. Ils ne donnent pas, pour \(n\) générateurs génériques, la borne polynomiale en \(n\) recherchée. Aucun théorème applicable trouvé dans cette branche ne la donne. Cette constatation bibliographique n'est pas un théorème d'impossibilité pour les circuits généraux.

## Sources primaires vérifiées

| Source | Énoncé vérifié | Adéquation et limite |
|---|---|---|
| [Björklund, Husfeldt, Kaski, Koivisto, *Fourier Meets Möbius: Fast Subset Convolution*, STOC 2007, th. 1 et §2](https://www.cs.helsinki.fi/u/mkhkoivi/publications/stoc-2007.pdf) | Convolution \(h(S)=\sum_{T\subseteq S}f(T)g(S\setminus T)\) en \(O(n^2 2^n)\) additions/multiplications dans tout anneau, même non commutatif. | Compile exactement une fusion de deux éléments de \(A_n\). Valable modulo \(Q\), sans hypothèse de division. Toutes opérations scalaires comptées. |
| [Brand, Dell, Husfeldt, *Extensor-Coding*, 2018, lemme 14 et §2.3](https://arxiv.org/html/1804.09448) | La sous-algèbre engendrée par \(e_j\wedge e_{n+j}\) est commutative, de dimension \(2^n\), générateurs de carré nul ; opérations en \(2^n\operatorname{poly}(n)\) opérations du corps. | Identifie notre orientation à un relèvement extérieur de degré pair. Employer directement des vecteurs extérieurs de degré un changerait les signes. Le relèvement conserve le nombre exponentiel de coordonnées. |
| [Schott, Staples, *On the Complexity of Cycle Enumeration using Zeons*, introduction, cor. 2.10 et th. 2.12](https://members.loria.fr/RSchott/staceyTOCmay10.pdf) | Distingue \(O(n^\alpha\log k)\) opérations dans l'algèbre des opérations sur ses coordonnées. Coût de leur méthode \(O(n^{\alpha+1}2^n)\) au pire, et \(O(n^{\alpha+k-1})\) pour \(k\) fixé. | Source directement pertinente sur la distinction entre une porte zeon et des portes scalaires. Le polynôme à degré dépendant de \(k\) n'est pas uniforme lorsque \(k=n\). Le problème de cycles est leur application, pas une réduction de notre objectif. |
| [Bläser, *A Complete Characterization of the Algebras of Minimal Bilinear Complexity*, SIAM J. Comput. 2004](https://doi.org/10.1137/S0097539703438277) | Rappelle la borne d'Alder–Strassen \(R(A)\ge2\dim A-t\), \(t\) nombre d'idéaux maximaux bilatères ; caractérisation du cas d'égalité sur tout corps. | Contrôle un compilateur bilinéaire universel de la multiplication de deux éléments arbitraires. Pour \(A_n\), local de dimension \(2^n\), \(t=1\). Ne borne pas un circuit arbitraire dont les opérandes sont des produits structurés et la sortie une seule lecture. |
| [Staples, *Weakly Unitary Zeon Matrices*, arXiv:2610.33891v1, 24 octobre 2026](https://arxiv.org/html/2610.33891v1) | Définit des matrices spectrales à coefficients zeons ; les expressions de valeurs propres gardent des sommes sur \(I\subseteq[n]\). Aucun théorème de compilation scalaire polynomial en \(n\) identifié. | Prépublication récente. Le théorème 3.9 contient en outre une contradiction élémentaire avec la définition 3.5, vérifiée ci-dessous. Ne pas l'utiliser comme théorème de compilation. |

Qualité : quatre articles originaux présentant leurs propres constructions et coûts ; une prépublication originale récente dont un énoncé a été contrôlé directement et échoue. Les portails bibliographiques, ResearchGate et les articles sur le foncteur de Frobenius en caractéristique positive n'ont pas été utilisés comme preuves.

## Compilation générale en toutes portes : paramètre exact

Soit \(A\) une algèbre de dimension \(d\), munie d'un algorithme bilinéaire explicite de rang \(R\) :
\[
ab=\sum_{\ell=1}^R \alpha_\ell(a)\beta_\ell(b)c_\ell.
\]

Ce rang compte les multiplications bilinéaires essentielles. Il ne faut pas y assimiler automatiquement le nombre total de portes : les formes linéaires et la reconstruction sont à compiler.

Dérivation élémentaire (notre comptage, pas un nouvel énoncé attribué aux articles) :

- chacune des \(2R\) formes linéaires sur \(d\) coordonnées coûte au plus \(2d-1\) portes, multiplications par des constantes incluses ;
- les produits des deux formes coûtent \(R\) portes ;
- les \(d\) coordonnées de reconstruction coûtent au plus \(d(2R-1)\) portes.

D'où
\[
C_\times(A)\le 6dR-R-d\le6dR.
\]
Une addition dans \(A\) coûte \(d\) additions scalaires et une lecture linéaire coûte au plus \(2d-1\) portes. Un circuit ayant \(m\) multiplications et \(a\) additions dans \(A\) se compile donc en
\[
C_{\rm scalaire}\le6dRm+da+C_{\rm entrées}+C_{\rm lecture}.
\]

**Conclusion positive exacte :** une représentation de dimension \(d(n)\le n^u\), avec un algorithme bilinéaire explicite de rang \(R(n)\le n^v\) et entrées/lecture calculables polynomialement, donne une compilation de degré fixe. Mais les articles sur les zeons utilisent \(d=2^n\) ; ils ne construisent pas la représentation \(d=\operatorname{poly}(n)\).

Pour une famille uniforme de circuits, il faut aussi pouvoir générer ces constantes et formes en temps polynomial. Une existence non effective de petits rangs ne suffit pas à un compilateur uniforme.

La proposition 5 de Brand–Pratt, [*An Algorithmic Method of Partial Derivatives*](https://arxiv.org/abs/2005.05143), retrouvée également dans cette branche mais étudiée par l'agent principal, formalise un raccord étroit via l'algèbre apolaire. Attention à son modèle « multiplications non scalaires », qui laisse gratuites certaines opérations linéaires.

## Raccord exact avec l'architecture par fréquence

Pour
\[
L_i[f]=\sum_j B_{ij}\omega^{fd_j}q_j,\qquad
W[f]=\gamma\prod_i L_i[f],
\]
la phase \(\omega^{fd_j}\) est une constante scalaire ; elle ne change ni la règle de fusion ni la dimension de l'algèbre.

Le compilateur de convolution donne une borne valide
\[
O\!\left(N(n-1)n^2 2^n\right)
\]
pour appliquer \(n-1\) fusions générales indépendamment aux \(N\) fréquences. C'est une borne de référence et pas la meilleure pour ces opérandes particuliers.

En effet, l'ordre successif garde un facteur de degré un à chaque étape :
\[
p_i(S)=\sum_{j\in S}B_{ij}\omega^{fd_j}p_{i-1}(S\setminus\{j\}),\quad |S|=i.
\]
Le nombre de termes de toutes les sommes est
\[
\sum_{i=1}^n i\binom ni=n2^{n-1}.
\]
Cela donne déjà \(O(n2^n)\) portes par fréquence dans cette représentation, avant préparation et INTT. Ce décompte évite de présenter le coût d'une fusion générale comme une borne intrinsèque des produits structurés. Il ne constitue pas la représentation compacte recherchée.

La préparation des phases et l'INTT sur les lectures scalaires ajoutent des coûts polynomiaux en \(n,N\). Elles ne changent pas, à elles seules, le nombre de coordonnées nilpotentes manipulées par ces compilateurs.

## Ce que la lecture finale permet réellement d'éliminer

Observation algébrique élémentaire, prouvée ici et non attribuée à une source externe :

\[
\lambda(a)=[q_1\cdots q_n]a,\qquad
\lambda(q_Sq_T)=
\begin{cases}1&T=[n]\setminus S,\\0&\text{sinon.}\end{cases}
\]

La matrice de l'accouplement \((a,b)\mapsto\lambda(ab)\) est une matrice de permutation, donc non dégénérée sur tout corps. Ainsi
\[
\{a\in A_n:\lambda(ab)=0\text{ pour tout }b\in A_n\}=0.
\]

Un quotient linéaire universel préservant la lecture après **toute continuation possible** ne peut donc supprimer un élément non nul de \(A_n\). En revanche, cette observation ne s'applique pas à une méthode globale non linéaire qui compile directement les entrées structurées et le lecteur, sans transporter un état arbitraire de \(A_n\).

De même, il n'existe pas de diagonalisation fidèle de l'algèbre entière par des évaluations dans des corps : tout morphisme d'algèbres envoie \(q_j\) sur un scalaire de carré nul, donc sur zéro. Une NTT sur l'indice cyclique et une diagonalisation de la structure nilpotente sont deux opérations différentes. Ceci n'interdit pas d'exploiter la NTT conjointement à un autre mécanisme.

## Contrôle de la prépublication spectrale de 2026

Le [théorème 3.9 de la version v1](https://arxiv.org/html/2610.33891v1) prend un vecteur unitaire \(u=(z_1,\ldots,z_n)\), aux composantes distinctes, pose explicitement \(U=uu^\dagger\), qualifié de « rank-one projector », puis affirme que \(U\Psi_1\) est une « weakly unitary zeon matrix » et a des valeurs propres de parties scalaires \(z_j\). Ces deux courtes expressions sont des citations exactes de l'énoncé ; l'identification de \(U\) comme matrice de rang un ne dépend donc pas d'une interprétation.

La définition 3.5 impose qu'une matrice faiblement unitaire soit inversible ; même sans cette exigence explicite, la partie scalaire de \(\Xi^{\hat\dagger}\Xi=I+\Gamma\) impose \((\mathfrak C\Xi)^\dagger(\mathfrak C\Xi)=I\).

Prenons le graphe vide sur deux sommets et \(u=(3/5,4/5)\). La formule (3.2) donne \(\Psi_1=I\). Alors
\[
U\Psi_1=U=\frac1{25}\begin{pmatrix}9&12\\12&16\end{pmatrix}.
\]
Cette matrice a rang un, déterminant nul et valeurs propres \(0,1\), au lieu des parties scalaires annoncées \(3/5,4/5\). Elle n'est pas faiblement unitaire. Cette vérification réfute l'énoncé 3.9 tel qu'écrit dans v1, sans prétendre réfuter tous les autres résultats du papier. Même corrigé, ce résultat ne fournit pas une borne de compilation scalaire.

## Traçabilité de la recherche

Compteur demandé par la compétence Exa :

- requested_result_slots : **30**, somme des numResults des six appels, incluant un appel refusé par validation de schéma puis repris ; c'est le compteur nommé sources_reviewed par la compétence Exa, qui ne mesure pas des documents intégralement lus ;
- successful_result_slots : **25**, cinq recherches effectivement exécutées et 25 résultats retournés ; l'appel refusé n'a produit aucune source ;
- 25 URL de résultats distinctes ; plusieurs sont des versions ou notices du même article ;
- lectures complémentaires de sources connues par Exa Fetch puis web.open quand Exa n'exposait que le début ;
- aucune exhaustivité mondiale revendiquée.

Les cinq angles exécutés : convolution rapide des sous-ensembles ; extensor/zeon coding ; rang bilinéaire des algèbres ; dualité Frobenius ; calcul via algèbres apolaires.

URL retournées, dédupliquées :
1. https://dl.acm.org/doi/10.1145/1250790.1250801
2. https://www.cs.helsinki.fi/u/mkhkoivi/publications/stoc-2007.pdf
3. https://arxiv.org/abs/cs/0611101
4. https://researchportal.helsinki.fi/en/publications/fourier-meets-m%C3%B6bius-fast-subset-convolution/
5. https://www.lunduniversity.lu.se/publication/d23b0760-54e7-470f-a423-3e7c167049ba
6. https://arxiv.org/html/1804.09448
7. https://dlnext.acm.org/doi/10.1145/3188745.3188902
8. https://arxiv.org/pdf/2304.02091
9. https://researcher.itu.dk/ws/files/83633902/1804.09448.pdf
10. https://arxiv.org/html/2204.10819v2
11. https://doi.org/10.1137/s0097539703438277
12. https://doi.org/10.1007/3-540-48224-5_7
13. https://www.researchgate.net/publication/226966020_Lower_bounds_for_the_bilinear_complexity_of_associative_algebras
14. https://dlnext.acm.org/doi/10.5555/646254.683951
15. https://doi.org/10.1109/ccc.2002.1004346
16. https://ar5iv.labs.arxiv.org/html/2105.04782
17. https://doi.org/10.48550/arxiv.2203.09902
18. https://www.maths.gla.ac.uk/~ajb/SMSTC/HopfAlgebrasNotes.pdf
19. https://www.math.uchicago.edu/~may/VIGRE/VIGRE2007/REUPapers/FINALAPP/Allegretti.pdf
20. https://ar5iv.labs.arxiv.org/html/2009.01384
21. http://sites.cs.ucsb.edu/~daniello/papers/countingPathsSODA2021.pdf
22. https://arxiv.org/abs/1807.06194
23. https://arxiv.org/abs/2005.05143
24. https://theoretics.episciences.org/16626/pdf
25. https://drops.dagstuhl.de/storage/00lipics/lipics-vol198-icalp2021/LIPIcs.ICALP.2021.38/LIPIcs.ICALP.2021.38.pdf

