# Fusion scalaire de l'observateur de collisions

Cette construction reste dans les objets du raccord : transports, différences,
observation terminale et phases spectrales. Elle compile exactement la fusion
des facteurs du projecteur de B.11 sur un vecteur polynomial d'observations.
**Le composant reçoit ces observations en entrée. Leur initialisation depuis
les données originales reste à construire ; il ne constitue donc pas encore
un circuit de la chaîne entière.**

## Orbite scalaire du transport

Avec les horloges \(A_j=\sum_iB_{ij}E_{i+1,i}\), poser
\[
G_B(y)=\lambda_B(T_y1)
=e_n^T\left(I-\sum_jy_jA_j\right)^{-1}e_0
=\prod_{i=0}^{n-1}\left(\sum_jB_{ij}y_j\right).
\]
La dernière égalité vient de l'unique chemin de longueur \(n\) dans
l'horloge bidiagonale. Cette orbite possède un circuit scalaire polynomial
depuis \(B\), sans lecture d'un coefficient multivarié.

Pour \(h=\binom n2\), introduire l'opérateur choisi dans B.11 :
\[
L=\frac12\sum_j y_j^2\partial_{y_j}^2,
\qquad \pi_n(T)=\prod_{r=1}^{h}(1-T/r).
\]
Sur les formes homogènes de degré \(n\), il conserve exactement le
monôme auxiliaire sans répétition. L'identité terminale du raccord donne
directement, pour tous \(t_j\),
\[
\boxed{\lambda_B\!\left[\prod_j(T_{t_je_j}-I)1\right]
       =(\pi_n(L)G_B)(t).}
\]
À la fréquence \(f\), on prend \(t_j=\omega^{fd_j}\), puis on applique
l'INTT et le marqueur corrigé \(\widetilde\Omega\) du papier. Cette
identité n'impose aucune amplitude finale en entrée ni comme étape préalable.

## Un espace d'observations fermé sous tous les facteurs

Travailler en caractéristique zéro, ou dans un corps \(\mathbb F_Q\)
avec **\(Q>\max(2,h)\)**. Cette condition est distincte de l'existence
de la racine NTT. Pour un monôme \(y^m\) de degré total \(n\),
\[
Ly^m=\kappa(m)y^m,\qquad
\kappa(m)=\sum_j\binom{m_j}{2}\in\{0,\ldots,h\}.
\]
Par conséquent le polynôme universel
\[
\chi(T)=\prod_{r=0}^{h}(T-r)
       =T^{h+1}+\sum_{j=0}^{h}c_jT^j
\]
satisfait \(\chi(L)=0\) sur tout cet espace. Preuve : chaque monôme
est un vecteur propre dont la valeur propre est une racine de \(\chi\),
et les monômes forment une base. Les coefficients peuvent appartenir à
\(\mathbb F_Q[\{a_{ij}\},z]\), car \(L\) n'agit que sur \(y\).

Fixer un point spectral \(t\). Pour toute forme homogène \(F\) de
degré \(n\), définir le vecteur de \(h+1\) observations
\[
\mu(F;t)=\big((L^jF)(t)\big)_{j=0}^{h}.
\]
Il ne s'agit pas d'une liste de coefficients par sous-ensemble. La relation
\(\chi(L)=0\) donne l'observation suivante sans dériver de nouveau :
\[
\mu_{h+1}=-\sum_{j=0}^{h}c_j\mu_j.
\]
Pour fusionner \(F'=(I-L/r)F\), la mise à jour exacte est donc
\[
\boxed{\begin{aligned}
\mu'_j&=\mu_j-\mu_{j+1}/r &&(0\le j<h),\\
\mu'_h&=\mu_h+\frac1r\sum_{j=0}^{h}c_j\mu_j.
\end{aligned}}
\]
Chaque facteur conserve l'homogénéité, donc la même relation reste valable
à tous les stades. Après \(r=1,\ldots,h\), la lecture recherchée est
le fil \(\mu_0\). Toutes les autres observations sont nulles, puisque
le résultat appartient à la valeur propre zéro de \(L\).

Pour \(n=1\), \(h=0\), \(\chi(T)=T\), le produit est vide : le
composant restitue son unique fil \(\mu_0\) sans aucune porte.

## Coût exact du composant

Le prototype ne simplifie aucune opération, même un produit par zéro.
Pour un facteur, l'observation haute est accumulée directement sous la forme
\(\mu_h+\sum_{j=0}^{h}(c_j/r)\mu_j\), avec les \(c_j/r\) préparés
comme constantes structurelles. Elle coûte \(h+1\) multiplications et
\(h+1\) additions. Les \(h\) observations basses coûtent chacune une
multiplication et une addition. Le total est
\[
\boxed{4h+2\text{ portes par facteur},\qquad
h(4h+2)\text{ portes pour tous les facteurs}.}
\]
Cela comprend \(h(2h+1)\) additions et \(h(2h+1)\)
multiplications. Le vecteur complet reste la sortie du composant ; sa
lecture terminale est une sélection de fil. Pour \(N\) fréquences,
\(Nh(4h+2)\) est une borne pour des copies indépendantes du composant.

Les coefficients \(c_j\) se construisent structurellement en multipliant
les \(h+1\) facteurs linéaires de \(\chi\). Leur génération demande
un nombre polynomial d'opérations entières et leur longueur binaire est
\(O(h\log(h+1))\) par coefficient. Dans le prototype modulo \(Q\),
ils sont réduits en constantes de corps, ainsi que les inverses de
\(1,\ldots,h\). Aucune de ces constantes ne dépend des amplitudes.

## Obligation d'initialisation

Le composant scalaire commence aux fils
\[
\mu_j^{(0)}(f)=(L^jG_B)(t(f)),\qquad 0\le j\le h.
\]
Sa borne polynomiale ne compte pas leur construction. Une fermeture
générale exige un circuit partagé qui les produise depuis \(a_{ij},z\)
en coût polynomial, ou une fusion avec \(G_B\) qui évite de les exposer
séparément. Ni leur simple définition par dérivées, ni la taille
polynomiale de \(G_B\), ne sont utilisées ici comme une implémentation
de cette initialisation. Aucun de ces fils n'est annoncé comme gratuit
dans un circuit complet de \(\mathcal Z\).

Le résultat obtenu est précisément une fusion et une lecture scalaires
polynomiales **conditionnées à des observations déjà disponibles**, avec
une règle et un compte explicites. Il ne prouve pas encore la fermeture
générale depuis les données originales.

## Vérification

`python verify_collision_observer.py` vérifie toutes les étapes du DAG
sur des mélanges synthétiques de monômes homogènes de degré \(n\),
avec collisions, monôme sans répétition et phases NTT. La référence
applique directement les poids diagonaux \(1-\kappa/r\) aux monômes
fournis ; elle n'utilise ni états de sous-ensembles ni énumération de
colonnes distinctes. Une INTT de référence vérifie également tous les
canaux de sortie à partir des fréquences ; son travail de vérification
n'est pas compté comme une partie du composant d'observation.
Les tests vérifient aussi les comptes de portes,
le cas \(n=1\) et le rejet de \(Q\le\max(2,h)\).
`validation.json` conserve les mélanges, les paramètres et les empreintes
des deux sources. Les tests ne simulent pas une initialisation générale
de \(\mu\) depuis les amplitudes originales.
