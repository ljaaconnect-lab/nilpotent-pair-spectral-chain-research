# Apport du papier ETH à la compilation orientée et spectrale

**Mise à jour après étude de l'existence :** la reprise
`EXISTENCE_DEFORMATIONS_2026-11-02.md` démontre désormais que, dans
la famille dense de déformations linéaires d'incidences ci-dessous,
le degré effectif est au moins L(n−s−μ). Les conditions s+μ<n et
deg F<L sont incompatibles, dans toute caractéristique. Le critère
conditionnel et son compte restent corrects, mais ne fournissent
pas une voie générale dans cette famille précise.

Étude du 2 novembre 2026. La borne polynomiale générale de notre chaîne
reste à démontrer. Le résultat nouveau de cette note est un **critère
suffisant de compilation scalaire par valeurs**, avec son coût et ses
hypothèses explicites. Le papier apporte une construction de déformations
et de mesures partagées; ses paramètres publiés ne satisfont pas encore
ce critère pour nos entrées générales.

## Source et portée de la lecture

Papier fourni : *The Exponential Time Hypothesis is False*, OpenAI,
17 octobre 2026, révision du 25 octobre, 67 pages.
Copie conservée : `../sources/papiers/openai_eth_false_2026-10-25.pdf`.
SHA256 : `5b1612dc2eebb2cad5b4cbe62d1fed2982f01ab1908c26f70010a651487e8123`.

Les 67 pages ont été examinées, avec relectures séparées des sections
3–4, 5–6 et de l'appendice D. Les pages 25 et 53 ont aussi été rendues
et inspectées intégralement. La note utilise surtout le lemme 3.2
(pages 22–23), la proposition 3.4 (pages 25–26), la construction spectrale
de la section 4 et le théorème D.1 (page 53).

[Source officielle du papier](https://github.com/openai/math/blob/main/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf).
La [note officielle de portée Lean](https://github.com/openai/math/blob/main/lean/docs/378.md)
annonce un théorème de comptage exact en temps sous-exponentiel sur des
entrées booléennes canoniques, avec espace polynomial. Ce théorème ne
certifie pas notre circuit scalaire formel. Nous n'avons pas rejoué ici
la formalisation complète du papier.

## 1. L'idée transférable : déformer les raccords

Le papier étudie des sommes de produits de facteurs. Chaque occurrence
d'une variable dans un facteur reçoit sa propre forme linéaire, dépendant
d'un paramètre T. À T=0, les raccords originaux sont rétablis. À des valeurs
entières t=1,...,L, les facteurs se séparent en groupes après fixation d'un
petit nombre de mesures communes. Une interpolation exacte reconstruit
la sortie à T=0.

Cette méthode permet de calculer l'observation finale sans conserver
fidèlement toutes les coordonnées de l'algèbre orientée. Elle n'exige
pas non plus une factorisation de rang fixé de la matrice B. C'est son
apport essentiel par rapport à notre dernier essai.

Dans cette note, **L** est le nombre de points de reconstruction;
le **p** du champ F_p est le Q=c·2^m+1 de notre architecture.
Ces deux paramètres sont distincts.

## 2. Raccord exact à notre sortie, depuis a,z

Conservons

\[
B_{ij}=(1+a_{ij}^2)z^{2^{in+j}},\qquad
\widehat R_i[f]=\sum_j B_{ij}q_j\omega^{fd_j},
\quad q_j^2=0,\quad q_iq_j=q_jq_i.
\]

Les indices i,j vont de 0 à n−1. Après la correction universelle,
la coordonnée de la sortie selon l'orientation finale est décrite par

\[
F_f(0)=\sum_{x\in\{0,1\}^n}(-1)^{n-|x|}
             \prod_i\left(\sum_jB_{ij}\omega^{fd_j}x_j\right),
\qquad
\mathcal Z[k]=\left(\frac1N\sum_f\omega^{-fk}F_f(0)\right)
\widetilde\Omega.
\tag{1}
\]

**Preuve de (1).** La somme signée sur un bit annule tout monôme qui
ne contient pas ce bit. Un monôme de degré total n contenant les n
variables a nécessairement chaque exposant égal à un. Les termes
restants sont donc exactement ceux conservés par q_j²=0. Le signe
universel convertit q_0...q_(n−1) en l'orientation finale indiquée.
L'INTT conserve alors les labels prescrits.

La somme (1) est une identité de sortie. Son énumération n'est pas
proposée comme compilateur polynomial, et F_f(0) n'est pas une entrée.
Les seules données variables restent a,z; les exposants de z sont
formels et ne sont pas réduits modulo p−1.

Introduisons des lignes P_ij(T), avec P_ij(0)=e_j, et définissons

\[
F_f(T)=\sum_x(-1)^{n-|x|}
 \prod_i\left[\sum_j B_{ij}\omega^{fd_j}
                    \langle P_{ij}(T),x\rangle\right],
\qquad
H_k(T)=\frac1N\sum_f\omega^{-fk}F_f(T).
\tag{2}
\]

Alors H_k(0) est exactement la coordonnée de notre sortie. La famille
déformée porte ensemble les coefficients, l'orientation et les phases.
Avec deg P_ij≤R et les signes fixes, le majorant brut est **nR**.

La fusion fréquentielle connue à T=0 n'est pas automatiquement valable
pour T≠0 : une déformation peut réintroduire des contributions de
colonnes répétées. De plus, l'INTT est une transformation constante
inversible, donc

\[
\max_k\deg_T H_k=\max_f\deg_T F_f.
\tag{3}
\]

En effet, le vecteur du coefficient dominant non nul reste non nul
après multiplication par une matrice inversible. Certaines sorties
peuvent bénéficier d'annulations; la seule INTT ne réduit pas le degré
maximal de la table entière.

## 3. Le coût exact que le papier nous apprend à contrôler

À chaque point t, partitionnons les variables booléennes en g groupes
de taille au plus s. Soient μ le nombre total de mesures entières et
Δ une borne de la somme des valeurs absolues des coefficients de
chaque mesure. Chaque mesure prend au plus 2Δ+1 valeurs.

Une fois toutes ces mesures fixées, chaque facteur doit dépendre
uniquement des bits de son groupe. Le lemme 3.2 donne alors au plus

\[
2g(2\Delta+1)^\mu 2^s
\tag{4}
\]

évaluations de produits de groupes. Si une telle évaluation coûte E
portes scalaires, une borne sûre du coût arithmétique est
2g(E+3)(2Δ+1)^μ2^s. Les tests sur les bits et les mesures sont
indépendants de a,z; ils déterminent le câblage à la compilation.
Pour un résultat uniforme, leur construction doit aussi être bornée.

Le transfert en portes scalaires interprète les coefficients comme
des circuits dans Q[a,z], ou dans F_p[a,z] après vérification du
changement de caractéristique. Chaque somme et produit de coefficients
devient une porte ordinaire, sans développer les puissances de z.
Le coût E inclut leurs évaluateurs. Si l'anneau de coefficients était
plutôt l'algèbre orientée entière, le coût de ses produits resterait
à compiler : le théorème abstrait sur les opérations d'anneau ne
résoudrait pas à lui seul notre problème.

Le papier souligne explicitement qu'un petit **rang** des mesures
ne suffit pas : la mesure x_1+2x_2+...+2^(n−1)x_n prend 2^n valeurs.
L'objet à borner est bien le nombre de valeurs réalisables, ou son
majorant (2Δ+1)^μ.

Dans son procédé général, lorsque les L valeurs ne suffisent pas,
la proposition 3.4 ajoute des coefficients de Taylor. Son facteur
combinatoire supplémentaire est

\[
C_q=\sum_{j=0}^{\min(q,\nu)}2^j\binom\nu j,
\qquad q=\lfloor dR/L\rfloor,
\tag{5}
\]

pour ν variables booléennes et un degré d du produit initial.
Le compte est un facteur polynomial multiplié par
L·g·C_q·(2Δ+1)^μ·2^s. Nous ne réintroduisons pas cette procédure
par jets dans notre architecture active; (5) explique la portée
du résultat du papier.

## 4. Lecture par valeurs et fusion des translations

Voici une adaptation qui utilise uniquement les valeurs. Pour tout
anneau commutatif A, tout H∈A[T] et tout entier L≥1,

\[
\deg H<L
\quad\Longrightarrow\quad
\boxed{H(0)=\sum_{t=1}^{L}(-1)^{t-1}\binom Lt H(t).}
\tag{6}
\]

**Preuve.** Pour (T_yH)(X)=H(X+y), on a T_yT_z=T_(y+z).
La différence Δ_1=T_1−I abaisse le degré. Ainsi Δ_1^L H=0.
Le développement binomial de (T_1−I)^L, évalué en zéro, puis
l'isolement du terme t=0 donnent (6).

Il s'agit d'une identité entière : aucune division ni dérivée
n'est requise. Le lecteur coûte au plus **2L−1 portes** par
coordonnée, valeurs disponibles. Cela réutilise la même loi de fusion
pour compiler cette lecture par valeurs. Ces translations agissent
sur le paramètre univarié de déformation; les anciens transports
agissaient sur les variables du lecteur orienté. Un entrelacement
entre ces deux actions n'est pas établi par cette identité.

L'identité vaut aussi sur F_p[a,z]. Toutefois, sa validité en petite
caractéristique ne fournit pas des points faciles : si p≤L, certains
t sont égaux à zéro dans le champ. Un transfert du design rationnel
du papier exige aussi que ses dénominateurs restent inversibles et
que ses propriétés de séparation soient conservées. Choisir une
caractéristique compatible, notamment p>L, ou établir directement
le design dans notre champ fait donc partie de la construction.

### Théorème conditionnel de compilation scalaire complète

Supposons que l'on construise uniformément depuis les paramètres de
taille, sans résultat final pré-calculé :

1. les formes de remplacement et les groupes satisfaisant (4);
2. les circuits de coût E pour les produits de groupes depuis a,z;
3. une preuve **symbolique**, valable pour toutes les entrées, de
   deg F_f<L pour toutes les fréquences (équivalemment deg H_k<L
   pour toute la table).

Notons C_pré le coût des préparations et de l'INTT terminale. Il inclut
les 4n²−1 portes suffisantes pour B depuis a,z, les phases et tous les
autres circuits de préparation utilisés. Les poids entiers de (6)
sont des constantes de champ; leur génération doit être uniforme.
On obtient

\[
\boxed{
C_{\rm chaîne}(n)\le C_{\rm pré}+N(2L-1)
   +2LNg(E+3)(2\Delta+1)^\mu2^s.
}
\tag{7}
\]

On peut reconstruire les valeurs à fréquence fixée puis terminer
par l'INTT, ou partager les combinaisons linéaires avec cette INTT.
La borne (7) reste valide sans exiger ce partage supplémentaire.

En particulier, pour des constantes indépendantes de n, si

\[
C_{\rm pré}+N(2L-1)+2LNg(E+3)\le K_0 n^a,
\quad s\le b\log_2 n,
\quad \mu\log_2(2\Delta+1)\le h\log_2 n,
\tag{8}
\]

alors, puisque le facteur d'énumération est au moins un,

\[
\boxed{C_{\rm chaîne}(n)\le K_0 n^{a+b+h}.}
\tag{9}
\]

Cette implication est une preuve de coût, et non une preuve que les
hypothèses (8) et le petit degré existent déjà pour nos facteurs.
Le nombre N de fréquences est explicitement compté. Aucune amplitude
ni aucun moment n'est fourni gratuitement au compilateur.

### Constantes explicites pour les facteurs de notre chaîne

Pour la famille (2), E peut être éliminé de la borne. Fixons un point,
une fréquence, une valeur des mesures et une affectation locale.
Chaque coefficient ω^(fd_j)⟨P_ij(t),x⟩ est alors une constante de champ
précompilée. Une ligne est une forme linéaire en les n entrées B_ij,
calculable en au plus 2n−1 portes. Pour r_i lignes dans un groupe,
leur produit et le signe local portent le total à au plus 2nr_i,
donc **E≤2n²**. Un groupe sans ligne donne une constante.

En utilisant une INTT naïve, dont les constantes comprennent 1/N,
le compte entièrement explicite est

\[
\begin{split}
C_{\rm chaîne}\le{}&4n^2-1+N(2N-1)+N(2L-1)\\
&+2LNg(2n^2+3)(2\Delta+1)^\mu2^s.
\end{split}
\tag{9a}
\]

Pour n≥2, N≤2n, g≤n et L≥1, cela donne la borne sûre

\[
\boxed{C_{\rm chaîne}(n)\le16Ln^4(2\Delta+1)^\mu2^s.}
\tag{9b}
\]

Justification numérique : le dernier terme est au plus
12Ln^4(2Δ+1)^μ2^s; les préparations et l'INTT coûtent au plus 12n²,
donc au plus 3Ln^4(2Δ+1)^μ2^s; le lecteur coûte au plus 4Ln,
donc au plus (1/2)Ln^4(2Δ+1)^μ2^s. La constante 16 majore la somme.

Ainsi, sous les hypothèses de degré et de design déjà explicitées,

\[
L\le C_Ln^\ell,\quad s\le b\log_2n,\quad
\mu\log_2(2\Delta+1)\le h\log_2n
\quad\Longrightarrow\quad
\boxed{C_{\rm chaîne}(n)\le16C_Ln^{\ell+4+b+h}.}
\tag{9c}
\]

Ce sont des constantes explicites : K=16C_L et c=ℓ+4+b+h.
Le modèle autorise les constantes de champ précompilées; leur génération
uniforme, la compatibilité de la caractéristique et l'existence du design
restent exigées. La borne ne suppose aucun évaluateur scalaire inconnu
pour les produits de groupes. Elle ne démontre toujours pas l'existence
générale des paramètres satisfaisant ses hypothèses.

## 5. Pourquoi le design publié ne donne pas encore ces hypothèses

### Application directe aux facteurs denses

Dans (1), ν=n, chaque facteur de ligne lit n variables et chaque
variable est lue par n facteurs de lignes. Avec les facteurs de signe,
les paramètres sont w=n, b=n+1 et n²+n incidences.
La construction efficace de la section 4 est destinée à des portées
et incidences au plus polylogarithmiques en ν; ce n'est pas notre cas.

On peut préciser le problème pour ce type exact de déformation.
Pour une ligne i, assemblons les P_ij(T) dans une matrice n×n,
notée P_i(T). Elle vaut I en zéro. Au point t, chaque ligne est dans
la somme de l'espace local du groupe du facteur et des espaces des
mesures. D'où rank P_i(t)≤s+μ.

Un défaut de rang de a en t implique que (T−t)^a divise det P_i(T) :
des opérations de lignes constantes annulent a lignes en t, puis on
factorise T−t dans chacune. Aux L points distincts, avec
deg det P_i≤nR et det P_i(0)=1, on obtient

\[
nR\ge\sum_{t=1}^L(n-\operatorname{rank}P_i(t))
\ge L(n-s-\mu).
\tag{10}
\]

Ainsi, avec le majorant brut nR adapté à nos signes fixes,
q=floor(nR/L)≥a_0:=max(0,n−s−μ), et

\[
C_q\ge 2^{a_0}\binom n{a_0}\ge2^{a_0}.
\tag{11}
\]

Si s+μ=O(log n), la procédure générale du papier conserve donc un
facteur combinatoire au moins 2^(n−O(log n)). Ceci concerne son
développement standard et ce raccord dense. Cela ne démontre pas
une borne inférieure pour tous les circuits. Cela ne prouve pas non
plus que le **degré réel de F_f** atteint nR. La reprise sur
l'existence apporte toutefois une autre borne, portant directement
sur le degré effectif, qui exclut deg F_f<L lorsque s+μ<n dans
cette famille. Voir EXISTENCE_DEFORMATIONS_2026-11-02.md.

### Encodage local exact : utile, mais sa taille se compte

On peut rendre tous les facteurs locaux avec des bits x_ij et des
sommes préfixes de lignes et de colonnes. Le facteur

\[
T(a,b,c)=(1-a)(1-b)(1-c)+(a+b-2ab)c
\]

autorise exactement les triplets 000,011,101 : c=a+b sans dépassement.
Chaque préfixe commence à 0 et finit à 1. Un poids
1+(B_ij−1)x_ij introduit l'entrée marquée. Une sélection admissible
détermine une unique extension aux bits de préfixe.

Cet encodage a ν=3n²−2n variables, au plus 3n² facteurs de portée
au plus trois et une incidence au plus trois. Il satisfait donc les
conditions locales de la section 4, mais le coût transféré est de
l'ordre de

\[
\exp O\!\left(\frac{n^2(\log\log n)^2}{\sqrt{\log n}}\right).
\]

Cette application exacte ne donne aucune amélioration asymptotique
sur nos méthodes de référence en 2^O(n). Elle montre pourquoi il faut
compter les variables auxiliaires introduites par une localisation.

## 6. Ce que le spectral du papier ajoute

Dans la section 4, des involutions commutantes Π_s décrivent des
échanges de raccords. L'opérateur

\[
W_0=\tfrac12\sum_s(I-\Pi_s),\qquad
M_0=\left(\prod_s\Pi_s\right)f_I(W_0)
\]

utilise un polynôme qui reproduit le signe (−1)^j sur une bande de
valeurs propres entières. Les directions hors bande sont conservées
exactement par des mesures partagées. Il ne s'agit pas d'écarter une
erreur numérique. Cette séparation entre action spectrale traitée
collectivement et correction exacte commune est une piste concrète
pour nos opérateurs orientés.

La réalisation publiée emploie cependant un espace auxiliaire de
dimension g^(2L). La seule petite description de cet opérateur ne
donne pas son coût scalaire polynomial. Il faut compiler son action
sur nos facteurs et compter les mesures restantes, comme dans (7).

L'appendice D traite aussi des contractions exactes de réseaux en
temps polynomial multiplié par 2^O(s_r/√log s_r), où s_r contrôle
les fils du réseau. Il utilise des coefficients modulo des puissances
de deux, des valuations, des relèvements entiers et des divisions
exactes. Le filtrage de modes ainsi obtenu ne se transporte pas
automatiquement aux portes +,× de notre champ de caractéristique
impaire. Une quantité divisible par 2^w n'y est pas nulle.
Notre orientation ne fournit pas cette propriété :
(q_0+q_1)²=2q_0q_1 reste non nul en caractéristique impaire.

## 7. Résultat de cette reprise et obligation restante

L'apport retenu est la **déformation des incidences avec mesures
partagées, reconstruite par valeurs**. Elle s'applique à la sortie
globale et conserve a,z comme seules données variables. Le lecteur
(6) et le compte (7) raccordent précisément cette méthode à la fusion
des translations et à l'INTT terminale.

Pour obtenir la borne générale, il reste à construire, pour nos
facteurs orientés généraux, un design dont :

- les valeurs se calculent avec seulement n^O(1) configurations de
  groupes et de mesures;
- le degré effectivement reconstruit est inférieur au nombre
  polynomial de points;
- tous les coefficients, évaluateurs et raccords se compilent dans
  notre modèle scalaire, avec une caractéristique compatible.

Ces obligations ne sont pas des entrées supplémentaires ni des
hypothèses déjà prouvées. La reprise sur l'existence démontre
désormais leur incompatibilité dans la famille linéaire dense
indépendante des données étudiée ici. Une autre interface de
déformation ou de lecture requiert une construction et une preuve
distinctes.

## Vérifications et fichiers reproductibles

Les validations locales sont dans `papier-eth-2026-11-02/` : identité
orientée/somme signée, phases et INTT avec z formel, lecteur par valeurs
en plusieurs caractéristiques, et table de vérité du facteur local.
Ces tests ne prétendent pas implémenter le nouvel algorithme complet
du papier ni établir une borne asymptotique générale.

Résultats des tests : 16 matrices n=1,...,4, 264 fréquences,
264 coordonnées INTT, 570 cas du lecteur avec deg H<L et huit cas
de la table de vérité locale. Les exposants formels vérifiés atteignent
33 825, sans réduction modulo 96. Des cas de degré égal à L vérifient
également que la condition de degré ne peut pas être omise en général.

La formalisation Lean locale est dans
`papier-eth-2026-11-02/lean/FiniteDifferenceReadout.lean`, avec son
`replay.py` et son `validation.json`. Le noyau a vérifié le théorème
`eval_zero_from_positive_samples` sur tout anneau commutatif, sans
`sorry`; seuls les axiomes standards de Lean apparaissent. L'identité
`translate_fusion` est également formalisée. La copie inchangée du
module Mathlib utilisé est conservée dans `lean/deps/` avec sa licence.

Le théorème de coût conditionnel (7)–(9c) est une démonstration écrite,
relue indépendamment; il n'est pas formalisé dans ce fichier Lean.
L'identité de lecture seule ne certifie ni le design des points ni
leur coût de génération.
