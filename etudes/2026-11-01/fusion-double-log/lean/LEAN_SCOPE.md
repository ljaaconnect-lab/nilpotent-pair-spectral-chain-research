# Portée de la vérification Lean

Le fichier `DoubleLogConjugation.lean` formalise des identités algébriques locales
du changement de variable à deux logarithmes. Il travaille dans un anneau
commutatif arbitraire, avec des applications additives satisfaisant Leibniz.

Pour une telle dérivation `D`, Lean déduit d'abord `D 1 = 0`. Sous la seule
hypothèse supplémentaire `D E = E * w`, il vérifie

\[
(D^2-D)(E-1)+(D(E-1))^2
=E(Dw-w)+(E+E^2)w^2.
\]

La version sommée porte sur toute famille finie de dérivations et tout scalaire
`c`. En prenant `c = 1/2`, lorsque 2 est inversible, elle fournit l'identité

\[
L(E-1)+\frac12\sum_j(D_j(E-1))^2
=E\,LV+\frac12(E+E^2)\sum_j(D_jV)^2,
\]

après identification `w_j = D_j V` et
`L = (1/2) Σ_j (D_j² − D_j)`. Le fichier ne définit pas de logarithme ou
d'exponentielle : la relation `D_j E = E * D_j V` demeure une hypothèse
explicite. Son interprétation `E = exp(V)` dans les séries formelles tronquées
demande donc séparément les hypothèses d'inversibilité des dénominateurs.

La factorisation du facteur de lecture est également vérifiée. Elle exprime
une fusion algébrique réelle du facteur commun `E`, sans présumer que les
dérivées qui alimentent le facteur ont un petit circuit.

La vérification ne porte pas sur la taille, la profondeur, l'initialisation ou
la chaîne complète. Aucune borne polynomiale ou quasi-polynomiale générale
n'en découle à elle seule.

Reproduction depuis la racine du projet :

```powershell
python -X utf8 etudes/2026-11-01/fusion-double-log/lean/replay_lean.py
```

Le script vérifie le code de sortie du noyau, l'absence de changement du source
pendant la compilation, l'absence d'avertissements et l'absence de `sorryAx`.
Le rapport JSON contient le SHA-256 du source et la sortie de `#print axioms`
pour chaque théorème.
