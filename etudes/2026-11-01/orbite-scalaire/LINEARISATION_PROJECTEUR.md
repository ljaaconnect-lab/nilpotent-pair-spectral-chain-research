# Linéariser la fusion des opérateurs dans leurs coefficients scalaires

L'entrelacement de `ORBITE_ET_FERMETURE.md` raccorde le produit complet
de différences à \((\pi_n(L)G_B)(t)\), où

\[
h=\binom n2,\qquad \pi_n(X)=\prod_{r=1}^{h}(1-X/r).
\]

La NTT peut maintenant porter sur **les coefficients scalaires du
polynôme d'opérateur**, sans développer son action dans une algèbre de
jets. La fusion ainsi compilée est un composant de la chaîne ;
l'initialisation des observations depuis les données reste à construire.

## 1. Deux longueurs distinctes

La longueur \(N\) désigne la NTT des labels \(d_j\) qui produit les
slots de \(\mathcal Z\). Pour la fusion du projecteur, choisir une
seconde longueur \(M\), puissance de deux avec \(M>h\), et une
racine \(\eta\) d'ordre \(M\). Les conditions sont

\[
Q>\max(2,h),\qquad N\mid Q-1,\qquad M\mid Q-1.
\]

Avec \(Q=c2^m+1\) premier, il suffit de choisir \(m\) assez grand
pour les deux longueurs et de fournir des racines d'ordres exacts. On
ne transforme ni les adresses exponentielles de \(z\), ni les
sous-ensembles de colonnes.

## 2. Fusion point par point, puis lecture globale

Chaque facteur possède la liste de coefficients
\(a_r=(1,-1/r,0,\ldots,0)\), donc

\[
\widehat a_r[\ell]=1-\eta^\ell/r.
\]

La formule de linéarisation devient

\[
\boxed{
(p_0,\ldots,p_h,0,\ldots,0)
=\operatorname{INTT}_M
 \left[\left(\prod_{r=1}^{h}(1-\eta^\ell/r)\right)_{\ell=0}^{M-1}\right],
\qquad \pi_n(X)=\sum_{j=0}^{h}p_jX^j.
}
\]

Elle est exacte : le produit a degré \(h<M\), donc la convolution
cyclique ne replie aucun coefficient. Les \(p_j\) sont partagés par
toutes les fréquences \(f\). Avec les observations
\(\mu_{j,f}=(L^jG_B)(t(f))\), la chaîne restante est

\[
\boxed{
\mathcal Z_Q[k]=\widetilde\Omega\,
\operatorname{INTT}_N
 \left[\left(\sum_{j=0}^{h}p_j\mu_{j,f}\right)_{f=0}^{N-1}\right][k].
}
\]

Les deux transformées ont donc des rôles précis : la première fusionne
les facteurs du projecteur ; la seconde lit les slots spectraux. Le
programme n'applique aucune lecture cachée aux facteurs orientés : il
reçoit explicitement les observations annoncées à son interface.

## 3. Portes scalaires du composant

Pour \(h\ge1\), le prototype conserve tous les produits par constantes
et toutes les additions. Il compte :

| Bloc | Portes scalaires |
|---|---:|
| \(1-\eta^\ell/r\), pour tous \(r,\ell\) | \(2hM\) |
| Produits point par point | \(M(h-1)\) |
| INTT interne normalisée | \(2M\log_2M+M\) |
| Lectures \(\sum_jp_j\mu_{j,f}\) | \(N(2h+1)\) |
| INTT externe normalisée | \(2N\log_2N+N\) |

Le total est

\[
\boxed{3hM+2M\log_2M+N(2h+1)+2N\log_2N+N.}
\]

Pour \(h=0\), \(\pi_n=1\) : les fils \(\mu_{0,f}\) alimentent
directement l'INTT externe, qui coûte \(2N\log_2N+N\) portes.
Les inverses \(1/r\), racines et phases sont des constantes de
paramètres, produites indépendamment des données. La génération de
ces constantes et leur stockage ont un coût polynomial.

La borne est polynomiale en \(n,N\), puisque \(M\le2(h+1)\).
Elle inclut la fusion et la lecture effective des observations, mais
**pas leur initialisation**. Le coût complet doit ajouter un circuit
pour les \(\mu_{j,f}\), ou fusionner cette préparation avec le lecteur
sans matérialiser l'interface.

## 4. Fermeture des polynômes d'opérateur à tout ordre

Sur les formes homogènes de degré \(n\),
\(\chi_n(L)=0\), avec \(\chi_n(X)=\prod_{r=0}^{h}(X-r)\).
Chaque polynôme d'opérateur se représente donc par son reste de degré
au plus \(h\) modulo \(\chi_n\). Deux représentants se fusionnent
par multiplication puis reste modulo ce polynôme monique. La division
polynomiale n'inverse aucune donnée ; même l'algorithme quadratique
coûte \(O(h^2)\) opérations scalaires.

Pour utiliser la NTT lors d'une fusion générale de deux représentants,
prendre une longueur strictement supérieure à \(2h\), car leur
produit peut atteindre le degré \(2h\). La longueur \(M>h\) utilisée
dans le prototype suffit au produit particulier des \(h\) facteurs
linéaires de \(\pi_n\). Cette distinction évite un repliement indu.

Cette fermeture est celle des **coefficients des opérateurs** et de leur
lecture contre un vecteur d'observations disponible. Elle ne suppose
pas que l'action de \(L\) sur un circuit arbitraire soit une porte
scalaire gratuite, et ne démontre pas l'initialisation générale.

## 5. Vérification du circuit réel

`spectral_projector.py` émet uniquement des portes scalaires \(+,\times\).
Les papillons des deux INTT, leurs normalisations et les contractions
sont réellement exécutés. Le vérificateur contrôle 22 vecteurs de
coefficients contre une multiplication polynomiale indépendante, puis
44 cas, 300 fréquences et 44 tables INTT complètes. Les coefficients
d'indices supérieurs à \(h\) sont nuls comme prévu. Les coûts observés
pour \(n=1,\ldots,8\) sont
\(6,42,100,352,832,1152,2736,4064\) portes, depuis les observations.

Le rapport `spectral-projector-validation.json` conserve les empreintes,
les paramètres, les sorties et le contrat excluant l'initialisation des
observations. La vérification indépendante réussit également ; elle
ne constitue pas une preuve du coût de cette initialisation.
