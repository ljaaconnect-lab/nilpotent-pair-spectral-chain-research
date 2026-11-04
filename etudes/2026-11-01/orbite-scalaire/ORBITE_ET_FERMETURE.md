# Reprendre les objets polynomiaux choisis

Cette reprise suit la demande de l'auteur : conserver la fusion des
transports, les différences et le spectral dans une représentation
globale. La représentation récursive par jets de `fermeture-adaptative`
est un candidat auxiliaire ; son coût n'est pas une borne pour les
représentations autorisées ici.

**Une fusion et une lecture polynomiales sont établies ci-dessous sur un
état de \(1+\binom n2\) observations scalaires. La construction de cet
état depuis les entrées originales n'est pas encore bornée
polynomialement. La chaîne générale complète n'est donc pas démontrée.**

## 1. Une orbite scalaire compacte, sans évaluation matricielle

Pour tout \(F\) de l'algèbre libre tronquée du raccord NTT, poser

\[
\Phi_F(s)=\lambda_B(T_sF).
\]

La linéarité de \(\lambda_B\) et des transports, puis la loi de fusion,
donnent exactement

\[
\begin{aligned}
\Phi_{(T_y-I)F}(s)
 &=\lambda_B(T_sT_yF)-\lambda_B(T_sF)\\
 &=\Phi_F(s+y)-\Phi_F(s).
\end{aligned}
\]

Les différences d'opérateurs deviennent donc des différences ordinaires
des paramètres de l'orbite. Cette identité se compose pour toute liste
de directions ; \(T_0=I\) permet ensuite de lire la valeur au point zéro.
Elle est un entrelacement avec l'observation, pas une
substitution des produits d'opérateurs par des produits de valeurs.

Pour \(F=1\), l'orbite est le polynôme scalaire

\[
\boxed{G_B(s)=\Phi_1(s)
 =\prod_{i=0}^{n-1}\left(\sum_{j=0}^{n-1}B_{ij}s_j\right),
 \qquad B_{ij}=(1+a_{ij}^2)z^{2^{in+j}}.}
\]

Le circuit prépare tous les \(B_{ij}\) en \(4n^2-1\) portes, puis
\(G_B\) en \(2n^2-1\) portes supplémentaires. Il comporte donc
\(6n^2-2\) portes depuis \(a,z,s\). Aucune matrice ne doit être
construite pour l'exécuter ; les horloges servent à démontrer l'identité
de l'orbite. Les puissances de \(z\) restent formelles et sont partagées.

Si \(\delta_yG(s)=G(s+y)-G(s)\), la chaîne choisie devient

\[
\mathcal Z_Q[k]=\widetilde\Omega\,
\operatorname{INTT}_N\!\left[
 \left(
  (\delta_{t_{n-1}e_{n-1}}\cdots\delta_{t_0e_0}G_B)(0)
 \right)_{f=0}^{N-1}\right][k],
\qquad t_j=\omega^{fd_j}.
\]

C'est toujours la chaîne entière depuis les entrées originales ; aucune
amplitude terminale n'apparaît parmi les feuilles.

## 2. Raccord global avec B.11 du papier

Le papier, proposition B.26, fournit l'opérateur global

\[
h=\binom n2,\quad
L=\frac12\sum_j s_j^2\partial_{s_j}^2,\quad
\pi_n(X)=\prod_{r=1}^{h}(1-X/r).
\]

Travailler modulo un premier \(Q>\max(2,h)\), en plus des conditions
\(N=2^s\mid Q-1\) du raccord spectral. La forme \(Q=c2^m+1\)
ne suffit pas seule : ces inégalités et l'ordre exact de \(\omega\)
font partie des paramètres.

Pour un monôme \(s^m\) de degré total \(n\),
\(Ls^m=\kappa(m)s^m\), avec
\(\kappa(m)=\sum_j\binom{m_j}{2}\in\{0,\ldots,h\}\).
Le projecteur \(\pi_n(L)\) conserve exactement le cas où tous les
\(m_j\) valent un.

De son côté, \((\delta_{t_{n-1}e_{n-1}}\cdots
\delta_{t_0e_0}s^m)(0)\) est nul s'il manque une variable. Comme
\(\sum_jm_j=n\), utiliser toutes les variables impose aussi
\(m_j=1\) pour tout \(j\). Dans ce cas, la valeur est
\(\prod_jt_j\). Par linéarité,

\[
\boxed{
(\delta_{t_{n-1}e_{n-1}}\cdots\delta_{t_0e_0}G_B)(0)
 =(\pi_n(L)G_B)(t).
}
\]

La correction universelle est déjà comprise dans
\(\gamma_nq_{[n]}=\widetilde\Omega\). Aucun second signe n'est ajouté.

Cette équivalence porte sur le produit complet de différences et son
observation. Elle n'identifie pas un transport individuel à un facteur
\(I-L/r\). L'adaptation change la représentation de la chaîne entière.

## 3. Un état polynomial qui ferme l'action du projecteur

Poser

\[
\chi_n(X)=\prod_{r=0}^{h}(X-r)
 =X^{h+1}+\sum_{j=0}^{h}c_jX^j.
\]

Chaque monôme de degré \(n\) est un vecteur propre de \(L\) associé
à l'un des entiers \(0,\ldots,h\). Ainsi
\(\chi_n(L)H=0\) pour toute forme homogène \(H\) de degré \(n\),
y compris après chaque facteur du projecteur.

À une fréquence fixée, définir l'état

\[
\boxed{m_j=(L^jH)(t),\qquad 0\le j\le h.}
\]

Il contient \(h+1=O(n^2)\) scalaires. La mise à jour
\(H'=(I-L/r)H\) s'écrit exactement

\[
\begin{aligned}
m'_j&=m_j-m_{j+1}/r &&(0\le j<h),\\
m'_h&=m_h+\frac1r\sum_{j=0}^{h}c_jm_j.
\end{aligned}
\]

La dernière ligne utilise \(L^{h+1}H=-\sum_jc_jL^jH\).
Toutes les valeurs de droite proviennent de l'ancien état. Les constantes
\(c_j/r\) dépendent seulement des paramètres, et non des données.
En comptant un produit par constante et une addition séparément, un
facteur coûte au plus \(4h+2\) portes et les \(h\) facteurs au plus
\(4h^2+2h\). À la fin, la lecture est le fil \(m_0\).
Pour \(n=1\), \(h=0\), aucun facteur n'est appliqué.

La génération de \(\chi_n\) par produits successifs de facteurs
linéaires a elle aussi un coût polynomial. Plus généralement, les
opérateurs \(p(L)\) se fusionnent par multiplication de polynômes
modulo \(\chi_n\). Cette algèbre de coefficients a dimension
\(h+1\) ; elle ne réintroduit pas les sous-ensembles de colonnes.

## 4. Couplage spectral et coût de la chaîne à démontrer

Les substitutions diagonales \(s_j\mapsto\alpha_js_j\) commutent
avec \(L\). On peut donc garder les phases dans \(t_j=\omega^{fd_j}\),
ou appliquer la même mise à jour à une table de \(N(h+1)\) observations.
La fusion et l'INTT s'articulent par linéarité, avec le même résultat
terminal que la chaîne des différences.

L'état est construit pour la **forme complète** \(G_B\), de degré \(n\),
puis pour l'action du projecteur. On ne lui demande pas de représenter
tous les produits partiels de lignes, ni toutes leurs continuations.
C'est précisément la liberté de compilation globale autorisée en B.11.

Noter \(I(n,N)\) le coût de construction **depuis \(a,z\)** de
la table initiale

\[
\mu_{j,f}=(L^jG_B)(\omega^{fd_0},\ldots,\omega^{fd_{n-1}}),
\qquad 0\le j\le h,\quad 0\le f<N.
\]

Le coût complet de cette réalisation satisfait alors

\[
\boxed{I(n,N)+N(4h^2+2h)+2N\log_2N+N,}
\]

auxquels s'ajoute, si elle n'est pas déjà incluse dans \(I\), la
préparation polynomiale des constantes. Le coût de l'INTT compte
explicitement la soustraction comme produit par \(-1\) puis addition.

**La fusion et la lecture de cet état sont donc réellement polynomiales.
Pour compléter cette réalisation, il faut un circuit simultané pour
\(\mu_{j,f}\) avec \(I(n,N)\) polynomial, ou fusionner sa préparation
avec le projecteur sans matérialiser ce vecteur.** La présence de seulement
\(O(Nn^2)\) observations ne fournit pas leur circuit. Inversement,
le coût exponentiel d'une représentation par jets n'est pas un argument
qui imposerait ce coût à une autre construction de ces observations.

Cette interface est une réalisation suffisante, pas une étape imposée
à toute compilation globale de \(\mathcal Z\). La cible reste le
circuit conjoint depuis \(a,z\), avec son partage de calculs.

Les premières observations ont déjà des constructions directes. En posant
\(\ell_i=\sum_jB_{ij}t_j\), la règle de Leibniz donne

\[
\mu_0=\prod_i\ell_i,\qquad
\mu_1=\sum_{i<k}
 \left(\sum_jB_{ij}B_{kj}t_j^2\right)
 \prod_{r\notin\{i,k\}}\ell_r.
\]

La seconde formule demande \(O(n^3)\) portes, sans division par
une donnée. Les deux dérivations doivent toucher deux facteurs de
lignes différents, ce qui prouve la formule et annule le facteur
\(1/2\) de \(L\). Elle ne donne pas par elle-même une borne uniforme
pour tous les \(j\le h\).

Les observations restantes ne sont pas fournies comme constantes ou comme
oracles dans une prétendue solution de la chaîne entière. Le petit
compilateur de fusion joint à cette étude est seulement un composant,
dont les entrées d'observation sont annoncées comme telles.

## 5. Linéarisation NTT de la fusion globale

La récurrence précédente expose une fermeture à chaque étape. On peut
aussi partager directement le polynôme du projecteur entre toutes les
fréquences. Prendre \(M>h\), puissance de deux divisant \(Q-1\), et
\(\eta\) d'ordre \(M\). La NTT des coefficients de \(1-X/r\)
vaut \(1-\eta^\ell/r\), d'où

\[
(p_0,\ldots,p_h,0,\ldots,0)
=\operatorname{INTT}_M
 \left[\left(\prod_{r=1}^{h}(1-\eta^\ell/r)\right)_\ell\right].
\]

Ensuite, \((\pi_n(L)G_B)(t(f))=\sum_jp_j\mu_{j,f}\), avant
l'INTT de longueur \(N\). Cette variante fusionne les opérateurs
dans leurs coefficients scalaires, puis effectue la lecture globale.
Elle ne multiplie pas des valeurs orientées comme si elles étaient
des scalaires. La longueur \(M\) concerne le degré du projecteur ;
la longueur \(N\) conserve le rôle spectral du papier.

Pour \(h\ge1\), le composant scalaire correspondant compte exactement

\[
3hM+2M\log_2M+N(2h+1)+2N\log_2N+N
\]

portes depuis la table des observations, hors initialisation. Les
preuves, les conditions et le cas \(h=0\) figurent dans
`LINEARISATION_PROJECTEUR.md`. La même obligation de construction
conjointe depuis \(a,z\) demeure.

## 6. Portée des vérifications

La preuve écrite raccorde la fusion des transports, les différences
ordinaires et le projecteur B.26 à tout ordre. La formalisation
`OrbitDifference.lean` vérifie l'entrelacement et son itération pour
toute liste sous les hypothèses explicites de linéarité et de fusion.
Elle ne certifie pas le coût de construction des observations.

La recompilation indépendante des deux théorèmes avec Lean 4.34.1
réussit sans erreur, avertissement ni `sorryAx`. Les seuls axiomes
déclarés sont `propext`, `Classical.choice` et `Quot.sound` ; le rapport
`lean-validation.json` conserve l'empreinte et la sortie du compilateur.

Le vérificateur du composant de fusion contrôle la récurrence sur
des observations initiales calculées indépendamment pour des mélanges
finis de monômes. Ces calculs de référence sont des tests ; ils ne sont
pas le compilateur polynomial \(I(n,N)\) recherché.

Le composant compagnon passe 44 tableaux synthétiques, 300 fréquences
et 90 252 coordonnées intermédiaires. Le raccord aux entrées originales
passe 36 tables complètes, dont 16 avec \(z\) formel : il contrôle
aussi la préparation directe de \(\mu_0,\mu_1\), 1008 états du
projecteur, les différences ordinaires et l'INTT. Les moments restants
sont initialisés par énumération uniquement dans ce vérificateur.

Sources de cette reprise : `sources/textes/raccord-spectral.txt`,
§§13.6–13.14 et B.10–B.11 ; `reprise-flot-rationnel/REPRISE.md` ;
`fusion-ntt/RACCORD_NTT.md`. La proposition B.26 est celle du papier,
pas une découverte de cette étude.
