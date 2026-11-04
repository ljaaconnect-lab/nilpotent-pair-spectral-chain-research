# Compilation scalaire des produits orientés — 2 novembre 2026

**Résultat : la borne polynomiale générale demandée n'est pas démontrée.**
Cette reprise examine le bloc précis des `n−1` produits orientés, avec
fusion des fréquences et lecture INTT conservées. Elle établit une
construction scalaire pour une famille à rang factorisé fixé et précise
pourquoi une petite représentation matricielle universelle des `q_j`
ne permet pas d'appliquer directement le compilateur n57–n59.

Ces résultats ne remplacent pas la cible générale par une famille
restreinte. Aucun minorant pour les circuits scalaires globaux arbitraires
n'est revendiqué.

## 1. Cible et partage entre les fréquences

Sur le corps `K=F_Q`, l'algèbre concernée est

\[
 A=K[q_0,\ldots,q_{n-1}]/(q_0^2,\ldots,q_{n-1}^2),
 \qquad q_iq_j=q_jq_i.
\]

Écrivons `tau` pour la coordonnée de `q_0...q_(n−1)`. C'est une
notation de spécification de la sortie, jamais une feuille d'entrée.
Les données et les lignes spectrales restent

\[
 B_{ij}=(1+a_{ij}^2)z^{2^{in+j}},\qquad
 L_i[f]=\sum_j B_{ij}\omega^{fd_j}q_j.
\]

Le produit terminal et la lecture sont

\[
 W[f]=\gamma_n\prod_i L_i[f],\qquad
 \mathcal Z[k]=\frac1N\sum_f\omega^{-fk}W[f].
\]

L'identité déjà prouvée dans le projet donne, dans `A`,

\[
 \prod_iL_i[f]=\omega^{fD_*}\prod_iL_i[0],
 \qquad D_*=\sum_jd_j.
\]

La correction universelle convertit le monôme terminal en
`Omega_tilde`, puis l'INTT route la sortie vers `D_* mod N`.
Une compilation conjointe peut donc partager toutes les fréquences.
Il n'est pas nécessaire de construire une amplitude scalaire autonome
avant cette compilation.

## 2. Une construction scalaire exacte à rang factorisé fixé

Supposons qu'une factorisation

\[
 B_{ij}=\sum_{\alpha=1}^rU_{i\alpha}V_{j\alpha}
\]

soit disponible, ou calculée depuis les données au coût `C_fac`.
Une hypothèse de rang abstraite ne donne pas gratuitement ce circuit
de factorisation, en particulier dans le modèle sans division.

Posons

\[
 H_U(t)=\prod_{i=1}^n\sum_{\alpha=1}^rU_{i\alpha}t_\alpha
       =\sum_{|k|=n}h_kt^k,
 \qquad
 H_V(t)=\prod_{j=1}^n\sum_{\alpha=1}^rV_{j\alpha}t_\alpha
       =\sum_{|k|=n}g_kt^k.
\]

Le circuit construit les coefficients par la récurrence

\[
 h^{(d)}_k=
 \sum_{\alpha:k_\alpha>0}U_{d\alpha}h^{(d-1)}_{k-e_\alpha},
 \qquad h^{(0)}_0=1,
\]

et la même récurrence pour `g`. Ses états sont des compositions dans
`r` modes, pas des listes de colonnes utilisées.

La sortie exacte est

\[
 \boxed{
 \tau\!\left(\prod_iL_i[0]\right)
 =\sum_{|k|=n}\left(\prod_{\alpha=1}^r k_\alpha!\right)h_kg_k.
 }
\]

Pour le démontrer, poser `Q_alpha=sum_j V_(j,alpha) q_j` et développer
le produit des lignes suivant les modes : il devient
`sum_k h_k product_alpha Q_alpha^(k_alpha)`. Pour obtenir le monôme
terminal, chaque colonne doit apparaître une fois. Une affectation des
colonnes aux modes de multiplicité `k` est comptée dans `g_k`. Les ordres
des facteurs de chaque mode donnent exactement `product_alpha k_alpha!`.
L'identité ne nécessite aucune division ni inversion de factorielle.

À l'étape `d`, le nombre de multiplications est
`r binom(d+r−2,r−1)` et le nombre d'additions est ce nombre moins
`binom(d+r−1,r−1)`. Une table complète coûte donc

\[
 E(n,r)=2r\binom{n+r-1}{r}-\binom{n+r}{r}+1.
\]

On compte ici aussi une multiplication par `1`; des simplifications
peuvent réduire ce nombre. Il y a
`M(n,r)=binom(n+r−1,r−1)` coordonnées terminales. Deux multiplications
par terme et `M−1` additions donnent

\[
 \boxed{
 C_{\rm fact}(n,r)\le C_{\rm fac}+2E(n,r)+3M(n,r)-1.
 }
\]

En particulier, pour `n,r>=1`, les compositions fournissent les majorations
`binom(n+r−1,r)<=(n+1)^r` et
`M(n,r)<=(n+1)^(r−1)`. Ainsi

\[
 C_{\rm fact}(n,r)
 \le C_{\rm fac}+(4r+3)2^r n^r.
\]

C'est une borne polynomiale en `n` si `r` est fixé et si `C_fac` est
lui-même polynomial. Elle ne donne pas un exposant absolu quand `r`
croît avec `n`.

La modulation remplace `V_(j,alpha)` par
`omega^(f d_j) V_(j,alpha)`. Elle multiplie tout `H_V` par la même
constante `omega^(f D_*)`. Une seule construction des deux tables suffit
donc pour toutes les fréquences; l'INTT et le signe corrigé sont intégrés
au routage terminal.

## 3. Pourquoi le rang fixé n'est pas acquis pour nos entrées

Même en spécialisant tous les `a_ij` à zéro, la matrice marquée

\[
 B_{ij}=z^{2^{in+j}}
\]

a rang `n` sur `K(z)`. En effet, les termes de son déterminant ont
des exposants de `z` distincts : les sommes de puissances de deux
encodent des ensembles distincts de cellules. Leurs coefficients
`+1` ou `−1` sont non nuls; aucune annulation entre ces monômes
n'est possible. Ce déterminant sert uniquement à prouver le rang de
la matrice marquée, pas à remplacer la cible orientée.

La factorisation à rang fixé constitue donc une piste constructive
conditionnelle; elle n'établit pas le théorème général depuis `a,z`.
La restriction aux exposants formels, sans réduction modulo `Q−1`,
est conservée dans cet argument.

La NTT ne fournit pas non plus un rang borné pour cette piste : après
padding, la matrice des coefficients linéarisés est
`C=N^(-1) B_tilde F`, avec `F` la matrice Fourier inversible. Ainsi
`rang(C)=rang(B_tilde)=rang(B)=n` pour la famille ci-dessus. Les phases
de colonnes sont également inversibles. Cette observation concerne le
rang matriciel utilisé dans cette factorisation, pas la taille minimale
d'une autre représentation du calcul conjoint.

## 4. Portée d'une compilation par état linéaire

La composante homogène `A_k` a pour base les `q_S` avec `|S|=k`.
Pour `|T|=n−k`,

\[
 \tau(q_Sq_T)=\begin{cases}1&T=S^c,\\0&T\ne S^c.\end{cases}
\]

La matrice de la lecture du produit, en indexant la seconde base par
les compléments, est donc l'identité de taille `binom(n,k)`.
Si un encodage **linéaire** `E_k:A_k -> K^(r_k)` permet de reproduire
cette lecture pour toutes les continuations, il est injectif : deux
états identifiés auraient toutes leurs coordonnées égales, puisque
chaque continuation `q_(S^c)` lit précisément la coordonnée `S`.
D'où

\[
 \boxed{r_k\ge\binom nk.}
\]

Cette preuve concerne une interface linéaire universelle. Elle ne
prouve pas qu'un circuit global doit matérialiser cette interface.
En particulier, une représentation non linéaire dépendant des facteurs
ou des calculs qui traversent la coupure n'est pas couverte.

La restriction aux données du projet ne supprime pas cet argument
dans ce modèle. À `z=1`, les lignes accessibles comprennent le vecteur
de tous les `1` et ce vecteur augmenté de `e_j`, en choisissant
respectivement `a_i=0` et `a_i=e_j`. Ces lignes engendrent `K^n`;
leurs produits engendrent `A_k` par multilinéarité.

Les phases sont des changements de base diagonaux inversibles
`q_j -> omega^(f d_j) q_j`. Elles multiplient le couplage par la
constante non nulle `omega^(f D_*)` et n'en changent pas le rang.

Le principe de séparation par ce couplage est formalisé dans
[PairingCompression.lean](produits-orientes-2026-11-02/lean/PairingCompression.lean).
Le périmètre exact du certificat est décrit dans son rapport de
vérification; le quotient orienté et un compilateur complet ne sont
pas formalisés par ce seul lemme.

## 5. Application précise au compilateur matriciel n57–n59

Supposons que des matrices `Q_j` sur un espace `V` représentent les
générateurs comme identités d'opérateurs :

\[
 Q_iQ_j=Q_jQ_i,\qquad Q_j^2=0.
\]

Si un vecteur `v` a `Q_0...Q_(n−1) v != 0`, alors

\[
 \boxed{\dim V\ge 2^n.}
\]

Preuve : considérer les `2^n` vecteurs `v_S=product_(j in S) Q_j v`.
Dans une relation linéaire non nulle, choisir un support `S` de cardinal
minimal de coefficient non nul. Appliquer le produit des `Q_j` pour
`j` hors de `S`. Tout terme `T` non inclus dans `S` s'annule par un
carré; tout terme `T` strictement inclus dans `S` a un coefficient nul
par minimalité. Seul subsiste un multiple non nul de
`Q_0...Q_(n−1) v`, contradiction.

Un lecteur donnant une valeur non nulle sur ce vecteur terminal impose
l'hypothèse. Aucune hypothèse préalable de fidélité n'est nécessaire.

Le compilateur n57–n59 reste correct et polynomial en la dimension
`r=dim V`. Ce modèle particulier de représentation ne lui fournit pas
`r<=n^d`. Le résultat ne concerne pas une matrice construite autrement
à partir de toute l'instance et reproduisant seulement la sortie, ni un
DAG scalaire global arbitraire. La preuve de ce paragraphe est écrite;
elle n'est pas déclarée vérifiée dans Lean par le certificat du §4.

## 6. État de la démonstration générale

Les comptes déjà établis pour les préparations et l'INTT restent valables.
Ils ne permettent pas encore de donner des constantes absolues `K,c`
pour compiler le produit orienté général en `K n^c` portes scalaires.
Le cas à rang factorisé fixé ci-dessus est réellement constructif,
mais son hypothèse n'est pas celle des entrées générales.

La recherche générale reste donc une compilation conjointe dépendant
des facteurs, de leurs annulations et de la sortie spectrale. Elle
n'impose ni une amplitude en entrée, ni des moments, ni une petite
représentation fidèle de toute l'algèbre.

## Références et vérifications

Le circuit et son compte de portes passent 96 instances sur `F_1009`,
pour `1<=n<=6` et `1<=r<=4`. Les tests indépendants vérifient aussi
432 fréquences et 432 coordonnées après INTT. Les permutations
n'apparaissent que dans l'oracle de test, jamais dans le compilateur.
La preuve générale de cette construction à rang fixé est écrite au §2;
les essais numériques ne sont pas présentés comme son substitut.

Lean 4.34.1 accepte les trois théorèmes `encoding_injective`,
`card_le_finrank` et `choose_le_finrank`, sans avertissement ni `sorry`.
Ils formalisent la séparation de l'appariement abstrait et sa conséquence
dimensionnelle, sous l'hypothèse explicite de reproduction exacte de
cet appariement. Ils ne formalisent ni le compilateur Python, ni la
preuve matricielle du §5, ni la borne polynomiale générale recherchée.

- [Cadre actif avec INTT](LECTURE_INTT_ET_MOMENTS_2026-11-02.md).
- [Compilateur générique acquis](AUDIT_COMPILATION_GENERIQUE_2026-11-02.md).
- [Archives des arguments de dimension et de canaux](../etudes/2026-11-01/linearisation-mod-Q/ADAPTATION.md), sections 5–6. Le résultat sur l'algèbre et la coupure était déjà établi; la version sur le module cyclique précise ici la dimension matricielle requise.
- [Circuit à rang factorisé](produits-orientes-2026-11-02/rank_factorisation.py) et [rapport](produits-orientes-2026-11-02/rank-validation.json). Les feuilles de ce circuit sont les facteurs `U,V`, pas les entrées originales générales. Le rapport l'indique explicitement.
- [Rejeu Lean](produits-orientes-2026-11-02/lean/replay.py) et [rapport](produits-orientes-2026-11-02/lean/validation.json).

Une vérification bibliographique a aussi confirmé le coût
`O(n^2 2^n)` de la convolution sur des tables de sous-ensembles,
dans [Björklund, Husfeldt, Kaski et Koivisto](https://arxiv.org/abs/cs/0611101).
Cette représentation n'est pas utilisée par le nouveau circuit à rang
factorisé et ce résultat externe n'est pas présenté comme un minorant
de notre cible.
