# Candidate testée : fusion des noyaux de chirp avant la lecture

Cet addendum examine une seule candidate de raccord depuis les entrées
originales. Elle compile effectivement la chaîne en portes scalaires,
mais son décompte n'est pas polynomial. Ce résultat ne prétend pas
borner les autres représentations autorisées.

## 1. Séparer les colonnes, puis commuter la moyenne

Prendre deux puissances de deux \(K>n\) et \(M>h=\binom n2\),
divisant \(Q-1\), et des racines \(\zeta,\eta\) d'ordres exacts
\(K,M\). Pour \(u_\ell=\eta^\ell\), poser

\[
w_{\ell,r}=\frac1K\sum_{a=0}^{K-1}
 u_\ell^{\binom a2}\zeta^{-ra},\quad 0\le r<K.
\]

L'orthogonalité des caractères donne, pour \(0\le a\le n<K\),

\[
\sum_{r=0}^{K-1}w_{\ell,r}\zeta^{ra}
=u_\ell^{\binom a2}.
\]

En appliquant cette identité indépendamment aux colonnes et en
distribuant le produit des lignes, on obtient

\[
C_B(u_\ell;t)=\sum_{r\in\{0,\ldots,K-1\}^n}
 \left(\prod_jw_{\ell,r_j}\right)
 G_B(t_0\zeta^{r_0},\ldots,t_{n-1}\zeta^{r_{n-1}}).
\]

La moyenne NTT peut donc être fusionnée avant toute valeur \(C_B\) :

\[
W(r)=\frac1M\sum_{\ell=0}^{M-1}\prod_jw_{\ell,r_j},\qquad
S_B(t)=\sum_r W(r)G_B(t_j\zeta^{r_j})_j.
\]

La table \((w_{\ell,r})\) a \(MK\) entrées et dépend seulement
des paramètres. La description de \(W\) est une somme de \(M\)
produits de facteurs indépendants par colonne. Ces deux observations
sont des compressions exactes des **poids**. Elles ne sont pas un
décompte du coût de leur contraction avec \(G_B\).

## 2. Partage effectif entre fréquences du papier

Le filtre ne conserve que \(m_j=1\) pour chaque colonne. En posant
\(D=\sum_jd_j\), il en résulte

\[
S_B(t(f))=\omega^{fD}S_B(1,\ldots,1).
\]

La candidate calcule donc une seule contraction globale, en partage
les données entre tous les \(f\), puis exécute les modulations et
l'INTT. Le fil \(S_B(1)\) est produit à partir de \(a,z\) dans
ce même circuit ; ce n'est ni une entrée ni un oracle. Cette organisation
est une candidate de compilation globale, sans imposer cet intermédiaire
aux autres recherches.

Ce partage élimine le facteur \(N\) devant la contraction. Il ne
réduit pas, à lui seul, le nombre de points \(r\).

## 3. Portes réellement exécutées

Le programme compagnon ne matérialise ni les moments \(\mu_r\),
ni les valeurs \(C_B(u_\ell;t(f))\), ni les sous-ensembles de
colonnes. Il évalue les points de quadrature, avec uniquement des portes
scalaires \(+\) et \(\times\). Il conserve volontairement les
produits par zéro et par un pour rendre le décompte reproductible.

Avec \(V=K^n\), les comptes exacts sont :

| Bloc | Portes |
|---|---:|
| Préparation de \(B\) depuis \(a,z\), carrés successifs partagés | \(4n^2-1\) |
| Table des chirps par transformée directe | \(2MK^2\) |
| Poids \(W(r)\) pour tous les points | \(MnV\) |
| Valeurs du produit compact pour tous les points | \((2n^2-1)V\) |
| Produits poids-valeur et sommation finale | \(2V-1\) |
| Modulation commune et INTT radix-2 | \(2N\log_2N+2N\) |

Le total vérifié est donc

\[
\boxed{4n^2-1+2MK^2+(2n^2+Mn+1)K^n-1
       +2N\log_2N+2N.}
\]

Le premier \(Q\) et les racines admissibles \(\eta,\zeta,\omega\)
sont des **paramètres fournis**. Cette étude ne démontre pas leur
génération déterministe en temps polynomial en \(n,\log Q\).
Une fois ces paramètres fournis, l'ordre exact des racines d'ordre
puissance de deux se vérifie par exponentiation, et leurs puissances
ainsi que les inverses \(K^{-1},M^{-1},N^{-1}\) se génèrent en un
nombre polynomial d'opérations en \(n,\log Q\), sans donnée originale.
Le coût de la table des chirps elle-même est inclus ci-dessus. Une FFT
peut diminuer ce bloc polynomial, sans supprimer le facteur \(K^n\)
de la contraction choisie.

Le vérificateur utilise une recherche élémentaire de racine primitive
sur les deux petits corps testés. Cette routine de préparation des tests
énumère des candidats et des facteurs de \(Q-1\) ; elle n'est pas
présentée comme une génération uniforme polynomiale des paramètres.

## 4. Conclusion limitée à cette candidate

Le raccord par chirps est exact, et la moyenne du lecteur peut être
fusionnée avec ses poids avant d'appliquer le produit compact. La phase
commune permet un partage effectif entre toutes les fréquences finales.
Toutefois, le compilateur présent parcourt encore \(K^n\) points :
**cette candidate ne donne pas la fermeture polynomiale générale**.

Le reste à inventer dans cette approche est une contraction de la somme
de produits \(W\) avec \(G_B\) qui exploite leur description conjointe
sans parcourir la grille. La petitesse des tables de paramètres ne suffit
pas à déclarer cette contraction gratuite.

`verify_chirp_contraction.py` exécute ce circuit et compare chaque slot
à une référence indépendante par choix de colonnes sur de petits ordres.
Cette référence n'appartient pas au circuit. Le rapport conserve le
décompte observé et la portée exacte de la validation.

Les 16 tables testées couvrent \(n=1,\ldots,4\), deux jeux de données
par ordre dans chacun des corps de 17 et 97 éléments. Tous les slots
coïncident avec la référence. Les tailles exactes observées sont
26, 310, 2 170 et 267 390 portes pour ces quatre ordres, ce qui confirme
le décompte et ne constitue pas une borne polynomiale.
