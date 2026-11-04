# Induction sur la chaîne native et vérification Lean

3 novembre 2026. Cette reprise suit exclusivement les constructions de
notre architecture : préparation linéarisée, produits orientés partagés,
correction du signe, fusion des phases et INTT.

**Le raisonnement inductif de composition est valide.** Il faut l'appliquer
à un invariant qui conserve à la fois la valeur représentée, les fils
effectivement construits et leur coût. La récurrence ci-dessous ferme pour
les représentants linéarisés de toute la chaîne. Sa propriété terminale
est explicitement une représentation dans le quotient ; elle ne devient
pas, par induction sur la taille, une sortie scalaire sans auxiliaires.

## 1. Théorème général de récurrence des coûts partagés

Fixer la taille du problème `n`. Le rang `i` désigne l'étape courante,
et non une nouvelle instance de taille différente. Soit `S_i` le nombre
de portes du circuit partagé déjà construit.

Supposons qu'une transition conserve le même invariant de représentation
et ajoute au plus `b_i` portes. Alors

\[
S_{i+1}\le S_i+b_i.
\]

Par induction sur `m`,

\[
\boxed{S_m\le S_0+\sum_{i<m}b_i.}
\]

La base `m=0` est immédiate. À l'étape suivante,

\[
S_{m+1}\le S_m+b_m
 \le S_0+\sum_{i<m}b_i+b_m
 =S_0+\sum_{i<m+1}b_i.
\]

En particulier, si les constantes et exposants sont indépendants du rang
et de la taille de l'instance,

\[
S_0\le K_0n^a,\qquad m\le An^b,\qquad b_i\le Kn^c,
\]

alors, pour `n>=1`,

\[
\boxed{S_m\le K_0n^a+AKn^{b+c}
 \le(K_0+AK)n^{\max(a,b+c)}.}
\]

C'est la forme précise de l'argument proposé : un nombre polynomial
d'étapes avec un incrément uniformément polynomial donne un coût total
polynomial. Une borne seulement décrite comme « polynomiale », dont
l'exposant varierait avec le rang, ne serait pas cette hypothèse.

Le partage intervient dans l'hérédité : le préfixe déjà construit est
réutilisé par ses fils, et son coût n'est pas facturé une seconde fois.

## 2. Invariant de notre préparation et de nos produits

Prendre `n<N<=2n`, avec `N` puissance de deux, `ell=log_2 N<=n`, et les
paramètres de corps admissibles fournis. Nos objets sont

\[
B_{ij}=(1+a_{ij}^2)z^{2^{in+j}},\qquad
C_{ir}=\frac1N\sum_{j<n}B_{ij}\omega^{rj},
\]
\[
L_i(x)=\sum_{r<N}C_{ir}x_{-r},\qquad
H_0=1,\qquad H_{i+1}=H_iL_i.
\]

Le nom `H_i` désigne le préfixe de `i` lignes. Le produit complet `H_n`
est notre représentant `F_0(x)` à fréquence zéro. On ne change pas de
représentation ; cette notation distingue le rang du préfixe de la fréquence.

Noter `rho_x` l'interprétation des coordonnées linéarisées dans le quotient
orienté. L'identité d'initialisation est

\[
\rho_x(L_i)=\sum_{j<n}B_{ij}q_j.
\]

L'invariant au rang `i` est donc :

1. `H_i` est le fil de sortie d'un circuit partagé sur les mêmes entrées
   `a,z,x`, avec les mêmes `N` auxiliaires ;
2. sa valeur vérifie
   \[
   \rho_x(H_i)=\prod_{t<i}\sum_{j<n}B_{tj}q_j;
   \]
3. son coût cumulé satisfait la récurrence additive annoncée.

**Initialisation.** Le préfixe vide vaut `1` et son image vaut `1`.
Les coefficients `C` sont construits une seule fois depuis `a,z`.

**Hérédité sémantique.** Puisque `rho_x` est un morphisme d'anneaux,

\[
\rho_x(H_{i+1})=\rho_x(H_i)\rho_x(L_i)
 =\prod_{t<i+1}\sum_{j<n}B_{tj}q_j.
\]

**Hérédité du coût.** La forme suivante exige au plus `2N-1` portes,
puis son produit avec le préfixe au plus une porte. Ainsi

\[
S_{i+1}\le S_i+2N,
\qquad S_i\le G_C+2iN,
\]

où

\[
G_C\le4n^2-1+2nN\ell+nN.
\]

La première multiplication par `1` s'efface. Pour `i>=1`, la borne plus
précise est `S_i<=G_C+2iN-1`.

Cette induction ne réduit pas chaque état dans une base de sous-ensembles.
Le quotient intervient dans la preuve de sa valeur, pas comme une porte
supplémentaire du programme.

## 3. Le même raccord dans le véritable type de circuit Lean

La formalisation réutilise `DenseScalar.Circuit`, le type de circuit
partagé déjà présent dans le projet. Elle peut préparer toutes les formes
`L_i` ensemble avant de composer leurs produits. Le circuit `prepare`
est alors conservé une seule fois.

Avec les formes disponibles par références de fils, la récurrence devient

\[
g_1=0,\qquad g_{i+1}=g_i+1,
\qquad \boxed{g_i=i-1\quad(i\ge1)}.
\]

Il s'agit du même décompte, regroupé différemment :

\[
\begin{aligned}
S_n
&\le\underbrace{G_C+n(2N-1)}_{\text{préparation partagée des formes}}
   +\underbrace{(n-1)}_{\text{produits ajoutés}}\\
&\le4n^2-2+2nN\ell+3nN=:P(n,N)\le18n^3.
\end{aligned}
\]

La preuve Lean des préfixes porte conjointement sur le programme,
son évaluation, son compte de portes et son image par `rho_x`. La
construction initiale `prepare` reste un paramètre explicite de ce
théorème : sa réalisation Python et les formules de son coût ne sont
pas intégralement formalisées dans ce fichier.

Pour raccorder le suffixe spectral, le programme lui transmet à la fois
le fil du produit et le faisceau des sorties de préparation. Les
constantes de Fourier autorisées sont conservées dans ce faisceau.
Leur transmission est un câblage sans porte arithmétique ; la préparation
reste construite une seule fois. Cette précision compte dans le modèle
Lean utilisé, dont les seuls constructeurs de constantes internes sont
`0` et `1` : les autres constantes de corps doivent être explicitement
fournies par les feuilles structurelles et conservées jusqu'à leur usage.

## 4. Fermeture avec le signe et la lecture spectrale

Une fois les `n` lignes fusionnées, poser

\[
D_*=\sum_jd_j,\qquad k_*=D_*\bmod N,
\qquad \widetilde W_f=\gamma_n\omega^{fD_*}H_n.
\]

La phase commune s'utilise au degré terminal. Elle n'est pas supposée
commune aux termes de chaque préfixe de degré inférieur.

L'INTT est une application linéaire finie. Elle conserve l'interprétation
par `rho_x`, car celui-ci préserve les sommes et les produits. L'identité
de son noyau spectral donne

\[
\widetilde Z_k=\gamma_n\delta_{k,k_*}H_n,
\qquad \rho_x(\widetilde Z_k)=\mathcal Z[k].
\]

Le signe ajoute au plus `epsilon_n<=1` porte. Les phases et la vraie INTT
ajoutent au plus `B(N)=2N ell+3N-3`. La récurrence de composition donne

\[
\boxed{S_{\mathrm{chaîne,représentants}}
 \le P(n,N)+\varepsilon_n+B(N)\le29n^3.}
\]

Après fusion de la lecture spectrale en routage,

\[
\boxed{S_{\mathrm{chaîne,représentants,fusionnée}}\le18n^3+1.}
\]

Le coût du produit complet est compté une fois pour toute la table.
Le raccord ne reçoit aucune amplitude finale comme entrée.

## 5. Propriété terminale encore nécessaire pour la cible scalaire

La propriété effectivement prouvée par cette induction est

\[
\text{« un fil }\widetilde Z_k(a,z,x)\text{ de taille polynomiale,
 avec }\rho_x(\widetilde Z_k)=\mathcal Z[k]\text{ ».}
\]

La cible demandée exige également

\[
\text{« un fil scalaire de sortie ne dépendant que de }a,z\text{,
 qui donne la coordonnée finale voulue ».}
\]

Cette propriété n'est pas une conséquence de l'inégalité sur `S_i`.
Dans la construction actuelle, le fil terminal reste
`gamma_n H_n(x)` au slot voulu. L'induction maintient les auxiliaires ;
elle ne contient aucune transition qui les élimine en produisant le
scalaire requis.

Un invariant renforcé peut permettre cette élimination dans la dernière
transition, conjointement avec l'INTT. Pour appliquer le théorème général
de la section 1 à cette cible, cette transition doit posséder à la fois
sa preuve de correction et sa borne uniforme de portes. La mettre comme
hypothèse dans Lean ne démontrerait pas son existence.

## 6. Vérification formelle et expérimentale

Les fichiers Lean et leurs rapports se trouvent dans
[induction-native-2026-11-03](induction-native-2026-11-03/).

| Fichier | Propriété formalisée | Hypothèses qui restent explicites |
|---|---|---|
| [SharedCostInduction.lean](induction-native-2026-11-03/SharedCostInduction.lean) | Induction des coûts et exposant uniforme `max(a,b+c)` | Coût initial, nombre d'étapes et incréments |
| [NativePrefixInduction.lean](induction-native-2026-11-03/NativePrefixInduction.lean) | Programme des préfixes, évaluation correcte, exactement `n-1` multiplications ajoutées, compatibilité avec `rho` | Circuit de préparation fourni ; morphisme d'interprétation |
| [SpectralReadoutCompatibility.lean](induction-native-2026-11-03/SpectralReadoutCompatibility.lean) | Compatibilité du passage au quotient avec la lecture linéaire ; mise en facteur du préfixe partagé | Identité d'orthogonalité du noyau pour le théorème de routage |
| [NativeChainInduction.lean](induction-native-2026-11-03/NativeChainInduction.lean) | Évaluation du programme raccordé, compte exact `prepare.gates+(n-1)+suffix.gates` et borne `29n³` sur ce programme | Préparation et suffixe fournis avec leurs bornes ; provenance admissible de leurs feuilles |

Les rapports associés sont
[récurrence des coûts](induction-native-2026-11-03/shared-cost-induction-validation.json),
[préfixes](induction-native-2026-11-03/native-prefix-lean-validation.json) et
[compatibilité spectrale](induction-native-2026-11-03/spectral-readout-lean-validation.json),
ainsi que le [programme raccordé](induction-native-2026-11-03/native-chain-lean-validation.json).
Les quatre fichiers totalisent 18 théorèmes acceptés par Lean, sans
erreur, avertissement, `sorry` ni axiome ajouté. Les empreintes des sources
et des dépendances compilées ont été contrôlées.
La vérification des énoncés ci-dessus ne constitue pas une formalisation
complète de l'algorithme Python de préparation ni de l'algorithme de
papillons INTT, et ne prouve pas la suppression des variables auxiliaires.

Le [vérificateur des préfixes](induction-native-2026-11-03/verify_prefix_induction.py)
contrôle tous les rangs pour `n=1..8`. Le
[rapport](induction-native-2026-11-03/prefix-induction-validation.json)
donne 44 contrôles structurels de rang, 264 identités orientées,
264 évaluations ordinaires et 9 identités gardant `z` formel. Les coûts
ne comptent que les portes atteignables, avec la préparation `C` partagée.
Ces contrôles finis complètent les preuves générales ; ils ne les remplacent pas.

La conclusion actuelle est donc précise : **l'induction de composition
et celle des produits partagés ferment avec une borne polynomiale pour
la représentation de toute la chaîne. L'induction donnant les sorties
scalaires finales depuis `a,z` seuls n'est pas encore fermée.**
