# Tentative de clôture : fusion et lecture sur le même circuit

3 novembre 2026. **La borne polynomiale générale n'a pas été obtenue.**
Les contrôles ci-dessous éprouvent deux simplifications concrètes de la
compilation native. Ils ne sont ni une preuve de cette borne ni une
preuve de son impossibilité.

Le problème reste exactement celui du
[compte partagé](COUT_MEME_CIRCUIT_2026-11-03.md) : construire la famille
scalaire exacte et démontrer, sur ses propres portes,

\[
J_n=|T_n\setminus P_n|\le\kappa n^e.
\]

Aucune condition de lecture ultérieure n'est ajoutée à cet objectif.
L'existence de normalisateurs exacts demeure acquise. La borne précédente
sur les représentants et les règles conditionnelles de fermeture ne
démontrent pas cette inégalité.

## 1. Tentative : fusionner les directions puis lire

Le raccord natif utilise les translations \(T_uD(y)=D(y+u)\), avec
\(T_uT_v=T_{u+v}\), et les différences \(\Delta_u=T_u-I\).
La règle exacte est

\[
\Delta_u\Delta_v=T_{u+v}-T_u-T_v+I.
\]

La tentative examinée consiste à ne conserver que la direction cumulée
\(u+v\), puis à effectuer l'observation terminale. Pour deux orientations,
dans les coordonnées obtenues par inversion Fourier, poser
\(D(y)=y_0y_1\). La lecture exacte est

\[
\begin{aligned}
\delta(u,v)
&=D(u+v)-D(u)-D(v)+D(0)\\
&=u_0v_1+u_1v_0.
\end{aligned}
\]

Cette identité fournit bien le calcul scalaire exact à deux lignes. Elle
ne permet pas de remplacer ses données par la seule somme des directions.

## 2. Contre-exemple dans les entrées originales

Prendre \(n=2,Q=97,N=4,\omega=22,z=1\), et les étiquettes \((0,1)\).
Ce sont des paramètres admissibles du compilateur natif. Les entrées

\[
a=\begin{pmatrix}0&2\\2&0\end{pmatrix},\qquad
a'=\begin{pmatrix}14&14\\14&14\end{pmatrix}
\]

donnent, par la préparation réelle \(B_{ij}=(1+a_{ij}^2)z^{2^{in+j}}\),

\[
B=\begin{pmatrix}1&5\\5&1\end{pmatrix},\qquad
B'=\begin{pmatrix}3&3\\3&3\end{pmatrix}
\quad\text{dans }\mathbb F_{97}.
\]

Les deux sommes de lignes et les deux sommes de colonnes valent 6 dans
les deux cas. Les directions cumulées dans les coordonnées Fourier du
programme sont également identiques : \((3,17,0,83)\).
Cependant,

\[
\delta((1,5),(5,1))=36-5-5=26,
\]
\[
\delta((3,3),(3,3))=36-9-9=18.
\]

Il n'existe donc aucune fonction de la seule direction cumulée qui donne
la lecture correcte pour ces deux entrées. Même connaître toute la
trajectoire \(D(t(u+v))=36t^2\) ne les distingue pas.

La réparation exacte à cet ordre conserve les deux observations
individuelles \(D(u),D(v)\). Elle utilise les portes ordinaires de la
formule de \(\delta\). Son coût constant pour deux lignes ne fournit pas
une borne uniforme pour un nombre arbitraire de lignes.

## 3. Contrôle sur le programme complet, avec son INTT

Le vérificateur réutilise
[le compilateur natif](composition-native-2026-11-03/compose_native_representatives.py)
sans le modifier : mêmes fils \(C_{ir}\), même produit partagé, même signe
et vraie INTT. La référence dans le quotient orienté sert uniquement au
contrôle de petites instances.

Une seconde simplification testée remplace les auxiliaires par le signal
Fourier des valeurs scalaires \(q_0=q_1=1\), soit
\(x=(2,23,0,76)\). Elle donne \(F_0(x)=36\) dans les deux cas.
Après le signe universel \(-1\) et l'INTT, les sorties ordinaires valent
toutes deux \((0,61,0,0)\). Les coefficients exacts de la sortie orientée
dans le label \(\widetilde\Omega\) sont respectivement
\((0,26,0,0)\) et \((0,18,0,0)\).

L'INTT et le signe sont donc bien inclus dans ce test. Cette substitution
scalaire n'est pas une normalisation du représentant orienté.

Le même contrôle a été exécuté pour \(n=2,\ldots,8\) sur les blocs
\(\operatorname{diag}(B,I_{n-2})\) et
\(\operatorname{diag}(B',I_{n-2})\), toujours dans \(\mathbb F_{97}\).
Les zéros sont réalisables avec \(a_{ij}=22\), puisque \(1+22^2=0\).
Les sorties exactes restent 26 et 18 au canal attendu ; les trajectoires
cumulées sont identiques, égales à \(36t^n\).

Ces expériences ne concernent pas un programme qui conserverait davantage
d'informations que ces deux simplifications. Elles n'établissent aucune
borne inférieure sur les circuits scalaires généraux.

## 4. Fichiers et portée de la vérification

- [Vérificateur du circuit natif](tentative-cloture-2026-11-03/verify_fusion_candidates.py).
- [Rapport exact des contrôles](tentative-cloture-2026-11-03/fusion-candidates-validation.json).
- [Preuve Lean du cas à deux lignes](tentative-cloture-2026-11-03/TotalFusionObstruction.lean).
- [Rejeu Lean](tentative-cloture-2026-11-03/replay_total_fusion_obstruction.py).
- [Rapport Lean](tentative-cloture-2026-11-03/total-fusion-lean-validation.json).

```text
python -B documents/tentative-cloture-2026-11-03/verify_fusion_candidates.py
python -B documents/tentative-cloture-2026-11-03/replay_total_fusion_obstruction.py
```

Les cinq théorèmes sont acceptés par Lean 4.34.1, sans erreur,
avertissement ni `sorry`. Les audits n'emploient que les axiomes standards
`propext` et `Quot.sound`.

La preuve Lean porte sur l'identité de différence, la légalité des quatre
lignes, l'égalité de leurs sommes, les valeurs 26 et 18 et l'absence d'une
fonction de la somme satisfaisant ces deux lectures. Le raccord aux fils
du compilateur et à l'INTT est vérifié séparément par le programme Python.
Une validation de ces énoncés n'est pas une validation de
\(J_n\le\kappa n^e\).

**Le projet reste ouvert sur cette même borne quantitative.** La tentative
ne justifie ni une valeur de \(\kappa,e\), ni l'annonce d'une clôture
polynomiale générale.
