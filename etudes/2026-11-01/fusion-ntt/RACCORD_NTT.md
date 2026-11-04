# Raccorder la linéarisation modulo Q à la fusion des transports

Cette construction adapte le schéma demandé
\(\operatorname{NTT}(M_j)\), produit point par point, puis INTT, à la loi
\(T_yT_z=T_{y+z}\). Elle supprime de la formule finale l'extraction du
coefficient mixte et toute sélection explicite des colonnes distinctes.
**Le produit point par point reste un produit d'opérateurs : sa compilation
générale en portes scalaires polynomiales n'est pas encore démontrée.**

## 1. Le domaine de la linéarisation

Choisir \(N=2^s>n\), un premier \(Q=c2^m+1\) avec \(m\ge s\), et une racine
\(\omega\in\mathbb F_Q\) d'ordre exactement \(N\). On travaille sur
\(K=\mathbb F_Q[\{a_{ij}\},z]\), ou sur \(\mathbb F_Q[z]\) lorsque les
entrées \(a_{ij}\) sont évaluées dans \(\mathbb F_Q\). On ne remplace pas
\(z\) formel par un résidu numérique. La sortie \(\mathcal Z_Q\) désigne
la réduction modulo \(Q\) de la sortie du papier ; cette construction ne
fournit pas à elle seule un procédé de relèvement en caractéristique zéro.

La NTT transforme une convolution cyclique en produit point par point. Le
remplissage par zéros permet de calculer un produit ordinaire lorsque le
degré est inférieur à la longueur de transformée; voir
[Harvey–van der Hoeven–Lecerf, §2.4](https://www.texmacs.org/joris/ffmul/ffmul.pdf).
Ici les coefficients sont des opérateurs. La même identité s'étend à cette
algèbre car les puissances de \(\omega\) sont centrales; l'ordre de
composition des opérateurs est conservé.

Poser
\[
V_n=K\langle X_0,\ldots,X_{n-1}\rangle/(\text{mots de longueur}>n).
\]
Il s'agit du domaine mathématique des opérateurs, et non d'une table que
l'on déclare gratuite. On n'attribue pas une taille scalaire polynomiale à
la représentation de tous ses éléments.

Dans ce quotient, le transport de la reprise précédente est bien défini :
\[
R_y=\left(1-\sum_jy_jX_j\right)^{-1}
 =\sum_{r=0}^n\left(\sum_jy_jX_j\right)^r,
\qquad T_yF=F(X_j\mapsto R_yX_j)R_y.
\]
La substitution ne diminue jamais la longueur des mots, donc préserve le
quotient. Les inverses désignent ici des sommes finies. La loi exacte est
\(T_yT_z=T_{y+z}\), en toute caractéristique.

## 2. Le facteur qui remplace la sélection finale

Pour chaque colonne \(j\), définir une différence de transports :
\[
\boxed{D_j(t)=T_{t e_j}-I=\sum_{r=1}^n t^r C_{j,r}.}
\]
Il n'y a pas de terme constant. Pour un mot de longueur \(a\),
\(C_{j,r}\) produit seulement des mots de longueur \(a+r\).

En effet, sur \(X_{i_1}\cdots X_{i_a}\), le transport vaut
\[
R_j(t)X_{i_1}R_j(t)X_{i_2}\cdots R_j(t)X_{i_a}R_j(t),
\quad R_j(t)=\sum_{b=0}^n t^bX_j^b.
\]
Le coefficient de \(t^r\) répartit exactement \(r\) copies de \(j\) entre
les \(a+1\) interstices. Pour \(r=1\), il s'agit de l'insertion complète
\(C_{j,1}=\mathcal I_j\), déjà étudiée.

**Identité terminale, valable à tout ordre :** pour tous scalaires \(t_j\),
\[
\boxed{D_{n-1}(t_{n-1})\cdots D_0(t_0)1
 =\left(\prod_jt_j\right)
 \mathcal I_{n-1}\cdots\mathcal I_0(1).}
\]

Preuve. Dans le développement, chaque facteur fournit un indice
\(r_j\ge1\). Si un indice est supérieur à 1, alors
\(\sum_jr_j>n\), et le terme est nul dans \(V_n\). Il reste donc uniquement
\(r_j=1\) pour chaque \(j\). Les insertions de lettres nouvelles produisent
chaque mot-permutation une fois. Il n'y a ni coefficient mixte à extraire
après cette opération ni état de colonnes déjà utilisées dans son énoncé.

Cette identité ne dit pas que le développement doit être réalisé. Elle
donne la spécification exacte du nouveau produit d'opérateurs.

## 3. Les entrées adaptées à la NTT

Utiliser les labels \(d_j\) du papier et définir les signaux **opérateurs**
\[
\boxed{M_j[s]=
 \sum_{\substack{1\le r\le n\\r d_j\equiv s\ (\mathrm{mod}\ N)}}C_{j,r}.}
\]
Leur transformée est exactement
\[
\begin{aligned}
\widehat M_j[f]
 &=\sum_{s=0}^{N-1}\omega^{fs}M_j[s]
 =\sum_{r=1}^n\omega^{frd_j}C_{j,r}\\
 &=\boxed{T_{\omega^{fd_j}e_j}-I}.
\end{aligned}
\]

C'est l'adaptation du schéma fourni : les lignes de coefficients de la
NTT décrivent maintenant les différences de transports. Le produit point
par point est une composition dans \(\operatorname{End}_K(V_n)\).
Il donne, sans extraction de colonnes,
\[
\left(\prod_j\widehat M_j[f]\right)1
 =\omega^{f\sum_jd_j}\mathcal I_{n-1}\cdots\mathcal I_0(1).
\]
Les facteurs commutent par la loi des transports; on peut aussi conserver
l'ordre d'insertion affiché précédemment.

Le repliement des indices \(rd_j\bmod N\) ne crée pas de terme parasite,
même lorsque \(d_j=0\). Les termes contenant un \(r_j>1\) s'annulent par la
troncature avant l'observation terminale. Ce mécanisme n'exige pas des
labels qui distinguent toutes les affectations de colonnes.

## 4. La chaîne entière depuis les entrées originales

Préparer
\[
B_{ij}=(1+a_{ij}^2)z^{2^{in+j}},\qquad
A_j=\sum_{i=0}^{n-1}B_{ij}E_{i+1,i}.
\]
Les phases sont déjà dans \(\widehat M_j[f]\); ces \(A_j\) n'en contiennent
pas une seconde copie. L'évaluation \(\mathrm{ev}_A:V_n\to\operatorname{Mat}_{n+1}(K)\)
est bien définie car tous les produits de plus de \(n\) horloges sont nuls.
Poser \(\lambda_B(F)=\mathrm{ev}_A(F)_{n,0}\).
L'ordre des horloges est explicite :
\[
\lambda_B(X_{j_0}\cdots X_{j_{n-1}})
 =\prod_{i=0}^{n-1}B_{i,j_{n-1-i}}.
\]
Le renversement de l'ordre parcourt encore toutes les permutations.

La formule raccordée est
\[
\boxed{
\mathcal Z_Q[k]=\widetilde\Omega\,
\operatorname{INTT}_N\!\left[
 \left(\lambda_B\left[
 \left(\prod_{j=0}^{n-1}
    (T_{\omega^{fd_j}e_j}-I)\right)1
 \right]\right)_{f=0}^{N-1}
\right][k].
}
\]

Elle est égale à la réduction modulo \(Q\) de la sortie du papier : le produit terminal contient chaque
affectation bijective une fois, avec les amplitudes et adresses initiales.
Chaque terme porte la phase commune \(\omega^{f\sum_jd_j}\); l'INTT produit
donc le canal \(\sum_jd_j\bmod N\). La correction universelle est déjà incluse
par \(\gamma_nq_{[n]}=\widetilde\Omega\). Aucune amplitude \(P_A\) n'est
fournie en entrée ou imposée comme intermédiaire préalable.

La lecture \(\lambda_B\) est la spécification de l'observation. Son coût
doit faire partie de toute compilation scalaire de la formule.

## 5. La loi de fusion à compiler

En écrivant \(\Delta_y=T_y-I\), la loi adaptée est
\[
\boxed{\Delta_y\Delta_z=\Delta_{y+z}-\Delta_y-\Delta_z.}
\]
Elle découle directement de \(T_yT_z=T_{y+z}\). C'est cette loi, avec les
sommes et soustractions qu'elle contient, qui doit fermer l'action des
produits point par point.

Le coût polynomial d'un transport simple démontré dans la reprise
précédente ne suffit pas à borner cette action composée. Une NTT accélère
la convolution des coefficients lorsque leurs opérations sont disponibles;
elle ne remplace pas leur composition par une multiplication scalaire.

Par exemple, à \(n=2\), \(a_{ij}=0\), prendre
\(A_0=zE_{10}+z^4E_{21}\), \(A_1=z^2E_{10}+z^8E_{21}\).
La vraie composition \(\Delta_{e_0}\Delta_{e_1}1\), évaluée au coin \((2,0)\),
donne \(z^6+z^9\). Le produit des deux valeurs matricielles séparées
\((R_{e_0}(A)-I)(R_{e_1}(A)-I)\) donne seulement \(z^6\).
Le transport agit aussi par substitution sur les générateurs de l'opérande
suivant; cette action fait partie du circuit à construire.

## 6. Vérifications et statut

Les fichiers Lean de ce dossier contiennent sept lemmes généraux :

- `FusionFourier.lean` : `fourier_pairs`, `fourier_fused`,
  `difference_fusion`, `fourier_convolution`. Les coefficients peuvent
  être non commutatifs. La multiplicativité des caractères, la centralité
  des phases et la loi de fusion utilisée sont des hypothèses explicites.
  Le dernier lemme regroupe effectivement les paires d'indices par leur
  somme ; prendre le groupe fini `ZMod N` donne la convolution cyclique.
- `TerminalDifference.lean` : `coeff_product_below_length`,
  `coeff_product_at_length`, `coeff_transport_differences`. Pour une liste
  de \(n\) facteurs de terme constant nul, les coefficients de degré
  inférieur à \(n\) sont nuls et celui de degré \(n\) est le produit
  ordonné des coefficients linéaires. Le corollaire l'applique à
  \(\prod_j(T_j(t)-1)\) lorsque \(T_j(0)=1\).

Ces lemmes sont le noyau algébrique de la preuve écrite : l'application
aux opérateurs \(C_{j,r}\), qui augmentent la longueur de \(r\), utilise
en plus l'argument de graduation de la section 2. Le rapport
`lean-validation.json` consigne une recompilation indépendante, les
empreintes des sources et les axiomes de chaque théorème.
L'ensemble du raccord avec \(\lambda_B\), les horloges et la NTT finale
n'est pas présenté comme un compilateur entièrement formalisé.

`verify_bridge.py` développe les transports seulement pour vérifier les
identités à de petits ordres et compare les tables marquées à une référence
indépendante. C'est un vérificateur, pas un compilateur scalaire polynomial.
Les 30 tables complètes passent pour \(n=1,\ldots,5\) sur
\(\mathbb F_{17}\), \(\mathbb F_{97}\) et \(\mathbb F_{998244353}\), avec
labels tous nuls ou aléatoires. Sont également contrôlées 564 égalités
entre facteurs NTT et transports, et 156 identités de mots avant
spécialisation des amplitudes. Le rapport `bridge-validation.json`
conserve les entrées, les sorties formelles et l'empreinte du vérificateur.

**Résultat acquis :** un raccord exact entre la NTT modulo \(Q\) et les
différences de transports, avec annihilation des répétitions au degré
terminal et sans sélection finale de colonnes distinctes.

**Résultat encore manquant :** une borne polynomiale du coût scalaire de
l'action composée des différences et de leur observation. La construction
ne revendique pas cette borne à partir du seul nombre d'opérateurs.
