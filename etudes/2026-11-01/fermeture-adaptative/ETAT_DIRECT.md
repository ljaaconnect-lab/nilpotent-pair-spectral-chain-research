# État direct par élimination orientée et jets

Recentrage demandé par l'auteur : construire la chaîne entière, en conservant
orientation et spectral, et chercher une fermeture scalaire de sa composition
et de sa lecture. La recherche de réductions vers un autre problème est arrêtée.

**Cette construction est exacte à tout ordre, mais son coût scalaire actuel
reste exponentiel. La fermeture polynomiale générale n'est pas démontrée.**

## 1. État et mise à jour

La nouvelle représentation élimine simultanément une ligne et une colonne.
Elle utilise une matrice résiduelle dont les coefficients sont des jets.
Il n'y a aucune division ni condition de pivot non nul.

Pour un anneau commutatif \(R\), noter
\(\operatorname{Dual}(R)=R[\varepsilon]/(\varepsilon^2)\). Un élément est
une paire \((u_0,u_1)\), avec

\[
(u_0,u_1)(v_0,v_1)=(u_0v_0,\ u_0v_1+u_1v_0).
\]

Définir récursivement le lecteur \(L_R\) d'une matrice :

\[
L_R([a])=a,
\qquad
B=\begin{pmatrix}a&r\\c&D\end{pmatrix},
\qquad C_{ij}=(D_{ij},c_i r_j)\in\operatorname{Dual}(R).
\]

Calculer \((H_0,H_1)=L_{\operatorname{Dual}(R)}(C)\), puis lire

\[
\boxed{L_R(B)=aH_0+H_1.}
\]

Pour les identités par blocs, on complète cette définition par
\(L_R(\varnothing)=1\). Le prototype reçoit des matrices non vides ;
la convention vide sert uniquement à écrire la fusion lorsque tous les
pivots ont été éliminés.

Il s'agit d'une règle complète de mise à jour et de lecture. Les jets sont
développés en portes scalaires dans le prototype ; ils ne sont pas comptés
comme des scalaires gratuits.

## 2. Preuve directement dans l'algèbre orientée

Après correction du signe universel, les colonnes portent les générateurs
pairs \(q_j\), qui commutent et satisfont \(q_j^2=0\). Isoler \(q_0\).
Les formes des lignes s'écrivent

\[
a q_0+\rho,
\qquad D_i+c_i q_0\quad(i>0),
\qquad
\rho=\sum_{j>0}r_jq_j,\quad D_i=\sum_{j>0}D_{ij}q_j.
\]

Poser

\[
P=\prod_{i>0}D_i,
\qquad
S=\sum_{i>0}c_i\prod_{\ell>0,\ell\ne i}D_\ell.
\]

Le carré nul de \(q_0\) donne
\(\prod_{i>0}(D_i+c_iq_0)=P+q_0S\).
De plus, \(\rho P=0\) : ce produit a degré \(n\) dans seulement
\(n-1\) générateurs résiduels carrés-nuls. Donc

\[
(a q_0+\rho)\prod_{i>0}(D_i+c_iq_0)
=q_0(aP+\rho S).
\]

Or

\[
\prod_{i>0}(D_i+\varepsilon c_i\rho)
=P+\varepsilon\rho S\pmod{\varepsilon^2}.
\]

Ses formes de ligne ont précisément les coefficients
\(D_{ij}+\varepsilon c_i r_j\). La lecture \(aH_0+H_1\) reproduit ainsi
la contraction orientée du bloc initial. Une induction sur la taille,
formulée simultanément pour tous les anneaux commutatifs \(R\), permet
d'appliquer l'hypothèse à \(\operatorname{Dual}(R)\). Elle établit
l'identité à tout ordre, avec les mêmes amplitudes et marqueurs.

Cette preuve ne remplace pas l'annihilation par une énumération des
colonnes utilisées : elle la transporte dans le carré nul du nouveau jet.

## 3. Raccord spectral intégré

Pour chaque fréquence \(f\), les entrées du lecteur sont directement

\[
B_{ij}[f]=(1+a_{ij}^2)z^{2^{in+j}}\omega^{fd_j}.
\]

Le circuit prépare ces valeurs, exécute l'élimination ci-dessus, puis
applique une vraie INTT :

\[
\boxed{\mathcal Z_Q[k]
=\widetilde\Omega\,
\operatorname{INTT}_N[(L_K(B[f]))_f][k].}
\]

Les phases sont présentes avant les éliminations. La correction du signe
est celle du papier : \(\gamma_nq_{[n]}=\widetilde\Omega\). Aucune
amplitude de sortie n'est donnée en entrée au circuit.

La construction respecte aussi le raccord aux différences de transports :
le lecteur obtenu est exactement
\(\lambda_B[\prod_j(T_{\omega^{fd_j}e_j}-I)1]\), par l'identité terminale
démontrée dans `fusion-ntt`. C'est une autre compilation de cette action
composée et de son observation.

## 4. Fusion compacte du résiduel et du lecteur

Les mises à jour de rang un se regroupent dans un même résolvant. Pour un
ensemble de pivots déjà éliminés \(K\) et des indices restants \(S\),
travailler dans
\(A_K=R[\varepsilon_i:i\in K]/(\varepsilon_i^2)\), avec une direction
fraîche pour chaque pivot. Pour
\(E_K=\operatorname{diag}(\varepsilon_i)_{i\in K}\), poser

\[
\begin{aligned}
\mathsf R_K&=B_{SS}+B_{SK}(I-E_KB_{KK})^{-1}E_KB_{KS},\\
\mathsf J_K&=\det(I-E_KB_{KK})^{-1}.
\end{aligned}
\]

Chaque \(\varepsilon_i\) est carré-nul et les directions commutent. Si
\(|K|=k\), la matrice \(E_KB_{KK}\) a sa puissance \(k+1\) nulle ;
l'inverse est donc une somme géométrique finie. Le déterminant possède
un terme constant égal à un. Aucun inverse d'une donnée scalaire n'est
introduit.

La fusion porte simultanément sur la matrice résiduelle et le lecteur :

\[
\boxed{
L_R(B)=[\prod_{i\in K}\varepsilon_i]\;
\mathsf J_K\,L_{A_K}(\mathsf R_K).
}
\]

Pour un pivot, \(\mathsf J_{\{i\}}=1+\varepsilon_i a\), et le coefficient
de \(\varepsilon_i\) de son produit avec \(H_0+\varepsilon_iH_1\) est
exactement \(aH_0+H_1\). Pour plusieurs pivots, l'élimination par blocs
de \(I-E B\) donne le résiduel affiché ; la factorisation de son
déterminant multiplie les lecteurs \(1+\varepsilon_i a_i\). C'est la
même règle composée, avec les pivots successifs \(a_i\). La nouvelle
direction étant fraîche, le lecteur antérieur n'en dépend pas : les
extractions successives se composent donc exactement en l'extraction
\([\prod_i\varepsilon_i]\). Pour un ensemble \(K\) non préfixe, on
permute simultanément lignes et colonnes ; les générateurs pairs
n'introduisent aucun signe supplémentaire.

Cette formule fournit une expression commune compacte, dépendant des
données, pour l'état et sa lecture. Le coefficient terminal reste à
compiler : le résolvant est actuellement calculé dans l'anneau des jets,
dont les opérations ne valent pas une porte scalaire. Les vérifications
de `verify_shared_resolvent.py` portent sur cet invariant exact, sans
attribuer un coût polynomial à son extraction.

## 5. Compte scalaire, sans cacher les jets

À profondeur \(k\), l'anneau des coefficients est
\(R_k=\operatorname{Dual}^k(K)\). Dans la représentation exacte actuelle,
une addition coûte \(A_k=2^k\) portes et une multiplication
\(M_k=2\cdot3^k-2^k\) portes. En effet,

\[
A_0=M_0=1,
\qquad A_{k+1}=2A_k,
\qquad M_{k+1}=3M_k+A_k.
\]

Pour une matrice résiduelle de taille \(n-k\), la préparation des produits
extérieurs coûte \((n-k-1)^2 M_k\), et la lecture du pivot coûte
\(M_k+A_k\). Le compte total du cœur est donc

\[
\begin{aligned}
G_n
 &=\sum_{k=0}^{n-2}
   \left(((n-k-1)^2+1)M_k+A_k\right)\\
 &=\boxed{4\cdot3^{n-1}-3\cdot2^n+n+1}\quad(n\ge1).
\end{aligned}
\]

Les premières valeurs sont \(0,3,16,65,234,787,2540\).
Avec \(N\) fréquences et l'INTT, le prototype sans simplification émet

\[
\boxed{4n^2-1+Nn^2+NG_n+2N\log_2N+N}
\]

portes scalaires. Les quatre contributions sont la préparation depuis
\(a,z\), les phases, les éliminations et l'INTT normalisée. Le comptage
donne \(11,63,155,767,2227,6783,20963\) pour \(n=1,\ldots,7\), avec
\(N\) la plus petite puissance de deux strictement supérieure à \(n\).
La préparation et les transformées ont un coût polynomial, mais elles
ne changent pas ce majorant exponentiel du cœur.

**Le point non résolu est maintenant la fusion de plusieurs directions
de jets indépendantes dans un état scalaire de taille et de coût
polynomiaux, tout en préservant cette lecture.** Remplacer simplement
ces directions par une même variable ne préserve pas en général les
termes mixtes. Aucun tel remplacement n'est supposé ici.

## 6. Vérification

Le programme `schur_jet.py` matérialise les opérations de chaque jet en
portes scalaires ordinaires. Le programme `verify_schur.py` compare la
table complète à une référence indépendante et contrôle les comptes.
Les 14 tables numériques jusqu'à \(n=7\), les cinq tables avec \(z\)
formel jusqu'à \(n=5\), les fréquences et les comptes de portes passent.
Les rapports conservent les empreintes des sources.

Le résolvant partagé, son facteur de lecture et l'extraction composée
passent 30 cas exacts, pour \(n=2,\ldots,6\) modulo 17 et 97. Ce
vérificateur développe les jets uniquement pour contrôler les identités ;
il ne leur attribue pas un coût scalaire polynomial.

Le noyau `SchurJet.lean` porte sur les identités de jets et l'élimination
d'un bloc dans un anneau commutatif, avec les hypothèses de carré nul et
de degré explicitement exposées. Ses trois théorèmes (`jet_eval`,
`jet_scale`, `block_eliminate`) ont été recompilés indépendamment avec
Lean 4.34.1 : aucune erreur, aucun avertissement, aucun `sorryAx`,
seul axiome déclaré `propext`. Le rapport `lean-validation.json` enregistre
la sortie et l'empreinte du fichier vérifié.

Le théorème de bloc prend \(q^2=0\) et \(\rho P=0\) comme hypothèses.
L'argument de degré qui établit \(\rho P=0\), l'induction complète et
le raccord spectral sont les démonstrations écrites ci-dessus ; ils
ne sont pas formalisés dans ce fichier Lean. Aucune fermeture polynomiale
de la représentation scalaire n'est supposée ni démontrée.
