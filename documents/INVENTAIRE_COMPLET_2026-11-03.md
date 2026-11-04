# Inventaire corrigé : architecture retenue, sans groupes ajoutés

Le [registre des démonstrations](INVENTAIRE_DEMONSTRATIONS_POLYNOMIALES_2026-11-03.md)
détaille, pour chaque borne, la preuve, ses hypothèses et sa portée Lean.

La [vérification du raccord de normalisation](RACCORD_NORMALISATION_MEME_CIRCUIT_2026-11-03.md)
établit que les fils inchangés du représentant ne satisfont pas le
certificat de coefficient requis. Les coûts de représentants ci-dessous
restent valides ; ils ne deviennent pas des coûts de coefficients par
simple effacement des auxiliaires.

3 novembre 2026. Correction après contestation de G=2^n−1 par l'auteur.
Le précédent inventaire a présenté le coût de la récurrence expérimentale
R comme celui de l'architecture retenue. Ce changement de périmètre était
incorrect. **G, s_k et W sont retirés du compte de l'architecture.**
Les mesures de cette récurrence sont conservées séparément dans
l'[inventaire du prototype R](INVENTAIRE_PROTOTYPE_R_2026-11-03.md).

## 1. Origine précise du G ajouté

Dans [compiler_joint_convolution.py](reanalyse-quotient-2026-11-03/compiler_joint_convolution.py),
`JointConvolution.contract` part des n singletons de lignes puis branche
sur tous les retraits de groupes et toutes les fusions de paires.
`vector_pool` et `row_pool` mémorisent les résultats sous des clés qui
sont des tuples d'indices de lignes. Ce choix de récurrence visite tous
les groupes non vides, d'où G=2^n−1. Ses états sont des partitions de
parties de lignes, d'où les s_k et le majorant W.

Ce décompte est correct pour ce code, mais le choix de développer et de
mémoriser ces groupes n'est pas une étape de l'architecture retenue.
La réduction algébrique exacte qui justifie R n'en fait pas une compilation
obligatoire. Ni G=2^n−1 ni les mesures 45,399,7374 ne doivent être attribués
au circuit compact recherché. On ne remplace pas non plus G par n ou n−1 :
on retire cet objet auxiliaire du décompte de l'architecture.

## 2. Les objets effectivement retenus

Le [constructeur natif](composition-native-2026-11-03/compose_native_representatives.py)
conserve les formules

\[
B_{ij}=(1+a_{ij}^2)z^{2^{in+j}},\qquad
C_{ir}=\frac1N\sum_{j<n}B_{ij}\omega^{rj},
\]
\[
L_i(x)=\sum_{r<N}C_{ir}x_{-r},\qquad
F_0(x)=\prod_{i<n}L_i(x).
\]

Après fusion des fréquences, dans le quotient orienté,

\[
[F_f]=\omega^{fD_*}[F_0],\qquad
\mathcal Z[k]=\operatorname{INTT}_N
\bigl[(\gamma_n\omega^{fD_*}[F_0])_{f<N}\bigr][k].
\]

Cette construction utilise n vecteurs C de longueur N, n formes L_i,
n−1 produits partagés, un signe, N valeurs spectrales partagées et une
INTT. Elle ne construit aucune collection de tous les groupes de lignes
ni de tous les sous-ensembles de colonnes. Le padding ajoute des zéros.

Les relations de convolution et de padding définissent l'interprétation
orientée de ces représentants. Elles ne commandent pas une énumération
de groupes I. La loi T_y T_z=T_(y+z) reste une identité de fusion ; aucun
développement exhaustif des différences n'est ajouté au compte.

## 3. Coût prouvé du programme compact de représentants

On compte les portes binaires + et ×, avec les constantes structurelles
fournies et les fils partagés gratuits. Poser n<N≤2n, ell=log_2(N), et
epsilon_n=1 si n est congru à 2 ou 3 modulo 4, zéro sinon.

| Bloc retenu | Nombre d'objets | Majorant de portes supplémentaires du représentant |
|---|---:|---:|
| Puissances partagées de z | n² marquages | n²−1 |
| Construction des B_ij | n² coefficients | 3n² |
| NTT et normalisation des C_ir | n vecteurs de longueur N | 2nN ell+nN |
| Formes linéarisées L_i | n formes | n(2N−1) |
| Produit partagé F_0 | n−1 multiplications | n−1 |
| Signe universel | une correction | epsilon_n≤1 |
| Phases communes | N valeurs depuis le même F_0 | N−1 |
| Vraie INTT | une transformée de longueur N | 2N ell+N |

La somme donne

\[
\boxed{C_{\rm rep}\le
(4n^2-1)+(2nN\ell+nN)+(2nN-1)
+\varepsilon_n+(2N\ell+2N-1).}
\]

Il s'agit de O(n² log(n+1)), et le majorant commode déjà vérifié
C_rep≤29n³ reste valide. Ce compte ne comporte aucun G, s_k ou W.
La fusion spectrale évite de répéter N fois le produit F_0.
Les [mesures natives existantes](cout-meme-circuit-2026-11-03/same-dag-measurements.json)
restent la référence pour les portes de ces représentants, par exemple
330,1494,6766,30558 pour n=4,8,16,32 aux paramètres consignés.

## 4. Portée exacte pour la cible en portes scalaires

Le tableau précédent compte le programme dont les représentants contiennent
les coordonnées auxiliaires x. Il ne déclare pas qu'une multiplication
orientée ou une interprétation dans le quotient est une porte scalaire
gratuite depuis a,z seuls.

Le retrait de G rétablit l'objet à compiler ; il n'ajoute ni une preuve
d'exponentialité ni une preuve nouvelle de fermeture scalaire polynomiale.
Le résultat recherché reste une compilation conjointe des produits,
relations orientées, fusions et INTT, sur un même DAG scalaire depuis a,z.
La normalisation exacte générale est déjà acquise ; son coût polynomial
uniforme sur ce même circuit reste à raccorder.

Le compte fixé reste

\[
\boxed{C(\Gamma_n)=|T_n\cap P_n|+J_n\le10n^3+J_n,}
\]

où J comprend toutes les portes utiles hors préparation, spectral et
normalisation inclus. **Aucune expression en G ou W n'est imposée à J.**
Les valeurs de J mesurées pour le prototype R restent propres à ce
prototype ; elles ne mesurent pas une famille compacte qui utiliserait
un autre raccord. Aucun lecteur supplémentaire n'est imposé après J.

## 5. Conservation des résultats expérimentaux

Les preuves de correction et mesures du prototype R ne sont pas effacées.
Le [rapport de ses coûts](inventaire-complet-2026-11-03/complete-inventory-validation.json)
et son [mesureur](inventaire-complet-2026-11-03/measure_complete_inventory.py)
restent reproductibles ; le rôle expérimental est indiqué dans
l'[inventaire séparé](INVENTAIRE_PROTOTYPE_R_2026-11-03.md).

Cette correction porte sur le périmètre de l'inventaire. Elle ne change
ni les programmes ni leurs résultats de vérification, et n'ajoute aucun
théorème Lean de compilation scalaire générale.
