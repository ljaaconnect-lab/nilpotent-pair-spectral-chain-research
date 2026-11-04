# Composition des différences et lecture : résultat de la reprise

**Direction interrompue à la demande de l'auteur.** Ce document conserve
la recherche déjà effectuée avant le recentrage. La suite active est
`../fermeture-adaptative/ETAT_DIRECT.md` et porte sur la construction
directe de la chaîne orientée et spectrale.

**La fermeture polynomiale générale demandée n'est pas établie.** Cette
reprise construit une réduction exacte, avec toutes ses portes scalaires
comptées, de la sortie de la chaîne vers le permanent générique. Elle
vérifie aussi plusieurs propositions de fermeture. Aucun résultat négatif
sur un modèle restreint n'est présenté comme une impossibilité générale.

## 1. Cible maintenue

On conserve les entrées originales, les marqueurs et la correction du signe :

\[
B_{ij}=(1+a_{ij}^2)z^{2^{in+j}},\qquad
\mathcal Z_Q[k]
=\widetilde\Omega\,\operatorname{INTT}_N
 \left[\left(\lambda_B\left[
   \prod_j(T_{\omega^{fd_j}e_j}-I)1\right]\right)_f\right][k].
\]

La cible est un circuit de portes scalaires ordinaires \(+,\times\), depuis
\(a_{ij},z\) et les constantes autorisées, calculant cette expression
**comme polynôme formel**. Une soustraction coûte une multiplication par
\(-1\), puis une addition. L'ordre interne du circuit est libre ; aucune
amplitude \(P_A\) n'est une feuille ou un intermédiaire imposé.

Le coût de construction, de fusion et de lecture doit être inclus. Un
nombre polynomial de nœuds « opérateurs » ne donne pas encore ce coût.

## 2. Théorème de réduction avec borne explicite

Soit \(K\) un corps de caractéristique différente de deux, muni des
constantes spectrales nécessaires. Supposons **donné** un circuit scalaire
\(C_n\) de \(s(n)\) portes pour toute la table \(\mathcal Z_Q\), après
identification de sa coordonnée \(\widetilde\Omega\).

Alors on construit uniformément, à partir de ce circuit, un circuit pour
le permanent générique de \(X=(x_{ij})\), avec au plus

\[
\boxed{n^2+7(n+1)^2s(n)}
\]

portes scalaires sur le même corps \(K\). Le circuit \(C_n\) est une
hypothèse de cette implication, **pas une construction obtenue ici**.

### Substitution des entrées originales

Travailler dans l'algèbre commutative de dimension deux
\(E=K[\iota]/(\iota^2+1)\). Il n'est pas nécessaire de décider si
\(-1\) est un carré dans \(K\) ni de choisir une racine dans le corps.
Chaque élément de \(E\) est représenté par une paire de scalaires de \(K\).

Fixer \(z=1\) et substituer

\[
a_{ij}(t)=\iota-\frac{\iota}{2}t x_{ij}.
\]

L'identité exacte est

\[
\boxed{1+a_{ij}(t)^2=t x_{ij}-\frac{t^2}{4}x_{ij}^2.}
\]

Le terme constant est nul et le coefficient linéaire est exactement
\(x_{ij}\). Il n'y a ni racine carrée de donnée à calculer, ni série
infinie, ni division par une factorielle.

La formule de sortie déjà démontrée dans `fusion-ntt` donne, pour
\(k_* = \sum_j d_j\bmod N\),

\[
\begin{aligned}
\mathcal Z_Q[k_*](a(t),1)/\widetilde\Omega
 &=\sum_{\sigma\in S_n}\prod_{i=0}^{n-1}
 \left(t x_{i,\sigma(i)}-\frac{t^2}{4}x_{i,\sigma(i)}^2\right),\\
\boxed{[t^n]\bigl(\mathcal Z_Q[k_*](a(t),1)/\widetilde\Omega\bigr)}
 &=\boxed{\operatorname{perm}(X)}.
\end{aligned}
\]

La notation `/Omega` désigne la coordonnée dans la base terminale, pas
une division par un élément extérieur. L'orientation et le signe sont
ceux de la chaîne corrigée. La seconde égalité résulte du fait que les
\(n\) facteurs ont tous un degré minimal égal à un. Prendre un terme
quadratique ferait dépasser le degré \(n\).

Cette réduction agit sur **la sortie entière** du circuit recherché. Elle
ne demande jamais de fournir \(P_A\) à ce circuit.

### Compilation scalaire de l'extraction

Remplacer chaque fil du circuit par ses \(n+1\) coefficients en \(t\),
modulo \(t^{n+1}\), chacun représenté par une paire de scalaires. La
troncature commute avec les additions et multiplications. On ne développe
ni les monômes en \(x_{ij}\), ni des sous-ensembles de colonnes : chaque
coefficient est lui-même un fil scalaire du circuit produit.

Pour les paires,

\[
(u,v)(r,s)=(ur-vs,\,us+vr).
\]

Cette opération utilise sept portes \(+,\times\) : quatre produits,
une multiplication par \(-1\), puis deux additions. L'addition de deux
paires utilise deux portes. Ainsi :

| Opération du circuit source | Portes scalaires après simulation |
|---|---:|
| Addition | \(2(n+1)\) |
| Multiplication | \(7\frac{(n+1)(n+2)}2+n(n+1)=\frac{(n+1)(9n+14)}2\) |
| Préparation de tous les \(a_{ij}(t)\) | au plus \(n^2\) |
| Lecture du coefficient réel de degré \(n\) | zéro, sélection d'un fil |

Le coût d'une multiplication est au plus \(7(n+1)^2\), ce qui prouve
la borne annoncée. La partie imaginaire du coefficient lu est nulle,
puisque l'identité donne un polynôme à coefficients dans \(K\).

Il s'agit d'un compilateur explicite, `jet_compiler.py`, et non d'une
extraction déclarée gratuite. Ce compilateur transforme un circuit source
disponible ; il ne crée pas le circuit polynomial encore recherché.

L'hypothèse d'identité formelle compte : un circuit seulement correct comme
fonction sur les points d'un corps fini peut contenir des termes
\(a^Q-a\). Ceux-ci ne s'annulent pas sous une substitution en jets. La
réduction ci-dessus ne s'appliquerait pas à ce contrat différent sans
argument supplémentaire.

## 3. Réduction spectrale plus courte avec le module du papier

Les constantes NTT autorisées donnent une réduction encore plus directe.
Pour \(n\ge2\), choisir \(n<N\le2n\), \(N\) puissance de deux et
\(\omega\in\mathbb F_Q\) d'ordre \(N\). Alors \(4\mid N\) et
\(\iota=\omega^{N/4}\) satisfait \(\iota^2=-1\) dans le corps initial.

Avec la même substitution affine, écrire
\(F(t)=\mathcal Z_Q[k_*](a(t),1)/\widetilde\Omega\). La sortie exacte
est supportée seulement entre les degrés \(n\) et \(2n\). Par conséquent
\(t^{-n}F(t)\) est un polynôme de degré au plus \(n<N\).
L'orthogonalité des racines donne

\[
\boxed{
\operatorname{perm}(X)
=\frac1N\sum_{r=0}^{N-1}\omega^{-nr}
\bigl(\mathcal Z_Q[k_*](a(\omega^r),1)/\widetilde\Omega\bigr).
}
\]

Preuve directe : pour chaque degré \(k\in[n,2n]\), son poids dans cette
somme est \(N^{-1}\sum_r\omega^{r(k-n)}\). Il vaut un si \(k=n\), zéro
sinon, puisque \(0\le k-n\le n<N\). Si \(k>n\), la somme géométrique
s'annule car \(\omega^{k-n}\ne1\) et \((\omega^{k-n})^N=1\).
La modulation par \(\omega^{-nr}\) empêche le repliement d'une éventuelle
puissance au-dessus de \(N\) : c'est la largeur du support après décalage
qui intervient, pas le seul degré maximal \(2n\).

Le circuit construit copie le circuit scalaire source aux \(N\) points.
Chaque substitution \(a_{ij}=\iota-(\iota/2)\omega^r x_{ij}\) coûte deux
portes. Les poids et la somme finale coûtent \(2N-1\) portes. D'où

\[
\boxed{N\,s(n)+2Nn^2+2N-1=O(ns(n)+n^3).}
\]

Pour \(n=1\), le permanent est simplement \(x_{00}\). Aucun passage par
une extension n'est nécessaire dans cette variante.

Cette réduction emploie exactement les entrées originales et les constantes
modulo \(Q\). Si le circuit source est formellement correct, elle produit
une identité polynomiale formelle. S'il n'est correct que comme fonction
sur \(\mathbb F_Q\), toutes les évaluations ci-dessus restent admissibles
et elle produit le permanent comme fonction sur ce corps. **Ce second
énoncé n'affirme pas une identité de polynômes multivariés.**

Cette variante spectrale est une démonstration écrite ; le développement
de son compilateur a été interrompu au recentrage et aucun fichier
`ntt_reduction.py` n'a été produit. La source de la construction devrait
déjà calculer la vraie chaîne ; cette réduction ne fournit pas la fermeture
manquante.

## 4. Comparaison dans l'autre sens

Si un circuit générique du permanent de taille \(p(n)\) est disponible,
on peut lui substituer les \(B_{ij}\), puis ajouter le raccord spectral
scalaire. La préparation des \(B_{ij}\) coûte \(4n^2-1\) portes :
\(2n^2\) pour \(1+a_{ij}^2\), \(n^2-1\) carrés successifs pour les
marqueurs et \(n^2\) produits. Le raccord spectral du papier coûte au plus
\(2N\log_2N+3N-3\), avec \(n<N\le2n\).

Par conséquent les deux familles de sorties ont des circuits de taille
polynomiale simultanément, dans ce modèle formel et à constantes de corps
autorisées. Cette comparaison ne prescrit aucun ordre de calcul aux
représentations globales que l'on cherche à inventer.

Sur un corps fixé de caractéristique zéro, l'existence de circuits
polynomiaux pour le permanent est la question centrale de la complexité
algébrique, présentée comme ouverte dans les travaux récents de
[Dwivedi, Pago et Seppelt (2026)](https://arxiv.org/abs/2601.09343).
La réduction ne prouve donc aucune impossibilité : elle établit précisément
le résultat qu'une fermeture générale fournirait. Pour des corps
\(\mathbb F_{Q(n)}\) variables, la comparaison s'entend séparément sur les
mêmes corps ; on n'en déduit pas un relèvement automatique en
caractéristique zéro.

## 5. Recherche de nouvelles fermetures

### Transport de base et chaînes de résolvantes

Dans le quotient tronqué au degré \(n\), tout \(T_y(1)-1\) a degré
positif. Le produit de \(n\) différences l'annihile. Donc

\[
\left(\prod_j\Delta_{t_je_j}\right)T_y(1)
=\left(\prod_jt_j\right)\mathcal I_{n-1}\cdots\mathcal I_0(1).
\]

On peut changer le transport de base sans changer la lecture terminale.
Mais sur l'état triangulaire, \(A'_j=R_yA_j\) conserve sa première
sous-diagonale, qui contient toutes les amplitudes \(B_{ij}\).

L'identité de résolvante
\(R_{S+j}-R_S=R_{S+j}A_jR_S\) permet également d'écrire les différences
mixtes comme sommes de chaînes. À la lecture terminale, les \(n\) facteurs
\(A_j\) occupent tout le degré et les facteurs de résolvante supplémentaires
ne contribuent que par leur identité. Aucune fusion scalaire polynomiale
des sommes de chaînes n'a été trouvée.

### Compression par déterminants

Une première dérivée directionnelle du produit des lignes admet une
compression déterminantielle. La famille proposée pour répéter cette
opération était \(\det(U^T\operatorname{diag}(x)V)\), avec
\(U,V\) de taille \(n\times(n-r)\) après \(r\) dérivées, indépendantes
des variables \(x_i\) (elles peuvent dépendre des directions).

Dès \(r=2,n=5\), cette famille échoue : pour deux directions toutes égales
à un, la dérivée vaut \(2e_3(x)\). Cauchy–Binet imposerait des coefficients
complémentaires \(p_{ij}q_{ij}=2\) pour \(i\ne j\), où \(p\) et \(q\)
sont des coordonnées de bivecteurs décomposables. Les matrices
antisymétriques correspondantes ont rang au plus deux ; leur produit
terme à terme a rang au plus quatre. Or la matrice des coefficients
\(2(J-I)\) a rang cinq sur \(\mathbb F_{17}\).

Ce résultat porte seulement sur cette réalisation déterminantielle.

### Une seule observation univariée

À \(n=3,z=1\), fixer les colonnes futures
\(b=(1,1,2)\), \(c=(2,2,1)\). Les deux colonnes déjà traitées
\(w=(1,2,5)\), \(w'=(5,2,1)\) donnent la même courbe après première
différence, sur la direction commune \(b+c=(3,3,3)\) :

\[
h(t)=(3t+1)(3t+2)(3t+5)-27t^3=72t^2+51t+10.
\]

Pourtant leurs lectures après les deux différences futures sont
respectivement \(35\) et \(39\), donc \(1\) et \(5\) modulo \(17\).
Toutes les entrées \(1,2,5\) ont la forme \(1+a^2\). La courbe, tous ses
coefficients et toute sa matrice de Hankel ne suffisent donc pas à cette
fermeture. Cela ne rejette pas un état enrichi qui conserve d'autres
informations, notamment les marqueurs formels.

## 6. Vérifications et portée

`verify_jets.py` vérifie la compilation sur 72 circuits aléatoires, en
comparant tous les coefficients avec une évaluation polynomiale indépendante
non tronquée. Il applique aussi la transformation à 33 tables complètes
des circuits d'insertion existants, jusqu'à \(n=5\), sur
\(\mathbb F_3,\mathbb F_{17},\mathbb F_{97}\). Tous les coefficients de
degré inférieur à \(n\), tous les canaux non cibles et toutes les parties
imaginaires s'annulent comme prévu. Les coûts exacts sont enregistrés.

Le circuit source de ces tests est celui de `fermeture-generale`, dont le
majorant reste exponentiel. Le fait que sa transformation soit polynomiale
**en sa taille** ne rend pas cette taille polynomiale en \(n\).

`TerminalReadout.lean` formalise le noyau algébrique annoncé dans ses
énoncés. L'agent auteur a compilé ce fichier ; la relecture indépendante
préparée par `replay_lean.py` a été interrompue au recentrage. Il n'existe
donc pas de rapport `lean-validation.json` pour cette étude. Les rapports
de tests ne certifient pas cette preuve ni la justification écrite du coût.
La fermeture scalaire générale n'est ni un théorème déclaré ni une
hypothèse dissimulée dans Lean.

**Ce qui manque demeure une construction uniforme du circuit source
\(C_n\) avec une borne \(s(n)\le Cn^c\), pour des constantes \(C,c\)
indépendantes de \(n\).** Les nouvelles identités et transformations ne
fournissent pas cette construction.
