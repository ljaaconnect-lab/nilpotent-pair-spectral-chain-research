# Fusions de l'architecture et double logarithme

Les fusions ci-dessous sont démontrées pour tout ordre admissible et
exécutées dans un compilateur de portes scalaires depuis a,z. Elles
réduisent effectivement le coût. **La borne polynomiale générale de
toute la chaîne reste non démontrée.**

## 1. Chaîne et paramètres conservés

On conserve B_ij=(1+a_ij^2)z^(2^(in+j)), le projecteur de collision
pi_n(L), L=(1/2)sum_j s_j^2 partial_j^2, la correction universelle et
la table Z_Q. Q est premier et Q>max(2,binom(n,2)); n<N<=2n,
N puissance de deux divisant Q-1. Ces paramètres sont fournis.

Le circuit ne reçoit aucun moment ni amplitude terminale en entrée.
Les seules variables des portes accessibles depuis les sorties sont a,z.
Les exposants de z restent formels.

## 2. Trois fusions effectivement utilisées

**Projection et spectral.** Après projection, un polynôme homogène de
degré n en n variables ne conserve que le monôme s_0...s_(n-1).
Toutes les fréquences sont donc une même valeur multipliée par
omega^(f sum_j d_j). L'INTT place cette valeur au seul indice
k*=sum_j d_j mod N. Le compilateur produit cette racine une seule fois
à s=1, puis la relie au bon fil de sortie; les autres sorties sont zéro.
C'est la simplification de la chaîne entière, sans nouvelle donnée en
entrée. Le facteur N de réplication et l'INTT explicite disparaissent.

**Fusion des facteurs inutiles.** Soit K_n l'ensemble des entiers
sum_b binom(b,2), pour les partitions de n en tailles positives b.
Les polynômes de degré au plus n ont exactement ces valeurs de collision
possibles (on complète les degrés inférieurs par des tailles 1). Ainsi

\[
\pi_n(L)=\prod_{r\in K_n\setminus\{0\}}(I-L/r)
\]

sur l'espace utilisé. K_n se prépare par une récurrence sur le degré
et la collision, avec un nombre polynomial d'états et de transitions
indépendants des données. Par exemple K_5={0,1,2,3,4,6,10}.
L'identité supprime réellement des facteurs, sans supposer leur action
scalaire gratuite.

**Deux niveaux terminaux et lecture.** Écrivons h_k=binom(k,2), n>=3,
I=K_n\{0,h_(n-1),h_n}, c_kappa=prod_(r in I)(1-kappa/r).
Après le préfixe I, les seules collisions non nulles restantes sont
h_(n-1) et h_n. Au degré n, elles correspondent uniquement aux profils
(n-1,1) et (n). Leurs contributions se retirent explicitement à la lecture.

À s=1, posons

\[
p_{ij}=\prod_{l\ne i}B_{lj},\quad
R_i=\sum_jp_{ij},\quad
C=\sum_j\prod_iB_{ij},\quad
S=\sum_i\left(\sum_jB_{ij}\right)R_i.
\]

Si X est le fil lu après le préfixe I, le fil final est exactement

\[
\boxed{X-c_{h_{n-1}}S+(n c_{h_{n-1}}-c_{h_n})C.}
\]

Les produits omettant une ligne se calculent avec préfixes et suffixes
dans chaque colonne, sans division par B. Cette correction entière,
sommes de lignes comprises, coûte **au plus 5n^2 portes depuis B**.
Elle fusionne les deux dernières éliminations, leur lecture et le
routage spectral. Ce théorème ne dépend pas des tests à petites tailles.

## 3. Logarithme et double logarithme raccordés à la même lecture

La normalisation homogène

\[
H_0^+(\varepsilon,s)=\prod_i(1+\varepsilon\ell_i(s)),\qquad
\ell_i=\sum_jB_{ij}s_j
\]

vérifie [epsilon^n]H_0^+=G_B. Le lecteur différentiel commute avec la
prise de ce coefficient. On travaille modulo epsilon^(n+1), puis on
reconstruit seulement ce qui est nécessaire à la lecture finale.

Les coordonnées sont U=log H^+, puis **W=log(1+U)**. Le logarithme
de U seul n'aurait pas de constante unité. Pour D_j=s_j partial_j,

\[
\mathcal B(W)=LW+\tfrac12(1+e^W)\sum_j(D_jW)^2,
\]

\[
W'=W+\log\left(1+e^{-W}
                  \log(1-e^W\mathcal B(W)/r)\right).
\]

Cette identité est exacte. Quand le correctif a valuation m en epsilon
et 2m>n, elle se réduit exactement à \(W'=W-\mathcal B(W)/r\).
Les coefficients stabilisés et les termes nuls sont omis.

Chaque log/exp est une récurrence scalaire sur n coefficients. Le partage
des j U_j dans la récurrence de l'exp donne au plus n^2+n-2 portes
pour un retour exponentiel. Le double retour en demande au plus deux
fois autant. Ces comptes supposent les coefficients d'entrée déjà
construits : leurs circuits différentiels restent comptés dans le préfixe.

La lecture à deux niveaux ci-dessus est appliquée **après le retour du
préfixe**. Il est donc inutile de reconstruire les coefficients corrigés
de U ou W après ces deux derniers niveaux. Cette fusion de la correction
avec la lecture est implémentée dans fused_circuit.py.

## 4. Coût mesuré, tous les paramètres identiques par ligne

| n | Ancien circuit direct avec INTT | Direct après fusions | Log après fusions | Double log après fusions |
|---|---:|---:|---:|---:|
| 1 | 9 | 3 | 3 | 3 |
| 2 | 65 | 23 | 31 | 36 |
| 3 | 450 | 72 | 94 | 109 |
| 4 | 4 383 | 362 | 1 973 | 3 182 |
| 5 | 35 645 | 2 858 | 20 620 | 42 001 |

Q=97; les labels sont indiqués dans le rapport. Les coûts de l'ancien
circuit sont recalculés avec exactement les mêmes paramètres, et non
recopiés d'une campagne utilisant d'autres labels.

Les fusions réduisent le coût du circuit direct. La variante double log
ne fournit aucun gain supplémentaire dans ces expériences. Les comptes
finis ne prouvent aucune classe asymptotique.

Validation : 120 tables numériques, 192 jets intermédiaires en epsilon,
9 tables avec z formel. Les cas z=0 et une ligne d'amplitude nulle sont
inclus. Le circuit d'origine, le circuit avec seul routage, et les trois
variantes finales sont comparés à une référence indépendante. Les
développements combinatoires existent uniquement dans le vérificateur.

## 5. Borne générale réellement obtenue

Pour le circuit direct, si S_I désigne le nombre de portes du préfixe
avant les deux niveaux terminaux, préparation de B comprise,

\[
\boxed{C_{\rm chaîne}\le S_I+5n^2.}
\]

Pour la variante log, on ajoute au plus n^2+n-2 portes de retour aux
coefficients du préfixe; pour la variante double log, au plus
2(n^2+n-2). Le spectral est déjà entièrement fusionné dans ces bornes.

Pour expliciter le majorant encore disponible pour S_I, soit d_n=|I|.
La traduction partagée des dérivées donne S_0<=6n^2-2 et
S_(j+1)<=(9n+1)S_j+3n+2. On a donc, pour n>=3,

\[
C_{\rm chaîne}\le
(9n+1)^{d_n}(6n^2-2)
+(3n+2)\frac{(9n+1)^{d_n}-1}{9n}+5n^2.
\]

Cette borne est générale, mais elle reste de type 2^(O(n^2 log n)).
Elle ne démontre ni un coût nécessaire, ni une impossibilité de partager
plus efficacement les calculs du préfixe. Le terme S_I n'est pas
remplacé par un polynomial sans preuve.

Le changement U<->W est lui-même inversible avec un surcoût O(n^2)
sur les coefficients disponibles. Il ne donne pas à lui seul la borne
manquante sur leur production et leurs dérivées. La note DOUBLE_LOG_FORMEL
précise cette portée et la transformation du terme quadratique.

## 6. Preuves et reproduction

- FUSIONS_ARCHITECTURE.md : démonstrations générales des fusions, dont
  les deux niveaux terminaux et la borne 5n^2.
- DOUBLE_LOG_FORMEL.md : double logarithme et portée de ses changements
  de coordonnées.
- fused_circuit.py, verify_fused_circuit.py, fusion-validation.json :
  circuits scalaires, vérifications et empreintes des sources.
- lean/DoubleLogConjugation.lean : quatre identités algébriques locales,
  vérifiées sans sorry ni avertissement. Elles ne formalisent pas la
  borne globale ni la fusion spectrale complète.

```powershell
python -X utf8 etudes/2026-11-01/fusion-double-log/verify_fused_circuit.py
python -X utf8 etudes/2026-11-01/fusion-double-log/lean/replay_lean.py
```
