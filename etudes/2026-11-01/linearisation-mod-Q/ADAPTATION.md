# Adapter la linéarisation modulo Q à l'architecture Z

Reprise du 1 novembre 2026, à partir de la correction de l'auteur :
la cible est toute la chaîne orientée et spectrale, sans amplitude P_A
fournie en entrée ni imposée comme étape préalable.

**Résultat de cette reprise.** Une déformation permet de traduire exactement
la chaîne en une NTT couplée à une transformée de signes. Le circuit produit
tous les slots depuis les entrées originales, conserve les marqueurs formels
et emploie uniquement des additions et multiplications scalaires.
Son évaluation peut fonctionner avec une mémoire polynomiale, sans table de
sous-ensembles. Cette construction conserve cependant un nombre exponentiel
de portes. Elle n'est pas une résolution de la conjecture générale.

## 1. Ce que l'on adapte de Cormen

La figure 30.1 et le théorème 30.2, pages imprimées 904–905
(pages PDF 925–926), utilisent une représentation par valeurs : le produit
des polynômes devient une multiplication point par point. Le problème 30-6,
pages imprimées 923–924 (PDF 944–945), établit la version modulaire, avec
un premier p = kL + 1 et une racine d'ordre L.

Dans notre notation, choisir :

\[
 N=2^s>n,\qquad Q=c2^m+1\ \text{premier},\qquad m\ge s,
 \qquad \omega=g^{(Q-1)/N}\in\mathbb F_Q.
\]

Le paramètre g est choisi pour que omega soit d'ordre exactement N.
Les inverses de N et de 2 existent. La forme arithmétique de Q, à elle seule,
ne désigne ni une racine ni un filtre de collisions.

Le coefficient z reste formel : les calculs sont effectués dans
\(\mathbb F_Q[z]\). La NTT porte sur les labels d_j modulo N, jamais sur
les adresses \(w_{ij}=2^{in+j}\). Les puissances de z sont préparées par
carrés successifs, en n²−1 portes, sans développer leurs coefficients.

## 2. Déformation adaptée au degré terminal

Posons, avec des indices i,j allant de 0 à n−1,

\[
 B_{ij}=(1+a_{ij}^2)z^{2^{in+j}},\qquad
 F_f(y)=\prod_{i=0}^{n-1}\left(\sum_{j=0}^{n-1}
 B_{ij}y_j\omega^{fd_j}\right).
\]

F_f est homogène de degré n. Dans l'algèbre orientée du papier,
\(q_j=x_jy_j\), les q_j commutent, q_j²=0 et
\(q_0\cdots q_{n-1}=\gamma_n\widetilde\Omega\).
La correction extérieure gamma_n donne donc

\[
 \gamma_n F_f(q)
 =[y_0\cdots y_{n-1}]F_f(y)\;\widetilde\Omega.
\]

Il n'est pas nécessaire de conserver ces relations nilpotentes à chaque
étape si l'on préserve cette observation finale. On peut travailler dans

\[
 \mathcal H=\mathbb F_Q[u_0,\ldots,u_{n-1}]/(u_j^2-1)
\]

et lire le coefficient de u_0...u_{n-1} **après le produit complet**.
En effet, un choix de colonnes de multiplicités m_j produit
\(u_0^{m_0}\cdots u_{n-1}^{m_{n-1}}\). Il atteint ce coefficient si tous
les m_j sont impairs. Puisque \(\sum_jm_j=n\), cela impose m_j=1 pour tout j.

La lecture terminale réalise donc exactement la même sélection que
l'annihilation orientée. Les valeurs intermédiaires peuvent différer.
Cette restriction au degré n est essentielle : la substitution q_j↦u_j
n'est pas un morphisme entre les deux algèbres.

## 3. Formule scalaire raccordée

Pour \(\epsilon\in\{-1,+1\}^n\), définissons directement les signaux

\[
 R_{i,\epsilon}[t]
 =\sum_{j:d_j\equiv t\pmod N}B_{ij}\epsilon_j,
 \qquad
 A_{i,\epsilon}[f]=\operatorname{NTT}_N(R_{i,\epsilon})[f]
 =\sum_jB_{ij}\epsilon_j\omega^{fd_j}.
\]

L'adaptation exacte de la chaîne est :

\[
\boxed{
 \mathcal Z_A[k]=\widetilde\Omega\,
 \operatorname{INTT}_N\!\left[
 \left(
 \frac1{2^{n-1}}
 \sum_{\substack{\epsilon\in\{\pm1\}^n\\\epsilon_{n-1}=1}}
 \left(\prod_j\epsilon_j\right)
 \prod_i A_{i,\epsilon}[f]
 \right)_{f=0}^{N-1}
 \right][k].
}
\]

Il s'agit d'une polarisation par signes appliquée à toute l'architecture Z,
avec les phases dans chaque entrée. Ce mécanisme de polarisation est
classique ; on ne revendique pas ici une nouvelle identité de permanent.
Le coefficient de sortie n'est jamais une feuille du circuit.

**Preuve de la lecture.** Pour un monôme de multiplicités m,

\[
 2^{-n}\sum_{\epsilon\in\{\pm1\}^n}
 \prod_j\epsilon_j^{m_j+1}
 =\prod_j\frac{1+(-1)^{m_j+1}}2.
\]

Cette quantité vaut 1 exactement lorsque tous les m_j sont impairs,
donc lorsqu'ils valent tous 1 au degré n. Les termes epsilon et −epsilon
contribuent de façon identique : F_f est de degré n et le poids a aussi
degré n. Cela permet de fixer le dernier signe à +1 et remplace 2^n
par 2^(n−1).

Le signe gamma_n ne manque pas dans la formule encadrée : il est déjà
compensé par la conversion \(q_{[n]}=\gamma_n\widetilde\Omega\).
Une seconde multiplication par gamma_n changerait à tort la sortie pour
n≡2 ou 3 modulo 4.

Chaque terme conservé porte la phase commune
\(\omega^{f\sum_jd_j}\). L'INTT le place donc au slot
\(k_*=\sum_jd_j\bmod N\), avec tous les autres slots nuls. C'est une
conséquence de la chaîne ; le compilateur fourni effectue effectivement
l'INTT et ne reçoit ni l'amplitude finale ni une table déjà filtrée.

## 4. Fusion en flux et compte de portes

Le code chaine_z.py compile la formule précédente en portes add/mul.
Les canaux epsilon sont parcourus en code de Gray. Lorsqu'un seul signe
epsilon_j change, chaque entrée spectrale se met à jour par

\[
 A_{i,\epsilon'}[f]
 =A_{i,\epsilon}[f]-2\epsilon_jB_{ij}\omega^{fd_j}.
\]

On garde les sommes spectrales courantes et leurs accumulateurs. Aucun
ensemble de colonnes déjà employées n'est mémorisé. L'évaluateur numérique
utilise O(Nn²) scalaires de travail, donc une mémoire polynomiale.
La description explicite du DAG comporte, elle, autant de nœuds que de
portes ; elle n'est pas de taille polynomiale.

Avec \(M=2^{n-1}\), le compte exact du compilateur fourni, depuis les a_ij
et z, est

\[
\begin{split}
 G(n)={}&4n^2-1+3Nn^2+N(n^2-1)\\
 &+2nN(M-1)+N\lfloor M/2\rfloor+2N+2N\log_2N.
\end{split}
\]

Ce compte inclut les préparations de phases, même les mises à jour
préparées mais inutilisées, ainsi que toutes les soustractions et tous les
papillons de l'INTT. Depuis les p_ij, retrancher 2n².
Il est \(O(Nn2^n+Nn^2+N\log N)\). La mémoire polynomiale n'est donc pas
une preuve d'un nombre polynomial de portes.

Exemples depuis A : n=4, N=8, 8 canaux, 1 111 portes ;
n=8, N=16, 128 canaux, 38 031 portes. Ces comptes ne constituent pas
une amélioration du meilleur compilateur exponentiel déjà archivé.

## 5. Pourquoi un remplacement scalaire direct des q_j ne suffit pas

Dans un corps, v_j²=0 implique v_j=0. On ne peut donc pas remplacer
chaque q_j par un unique élément de F_Q en préservant simultanément
sa nilpotence et son produit terminal non nul.

Plus généralement, soit une algèbre sur un corps contenant des éléments
commutants v_j tels que v_j²=0 et \(v_0\cdots v_{n-1}\ne0\).
Les 2^n produits \(v_S=\prod_{j\in S}v_j\) sont linéairement indépendants.

Pour le prouver, prendre dans une relation non nulle un S de cardinal
minimal dont le coefficient est non nul, puis multiplier par v_{S^c}.
Les termes T qui ne sont pas contenus dans S s'annulent par un carré ;
les sous-ensembles stricts de S ont coefficient nul par minimalité.
Il resterait un multiple non nul du produit terminal, contradiction.

Cela concerne une algèbre qui préserve ces relations. La déformation
terminale de la section 2 change précisément les relations intermédiaires.
Le lemme n'est pas une borne pour tout circuit scalaire calculant Z.

## 6. Nombre de canaux d'une linéarisation point par point

Considérons une architecture plus précise, de la forme

\[
 T(B)=\sum_{\alpha=1}^{D}\lambda_\alpha
 \prod_i\left(\sum_jv_{\alpha j}B_{ij}\right),
\]

avec des directions v et des poids constants indépendants de B,
les mêmes directions pour chaque ligne, et une lecture finale linéaire.
Si elle sélectionne exactement les affectations bijectives pour toutes
les données, elle doit avoir \(D\ge2^{n-1}\) sur notre corps F_Q,
puisque Q>n. Les 2^(n−1) canaux de la section 3 atteignent cette borne
**dans ce modèle de canaux**.

L'emploi de B comme variables indépendantes dans cette preuve est compatible
avec l'identité formelle requise depuis les entrées originales : la
substitution \(B_{ij}\mapsto(1+a_{ij}^2)z^{w_{ij}}\) est injective sur
l'anneau de polynômes, en travaillant au besoin sur F_Q(z). Chacun des
a_ij est une indéterminée indépendante. Une identité seulement testée sur
un échantillon numérique ne suffirait pas à ce raisonnement.

Voici une preuve, en précisant la caractéristique. En identifiant toutes
les lignes B_i à une même ligne x, l'identité donne

\[
 n!x_0\cdots x_{n-1}
 =\sum_\alpha\lambda_\alpha(\sum_jv_{\alpha j}x_j)^n.
\]

Fusionner les directions proportionnelles et supprimer les termes nuls.
Soit I l'idéal homogène de ces points projectifs et R=F_Q[y_0,...,y_{n−1}].
La dérivation des puissances, valide puisque Q>n, montre
\(I\subseteq (y_0^2,\ldots,y_{n-1}^2)=K\), l'idéal apolaire du monôme.
Posons \(I'=I:y_0\). Il correspond aux points où y_0≠0 et

\[
 I'\subseteq K:y_0=(y_0,y_1^2,\ldots,y_{n-1}^2).
\]

La multiplication par y_0 est injective sur R/I'. Les différences
successives de sa fonction de Hilbert montrent que le nombre D' de ces
points est \(\dim R/(I'+(y_0))\). Ce quotient surjecte sur
\(R/(y_0,y_1^2,\ldots,y_{n-1}^2)\), de dimension 2^(n−1).
Ainsi D≥D'≥2^(n−1).

L'argument suit la méthode apolaire de Carlini, Catalisano et Geramita,
[The Solution to Waring's Problem for Monomials](https://arxiv.org/pdf/1110.0745),
théorème 3.1 et corollaire 3.3. Le papier cité est en caractéristique zéro ;
le passage utilisé ici en caractéristique Q>n est justifié ci-dessus par
l'inversibilité des factorielles jusqu'à n et le même argument sur les points.

Si les directions diffèrent selon les lignes, une borne élémentaire plus
faible subsiste pour une somme de D produits séparés :
\(D\ge\binom n{\lfloor n/2\rfloor}\).
Scinder les lignes en k et n−k. Restreindre les affectations aux listes
croissantes de sous-ensembles S et T, puis indexer T par le complément
d'un autre S'. Le tenseur cible restreint est la matrice identité
\(\delta_{S,S'}\). Chaque produit séparé a rang au plus 1.
Cette preuve fonctionne sur tout corps.

La fréquence f peut être incluse parmi les canaux : ce sont alors les
D produits séparés totaux que la borne compte. Dans le cas des phases
par colonne du papier, les phases sont communes sur les bijections et
se rabattent exactement comme à la section 3.

Ces résultats ne minorent pas la taille d'un DAG arbitraire qui partage
les calculs et effectue des fusions entre canaux. Ils ne condamnent ni
une représentation dépendant de plusieurs lignes à la fois, ni une lecture
avec accès à d'autres fils du circuit. Une résolution polynomiale globale
reste à construire ; elle ne découle pas de la simple matérialisation
d'une NTT de valeurs suivie d'un produit scalaire par canal.

## 7. Vérifications reproductibles

Depuis ce dossier : `python -B verifier.py`.

Le vérificateur contrôle 3 413 affectations de colonnes, y compris toutes
les répétitions jusqu'à n=5 ; 216 tables spectrales numériques jusqu'à
n=9 sur quatre corps ; 48 DAG depuis A ou p ; 16 tables de polynômes
formels en z ; 17 cas où une collision tombe exactement sur le label
spectral attendu. Il vérifie aussi le compte de chaque porte et l'absence
de toute feuille portant une amplitude finale.

Les tables de sous-ensembles et les permutations ne figurent que dans
les oracles de vérification indépendants. Le compilateur emploie la
déformation, le parcours des signes et l'INTT.

La formule a également un sens en caractéristique zéro avec une racine
abstraite d'ordre N. Son évaluation modulo Q fournit une sortie modulo Q ;
un seul résidu ne reconstitue pas automatiquement une amplitude entière.
La preuve algébrique du filtre est indépendante d'une expérience numérique.

Fichiers : chaine_z.py, verifier.py, validation.json.

## 8. Contrat pour la suite

L'architecture de référence reste Z : entrées orientées, fusion raccordée,
correction universelle et lecture spectrale globale. Le programme de
recherche ne doit pas exiger P_A comme entrée ou étape initiale.

La présente adaptation donne une forme scalaire exacte sans mémoire des
colonnes déjà employées. La condition encore manquante est une fusion et
une lecture **globales** en un nombre polynomial de portes, sans matérialiser
les canaux exponentiels de cette polarisation. Les bornes des sections 5–6
ne sont pas une impossibilité de cette recherche plus générale.
