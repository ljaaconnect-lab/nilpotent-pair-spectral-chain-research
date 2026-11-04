# Coût de toute la chaîne sur le même circuit partagé

L'[inventaire corrigé](INVENTAIRE_COMPLET_2026-11-03.md) retire G, s_k et W
du périmètre de l'architecture : ces objets appartiennent à un prototype
récursif ajouté. Ils ne sont pas imposés au J général défini ci-dessous.

Complément : la [réanalyse du quotient de convolution](REANALYSE_QUOTIENT_2026-11-03.md)
construit un candidat scalaire depuis a,z seuls et mesure ses deux variantes,
vraie INTT comprise. Le partage associatif et la fusion avec la préparation
sont appliqués. Le compte reste exactement |T∩P|+J ; aucun coût de lecteur
n'est ajouté après J. Le majorant prouvé pour ce candidat n'est pas
polynomial et ne constitue pas une borne inférieure de l'architecture.

3 novembre 2026. Le problème fixé est la taille totale d'un circuit
scalaire général calculant la sortie native corrigée, avec orientation,
forme linéarisée, fusion et INTT. La normalisation exacte générale est
déjà acquise dans les constructions recensées par
[l'audit](AUDIT_NORMALISATION_EXISTANTE_2026-11-03.md).

**Résultat de ce travail :** mesure exacte de toutes les portes utiles du
programme natif actuellement construit ; définition et preuve du compte
complet pour une réalisation scalaire normalisée sur un même graphe ;
identification d'une seule obligation quantitative, portant sur les portes
restantes de ce graphe. Cette obligation n'est pas démontrée ici.

## 1. Objet et mesure fixés

La chaîne conserve les entrées a_ij,z et les paramètres de corps et de
phase admissibles. On a n≥1, N la plus petite puissance de deux strictement
supérieure à n, n<N≤2n, ell=log₂N≤n. La sortie est la table complète
mathcal Z, après correction du signe et lecture spectrale.

Le coût d'un DAG scalaire Γ est le nombre d'identifiants distincts de portes
binaires + ou × atteignables depuis toutes ses sorties. Une porte partagée
est comptée une seule fois. Les entrées, constantes structurelles et fils
ne sont pas des portes arithmétiques. Les constantes dépendant seulement
du corps et des étiquettes sont préévaluées comme dans le compilateur.

La cible demeure

\[
\exists K,d\;\forall n\ge1:\quad
\Gamma_n(a,z)_k\widetilde\Omega=\mathcal Z_n(a,z)_k,
\qquad C(\Gamma_n)\le Kn^d,
\]

avec une construction uniforme, les paramètres admissibles et les
constantes autorisées du projet. La correction et le coût doivent se
rapporter à la même famille Γ_n. Le raccord peut être réorganisé globalement.

## 2. Mesure du programme actuellement construit

Le programme fixé pour cette mesure est
[compile_native_representatives](composition-native-2026-11-03/compose_native_representatives.py).
Les racines sont **tous les slots de sa véritable INTT**, sans remplacement
par les racines de routage. Pour chaque instance, un seul DAG est construit.

Le [mesureur](cout-meme-circuit-2026-11-03/measure_same_dag.py) parcourt ses
ancêtres par un second algorithme, indépendant de `DAG.reachable`. Il
intersecte les portes de chaque étape avec les ancêtres des sorties finales
et retire toutes les portes déjà attribuées. La somme des contributions
est donc exactement le nombre de portes utiles distinctes, sans recopier
la préparation ou les préfixes.

| Portes nouvelles utiles de cette étape | Majorant de l'étape | n=4 | n=8 | n=16 | n=32 |
|---|---:|---:|---:|---:|---:|
| Préparation des B_ij | 4n²−1 | 63 | 255 | 1023 | 4095 |
| NTT des coefficients et normalisation | 2nN ell+nN | 148 | 840 | 4368 | 21536 |
| Formes linéaires auxiliaires | n(2N−1) | 60 | 248 | 1008 | 4064 |
| Produit partagé de ces formes | n−1 | 3 | 7 | 15 | 31 |
| Signe universel | epsilon_n≤1 | 0 | 0 | 0 | 0 |
| Phases communes | N−1 | 7 | 15 | 31 | 63 |
| Vraie INTT | 2N ell+N | 49 | 129 | 321 | 769 |
| **Total distinct** | **≤29n³** | **330** | **1494** | **6766** | **30558** |

Les paramètres de ces colonnes sont respectivement (Q,N)=(97,8), (17,16),
(97,32), (193,64). Les étiquettes sont d_j=j²+3j−2n, avec d_0 augmenté de
un. Les nombres de portes peuvent varier avec les constantes ; les majorants
sont uniformes sous les conditions annoncées.

Le [rapport](cout-meme-circuit-2026-11-03/same-dag-measurements.json) couvre
les 17 tailles n=1,…,16 et n=32. Il conserve les empreintes du code et de
chaque graphe avec ses sorties. Les partitions exactes, l'ordre topologique,
les majorants par étape et le total ont été contrôlés. Aucune dérivation ni
aucun projecteur de collisions n'a été appelé.

La formule du compte complet de ce programme est déjà acquise :

\[
P(n,N)=4n^2-2+2nN\ell+3nN,
\]
\[
C_{\rm rep,INTT}\le P(n,N)+\varepsilon_n+2N\ell+3N-3\le29n^3.
\]

**Portée exacte :** ces sorties sont des représentants en a,z,x. Le
programme conserve N entrées auxiliaires x_r. La mesure de sa table complète
ne constitue pas la mesure d'une table de coefficients scalaires en a,z
seuls. Aucun coût de normalisation d'un autre programme n'est ajouté à ces
nombres. Le rapport laisse le champ correspondant au total scalaire
normalisé non renseigné, au lieu d'y inscrire zéro ou le compte précédent.

## 3. Décompte complet du même circuit scalaire normalisé

La préparation qui produit les C_ir a déjà des entrées uniquement a,z :

\[
B_{ij}=(1+a_{ij}^2)z^{2^{in+j}},\qquad
C_{ir}=N^{-1}\sum_{j<n}B_{ij}\omega^{rj}.
\]

Dans une réalisation scalaire Γ_n de la chaîne entière, on conserve cette
préparation dans le même magasin de portes. Elle coûte au plus

\[
A(n,N)=4n^2-1+2nN\ell+nN\le10n^3.
\]

La dernière inégalité vient de 2nN ell≤4n³ et 4n²+nN≤6n²≤6n³.
Si des portes de préparation deviennent inutiles après fusion, elles ne
sont pas facturées dans le total atteignable.

Définir, **dans ce même DAG Γ_n** :

- P_n : portes arithmétiques de la préparation des C_ir ;
- T_n : portes arithmétiques atteignables depuis toutes les sorties finales ;
- J_n=|T_n\P_n| : nombre de portes utiles restantes.

La partition disjointe donne l'identité exacte

\[
\boxed{C(\Gamma_n)=|T_n\cap P_n|+J_n.}
\]

Donc

\[
\boxed{C(\Gamma_n)\le A(n,N)+J_n\le10n^3+J_n.}
\]

J_n compte les portes restantes du circuit final ; il ne désigne pas un
nouvel opérateur ni une nouvelle étape. Il comprend conjointement les portes de
fusion orientée, de normalisation et de calcul spectral qui ne sont pas
déjà dans P_n. Toute fusion et tout partage entre ces calculs sont permis.
On n'ajoute donc ni un second coût de lecture ni un second coût d'INTT
après J_n. Aucun calcul scalaire préalable de P_A n'est imposé.

Le budget 29n³ des représentants et ce décompte du circuit scalaire
normalisé concernent deux portées différentes. Le premier ne remplace pas
J_n ; les deux ne sont pas additionnés artificiellement.

## 4. Un seul énoncé quantitatif reste à établir

Sur une famille uniforme de circuits Γ_n satisfaisant le certificat exact
de sortie, démontrer

\[
\boxed{\exists\kappa,e\;\forall n\ge1:\quad
|T_n\setminus P_n|\le\kappa n^e.}
\]

Les constantes doivent être indépendantes de n, des données a,z, des
étapes de fusion et des paramètres admissibles de corps et de phase.
Ce seul résultat entraîne

\[
C(\Gamma_n)\le10n^3+\kappa n^e
\le(10+\kappa)n^{\max(3,e)}.
\]

Ainsi les constantes du majorant demandé seraient explicitement

\[
\boxed{K=10+\kappa,\qquad d=\max(3,e).}
\]

Il s'agit toujours du coût de la chaîne complète sur la même réalisation,
avec son certificat de correction. La normalisation exacte générale, les
identités de fusion et l'INTT ne deviennent pas de nouvelles questions
d'existence. La borne des portes restantes n'a pas été obtenue par le
présent comptage : aucune valeur générale de kappa,e n'est annoncée.

## 5. Forme inductive de ce même décompte

Pour un calendrier de compilation partagé fixé, soit E_i l'union des
portes déjà comptées, toujours dans le graphe final, et U_i celles rendues
nécessaires par le bloc suivant. Alors

\[
E_{i+1}=E_i\cup U_i,\qquad
\Delta_i=U_i\setminus E_i,
\]
\[
|E_{i+1}|=|E_i|+|\Delta_i|.
\]

Si ce calendrier couvre exactement le reste T_n\P_n, le coût J_n est la
somme des contributions disjointes correspondantes. Une preuve uniforme
sur ces incréments est une manière de prouver l'inégalité de la section 4.
Une preuve directe sur l'ensemble final est également possible ; aucun
calendrier supplémentaire n'est imposé à la fusion globale.

Un majorant polynomial dans la taille du graphe courant ne donne pas
automatiquement un majorant uniforme en n après toutes les compositions.
L'estimation à établir doit concerner les portes nouvelles réellement
partagées de cette réalisation, ou leur total J_n.

## 6. Reproduction et vérification

```text
python -B documents/cout-meme-circuit-2026-11-03/measure_same_dag.py
python -B documents/cout-meme-circuit-2026-11-03/replay_same_dag_cost.py
```

La mesure porte sur le compilateur existant, dont le
[rapport de correction](composition-native-2026-11-03/native-composition-validation.json)
reste la référence sémantique. Les nouveaux contrôles portent sur le
comptage et ne remplacent pas ce rapport.

Les identités d'ensembles et le passage du budget J_n au budget total
sont formalisés dans
[SameDAGCost.lean](cout-meme-circuit-2026-11-03/SameDAGCost.lean).
Les quatre théorèmes sont acceptés par Lean 4.34.1, sans erreur,
avertissement ni `sorry` : partition exacte, préparation ≤10n³, borne
du total sous celle du reste, et famille avec constantes fixées avant n.
Le [rapport](cout-meme-circuit-2026-11-03/same-dag-cost-lean-validation.json)
enregistre les empreintes et les audits d'axiomes standards.

Cette formalisation compte les ensembles de portes fournis. La liaison
au graphe mesuré est contrôlée par le mesureur Python. Elle ne construit
pas un nouveau compilateur scalaire général et garde explicitement la
borne sur J_n comme hypothèse. Elle ne certifie donc pas encore le
majorant polynomial de toute la sortie scalaire native.

La [tentative de clôture suivante](TENTATIVE_CLOTURE_2026-11-03.md) teste
deux simplifications sur ce même programme. Elle ne démontre pas la borne
de J et ne change pas l'obligation quantitative fixée ci-dessus.
