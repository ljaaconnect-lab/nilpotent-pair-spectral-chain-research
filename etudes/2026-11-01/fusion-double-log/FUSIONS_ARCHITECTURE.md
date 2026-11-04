# Fusions exactes de l'architecture et coût scalaire

Cette note conserve le produit de lignes, le lecteur de collisions et la sortie
spectrale corrigée du papier. Elle démontre trois fusions effectives : suppression
des copies par fréquence, suppression des facteurs sans valeur propre atteinte,
et remplacement du dernier bloc différentiel par une correction explicite.
Ces gains ne constituent pas une borne polynomiale générale de la partie restante.

## Cadre

On travaille sur un corps de caractéristique première Q, avec
Q>max(2,n(n-1)/2), et avec les paramètres spectraux admissibles du papier.
Les seules données variables sont a et z. On pose

\[
B_{ij}=(1+a_{ij}^2)z^{2^{in+j}},\qquad
\ell_i(s)=\sum_j B_{ij}s_j,\qquad
G_B(s)=\prod_i\ell_i(s),
\]

\[
D_j=s_j\partial_j,\qquad
L=\frac12\sum_j(D_j^2-D_j),\qquad h_k=\binom{k}{2}.
\]

Les entiers 1,...,n sont inversibles dans ce corps. Les phases, labels et
constantes de transformée sont des paramètres de construction du circuit.
Les logarithmes employés ci-dessous sont des séries formelles tronquées ; ils
n'ajoutent aucune porte primitive log au modèle scalaire.

## 1. Normalisation homogène et lecture d'un seul coefficient

On peut remplacer la normalisation antérieure par

\[
H_0^+(\varepsilon,s)=\prod_i(1+\varepsilon\ell_i(s)),\qquad
U_0=\log H_0^+\pmod{\varepsilon^{n+1}}.
\]

La constante vaut 1 pour toutes les données, y compris en présence d'une ligne
nulle. La source recherchée est maintenant exactement

\[
[\varepsilon^n]H_0^+=G_B.
\]

Le lecteur n'agit pas sur epsilon. Par conséquent, pour tout polynôme p,

\[
[\varepsilon^n]p(L)H_0^+=p(L)G_B.
\]

La lecture correcte après retour exponentiel est le seul coefficient d'ordre n.
Il ne faut pas sommer les coefficients ni remplacer epsilon par 1 dans cette
nouvelle normalisation.

Chaque coefficient H_k est homogène de degré k en s. La formule du logarithme
montre que chaque U_k l'est également. Ces propriétés sont conservées par le
lecteur et par toute seconde coordonnée V=phi(U), phi(X)=X+O(X^2).

La préparation des B utilise au plus 4n^2-1 portes. La préparation de toutes
les ell_i, puis de

\[
U_{0,k}=\frac{(-1)^{k+1}}{k}\sum_i\ell_i^k
\]

avec partage des puissances, utilise au total au plus 8n^2-2n-2 portes,
préparation des B comprise. Ce décompte porte sur n>=1.

Après la dernière opération différentielle, on peut évaluer les coefficients
U_k en s=(1,...,1), puis calculer le coefficient d'ordre n de exp(U).
La récurrence

\[
E_0=1,\qquad E_k=\frac1k\sum_{j=1}^k jU_jE_{k-j}
\]

utilise au plus n^2+n-2 portes, en partageant jU_j et en omettant les produits
par E_0=1. Pour V=log(1+U), le retour U=exp(V)-1 suivi de exp(U) coûte au
plus 2(n^2+n-2) portes. Ces coûts concernent la lecture, pas la construction
des coefficients différentiés.

## 2. Fusion exacte de toutes les fréquences avec l'INTT

Sur s^m, L a la valeur propre

\[
\kappa(m)=\sum_j\binom{m_j}{2}.
\]

Le lecteur pi_n(L)=prod_{r=1}^{h_n}(1-L/r) annule exactement les monômes
à collision parmi ceux de degré n. Tout monôme restant est de degré n,
sans carré, dans n variables. Il est donc nécessairement s_0...s_{n-1}.
Il existe ainsi une sortie scalaire C_B, construite par le circuit, telle que

\[
\pi_n(L)G_B(s)=C_B\prod_j s_j,
\qquad C_B=(\pi_n(L)G_B)(1,...,1).
\]

C_B n'est ni une entrée nouvelle ni une hypothèse de disponibilité : c'est
la valeur de la racine du même circuit après sa compilation différentielle.
La substitution s=1 doit avoir lieu après les dérivations nécessaires.

Aux phases t_j(f)=omega^{fd_j}, la sortie vaut

\[
C_B\omega^{fD_*},\qquad D_*=\sum_jd_j.
\]

L'orthogonalité des racines donne exactement

\[
\frac1N\sum_{f=0}^{N-1}C_B\omega^{f(D_*-k)}
=\begin{cases}C_B&k\equiv D_*\pmod N,\\0&\text{sinon.}\end{cases}
\]

Il suffit donc de compiler une seule racine évaluée en s=1, puis de la relier
au slot k*=D_* mod N. Les autres sorties sont la constante zéro. Le routage
remplace l'ensemble « phases terminales + N copies + INTT » par zéro porte
arithmétique supplémentaire. Il conserve exactement le calcul spectral de
la chaîne ; c'est une fusion justifiée par sa forme de sortie.

La correction universelle d'orientation est déjà incorporée : le produit des
paires donne gamma_n Omega_tilde, et le correcteur multiplie par gamma_n,
avec gamma_n^2=1. La sortie corrigée est donc la table scalaire précédente
dans la direction fixe Omega_tilde. Aucun signe variable n'est écarté.

Si S désigne la taille d'un circuit symbolique avant phases, le majorant
NS+2N log_2(N)+N est remplacé par S. Si S_U désigne la taille des coefficients
logarithmiques après substitution s=1, le coût final est au plus
S_U+n^2+n-2. Pour les coefficients du double logarithme, il est au plus
S_V+2(n^2+n-2).

Le compilateur direct partagé existant, spécialisé de cette manière, donne :

| n | Ancienne table, d_j=j | Après fusion spectrale |
|---|---:|---:|
| 1 | 8 | 3 |
| 2 | 65 | 26 |
| 3 | 434 | 151 |
| 4 | 4 441 | 860 |
| 5 | 35 131 | 7 708 |
| 6 | 242 471 | 55 900 |

Une vérification supplémentaire a comparé la table entière du circuit initial
au routage de cette racine pour n=1,...,6, Q=97, d_j=j^2+2j-1 et trois
instances par taille, dont z=0 : les 18 comparaisons passent. Cette vérification
a exécuté le compilateur existant en mémoire sans modifier son fichier.
Empreinte de shared_operator_dag.py utilisée :
a17cbcdae56dc3338ae46d42239d2a1a99e0b169865f16fc62f5c83b31cb3b06.

## 3. Retirer les facteurs sans valeur propre atteinte

Soit K_n l'ensemble des nombres kappa(m) pour les occupations de somme n.
Tout profil de somme au plus n se complète par des parts 1, sans modifier
kappa. Il a au plus n parts. Le même ensemble K_n contient donc les valeurs
propres rencontrées par tous les coefficients de H_0^+.

Sur cet espace, les deux polynômes d'opérateurs

\[
\prod_{r=1}^{h_n}(1-L/r),\qquad
\prod_{\lambda\in K_n\setminus\{0\}}(1-L/\lambda)
\]

sont égaux : ils valent 1 sur la valeur propre zéro et zéro sur toute autre
valeur propre atteinte. Leur égalité n'est pas revendiquée sur tous les
polynômes de degré quelconque.

K_n se construit par une programmation dynamique de constantes. Un état
(d,c), 0<=d<=n, 0<=c<=h_n, signifie qu'une partition de d produit c.
Ajouter une part b envoie cet état vers (d+b,c+binom(b,2)). Il y a O(n^3)
états et au plus n transitions par état. Cette construction ne dépend pas
des données a,z et ne calcule aucune amplitude.

Par exemple, K_4={0,1,2,3,6} et K_5={0,1,2,3,4,6,10}.
La réduction conserve le projecteur final ; les états intermédiaires peuvent
différer de ceux du produit utilisant tous les entiers.

## 4. Dernier bloc : correction explicite sans aucune dérivation

Le dernier bloc permet une fusion plus forte que son remplacement par un
polynôme en L. Toute partition de n autre que la part unique n vérifie

\[
\kappa\le h_{n-1}.
\]

En effet, pour une somme fixée, fusionner deux parts positives augmente
la somme des binomiales. Parmi les partitions ayant au moins deux parts,
le maximum est donc atteint par (n-1,1).

Après les facteurs 1,...,h_{n-1}, les seules collisions encore présentes
au degré n sont ainsi les monômes purs s_j^n. Leur coefficient dans G_B
est explicitement prod_i B_ij. Posons

\[
P_n(s)=\sum_j\left(\prod_iB_{ij}\right)s_j^n,
\qquad
c_n=\prod_{r=1}^{h_{n-1}}\left(1-\frac{h_n}{r}\right).
\]

Pour n>=2, avec un produit vide égal à 1,

\[
c_n=(-1)^{h_{n-1}}\binom{h_n-1}{h_{n-1}}.
\]

Si H est l'état après ce préfixe, alors

\[
\boxed{\pi_n(L)G_B=H-c_nP_n.}
\]

Les n-1 derniers facteurs du lecteur initial peuvent donc être remplacés
par cette soustraction explicite, sans calculer L(H).

La même preuve vaut pour tout préfixe de facteurs qui a déjà annulé toutes
les valeurs propres atteintes autres que 0 et h_n. Si I est l'ensemble
des dénominateurs de ce préfixe, il faut prendre exactement

\[
c_n(I)=\prod_{r\in I}(1-h_n/r).
\]

Pour le lecteur comprimé, I=K_n\setminus\{0,h_n\}. Pour le lecteur complet
auquel on retire seulement son tout dernier facteur,
I={1,...,h_n-1} et c_n(I)=(-1)^{h_n-1}. Ces constantes ne doivent pas être
confondues avec celle du préfixe plus court s'arrêtant à h_{n-1}.

Dans H^+, tous les coefficients d'ordre inférieur à n sont déjà stabilisés.
La correction complète est donc

\[
H^+\longmapsto H^+-\varepsilon^n c_n(I)P_n.
\]

Puisque H^+(0,s)=1, le passage au logarithme donne exactement

\[
U_n\longmapsto U_n-c_n(I)P_n,
\qquad U_k\longmapsto U_k\quad(k<n).
\]

Pour V=log(1+U), le changement est encore le même sur le coefficient n :
V_n devient V_n-c_n(I)P_n. Tous les produits susceptibles de modifier ce
terme contiennent une puissance d'epsilon supérieure à n et disparaissent
dans le quotient. Cette fusion vaut donc aussi avec le double logarithme.

À s=1, calculer P_n(1) et l'appliquer à une racine déjà construite coûte au
plus n^2+1 portes supplémentaires, B étant déjà disponible. Ainsi le
compilateur direct peut satisfaire la borne constructive

\[
C_{\rm complet}\le S_{h_{n-1}}+n^2+1,
\]

où S_r est la taille de la construction symbolique après r facteurs,
préparation de B comprise. Avec le majorant antérieur
S_{r+1}<=(9n+1)S_r+3n+2, le nombre d'itérations devient h_{n-1}, au lieu
de h_n. Cela améliore la borne explicite sans changer son type asymptotique.

## 5. Fusion triangulaire des coefficients et seconde coordonnée

Pour un coefficient k quelconque, les coefficients U_a avec a<k sont fixes
à partir du stade r_0=h_{k-1}. Dans la fenêtre r_0<r<=h_k, posons

\[
F_k=\frac12\sum_j\sum_{a=1}^{k-1}(D_jU_a)(D_jU_{k-a}).
\]

F_k est fixe dans cette fenêtre. Le correctif logarithmique commence à
l'ordre k, de sorte que

\[
U_k\longmapsto(1-L/r)U_k-F_k/r.
\]

On obtient la fusion exacte

\[
U_k^{\rm fin}=p_k(L)U_k^{\rm debut}-q_k(L)F_k,
\quad
p_k(X)=\prod_{r=r_0+1}^{h_k}(1-X/r),
\quad q_k(X)=\frac{1-p_k(X)}X.
\]

q_k est un polynôme ; aucune inversion de L n'est utilisée.
La formule se prouve par composition des transformations affines et par
l'identité Xq_k=1-p_k.

Il existe aussi une correction explicite de ce seul coefficient :

\[
U_k^{\rm fin}=U_k^{(r_0)}-
\left[\prod_{r=1}^{r_0}(1-h_k/r)\right]
\sum_j e_k(B_{0j},...,B_{n-1,j})s_j^k.
\]

La preuve reprend celle du dernier bloc, car le coefficient pur s_j^k
de [epsilon^k]H_0^+ est l'élémentaire symétrique e_k de la colonne j.
Tous ces e_k se préparent en O(n^3) portes depuis B.

Cette formule ne permet pas de remplacer prématurément U_k par sa valeur
finale dans les états des coefficients supérieurs : ceux-ci utilisent ses
valeurs intermédiaires. La fusion du dernier bloc global, au paragraphe 4,
évite ce problème de synchronisation et s'applique directement au circuit.

Enfin, pour V=phi(U)=U+O(U^2), on a V_k=U_k+R_k(U_1,...,U_{k-1}).
Dans la fenêtre précédente, R_k est fixe, et

\[
V_k\longmapsto(1-L/r)V_k-(F_k-LR_k)/r.
\]

Le même p_k(L) décrit donc la partie linéaire du bloc après un second
logarithme. Cette identité autorise la fusion ; elle ne borne pas encore
polynomialement le coût scalaire de son application.

## 6. Fusion terminale de deux niveaux avec la lecture

Pour n>=3, on peut supprimer les deux valeurs propres terminales h_{n-1}
et h_n, et ne pas calculer leurs applications différentielles. Posons

\[
I=K_n\setminus\{0,h_{n-1},h_n\},\qquad
c_\kappa=\prod_{r\in I}(1-\kappa/r).
\]

Après ce préfixe, les seules valeurs propres restantes sont 0, h_{n-1}
et h_n. La valeur h_{n-1} apparaît seulement au degré n-1 dans les
monômes purs, et au degré n dans les profils (n-1,1). En effet, pour n>=4,
toute autre partition de n a une valeur au plus h_{n-2}+1<h_{n-1}; le
cas n=3 se vérifie avec les partitions (3), (2,1), (1,1,1).

Définissons les polynômes explicites

\[
A(s)=\sum_j e_{n-1}(B_{0j},...,B_{n-1,j})s_j^{n-1},
\]

\[
B_{\rm proche}(s)=
\sum_{j,i}\left(\prod_{l\ne i}B_{lj}\right)s_j^{n-1}
\bigl(\ell_i(s)-B_{ij}s_j\bigr),
\]

\[
C(s)=\sum_j\left(\prod_i B_{ij}\right)s_j^n.
\]

Dans B_proche, j est l'unique colonne de multiplicité n-1, et i l'unique
ligne choisissant l'autre colonne. Cette unicité exige n>=3. Si H désigne
l'état après le préfixe I, sa correction entière est exactement

\[
H_{\rm final}=H-
\varepsilon^{n-1}c_{h_{n-1}}A-
\varepsilon^n\bigl(c_{h_{n-1}}B_{\rm proche}+c_{h_n}C\bigr).
\]

La lecture ne demande que le coefficient d'ordre n. Par conséquent,

\[
\boxed{
[\varepsilon^n]H_{\rm final}=
[\varepsilon^n]H-
c_{h_{n-1}}B_{\rm proche}-c_{h_n}C.
}
\]

Il est inutile de calculer A pour cette lecture. On effectue le retour de
logarithme, ou de double logarithme, sur l'état du préfixe ; on lit son
coefficient n ; on soustrait les deux corrections explicites. Cette fusion
concerne ensemble le lecteur différentiel et sa lecture terminale.

À s=1, les corrections se préparent encore plus simplement. Posons

\[
p_{ij}=\prod_{l\ne i}B_{lj},\quad R_i=\sum_jp_{ij},\quad
C(1)=\sum_j\prod_iB_{ij}.
\]

Alors

\[
\boxed{B_{\rm proche}(1)=\sum_i\ell_i(1)R_i-nC(1).}
\]

Cette identité utilise p_ij B_ij=prod_l B_lj ; elle reste valable lorsque
des entrées sont nulles. Les produits p_ij se calculent par préfixes et
suffixes dans chaque colonne, sans division par une donnée. La préparation
des deux corrections et leur soustraction utilisent O(n^2) portes depuis
B. Un majorant simple, comprenant le calcul des sommes de lignes mais pas
la préparation des B, est 5n^2 portes pour n>=3.

Si S_I est la taille de la racine directe avant cette correction,
préparation des B comprise, on obtient donc

\[
C_{\rm complet}\le S_I+5n^2.
\]

Pour les coefficients logarithmiques du préfixe évalués en s=1, on obtient

\[
C_{\rm complet}\le S_{U,I}+n^2+n-2+5n^2;
\]

pour les coefficients du double logarithme, le coût de retour est au plus
2(n^2+n-2). Dans les trois cas, les copies spectrales et l'INTT sont déjà
fusionnées par le routage du paragraphe 2.

Pour vérifier également les coordonnées, écrivons
a=c_{h_{n-1}}A et b=c_{h_{n-1}}B_proche+c_{h_n}C. Dans U=log H,

\[
\Delta U_{n-1}=-a,\qquad \Delta U_n=-b+U_1a.
\]

Dans V=log(1+U),

\[
\Delta V_{n-1}=-a,\qquad \Delta V_n=-b+2V_1a.
\]

Tous les autres coefficients jusqu'à n restent inchangés. La preuve utilise
H^{-1}=1-H_1 epsilon+O(epsilon^2), H_1=U_1=V_1, et
2(n-1)>n : le carré du correctif ne contribue pas aux ordres conservés.
Ces formules de coordonnées sont exactes, mais la lecture ciblée précédente
permet de s'en dispenser dans le circuit final.

Vérification indépendante : pour n=3,...,7, trois matrices par taille
(générique, ligne nulle, ligne de somme nulle), Q=97 et des valeurs génériques
de s, le développement par occupations a été comparé aux corrections
précédentes. Les 15 cas passent à la fois pour H, U et V, soit 45 identités.
Cette expansion est uniquement un vérificateur ; elle n'intervient pas
dans les circuits O(n^2) de correction.

## Portée de la borne obtenue

Les coûts de préparation, de changement de coordonnées, de correction du
dernier bloc et de lecture finale sont explicitement polynomiaux. Le facteur
N de réplication spectrale est supprimé exactement. Des facteurs du lecteur
disparaissent et son dernier bloc ne demande plus de dérivées.

La construction des coefficients différentiés avant ce bloc reste à borner.
Le nombre polynomial de coefficients ou de facteurs ne suffit pas à borner
le nombre de portes de leurs circuits partagés. Les preuves de cette note
n'établissent donc pas la borne polynomiale générale demandée ; elles
identifient et exécutent des fusions précises de la chaîne existante.
