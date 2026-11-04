# Fermeture des états partagés et lecture terminale étiquetée

3 novembre 2026. On poursuit l'induction sur notre architecture native.
La construction ci-dessous donne une fermeture effective des états de
circuit partagé, puis une propriété terminale suffisamment forte pour
produire explicitement un circuit scalaire de même taille.

**Portée :** la fermeture des états est établie. La lecture scalaire est
construite à partir d'un certificat de normalisation terminale portant
sur un circuit de coefficient réellement construit. L'[audit des travaux
antérieurs](AUDIT_NORMALISATION_EXISTANTE_2026-11-03.md) confirme que des
normalisateurs exacts généraux existaient déjà. Ce qui reste à établir est
le raccord d'une telle normalisation à un budget polynomial uniforme pour
le même circuit partagé. La seule fermeture des représentants ne fournit
pas ce raccord de coûts.

## 1. L'état fermé conserve ses fils et sa représentation

On note `a` l'ensemble des entrées originales, comprenant les `a_ij`, `z`
et les constantes structurelles autorisées ; `x` désigne les auxiliaires
de représentation. Un état est un circuit partagé `C` dont les sorties
sont un faisceau de fils utilisables par la suite.

Si `U` est un bloc qui reçoit ce faisceau, on définit concrètement

\[
\operatorname{Ext}(C,U)
 =C\ ;\ (\operatorname{Id},U).
\]

Le nouveau circuit produit à la fois les anciens fils et les nouvelles
valeurs. Son évaluation et son coût satisfont exactement

\[
\operatorname{Ext}(C,U)(a,x)
 =\bigl(C(a,x),\ U(C(a,x))\bigr),
\]
\[
\boxed{|\operatorname{Ext}(C,U)|=|C|+|U|.}
\]

La préparation est conservée une fois. Les constantes nécessaires au
spectral restent accessibles dans le même faisceau. Cette construction
réalise un prolongement de programme ; elle ne développe pas son préfixe
en plusieurs copies.

Une suite quelconque de blocs compatibles satisfait donc

\[
|C_m|=|C_0|+\sum_{i<m}|U_i|.
\]

En utilisant la récurrence déjà vérifiée, si

\[
|C_0|\le K_0n^a,\qquad m\le An^b,\qquad |U_i|\le Kn^c
\]

avec des constantes uniformes et `n >= 1`, alors

\[
\boxed{|C_m|\le(K_0+AK)n^{\max(a,b+c)}.}
\]

Ce résultat compte les portes arithmétiques. Le type abstrait de circuit
accepte des interfaces arbitraires ; il ne certifie pas à lui seul leur
finitude ni le coût de description de leurs câblages. Pour l'application
native, les interfaces utilisées doivent être finies et les blocs
effectivement construits avec les dimensions annoncées. Le présent
théorème ne fournit pas une nouvelle instance native normalisée avec un
budget scalaire polynomial uniforme.

## 2. La correction est conservée par tout le circuit partagé

La fermeture ne porte pas seulement sur les nombres de portes. Pour tout
morphisme de semi-anneaux `rho : R -> A`, l'évaluation du type de circuit
utilisé dans le projet vérifie

\[
\boxed{\rho\bigl(\operatorname{eval}(C,u)\bigr)
 =\operatorname{eval}(C,\rho\circ u)}
\]

composante par composante. La preuve couvre les constantes `0,1`, les
fils, les additions, les multiplications, la juxtaposition, la
parallélisation et la composition. Le partage est donc inclus dans la
propriété.

Pour nos coordonnées linéarisées, `rho_x` interprète les auxiliaires dans
le quotient orienté. Il apparaît dans la preuve sémantique, sans être une
porte ajoutée au circuit. Ainsi, les représentants restent corrects sous
toutes les extensions arithmétiques compatibles : produits de lignes,
correction du signe, phases et lecture linéaire spectrale.

On peut donc énoncer l'invariant récurrent général sous la forme

\[
\mathcal F_i(n):\quad
\rho_x(C_i)=V_i,
\qquad |C_i|\le K_0n^a+iKn^c,
\qquad\text{les fils précédents restent accessibles.}
\]

Pour un bloc scalaire `U_i` dont l'interprétation est l'opération native
voulue et dont le coût est au plus `K n^c`, on construit

\[
C_{i+1}=\operatorname{Ext}(C_i,U_i),\qquad
V_{i+1}=(V_i,\operatorname{eval}(U_i,V_i)).
\]

La naturalité donne la première composante de `F_(i+1)` ; l'identité
de coût donne la deuxième ; la définition d'`Ext` donne la troisième.
Ainsi `F_i` implique `F_(i+1)` pour toute profondeur. La borne uniforme
sur le nombre de blocs donne ensuite le majorant polynomial de la
section 1. Cette hérédité concerne l'état complet du programme partagé,
pas des copies séparées de ses préfixes.

Cette propriété conserve une représentation d'éléments orientés. Elle
n'identifie pas automatiquement leur interprétation à un fil scalaire.

## 3. La propriété terminale générale à conserver

Une sortie terminale orientée est de la forme

\[
V(a)=b(a)\,\widetilde\Omega.
\]

Le label `Omega_tilde` est fixe. Écrire

\[
\iota(r)=r\widetilde\Omega
\]

désigne l'interprétation du coefficient scalaire avec son label, et non
une nouvelle primitive de lecture. Plus généralement, les preuves Lean
utilisent `iota(r)=sigma(r)*label`, où `sigma` inclut le corps ou l'anneau
de coefficients dans l'algèbre orientée.

La propriété de **normalisation terminale certifiée** est

\[
\boxed{\mathsf{Norm}_{\widetilde\Omega}(c,V)
\quad\Longleftrightarrow\quad
\forall a,x,k,\quad
\iota\bigl(c(a,x)_k\bigr)=V(a)_k.}
\]

Ici `c` est un circuit scalaire effectivement construit et compté. `V`
est la spécification de la sortie native complète, signe et INTT compris.
Il n'est ni un fil ajouté aux entrées ni une valeur fournie au programme.
Le candidat `c` peut résulter d'une compilation globale réorganisée ;
cette définition n'impose pas un calcul préalable avant le spectral.

Pour le label terminal, l'application `iota` est injective sur les
coefficients. La propriété `Norm` entraîne donc l'indépendance du
coefficient vis-à-vis de `x` : pour tous `x,y`,

\[
\iota(c(a,x)_k)=V(a)_k=\iota(c(a,y)_k)
\quad\Longrightarrow\quad c(a,x)_k=c(a,y)_k.
\]

L'injectivité porte sur les coefficients scalaires multipliant le label.
Elle ne prétend pas que la multiplication par ce label soit injective
sur l'algèbre orientée entière.

## 4. Construction effective de la lecture scalaire

Le programme de lecture est explicite :

\[
\boxed{\operatorname{Read}(c)(a)=c(a,0).}
\]

Il conserve les fils d'entrée originaux et remplace chaque auxiliaire
par une constante zéro. Ce remplacement n'ajoute aucune porte
arithmétique. La syntaxe du circuit vérifie exactement

\[
\boxed{|\operatorname{Read}(c)|=|c|.}
\]

Si `Norm(c,V)` est démontrée, alors

\[
\iota\bigl(\operatorname{Read}(c)(a)_k\bigr)=V(a)_k.
\]

Le circuit obtenu n'a plus d'entrée auxiliaire. Avec le label fidèle,
ses sorties sont les coefficients scalaires voulus. La borne de `c`
est conservée, y compris lorsqu'elle vient d'une longue composition
partagée.

Ce théorème donne un témoin de programme, `eraseAux c`, et son coût. Il
ne postule pas l'existence d'une opération de lecture à coût un.

Le raccord avec une chaîne partagée `C` est également formalisé. Si `s`
sélectionne ses fils de coefficient, le circuit produit est exactement

\[
D=\operatorname{eraseAux}
  \bigl(\operatorname{compile}(C)\ ;\ \operatorname{wire}(s)\bigr).
\]

La sélection n'ajoute aucune porte et

\[
|D|=\operatorname{budget}(C).
\]

Le théorème `certified_polynomial_family` raccorde ce programme à la
récurrence sur une famille entière. Sous le certificat `Norm` des fils
sélectionnés et les bornes uniformes de la section 1, il fournit, pour
tout `n >= 1`, un circuit `D_n` sur les seules entrées originales tel que

\[
\boxed{\iota(D_n(a)_k)=\mathcal Z_n(a)_k,
\qquad |D_n|\le(K_0+AK)n^{\max(a,b+c)}.}
\]

Les constantes sont fixées avant la quantification sur `n`. La fonction
`Z_n` dans l'énoncé reste une spécification sémantique ; le circuit fourni
n'en reçoit pas la valeur en entrée. L'hypothèse de normalisation n'est
pas supprimée par ce raccord.

Il est essentiel que `c` soit le circuit du **coefficient normalisé**.
La substitution zéro dans le représentant orienté ordinaire `H_n(x)`
ne réalise pas cette lecture.

## 5. Fermeture du format terminal sous les opérations spectrales

L'interprétation étiquetée satisfait les lois exactes

\[
\iota(u+v)=\iota(u)+\iota(v),\qquad
\iota(ru)=\sigma(r)\iota(u).
\]

Des coefficients déjà normalisés restent donc normalisés après addition
et multiplication par un scalaire construit depuis les données originales.
Lorsque leurs fils sont dans le même état partagé, chacune de ces
opérations ajoute une seule porte.

Plus généralement, pour une lecture linéaire finie,

\[
\boxed{\iota\!\left(\sum_f\alpha_{kf}u_f\right)
 =\sum_f\sigma(\alpha_{kf})\iota(u_f).}
\]

Cela couvre la correction universelle, les phases et l'INTT. Ainsi, le
format normalisé est fermé sous une suite arbitraire de ces opérations,
avec la récurrence additive de coût. Les auxiliaires du coefficient peuvent
être effacés à la toute fin.

Cette fermeture terminale ne transforme pas une multiplication de deux
éléments orientés de degrés intermédiaires en multiplication de leurs
coordonnées terminales. Les règles exactes de normalisation et leurs
réalisations antérieures sont recensées dans l'audit. Leur raccord à un
budget scalaire polynomial uniforme reste distinct de la fermeture
arithmétique des représentants.

## 6. Pourquoi le label doit rester explicite

Cette précision est nécessaire, même pour un produit sans collision.
Après correction du signe,

\[
\gamma_nq_0\cdots q_{n-1}=\widetilde\Omega
\]

a pour coefficient terminal `1`, alors que l'évaluation de ce représentant
en `q=0` vaut `0`. On doit lire le coefficient dans la paire
`(1, Omega_tilde)` et non remplacer l'élément orienté par un scalaire
constant dans la même algèbre.

Une preuve générale utilise l'augmentation `epsilon`, qui envoie chaque
générateur orienté sur zéro, et l'inclusion scalaire `sigma`. Comme
`epsilon sigma = id`,

\[
\varepsilon(V)=0,\quad \sigma(b)=V
\quad\Longrightarrow\quad b=0\quad\text{et}\quad V=0.
\]

Un élément terminal non nul ne possède donc pas un représentant scalaire
constant qui lui serait égal sans son label. Le certificat de normalisation
ci-dessus conserve précisément ce label.

## 7. Ce qui ferme et ce qui reste à construire

La propriété générale est maintenant organisée en deux règles compatibles :

\[
\begin{array}{c}
\text{état partagé correct et borné}
\\ \Downarrow\ \operatorname{Ext}
\\ \text{état partagé correct, coût augmenté du seul bloc}
\end{array}
\]

et

\[
\boxed{\mathsf{Norm}_{\widetilde\Omega}(c,\mathcal Z)
\ +\ |c|\le Kn^d
\quad\Longrightarrow\quad
\text{circuit scalaire final explicite de taille}\le Kn^d.}
\]

La première règle s'applique à nos représentants linéarisés. La seconde
est une construction effective de la lecture à partir d'un coefficient
normalisé. **Des constructions exactes générales satisfaisant `Norm`
existaient déjà ; leur existence ne reste pas à démontrer. En revanche,
le certificat `Norm` et un budget polynomial uniforme n'ont pas encore
été raccordés pour le même circuit général.** Poser `Norm` comme hypothèse
dans ce nouveau théorème ne démontre pas ce raccord de ressources.

Le travail restant est ainsi une hérédité précise : conserver ensemble
la correction normalisée et le budget scalaire polynomial dans une
compilation des fusions orientées et de l'observation finale. Ce raccord
peut être global ; aucun lecteur séparé ni amplitude préalable n'est imposé.

## 8. Fichiers vérifiables

- [SharedStateClosure.lean](fermeture-native-2026-11-03/SharedStateClosure.lean) :
  extensions d'état, préservation des fils, compte partagé et interprétation.
- [AuxiliaryErasure.lean](fermeture-native-2026-11-03/AuxiliaryErasure.lean) :
  substitution des auxiliaires et conservation exacte des portes.
- [TerminalTaggedClosure.lean](fermeture-native-2026-11-03/TerminalTaggedClosure.lean) :
  lois du label terminal et construction du lecteur à partir de `Norm`.
- [TerminalLabelNecessity.lean](fermeture-native-2026-11-03/TerminalLabelNecessity.lean) :
  nécessité de conserver le label, par l'augmentation.
- [CertifiedScalarClosure.lean](fermeture-native-2026-11-03/CertifiedScalarClosure.lean) :
  sélection des fils, lecteur explicite, coût exact et famille de bornes
  polynomiales sous les certificats énoncés.

Les **25 théorèmes** de ces cinq fichiers sont acceptés par Lean 4.34.1,
sans `sorry`, avertissement ni axiome ajouté. Les audits d'axiomes
affichent au plus `propext`, `Classical.choice` et `Quot.sound`. Le dernier
fichier réutilise les six lemmes de récurrence déjà vérifiés dans
[SharedCostInduction.lean](induction-native-2026-11-03/SharedCostInduction.lean).

Rapports :
[états partagés](fermeture-native-2026-11-03/shared-state-lean-validation.json),
[effacement](fermeture-native-2026-11-03/auxiliary-erasure-validation.json),
[label et spectral](fermeture-native-2026-11-03/tagged-closure-lean-validation.json),
[nécessité du label](fermeture-native-2026-11-03/terminal-label-lean-validation.json),
[raccord complet sous certificat](fermeture-native-2026-11-03/certified-closure-lean-validation.json).

Rejeu de l'ensemble, dans l'environnement Lean/Mathlib du projet :

```text
python -B documents/fermeture-native-2026-11-03/replay_all.py
```

Le script reconstruit les modules locaux dans l'ordre de leurs dépendances,
dont le lemme de récurrence réutilisé. Le cache du compilateur scalaire du
projet doit être disponible. Le
[rapport d'ensemble](fermeture-native-2026-11-03/all-closure-lean-validation.json)
conserve les empreintes des sources et les sorties du vérificateur.

Ces preuves sont symboliques. Elles n'infèrent pas une identité formelle
en `z` à partir de quelques évaluations dans un corps fini. Elles ne
formalisent pas intégralement les anciens compilateurs exacts généraux,
ni une réalisation normalisée de coût polynomial. Les indicateurs de
normalisation non construite dans leurs rapports décrivent la portée
de ces modules, et non l'absence historique de normalisateurs exacts.

Pour revendiquer une identité formelle en `z`, le certificat `Norm` doit
être démontré dans le semi-anneau de polynômes approprié. Une correction
seulement comme fonction sur le corps fini ne suffit pas à cette portée.
