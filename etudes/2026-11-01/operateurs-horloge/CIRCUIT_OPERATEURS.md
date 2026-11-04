# Nouveau circuit d'opérateurs : horloge, résolvantes et commutateurs

Reprise du 1 novembre 2026 après la demande explicite d'inventer un circuit
d'opérateurs au lieu de réénumérer les canaux exponentiels. Le prototype
principal se compile en un nombre polynomial de portes scalaires. Il est
exact jusqu'au quatrième ordre mais **réfuté à l'ordre cinq** : il ne résout
pas la chaîne générale. Les correcteurs ci-dessous ne sont pas une preuve
de fermeture à tous les ordres.

## 1. Réalisation différentielle exacte de la chaîne

Pour des variables auxiliaires x_j, poser

\[
 C_j=x_j-x_j^2\partial_{x_j},\qquad
 L_i[f]=\sum_jB_{ij}\omega^{fd_j}C_j.
\]

Sur un polynôme multiaffine F=g+x_jh, on a C_jF=x_jg. Une seconde
utilisation de la colonne j est donc annulée immédiatement. Les C_j
commutent et sont de carré nul sur cet espace invariant. Sur l'anneau
entier, C_j²=x_j^4∂_j² ; la nilpotence n'y est pas générale.

La réalisation exacte de l'architecture cible est

\[
 \mathcal Z_A[k]=\widetilde\Omega\operatorname{INTT}_N
 \left[\left((L_n[f]\cdots L_1[f]1)(1,\ldots,1)\right)_f\right][k].
\]

Les phases entrent dans chaque opérateur. La compensation de gamma_n
intervient lors du passage depuis les q_j vers la lecture positive finale.
Aucune amplitude finale n'est fournie en entrée.

Le flot d'une combinaison C_b=Σb_jC_j se calcule par transport rationnel :

\[
 T_b(t)F(x)=\prod_j(1+tb_jx_j)
 F\left(\frac{x_j}{1+tb_jx_j}\right),\qquad
 T_b(t)T_c(s)=T_{tb+sc}(1).
\]

La dérivation vérifie directement ∂_tT_b=C_bT_b et T_b(0)=Id.
Pour des jets d'ordre K, les inverses de constante 1 s'éliminent par des
séries géométriques tronquées, avec des portes ordinaires. Cette loi ferme
les flots, mais ne compile pas gratuitement le produit de n tangentes
différentes : ce premier opérateur n'est pas annoncé comme une solution.

## 2. Horloge de n+1 états, un seul paramètre de jet

Définir d=n+1 et les petites matrices

\[
 A_j[f]=\omega^{fd_j}\sum_{i=0}^{n-1}B_{ij}E_{i+1,i},
 \qquad H_f=\sum_j A_j[f]C_j.
\]

L'indice de l'horloge mémorise uniquement l'ordre des lignes, jamais un
ensemble de colonnes. L'action du générateur strictement triangulaire
donne

\[
 n![t^n](e^{tH_f}I)_{n,0}\big|_{x=1}
 =(L_n[f]\cdots L_1[f]1)(1).
\]

Le jet observable exact à reproduire est donc

\[
 U_r^*=\frac1{r!}\sum_{j_1,\ldots,j_r\ \mathrm{distincts}}
 A_{j_r}\cdots A_{j_1},\quad U_0^*=I.
\]

Cette somme définit l'invariant ; elle n'est pas l'algorithme proposé.
Le but est une dynamique fermée de matrices observables.

## 3. Circuit fermé proposé et correction universelle

Avec J_j(M)=(A_jM+MA_j)/2, le premier système proposé est

\[
 U'=\sum_jJ_jW_j,\quad W_j+tJ_jW_j=U,\quad U(0)=W_j(0)=I.
\]

Il se compile par les récurrences scalaires explicites

\[
 rU_r=\sum_jJ_jW_{j,r-1},\qquad W_{j,r}=U_r-J_jW_{j,r-1}.
\]

Ce système reproduit U_r^* pour r≤3. Pour deux matrices non nulles A,B,
il est exact à tous les ordres :
U=I+t(A+B)+t²(AB+BA)/2, W_A=I+tB et W_B=I+tA satisfont le système.
Pour trois colonnes ou davantage, le premier défaut est au degré quatre.

Une correction nouvelle a été dérivée et vérifiée dans l'algèbre libre.
En posant P=Σ_jA_j, P_2=Σ_jA_j² :

\[
\begin{aligned}
 T_1&=\sum_j[A_j,[A_j,P^2-A_jP-PA_j-P_2]],\\
 T_2&=\sum_j[A_j,P]^2-\sum_{j,k}[A_j,A_k]^2,\\
 T_3&=\sum_j\left(A_j(P-A_j)^2A_j-(P-A_j)A_j^2(P-A_j)\right),\\
 R_4&=(T_1-2T_2+2T_3)/24.
\end{aligned}
\]

Exactement, R_4=4(U_4^*−U_4^Jordan). Le système corrigé est

\[
 U'=\sum_jJ_jW_j+\frac{t^3}{2}(R_4U+UR_4),\qquad
 W_j+tJ_jW_j=U.
\]

Il reproduit les quatre premiers ordres pour une famille quelconque de
matrices, quelle que soit sa taille. La preuve consiste à comparer les
coefficients des mots : un mot de longueur quatre emploie au plus quatre
lettres ; les formules sont invariantes par renommage et aucune lettre
absente ne peut contribuer. Le contrôle rationnel exact sur quatre lettres
couvre donc toutes les familles. Ce n'est pas une formalisation Lean.

## 4. Coût scalaire réel

circuit.py émet un DAG composé exclusivement de portes add/mul depuis
les a_ij ou p_ij et z. Chaque entrée de matrice est un fil scalaire ; les
produits matriciels, soustractions, phases et papillons sont développés.
Les seules simplifications sont les zéros et unités connus à la construction.

La préparation de R_4 demande O(n²) produits matriciels, et les jets
O(n²) applications de Jordan. Pour d=n+1, la borne conservatrice est
O(N n²(n+1)³), donc O(n^6) avec n<N≤2n. On exige Q>max(n,3), Q premier,
et une racine d'ordre N. Les seules divisions sont par des constantes
contrôlées : 2, 24, les r≤n et N. Le lecteur est le fil n!U_n[n,0], suivi
de l'INTT effective de toutes les fréquences.

Le coût est polynomial, mais l'exactitude générale de ce circuit est
fausse. Les deux conditions doivent être distinguées.

## 5. Défaut exact au cinquième ordre

Le mot (1,1,1,3,4), en indices commençant à zéro, conserve le coefficient
1 après multiplication par 5!, alors que sa colonne répétée exige zéro.
Avec d_j=j, sa somme vaut 10, exactement la somme des cinq labels.
Un masque du seul slot attendu ne supprime donc pas ce défaut.

validation.json gèle aussi une entrée légale z=2, Q=998244353, avec
p_ij dans {2,5,10,17}, donc p_ij=1+a_ij² pour des a entiers. Au slot
attendu k=2, le prototype renvoie 618669892 au lieu de 131890214.
Le rapport porte explicitement le statut general_candidate_rejected.

Les vérifications positives portent sur 498 coefficients de mots,
40 tables numériques et 4 tables formelles en z jusqu'à n=4.
Le correcteur universel de degré quatre reste prouvé ; le prototype
n'est pas adopté comme compilateur de la chaîne générale.

Une fermeture non linéaire a aussi été testée : dans R_4, remplacer
A_j par A_j+t(α(A_jP+PA_j)+β A_j²). Les contraintes exactes du degré
cinq ont rang 2 et rang augmenté 3 : aucun α,β ne suffit pour cette
famille précise. Reproduction : sonder_fermeture.py, avec SymPy.

## 6. Autre circuit testé : racines matricielles et Vandermonde

Un second essai définit un polynôme matriciel monique
P(T,ε)=T^n+Σ_(k<n) C_k(ε)T^k avec les racines à droite
λ_jI+εA_j. À ε=0, le système de Vandermonde est scalaire et inversible.
Ses jets se calculent par récurrence matricielle et transformée de Fourier,
sans lire un coefficient multivarié.

L'hypothèse [ε^n]C_0 = (−1)^n Sym(A_1...A_n) est vraie pour n=2 avec
des racines opposées. Elle est fausse dès n=3 : les mots répétés subsistent
et les poids injectifs sont incorrects. La moyenne des attributions de
racines et le passage au quotient cyclique ont aussi été sondés ; ils
ne réparent pas le cas général. sonder_vandermonde.py conserve les calculs
dans F_241. L'énumération des mots sert uniquement à réfuter l'identité
proposée, pas à définir un algorithme de production.

## 7. Reproduction et cadre pour la suite

`python -B verifier.py` contrôle les identités positives et la réfutation.
L'option `--write-report` actualise explicitement le rapport gelé.
Les tests utilisant les permutations sont des oracles indépendants.

Le travail requis reste une fermeture globale exacte de la dynamique,
ou un autre circuit d'opérateurs, avec un nombre polynomial de portes
scalaires à tous les ordres. Une description courte d'un opérateur, un flot
isolé ou une suite de correcteurs d'ordre fixé ne suffit pas.

Sources primaires consultées pour situer ces essais :
[Bohnenblust–Spitzer non commutatif](https://arxiv.org/pdf/0705.1265)
pour le réordonnancement, sans invoquer son action comme porte gratuite ;
[Barvinok](https://arxiv.org/pdf/math/0007153), dont le coût O(n^(r+3))
concerne une algèbre de dimension fixe r et ne donne pas un exposant
constant si r croît avec n. Aucune priorité scientifique n'est revendiquée
pour les opérateurs élémentaires utilisés ici.
