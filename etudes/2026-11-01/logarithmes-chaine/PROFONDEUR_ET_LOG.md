# Logarithmes, équilibrage et action scalaire du lecteur existant

Cette note conserve le lecteur du projet :

\[
h=\binom n2,\qquad L=\frac12\sum_{j=1}^n s_j^2\partial_j^2,
\qquad \Pi=\pi_n(L)=\prod_{r=1}^h(I-L/r).
\]

Son entrée est le produit compact \(G_B(s)=\prod_i\sum_jB_{ij}s_j\),
avec les \(B_{ij}\) préparés depuis \(a,z\). La question est le coût
scalaire de \(\Pi G_B\), puis des phases et de l'INTT. Aucune des
identités ci-dessous ne donne gratuitement une porte d'application
d'opérateur, de dérivation, de logarithme ou d'exponentielle.

## 1. Ce que donne exactement un arbre équilibré

Les facteurs \(I-L/r\) commutent. Leur produit possède donc un arbre
de composition de profondeur \(\lceil\log_2h\rceil\), avec \(h-1\)
compositions. Cela réduit la profondeur de la *description par opérateurs*.

Pour voir pourquoi l'action n'est pas automatiquement réduite, supposons
que l'implantation scalaire d'une action \(A\) transforme un circuit de
taille \(S\) en un circuit de taille au plus \(cS+b\). Alors

\[
\operatorname{taille}(A\circ A)(S)\le c(cS+b)+b
=c^2S+(c+1)b.
\]

Après \(d\) étapes de doublement, la puissance décrite est \(A^{2^d}\)
et le facteur multiplicatif demeure \(c^{2^d}\), non \(c^d\).
Équilibrer une composition ne justifie donc pas de remplacer \(h\)
par \(\log h\) dans le majorant \((9n+1)^h\).

Le même point s'applique au calcul des coefficients : on peut multiplier
les \(h\) polynômes \(1-X/r\) par un arbre équilibré et compiler leurs
coefficients en un nombre polynomial de portes. Cela construit
\(\pi_n(X)\). Cela ne construit pas encore les actions \(L^kG_B\).

## 2. Une exponentiation rapide exacte du même projecteur

Soit \(Q\) premier, \(Q>\max(2,h)\), et soit \(V_n\) l'espace des
polynômes homogènes de degré \(n\) en \(s\), avec des coefficients qui
peuvent eux-mêmes dépendre formellement de \(a,z\). Pour tout monôme
\(s^m\) de degré \(n\),

\[
L(s^m)=\kappa(m)s^m,
\qquad \kappa(m)=\sum_j\binom{m_j}{2}\in\{0,\ldots,h\}.
\]

Le petit théorème de Fermat donne, dans \(\mathbb F_Q\),

\[
1-\kappa^{Q-1}=
\begin{cases}1,&\kappa=0,\\0,&1\le\kappa\le h.\end{cases}
\]

Les deux opérateurs ayant la même action sur chaque monôme de base,

\[
\boxed{\pi_n(L)=I-L^{Q-1}\quad\text{sur }V_n.}
\]

Il s'agit d'une autre écriture du projecteur existant, pas d'un nouveau
raccord. La puissance \(L^{Q-1}\) a une description par exponentiation
rapide utilisant \(O(\log Q)\) compositions. L'action scalaire de chaque
carré reste à compiler : l'identité ne démontre donc aucune borne
\(n^{O(\log n)}\) ou \(n^{O(1)}\) pour la chaîne.

Si une représentation explicite de dimension \(d(n)\) était disponible,
avec initialisation et matrice d'action de \(L\) en coût polynomial,
cette exponentiation coûterait au plus \(O(d(n)^3\log Q)\) portes par
la multiplication matricielle élémentaire, plus l'initialisation et la
lecture. Ce serait polynomial pour \(d(n)\) et \(\log Q\) polynomiaux.
Cette phrase est une implication conditionnelle ; elle ne suppose pas
une telle représentation déjà construite. En outre, si \(d(n)\) est
polynomial, appliquer successivement les \(h\) facteurs coûterait déjà
\(O(hd(n)^2)\) portes : la fermeture scalaire est le gain essentiel.

## 3. Logarithme formel des facteurs

Introduisons une indéterminée de calcul \(t\), et posons

\[
P(t)=\prod_{r=1}^h(1-tX/r),\qquad
H_{h,k}=\sum_{r=1}^h r^{-k}.
\]

Sur un corps de caractéristique zéro, ou modulo \(t^{h+1}\) en
caractéristique \(Q>h\), tous les dénominateurs utilisés sont inversibles.
On a exactement

\[
\log P(t)\equiv-\sum_{k=1}^h\frac{H_{h,k}}{k}t^kX^k
\pmod{t^{h+1}}.
\]

L'exponentielle formelle tronquée reconstitue alors \(P(t)\) modulo
\(t^{h+1}\). Comme \(P\) a degré au plus \(h\) en \(t\), son
représentant de degré au plus \(h\) est reconstitué exactement. On peut
ensuite évaluer ce représentant en \(t=1\) pour obtenir \(\pi_n(X)\).

Il ne faut pas évaluer séparément les séries tronquées en \(t=1\) en
prétendant conserver les identités de séries : l'évaluation en 1 ne
passe pas au quotient par \((t^{h+1})\).

Cette transformation offre une préparation polynomiale des coefficients
du même lecteur ; elle ne remplace pas les actions \(X^k\mapsto L^k\)
sur \(G_B\). Les logarithmes et exponentielles formels sont ici des
algorithmes sur des listes de coefficients, réalisables avec les portes
autorisées, et non des portes numériques nouvelles.

Pour \(n\ge2\), le projecteur \(\Pi\) possède un noyau non trivial :
\(\Pi(s_1^n)=0\). Il ne peut donc pas être l'exponentielle usuelle d'un
endomorphisme fini en caractéristique zéro, puisque celle-ci est
inversible. Le logarithme numérique \(\log\Pi\) n'est pas défini sur
son noyau. Un flot \(e^{-tL}\) donne un projecteur seulement dans une
limite lorsque le paramètre est réel et tend vers l'infini ; cette limite
ne fournit pas une lecture exacte par un circuit fini.

## 4. Conditions quantitatives qui suffiraient réellement

### Fermeture par fusion donnant du quasi-polynomial

Supposons qu'un compilateur scalaire fusionne *réellement* deux blocs
de facteurs de longueur \(m\), partage et lecture compris, selon

\[
T(2m,n)\le2n^cT(m,n)+n^d(2m)^e,
\qquad T(1,n)\le n^b,
\]

pour des constantes absolues \(b,c,d,e\). Cette hypothèse porte sur les
portes scalaires obtenues, et non sur un arbre symbolique d'opérateurs.
Un arbre équilibré de \(O(\log h)\) niveaux donne alors

\[
T(h,n)\le n^{O(\log h)}\,\operatorname{poly}(h)
=2^{O((\log n)^2)}=n^{O(\log n)},
\qquad h=\Theta(n^2).
\]

C'est une condition suffisante précise pour du quasi-polynomial. Elle
n'est pas établie pour le compilateur actuel : composer deux actions
peut multiplier leurs facteurs de croissance, au lieu de satisfaire
la récurrence ci-dessus.

### Fermeture par fusion donnant du polynomial

Une récurrence réellement prouvée

\[
T(2m,n)\le c_0T(m,n)+p(n,m)
\]

avec \(c_0\) constant et \(p\) polynomial suffit pour une borne
polynomiale, car \(h=O(n^2)\). En particulier, une fusion additive
\(T(A\cup B)\le T(A)+T(B)+p(n,|A|+|B|)\) suffit. Une borne
additive par facteur \(S_{r+1}\le S_r+p(n,r)\) suffit également.

Une autre formulation quantitative concerne une récurrence séquentielle
\(S_{r+1}\le(1+\varepsilon_n)S_r+b_n\), avec \(b_n\) polynomial.
Pour \(h=\Theta(n^2)\), les conditions suivantes suffisent :

- \(\varepsilon_n=O(\log n/n^2)\) donne un majorant polynomial ;
- \(\varepsilon_n=O((\log n)^k/n^2)\), pour \(k\) constant, donne
  \(\exp(O((\log n)^k))\) fois un facteur polynomial.

En effet, \((1+\varepsilon_n)^h\le\exp(h\varepsilon_n)\), et la
somme des contributions additives est au plus
\(hb_n\exp(h\varepsilon_n)\). Le facteur actuel \(9n+1\) ne vérifie
aucune de ces conditions.

## 5. Effet des couches spectrales

Si le noyau scalaire a une borne \(T(n)\), la substitution de phases
pour \(N\le2n\) fréquences, même sans partage entre fréquences, et
l'INTT donnent

\[
C(n,N)\le NT(n)+2N\log_2N+N.
\]

Ces couches préservent donc une borne polynomiale ou quasi-polynomiale
qui aurait été prouvée pour la fusion et la lecture. La correction
universelle ne modifie pas la classe asymptotique. Le logarithme du
majorant actuellement démontré reste \(O(n^2\log n)\) ; prendre ce
logarithme ne réduit pas le nombre de portes de son circuit.

**Résultat de cette piste :** profondeur logarithmique de la description
du lecteur, exponentiation rapide exacte du même projecteur et
préparation formelle polynomiale de ses coefficients. Aucune de ces
trois propriétés ne constitue encore la fermeture scalaire requise.
