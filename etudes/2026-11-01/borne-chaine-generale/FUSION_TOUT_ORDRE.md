# Fusion terminale à défaut quelconque

Cette note étend la correction terminale du raccord existant. Elle conserve
les entrées B issues de a,z, les facteurs de collision et la lecture spectrale
déjà fusionnée. Elle ne démontre pas une borne polynomiale de toute la chaîne.

## 1. Préfixe et identification exacte du bloc terminal

Écrivons h_d=d(d-1)/2, G(s)=prod_i sum_j B_ij s_j et
L=(1/2)sum_j s_j^2 partial_j^2. Le degré est n et les indices de lignes et
colonnes vont de 0 à n-1. Le corps a une caractéristique première Q>h_n,
Q>2. On suppose n>=3 et on choisit un entier 0<=R<n/2.

Posons b=n-R-1>=1 et n=qb+t, 0<=t<b. Définissons

\[
\tau_R=q h_b+h_t,\qquad
I_R=K_n\cap\{1,\ldots,\tau_R\},\qquad
c(X)=\prod_{\lambda\in I_R}(1-X/\lambda).
\]

Une occupation de somme n dont chaque composante est au plus b vérifie
kappa<=tau_R. En effet, si deux composantes sont strictement entre 0 et b,
transférer une unité de la plus petite vers la plus grande augmente la somme
des h_m; répéter donne q composantes b, une composante t et des zéros.
Le préfixe c(L) annule donc toutes ces occupations, hormis kappa=0.

Tout terme à collision encore présent possède par conséquent une colonne
de multiplicité n-r, avec 0<=r<=R. Cette colonne est unique puisque n-r>n/2.
Cette unicité évite tout double comptage. Les collisions de valeurs propres
entre différents profils sont traitées par c : toute valeur <=tau_R est
annulée, y compris lorsqu'un profil à colonne dominante la partage avec
un autre profil.

Pour une colonne dominante j, posons

\[
F_j(x,s)=\prod_i\left(B_{ij}+x\sum_{k\ne j}B_{ik}s_k\right).
\]

Le coefficient de x^r contient exactement les choix laissant n-r lignes
dans la colonne j. Sur ce coefficient, la collision totale vaut
h_(n-r)+kappa_residu. Par conséquent, avec L_j agissant seulement sur les
variables s_k, k!=j, la correction exacte est

\[
\boxed{
C_B=(c(L)G)(\mathbf1)-
\sum_{r=0}^{R}\sum_j
\left[c(h_{n-r}+L_j)[x^r]F_j(x,s)\right]_{s=\mathbf1}.
}
\]

C_B est la sortie corrigée de la chaîne. Son routage vers le seul indice
spectral restant ne demande aucune porte supplémentaire. La formule ne
prend ni C_B ni des moments inconnus comme entrées.

## 2. Une base exacte pour la lecture du résidu

Pour un résidu de degré r, soit B_r l'ensemble des partitions beta dont
toutes les parts sont >=2 et dont la masse |beta| est <=r. La partition
vide est incluse. Pour beta=(beta_1,...,beta_p), définissons

\[
M_\beta(m)=
\sum_{k_1,\ldots,k_p\text{ distincts}}
\prod_{l=1}^{p}\binom{m_{k_l}}{\beta_l}.
\]

La somme porte sur des tuples ordonnés. Ce choix détermine les facteurs de
multiplicité dans les coefficients ci-dessous.

Tout profil de degré r se décrit par ses parts >=2, notées lambda, et
r-|lambda| parts égales à 1. Les parts 1 ne contribuent pas à M_beta.
Une valeur M_beta(lambda) non nulle impose |beta|<=|lambda|. En cas
d'égalité, elle impose beta=lambda comme partitions : les colonnes marquées
doivent épuiser toutes les occupations >=2 et chaque inégalité beta_l<=m_k
devient une égalité. Ainsi la matrice de cette base est triangulaire par
masse et sa diagonale est

\[
M_\lambda(\lambda)=\prod_{d\ge2} a_d(\lambda)!,
\]

où a_d est la multiplicité de la part d. Cette diagonale est inversible
modulo Q, puisque a_d<=r<Q.

Pour toute fonction w définie sur les collisions résiduelles, il existe
donc des constantes alpha_beta telles que

\[
w(\kappa(m))=\sum_{\beta\in B_r}\alpha_\beta M_\beta(m).
\]

Elles se construisent exactement, par masses croissantes :

\[
\alpha_\lambda=
\frac{w(\kappa(\lambda))-
 \sum_{|\beta|<|\lambda|}\alpha_\beta M_\beta(\lambda)}
 {\prod_{d\ge2}a_d(\lambda)!}.
\]

Les partitions distinctes de même masse ont une entrée croisée nulle.
Le coefficient vide est alpha_empty=w(0). Pour le raccord, on choisit
exactement w(v)=c(h_(n-r)+v).

## 3. Chaque amplitude est une extraction de petits polynômes

Posons R_ij=sum_(k!=j) B_ik. Pour un tuple k_1,...,k_p distinct, évitant j,
on calcule

\[
P_{j,k}(x,y)=
\prod_i\left(B_{ij}+x\left[R_{ij}
                       +\sum_{l=1}^{p}B_{i k_l}y_l\right]\right).
\]

Le coefficient [x^r y_1^(beta_1)...y_p^(beta_p)] compte chaque choix avec
le facteur prod_l binom(m_(k_l),beta_l). Une occurrence choisissant la
colonne k_l peut être marquée par y_l ou rester dans R_ij; c'est précisément
le développement binomial. Après sommation des tuples et des j, on obtient
l'amplitude M_beta requise. Aucune division par une entrée B_ij n'intervient.

La multiplication progressive de ces n facteurs linéaires, tronquée aux
degrés x<=r et y_l<=beta_l, est un circuit scalaire explicite. Elle utilise
au plus

\[
(r+1)\prod_l(\beta_l+1)\le(r+1)3^{r/2}
\]

cases : b+1<=3^(b/2) pour tout entier b>=2. Il y a au plus floor(r/2)
colonnes marquées. Pour une partition beta, le nombre de couples
(j,tuple) est au plus n^(p+1). Chaque case est mise à jour à partir d'au
plus p+2 termes par ligne. On obtient donc un coût

\[
O\!\left(n^{\lfloor r/2\rfloor+2}(r+2)^2 6^r\right)
\]

pour un défaut r, en utilisant |B_r|<=2^r et en incluant les combinaisons
linéaires finales. Le facteur 6^r est un majorant volontairement large.
Les constantes alpha et c dépendent seulement de n,R,Q; elles ne cachent
aucune amplitude dépendant de a,z. Leur préparation est distincte du coût
du circuit sur les données. Elle est également effective : les valeurs
M_beta(lambda) se calculent par un tableau sur les sous-ensembles des
au plus r/2 positions marquées, sans recours aux données B.

En notant S_(I_R) le coût du préfixe disponible, préparation de B comprise,
le raccord donne ainsi la borne constructive

\[
\boxed{
C_{\rm chaine}\le S_{I_R}
 +O\!\left((R+1)(R+2)^2 6^R
             n^{\lfloor R/2\rfloor+2}\right).
}
\]

Cette borne du bloc terminal est polynomiale en n pour R fixé. Elle n'est
pas polynomiale uniformément en n et R. Elle ne fournit aucune borne
polynomiale ou quasi-polynomiale de toute la chaîne : S_(I_R) reste présent.

## 4. Première extension concrète : défaut au plus deux

Pour n>=5, on peut prendre R=2. Posons

\[
U_r=\sum_j[x^r]\prod_i(B_{ij}+xR_{ij}),\quad r=0,1,2,
\]

\[
V_2=\sum_{j\ne k}[x^2]\prod_i(B_{ij}+xB_{ik}).
\]

Le résidu de degré deux a seulement les collisions 0 et 1. La base est
M_empty=1, M_(2)=sum_k binom(m_k,2), donc alpha_empty=w(0) et
alpha_(2)=w(1)-w(0). Le raccord devient

\[
\boxed{
C_B=X-c(h_n)U_0-c(h_{n-1})U_1-c(h_{n-2})U_2
        -[c(h_{n-2}+1)-c(h_{n-2})]V_2,
\qquad X=(c(L)G)(\mathbf1).
}
\]

Les trois U se calculent ensemble en O(n^2) portes; V_2 en O(n^3) portes,
par multiplication de polynômes univariés de degré au plus deux. La
correction complète coûte donc O(n^3), depuis B.

Pour n=5 ou n>=7, les quatre valeurs terminales retirées du préfixe sont
h_n, h_(n-1), h_(n-2), h_(n-2)+1. Pour n=6, le profil (3,3) partage la
collision h_4=6 avec (4,1,1). Cette valeur doit rester dans le préfixe :
tau_2=6 et c(6)=0. Seules 7,10,15 sont alors retirées. La formule précédente
reste exacte avec ces constantes; omettre ce cas conduirait à une erreur.

## 5. Vérification indépendante effectuée

Un vérificateur exécuté séparément, sans réutiliser les extractions comme
référence, a contrôlé modulo 97 :

- 97 profils de base pour les degrés résiduels 0 à 9, avec des poids w
  arbitraires et vérification de l'inversion triangulaire;
- 30 lectures pondérées pour n=5,6,7 et r<=min(3,floor((n-1)/2)), comparées
  à l'énumération directe des lignes résiduelles et de leurs colonnes;
  matrices génériques, ligne nulle et ligne de somme nulle;
- 10 raccords complets pour n=3,4,5,6 et tous les R autorisés, comparés
  au développement indépendant par occupations de G.

Toutes ces vérifications passent. Elles contrôlent les coefficients et
les cas de collision partagée; elles ne remplacent pas les preuves
générales ci-dessus et ne constituent pas une preuve de complexité globale.

Le vérificateur initial a été enregistré dans `verify_terminal_fusion.py`,
avec sa graine 41 et le même ordre de tests. Le rapport
`terminal-fusion-validation.json` contient les empreintes SHA256 du script
et de cette note, et déclare explicitement `general_polynomial_closure=false`.

```powershell
python -X utf8 etudes/2026-11-01/borne-chaine-generale/verify_terminal_fusion.py
```

L'option `--write-report` régénère le rapport après une exécution réussie.
