# Taille du préfixe du compilateur direct retenu

## Énoncé et portée

On note `S_I^(1)(n)` le nombre de portes `+` et `*` atteignables depuis
la sortie du **compilateur direct actuel**, après substitution `s=1`,
avant la correction terminale, et en incluant la préparation de `B`
depuis `a,z`. C'est la quantité définie dans
`../BORNE_REVISEE_APRES_FUSION.md`.

Ce compilateur partage les nœuds syntaxiquement identiques, simplifie les
produits par zéro ou un, les sommes avec zéro et les opérations entre
constantes. Il ne collecte pas les termes symboliques et n'effectue pas
de simplification algébrique globale. La présente preuve dépend de ces
règles précises.

Pour tout entier pair `n=2m>=4`, et tous les paramètres admissibles,

\[
\boxed{S_I^{(1)}(2m)\ \ge\ \binom{2m}{m}\ \ge\ 2^m.}
\]

Il n'existe donc pas de majoration polynomiale uniforme de la taille de
**ce DAG**. Ce résultat ne donne aucune borne inférieure pour tous les
circuits scalaires calculant la même expression. Une autre compilation,
utilisant des identités globales ou des suppressions algébriques, n'est
pas couverte par cette preuve.

## 1. Paramètres et premières étapes réellement exécutées

Dans le corps `F_Q`, avec `Q` premier et `Q>max(2,binom(n,2))`, on pose

\[
B_{ij}=(1+a_{ij}^2)z^{2^{in+j}},\qquad
G(s)=\prod_{i=0}^{n-1}\left(\sum_{j=0}^{n-1}B_{ij}s_j\right),
\]

\[
L=\frac12\sum_{j=0}^{n-1}s_j^2\partial_j^2,
\quad K_n=\left\{\sum_b\binom b2:\ b\text{ est un bloc d'une partition de }n\right\},
\]

\[
I=K_n\setminus\{0,\binom{n-1}{2},\binom n2\}.
\]

Les éléments de `I` sont traités dans l'ordre croissant. Pour chaque
`1<=r<=m`, le profil constitué de `r` blocs de taille deux et de
`n-2r` singletons atteint la collision `r`. De plus,

\[
m<\binom{2m-1}{2}\qquad(m\ge2).
\]

Par conséquent, `1,...,m` sont exactement les `m` premiers éléments de
`I`. Les `m` premières étapes du compilateur sont bien

\[
H_0=G,\qquad H_r=H_{r-1}-\frac1r LH_{r-1}\quad(1\le r\le m).
\]

Les constantes `1/2` et `-1/r` sont non nulles dans `F_Q`.

## 2. Une propriété syntaxique de la dérivation partagée

Appelons **occurrence marquée de V** une occurrence atteignable depuis
une racine en suivant des additions et des multiplications dont l'autre
opérande est un monôme `c*s^beta`, avec `c!=0` dans `F_Q`. Le chemin vide
est autorisé. Il s'agit d'une propriété d'un chemin du graphe existant,
pas d'une représentation ajoutée au calcul.

Supposons que la dérivée de `V` considérée possède une partie non nulle
en les variables `a`; elle est donc non constante. L'implémentation de
`DAG.derivative` préserve une occurrence marquée de `partial_j V` :

* pour une addition, elle appelle la dérivation sur les deux enfants ;
* pour un produit, elle construit explicitement les deux branches de
  Leibniz. On suit celle qui dérive l'enfant marqué et laisse l'autre
  opérande inchangé ;
* le nœud retourné par l'appel récursif sur `V` est donc effectivement
  un enfant, éventuellement partagé, des opérations reconstruites ;
* un facteur monomial non nul ne devient pas le nœud zéro. Une addition
  contenant cette branche non constante ne peut pas être supprimée par
  le seul calcul entre constantes utilisé par le compilateur.

La même propriété s'applique deux fois et donne une occurrence marquée
de `partial_j^2 V`. L'élagage par degré ne supprime pas cet appel lorsque
la dérivée est non nulle : les degrés suivis par le compilateur sont des
majorants valides des degrés en chaque variable `s_j`.

Ensuite, la construction de `L` multiplie cette branche par `s_j^2/2`,
et la mise à jour de `H` la multiplie par `-1/r`, puis l'ajoute à la
racine précédente. Les nouveaux facteurs satisfont encore la condition
de monôme non nul.

**Conséquence.** Pour chaque mot `j_1,...,j_k` dont les dérivées
intermédiaires de `G` sont non nulles et non constantes en `a`, le DAG de
`H_k` contient une occurrence marquée du nœud effectivement calculé

\[
\partial_{j_k}^2\cdots\partial_{j_1}^2G.
\]

Cette assertion est une induction sur `k`, à partir de l'occurrence
vide de `G`. Elle ne suppose aucune expansion préalable en monômes.

## 3. Une famille de racines scalaires déjà présentes

Pour chaque ensemble `A` de `m` colonnes, ordonné de façon croissante
afin de fixer les appels au compilateur, considérons le nœud

\[
V_A=\left(\prod_{j\in A}\partial_j^2\right)G.
\]

Les dérivées intermédiaires après `k` colonnes sont homogènes de degré
`n-2k` en `s`. Cette homogénéité vaut aussi pour leur construction
syntaxique : une somme de dérivation assemble des termes de même degré,
un produit additionne les degrés non négatifs, et les branches de
dérivée nulle sont supprimées. Par induction depuis les formes de lignes,
un résultat de degré zéro ne possède donc aucun descendant variable `s_j`.
Il ne s'agit pas seulement d'une indépendance sémantique obtenue par
annulation de termes contenant encore `s`.

Ces dérivées ont un terme non nul de degré `2n` en `a` : on peut
affecter deux lignes à chacune des `k` colonnes déjà dérivées, et les
lignes restantes à une colonne non encore dérivée. Le coefficient de
la dérivation sur ce terme est `2^k`, non nul dans `F_Q`.

Les hypothèses de la section précédente sont donc satisfaites jusqu'à
`k=m`. Le nœud `V_A` est présent et atteignable dans `H_m`. Son degré en
`s` est nul. Sa formule exacte est

\[
V_A=2^m\!\sum_{\substack{\phi:\{0,\ldots,n-1\}\to A\\
                 |\phi^{-1}(j)|=2\ (j\in A)}}
                 \prod_{i=0}^{n-1}B_{i,\phi(i)}.
\]

Après substitution de la définition de `B`, sa partie de degré `2n` en
`a` est

\[
2^m\!\sum_{\substack{\phi:\{0,\ldots,n-1\}\to A\\
                 |\phi^{-1}(j)|=2\ (j\in A)}}
z^{\sum_i2^{in+\phi(i)}}\prod_i a_{i,\phi(i)}^2.
\]

Chaque application `phi` produit un monôme différent en `a`. Le support
des colonnes de ce monôme est exactement `A`. Pour `A!=A'`, les parties
de degré `2n` de `V_A` et `V_A'` ont donc des supports disjoints et sont
non nulles. En particulier, `V_A` et `V_A'` ne peuvent pas être le même
nœud du DAG, même après la préparation spécialisée depuis `a,z`.

Cette distinction porte sur des polynômes formels ; aucune réduction
des exposants de `z` modulo `Q-1` n'est utilisée.

Comme `V_A` a un terme de degré `2n` en `a`, sa racine n'est ni une
constante ni une variable d'entrée : elle compte comme une porte
arithmétique.

## 4. Conservation après les autres facteurs et après lecture

Chaque étape ultérieure garde la racine précédente comme opérande dans
`H-L(H)/r`. Le chemin marqué des nœuds `V_A` demeure donc présent
jusqu'au préfixe complet indexé par `I`.

La substitution `s=1` ne change pas `V_A`, puisqu'il ne dépend déjà plus
de `s`. Chacun des facteurs `c*s^beta` sur son chemin marqué devient la
constante non nulle `c`. Les simplifications des produits par un peuvent
raccourcir le chemin, mais elles ne suppriment pas son extrémité `V_A`.
Le calcul entre constantes ne peut pas supprimer une addition portant
cette branche non constante. Ainsi, toutes ces racines restent
atteignables après la substitution.

Il y a donc au moins `binom(2m,m)` racines de portes distinctes dans la
sortie scalaire du préfixe. En regroupant les `2m` colonnes en `m`
paires et en choisissant une colonne dans chaque paire, on obtient déjà
`2^m` ensembles distincts de taille `m`. Cela prouve l'énoncé annoncé.

Les ensembles `A` servent seulement à compter des nœuds déjà construits
par la dérivation. Le vérificateur les utilise comme témoins externes ;
il n'ajoute ni état de sous-ensembles ni table de jets au circuit étudié.

## 5. Vérification et limites de la vérification

`verify_derivative_roots.py` utilise la classe historique `DAG` sans la
modifier et reconstruit l'initialisation exacte depuis `a,z`. Pour
`n=4,6` et `Q=97`, il vérifie :

* que les facteurs initiaux sont effectivement `1,...,n/2` ;
* que toutes les racines témoins existent déjà : leur interrogation
  n'alloue aucun nœud supplémentaire ;
* qu'elles sont distinctes, sont des portes, et n'ont plus de dépendance
  en `s` ;
* qu'elles sont atteignables avant et après `s=1`, aussi bien après les
  `m` premiers facteurs qu'après le préfixe complet `I` ;
* que des spécialisations des entrées originales distinguent effectivement
  leurs valeurs : pour chaque `A`, choisir `z=1`, deux lignes par colonne
  de `A`, puis `a_ij=0` sur l'entrée choisie et `a_ij=22` ailleurs.
  Comme `1+22²=0` modulo 97, on obtient `G=prod_(j in A)s_j²`.
  La lecture des racines est donc exactement `V_A'=2^m delta_(A,A')`.
  Ces contrôles donnent 36 égalités pour `n=4` et 400 pour `n=6`.

Le rapport conserve l'empreinte du compilateur et celle du vérificateur.
Une deuxième compilation fraîche, sans substitution au checkpoint
intermédiaire, contrôle les mêmes racines et les mêmes comptes finaux.
Ces vérifications finies contrôlent le mécanisme décrit dans la preuve ;
elles ne remplacent pas l'argument général. La preuve générale de cette
note n'a pas été formalisée intégralement dans Lean.

Lean vérifie séparément, pour tout `m`, le lemme combinatoire
`2^m <= Nat.choose (2*m) m` et son transfert à un cardinal lorsqu'une
injection explicite est donnée. Les fichiers sont
`../lean/DirectDagCounting.lean` et
`../lean/direct-dag-counting-lean-validation.json`.
L'injection vers les portes du compilateur est prouvée dans les sections
précédentes ; elle n'est pas supposée gratuitement dans une revendication
de vérification Lean du compilateur entier.

Reproduction depuis la racine du projet :

```text
python etudes/2026-11-01/borne-chaine-generale/si-direct/verify_derivative_roots.py
```
