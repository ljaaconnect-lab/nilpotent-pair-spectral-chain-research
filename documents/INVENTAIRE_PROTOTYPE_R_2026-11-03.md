# Inventaire du prototype R : mesures hors architecture retenue

**Périmètre corrigé après contestation de G :** cette note conserve les
mesures exactes du compilateur expérimental `JointConvolution`. Ses groupes
I, G=2^n−1 et états s_k ont été introduits par la récurrence R ; ils ne sont
pas imposés par l’architecture retenue. Les nombres de portes de cet essai
ne constituent pas le coût de cette architecture. Voir l’[inventaire
corrigé](INVENTAIRE_COMPLET_2026-11-03.md).

3 novembre 2026. Ce décompte part des entrées originales a_ij,z et
se termine aux N sorties de la véritable INTT. Il porte sur les deux
variantes du compilateur de la récurrence par convolutions construit dans
la [réanalyse du quotient](REANALYSE_QUOTIENT_2026-11-03.md).
Chaque porte utile partagée est comptée une seule fois.

## 1. Modèle et paramètres

Une porte est une addition ou une multiplication binaire dans F_Q.
Les entrées, fils et constantes structurelles sont gratuits dans ce
modèle arithmétique. La multiplication d'une valeur variable par une
constante compte au plus une porte. La certification du corps, la
production des paramètres et leur coût binaire ne sont pas mesurés ici.

On prend n>=1, N la plus petite puissance de deux strictement supérieure
à n, ell=log_2(N), Q premier fourni avec N divisant Q−1, et omega d'ordre N.
Ainsi n<N<=2n et Q>n ; N et n! sont inversibles.

La fusion F_f=omega^(f D_*) F_0 est utilisée avant la compilation finale.
On prépare donc uniquement les coefficients C_i=C_(i,0,.) si on conserve
ce bloc, puis on reconstruit toutes les fréquences depuis un résultat
calculé à l'intérieur du circuit. Aucune amplitude n'est fournie en entrée.

## 2. Inventaire des formules et de leur coût local

Les coûts de cette table sont des majorants par construction. Les lignes
qui décrivent des variantes alternatives ne doivent pas être additionnées.

| Élément | Formule ou opération | Portes scalaires |
|---|---|---:|
| Marquages | z, z², …, z^(2^(n²−1)), par carrés partagés | n²−1 |
| Carrés des données | a_ij² | n² |
| Décalage | 1+a_ij² | n² |
| Coefficients orientés | B_ij=(1+a_ij²)z^(2^(in+j)) | n² supplémentaires |
| **Préparation totale de B** | Les quatre lignes précédentes | **4n²−1** |
| Coefficients linéarisés, si conservés | C_i=N⁻¹ NTT_N(B_i,0,…,0) | ≤2nN ell+nN supplémentaires |
| Formes auxiliaires, si conservées | L_i=Σ_r C_ir x_(−r) | ≤n(2N−1) |
| Produit des formes, si conservé | F_0=∏_i L_i | ≤n−1 |
| Une fusion directe | (c*c')_r=Σ_s c_s c'_(r−s), tous les r | ≤2N²−N |
| Une fusion avec la préparation | b_(I∪J)[j]=b_I[j]b_J[j], tous les j | ≤n |
| Un poids fusionné | m_I=Σ_j b_I[j]=Nc_I[0] | ≤n−1 après son vecteur |
| Un état R à k formes | Somme des retraits et des fusions de paires | 0 si k≤1 ; ≤2k+binom(k,2) si k≥2, hors poids |
| Normalisation finale | b=R/n! | ≤1 |
| Signe universel | Omega_tilde=gamma_n q_[n] | 0 porte supplémentaire dans ce label |
| Fréquences partagées | b, omega^(D_*)b, … | ≤N−1 |
| **Vraie INTT** | Papillons inverses et multiplication par N⁻¹ | **≤2N ell+N** |

Les relations de convolution, le padding et les coordonnées x sont les
identités de l'algèbre où les formes sont représentées. Leur normalisation
est compilée conjointement dans la récurrence R. Elles ne constituent pas
trois blocs supplémentaires à facturer après elle.

Les formes et leurs n−1 multiplications donnent des représentants qui
contiennent encore x. Ce coût ne s'ajoute pas à celui de R dans le circuit
scalaire final : R compile conjointement leur produit et sa normalisation.
De même, dans la variante fusionnée, les transformées C intermédiaires sont
absorbées par m_I=Σ_j b_I[j]. Les sommes réutilisées restent comptées.

Le signe est inclus dans le label de sortie, car gamma_n[F_0]=b Omega_tilde.
Avec le label q_[n] à la place, une multiplication par gamma_n coûterait
au plus une porte. On ne multiplie pas deux fois par ce signe.

## 3. Nombre d'objets et majorant du candidat complet

Poser G=2^n−1, le nombre de groupes non vides de facteurs de lignes du
compilateur actuel. Ces groupes ne sont pas des ensembles de colonnes
occupées. Les n groupes singletons réutilisent les B déjà préparés.

Soit s_k le nombre d'états distincts à k groupes visités par la récurrence,
S=Σ_k s_k, et

\[
W=\sum_{k=2}^{n}s_k\left(2k+\binom{k}{2}\right).
\]

Chaque appel retire un groupe ou fusionne une paire, donc diminue k.
La mémorisation partage les appels identiques. La preuve locale compte
k multiplications, k−1 additions, au plus binom(k,2)−1 additions pour les
paires, une multiplication par −2 et une addition finale. Pour k=0 ou 1,
le code replie les opérations sur zéro et un ; aucun coût hors poids.

Le pool canonique de la variante fusionnée coûte au plus

\[
\underbrace{n(G-n)}_{\text{vecteurs supplémentaires}}
+\underbrace{(n-1)G}_{\text{sommes des poids}}.
\]

Le majorant de toute la chaîne de ce candidat est donc

\[
\boxed{C_{\rm fusionne}\le
(4n^2-1)+n(G-n)+(n-1)G+W+1+(2N\ell+2N-1).}
\]

Les derniers termes comprennent la normalisation, les phases et la vraie
INTT. Aucun coût de lecteur n'est ajouté après eux.

Pour comparaison, la variante qui conserve les convolutions spectrales
directes satisfait

\[
\boxed{C_{\rm direct}\le
(4n^2-1)+(2nN\ell+nN)
+(G-n)(2N^2-N)+G+W+1+(2N\ell+2N-1).}
\]

On a S≤(n+1)^n : un état est une partition d'une partie des facteurs de
lignes ; chaque ligne est encodée par zéro si elle est absente, sinon par
un plus le plus petit indice de son bloc. Cet encodage est injectif.
Donc W≤3n²(n+1)^n. Ces majorants sont valides pour le candidat actuel,
mais ne sont pas polynomiaux. Ils ne sont pas des bornes inférieures
pour l'architecture ni une impossibilité de mieux partager les calculs.

Le budget spectral est resserré à 2N ell+2N−1 : N−1 phases et 2N ell+N
pour l'INTT. L'ancien majorant 2N ell+3N−3 restait valide ; il provisionnait
aussi N−2 multiplications entre constantes déjà préévaluées par le DAG.

## 4. Mesure exacte des portes utiles, après tous les partages

Le [mesureur](inventaire-complet-2026-11-03/measure_complete_inventory.py)
parcourt indépendamment les ancêtres des sorties, puis forme une partition
disjointe par blocs. Dans la variante fusionnée, les sommes réutilisées
depuis la préparation sont attribuées aux poids m_I. Leur date de création
ne provoque pas un second coût de NTT.

Paramètres Q=97, N=4,8,8 pour les trois colonnes, mêmes étiquettes et
graphes que le rapport de correction du compilateur :

| Bloc du circuit fusionné | n=2 | n=4 | n=6 |
|---|---:|---:|---:|
| Puissances de z | 3 | 15 | 35 |
| Carrés a_ij² | 4 | 16 | 36 |
| Sommes 1+a_ij² | 4 | 16 | 36 |
| Produits donnant B_ij | 4 | 16 | 36 |
| NTT intermédiaires, coût distinct après fusion | 0 | 0 | 0 |
| Vecteurs fusionnés b_I | 2 | 44 | 342 |
| Poids m_I | 3 | 45 | 315 |
| Récurrence R, hors pool déjà partagé | 4 | 190 | 6 517 |
| Multiplication par (n!)⁻¹ | 1 | 1 | 1 |
| Signe supplémentaire avec le label Omega_tilde | 0 | 0 | 0 |
| Phases communes | 3 | 7 | 7 |
| Vraie INTT | 17 | 49 | 49 |
| **Total distinct** | **45** | **399** | **7 374** |

Le nombre d'états est respectivement 5,52,877 et le nombre de groupes
3,15,63. La variante directe donne 72,1058,10623 portes sur ces paramètres.
Le cas n=2 admet aussi la normalisation spécialisée de trois portes sur
les B, donnant 38 portes au total ; ce circuit spécialisé n'est pas la
récurrence générique mesurée dans la table.

## 5. Compatibilité avec le même compte P,T,J

Conserver P comme l'ensemble des portes de préparation des C dans le DAG,
T comme l'ensemble des portes utiles finales et J=|T\\P|. On a exactement

\[
C=|T\cap P|+J\le10n^3+J.
\]

| n | Préparation réutilisée : \(\lvert T\cap P\rvert\) | J, tout le reste inclus | Total |
|---:|---:|---:|---:|
| 2 | 17 | 28 | 45 |
| 4 | 63 | 336 | 399 |
| 6 | 143 | 7 231 | 7 374 |

Dans la première ligne, deux sommes attribuées aux poids dans la table
précédente appartiennent aussi au préfixe P : 15 portes B plus ces deux
sommes donnent 17. Il s'agit de deux partitions du même ensemble T,
chacune disjointe ; on ne somme pas les deux tables.

L'obligation générale reste une borne uniforme J≤kappa n^e sur une même
famille exacte de circuits. Les budgets de B, des phases et de l'INTT sont
polynomiaux. Chaque fusion ou état individuel a un coût polynomial, mais
les nombres d'objets traités par la récurrence actuelle ne fournissent pas
la borne polynomiale générale demandée. L'inventaire ne déplace aucun coût
vers une étape de lecture ultérieure.

## 6. Vérification et reproduction

Le [rapport détaillé](inventaire-complet-2026-11-03/complete-inventory-validation.json)
couvre 18 compilations : les deux variantes jusqu'à n=6 et trois corps
supplémentaires aux tailles déjà testées. Chaque partition est disjointe,
complète, et sa somme concorde avec le
[rapport de correction existant](reanalyse-quotient-2026-11-03/joint-convolution-validation.json).
Chaque majorant par bloc est contrôlé ; les empreintes des sources et des
graphes finaux sont conservées. Ce nouveau contrôle porte sur les coûts ;
il ne constitue pas une nouvelle preuve Lean du compilateur général.

```powershell
python -B documents/inventaire-complet-2026-11-03/measure_complete_inventory.py
```
