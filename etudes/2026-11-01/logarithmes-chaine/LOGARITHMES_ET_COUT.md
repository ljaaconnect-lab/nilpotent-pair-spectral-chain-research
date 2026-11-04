# Introduction effective de logarithmes dans la chaîne

La transformation a été construite et exécutée depuis les entrées a,z.
Elle conserve G_B, chaque facteur I-L/r et la lecture spectrale finale.
Les logarithmes et exponentielles sont formels, tronqués et compilés en
portes scalaires ordinaires. Aucune borne générale polynomiale ou
quasi-polynomiale n'est obtenue par cette transformation.

## Transformation et retour exact

Avec h=binom(n,2), on introduit seulement une indéterminée de calcul :

\[
H_0(\varepsilon,s)=\prod_i[1+\varepsilon(\ell_i(s)-1)],\qquad
U_0=\log H_0\pmod{\varepsilon^{n+1}},\qquad
\ell_i(s)=\sum_j B_{ij}s_j.
\]

La constante de H_0 est 1 pour toutes les données. Le logarithme ne
nécessite aucune division par une somme de ligne. Les paramètres déjà
admissibles Q>max(2,h), Q premier, assurent aussi Q>n.

Pour D_j=s_j partial_j, posons

\[
A(U)=LU+\frac12\sum_j(D_jU)^2.
\]

Le facteur existant devient exactement

\[
\boxed{U_r=U_{r-1}+\log\left(1-\frac{A(U_{r-1})}{r}\right)
       \pmod{\varepsilon^{n+1}}.}
\]

En effet L(exp U)=exp(U) A(U). La normalisation est préservée à chaque
étape, et exp(U_h)=H_h modulo epsilon^(n+1). Comme H_h est effectivement
un polynôme de degré au plus n en epsilon, on retrouve exactement
pi_n(L)G_B en sommant ses coefficients. Ce n'est qu'après cette
reconstruction qu'epsilon est mis à 1. Les phases et l'INTT terminent
le même circuit, avec la correction universelle déjà incluse.

Les coefficients de chaque log et de l'exp finale se calculent par
des récurrences quadratiques en n. Le programme n'introduit aucune
porte log/exp numérique, aucune donnée inverse, aucun moment en entrée.

## Élagage exact

Le coefficient [epsilon^k]H_0 est de degré au plus k en s. Les facteurs
1-L/r annulent donc toutes ses collisions dès r=binom(k,2). Il en résulte
la stabilisation du coefficient [epsilon^k]U à ce même stade.

Au facteur r, le compilateur met exactement A(U)_k à zéro lorsque
r>binom(k,2). Cette annulation est démontrée avant l'évaluation des
données. Le nombre de mises à jour de coefficients actives vaut

\[
\sum_{k=2}^{n}\binom{k}{2}=\binom{n+1}{3}.
\]

Plus précisément, si m_r est le plus petit k tel que binom(k,2)>=r,
le correctif A commence à epsilon^(m_r). Son logarithme utilise au plus
floor(n/m_r) puissances. Lorsque 2m_r>n, le correctif logarithmique est
exactement -A/r dans le quotient. Les zéros correspondants sont exploités
par la récurrence scalaire du programme.

Ce nombre polynomial de mises à jour ne constitue pas un nombre
polynomial de portes : leurs entrées sont des fonctions de s, dont les
dérivées doivent elles aussi être calculées et partagées.

## Résultats exécutés avec le même modèle de coût

Le rapport log-circuit-validation.json compare les trois compilations
pour Q=97, d_j=j et la même racine de l'unité. Les seules variables aux
sorties sont a,z. Les décomptes comprennent l'INTT et le retour de log.

| n | Raccord direct partagé | Log sans élagage | Log avec élagage |
|---|---:|---:|---:|
| 1 | 8 | 10 | 10 |
| 2 | 65 | 145 | 145 |
| 3 | 434 | 1 336 | 1 215 |
| 4 | 4 441 | 25 373 | 18 114 |
| 5 | 35 131 | 303 890 | 184 673 |

Les 40 tables numériques passent, avec des cas z=0 et ligne d'amplitude
nulle. Les 200 jets intermédiaires en epsilon sont comparés à une
expansion indépendante, facteur par facteur. Trois tables complètes avec
z formel passent jusqu'à n=3. Le développement de référence n'est utilisé
que dans le vérificateur, jamais dans le compilateur.

L'élagage économise des portes dans la variante logarithmique. Aux tailles
mesurées, cette variante coûte davantage que le raccord direct partagé.
Ces cinq tailles ne prouvent aucune classe asymptotique.

## Ce qu'il faudrait pour une borne quasi-polynomiale ou polynomiale

Prendre le logarithme du majorant précédent ne réduit pas son circuit :
log C=O(n^2 log n) demeure compatible avec un majorant exponentiel.
Une borne quasi-polynomiale demanderait log C=O((log n)^k), pour un k
constant ; une borne polynomiale demanderait log C=O(log n).

La compilation logarithmique actuelle donne encore, en comptant tous
les sous-circuits des coefficients et leurs dérivées,

\[
S_r\le(9n+1)S_{r-1}+C_0(n+1)^3,\qquad S_0\le9n^2.
\]

Les couches finales ajoutent O(n^2) pour reconstruire exp(U_h), puis
au plus un facteur N<=2n et O(N log N) pour le spectral. Le majorant
global issu de cette récurrence reste 2^(O(n^2 log n)).

Une fusion scalaire prouvée de deux blocs selon
T(2m,n)<=2n^c T(m,n)+poly(n,m) donnerait n^(O(log n)) pour h=O(n^2).
Avec un facteur multiplicatif constant indépendant de n et m, elle
donnerait une borne polynomiale. Équilibrer seulement la description
des opérateurs ne démontre pas ces récurrences.

## Fichiers et portée de la preuve

- FORMALISME_LOG.md : preuve générale du changement de coordonnées,
  de son retour et de la stabilisation.
- PROFONDEUR_ET_LOG.md : logarithme des facteurs, exponentiation rapide
  et conditions suffisantes de complexité, distinguées des résultats acquis.
- log_circuit.py : compilation en portes scalaires.
- verify_log_circuit.py et log-circuit-validation.json : reproduction
  et résultats, avec empreintes des sources utilisées.
- lean/LogConjugation.lean : conjugaison d'une dérivation d'ordre deux,
  somme finie et passage d'un facteur du lecteur. Cette portée locale
  ne formalise ni log/exp tronqués, ni la stabilisation, ni le coût global.

Reproduction depuis la racine du projet :

```powershell
python -X utf8 etudes/2026-11-01/logarithmes-chaine/verify_log_circuit.py
python -X utf8 etudes/2026-11-01/logarithmes-chaine/lean/replay_lean.py
```

Les algorithmes de séries formelles sont un cadre classique ; voir
[Brent et Kung, Fast algorithms for manipulating formal power series](https://maths-people.anu.edu.au/~brent/pub/pub045.html).
Les récurrences employées ici sont explicites et leur coût est compté
directement ; aucun résultat externe n'est utilisé pour supposer la
fermeture du circuit différentiel.
