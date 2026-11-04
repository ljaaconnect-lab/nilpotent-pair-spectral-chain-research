# Raccord direct par la fréquence des collisions

Cette branche étudie une réorganisation globale qui ne demande pas les
observations \(\mu_r\) en entrée. Elle donne une identité exacte entre le
produit compact et le lecteur, mais **pas encore un circuit polynomial
en portes scalaires ordinaires**. Le coût du produit déformé défini
ci-dessous reste à compiler.

## 1. Une seule variable spectrale pour les collisions

Pour \(m=(m_0,\ldots,m_{n-1})\in\mathbb N^n\), poser
\(\kappa(m)=\sum_j\binom{m_j}{2}\). Si
\(G_B(s)=\sum_{|m|=n}g_m s^m\), définir

\[
C_B(u;t)=\sum_{|m|=n}g_m t^m u^{\kappa(m)}.
\]

Son degré en \(u\) est au plus \(h=\binom n2\). Il s'agit d'une
définition mathématique, pas d'une instruction de développement du
produit dans le circuit recherché. Pour \(E_u=u\partial_u\),

\[
\mu_r=(E_u^r C_B)(1;t),\qquad
(\pi_n(L)G_B)(t)=C_B(0;t).
\]

En effet, \(L\) et \(E_u\) multiplient le terme associé à \(m\)
par le même entier \(\kappa(m)\). Comme \(|m|=n\) avec \(n\)
colonnes, \(\kappa(m)=0\) impose \(m=(1,\ldots,1)\).

Pour \(M>h\) divisant \(Q-1\), et \(\eta\) d'ordre exact \(M\),
l'orthogonalité des caractères donne directement

\[
\boxed{C_B(0;t)=M^{-1}\sum_{\ell=0}^{M-1}C_B(\eta^\ell;t).}
\]

Ainsi une NTT sur le **nombre de collisions** remplace la contraction
avec les moments. Aucune interpolation des \(\mu_r\) n'est requise.
La moyenne utilise \(M-1\) additions et un produit par \(M^{-1}\).
Cette borne ne comprend pas la préparation des valeurs \(C_B\).

## 2. Fusion exacte depuis les formes de lignes

Introduire sur les polynômes en \(s\) le produit bilinéaire

\[
\boxed{s^m\star_u s^r=u^{\langle m,r\rangle}s^{m+r}.}
\]

Ce produit est unitaire, commutatif et associatif, puisque

\[
\langle m,r\rangle+\langle m+r,v\rangle
=\langle r,v\rangle+\langle m,r+v\rangle.
\]

La relation
\(\kappa(m+r)=\kappa(m)+\kappa(r)+\langle m,r\rangle\)
donne l'entrelacement exact

\[
\mathcal D_u(FG)=\mathcal D_u(F)\star_u\mathcal D_u(G),
\quad\mathcal D_u(s^m)=u^{\kappa(m)}s^m.
\]

Chaque forme linéaire est fixe par \(\mathcal D_u\). Par conséquent,

\[
\boxed{
C_B(u;t)=
\left(\mathop{\star_u}_{i=0}^{n-1}
             \sum_j B_{ij}s_j\right)_{s=t}.
}
\]

Cette identité relie directement les facteurs originaux au lecteur.
À \(u=1\), la fusion est le produit scalaire polynomial ordinaire.
À \(u=0\), elle annihile exactement les supports qui se rencontrent.
Elle retrouve ainsi la collision orientée après correction du signe,
sans introduire une amplitude terminale en entrée.

Pour \(u\ne0\), \(\mathcal D_u\) est un changement de base diagonal
inversible ; sa description compacte ne fournit pas le circuit de son
action. Pour \(u=0\), l'inverse n'existe pas et aucune division par
\(u\) n'est utilisée.

## 3. Raccord aux slots du papier

Conserver \(t_j(f)=\omega^{f d_j}\), les coefficients
\(B_{ij}=(1+a_{ij}^2)z^{2^{in+j}}\), et la correction universelle
\(\gamma_nq_{[n]}=\widetilde\Omega\). La chaîne devient

\[
\boxed{
\mathcal Z_Q[k]=\widetilde\Omega\,
\operatorname{INTT}_N\left[
\left(M^{-1}\sum_{\ell=0}^{M-1}
 C_B(\eta^\ell;t(f))\right)_{f=0}^{N-1}\right][k].
}
\]

Les deux transformées ont des axes distincts : \(\ell\) filtre les
collisions, \(f\) conserve les labels. Elles se composent par linéarité.
Un circuit préparant conjointement les valeurs de cette table en un
nombre polynomial de portes terminerait cette réalisation, sans passer
par les moments.

## 4. Ce que la loi de fusion demande encore

Le polynôme scalaire \(C_F(u;1)\) d'un facteur intermédiaire ne suffit
pas seul pour composer cette loi. Par exemple,

\[
C_{s_0}(u;1)=C_{s_1}(u;1)=1,
\quad C_{s_0^2}(u;1)=u,
\quad C_{s_1s_0}(u;1)=1.
\]

Le terme croisé \(\langle m,r\rangle\) doit donc être traité par
le circuit de fusion, ou évité par une compilation globale. Ceci ne
rejette aucune autre représentation ni compilation globale : cela
délimite seulement l'interface scalaire proposée ici.

Une diagonalisation par chirps ne rend pas cette contraction gratuite.
Pour une colonne et des exposants \(a,b\), le noyau de fusion est
\(u^{ab}\). Une NTT sur les occupations peut le traiter exactement,
mais utiliser indépendamment cette procédure dans les \(n\) colonnes
ne constitue pas une borne polynomiale. Aucun tel coût n'est supposé
dans cette étude.

## 5. Vérification

`verify_collision_spectrum.py` vérifie l'associativité, le raccord
\(\mathcal D_u(FG)\), la fusion des formes de lignes, l'identité des
moments et le filtre NTT. Les calculs par coefficients et par choix de
colonnes de ce programme sont **des oracles de vérification à petit
ordre**, pas le circuit demandé. Le rapport conserve ce contrat et
l'empreinte du programme. Aucun résultat Lean nouveau n'est revendiqué
dans cette branche.

La validation enregistrée passe 120 cas d'associativité, 120 cas
d'entrelacement, 692 valeurs spectrales et 596 observations. Les 12
tables complètes couvrent \(n=1,\ldots,6\) dans les corps de 17 et 97
éléments. Huit tables supplémentaires conservent \(z\) formel, pour
\(n=1,\ldots,4\), et contrôlent chaque exposant de chaque slot final.
