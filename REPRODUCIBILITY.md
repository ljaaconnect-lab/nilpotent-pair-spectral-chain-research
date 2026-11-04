# Reproduire les contrôles de la chaîne spectrale

Les commandes ci-dessous portent sur le constructeur actuel de représentants
en `a,z,x`, l'ajout de l'unité et sept noyaux Lean explicitement sélectionnés.
Les autres essais et rapports restent consultables dans leurs dossiers datés.
Une exécution réussie ne démontre pas la fermeture scalaire générale sur les
seules entrées `a,z` : cette question est formulée séparément dans l'article.

## Contrôles Python légers

Installer Python 3.10 ou plus récent. Aucune bibliothèque tierce n'est requise
pour ces deux commandes ; le `requirements.txt` historique concerne d'autres
expériences. Depuis la racine du dépôt :

```sh
python -B repro/run.py
python -B repro/run.py unit
```

La première commande est équivalente à `python -B repro/run.py smoke`.
Elle construit les représentants pour `n=1,2,4`, vérifie leurs comptes de
portes et compare la véritable INTT au routage sur des entrées déterministes.
Les nombres attendus de portes utiles sont `12,73,330`.

La commande `unit` teste les tailles `1,2,3,4,8,16`. Elle contrôle la
réutilisation du préfixe, le budget de représentants et l'identité entre les
sorties avant et après ajout de l'unité. Elle vérifie aussi que l'évaluation
`x=0` renvoie l'unité routée ; cette évaluation n'est pas le lecteur du
coefficient terminal. Ces essais sont des contrôles finis, distincts des
démonstrations générales données dans l'article.

Le point d'entrée retrouve la racine à partir de son propre emplacement ; il
fonctionne aussi depuis un autre répertoire. Il n'exécute pas les fonctions
`main` des anciens validateurs et ne réécrit aucun rapport historique.
Chaque exécution écrit un rapport JSON neuf dans
`reproducibility-results/`, dossier ignoré par Git. Un emplacement différent
peut être choisi avec `--report chemin/rapport.json`.

## Préparer Lean et Mathlib

Installer [Elan](https://github.com/leanprover/elan) et rendre la commande
`lake` disponible dans le `PATH`. Les fichiers de `repro/lean` demandent
exactement Lean `v4.34.1` et Mathlib au tag `v4.34.1`.

```sh
cd repro/lean
lake update
lake exe cache get
cd ../..
python -B repro/run.py lean
```

`lake update` résout le tag et écrit le `lake-manifest.json` local ; les
dépendances et les caches sont téléchargés dans `.lake/`. L'installation
initiale peut donc demander un téléchargement important. Le point d'entrée
ne lance pas cette installation implicitement. Il vérifie la version du
compilateur et appelle `lake env lean -j1` sur chacun des sept fichiers
originaux ci-dessous, sans modifier leurs sources ni les runners anciens.
Le paramètre `--timeout 600` fixe le délai maximal de chaque processus Lean.

| Fichier | Portée du noyau sélectionné |
|---|---|
| `documents/composition-native-2026-11-03/NativeCompositionBounds.lean` | Conséquences arithmétiques des hypothèses de coût des blocs. |
| `documents/induction-native-2026-11-03/SharedCostInduction.lean` | Induction additive sur les coûts d'un circuit partagé. |
| `documents/cout-meme-circuit-2026-11-03/SameDAGCost.lean` | Partition des portes et conséquence d'une borne sur le complément du préfixe. |
| `documents/induction-native-2026-11-03/SpectralReadoutCompatibility.lean` | Compatibilité des lectures et phases ; identité de noyau supposée dans le routage concerné. |
| `documents/raccord-intt-2026-11-04/INTTProjection.lean` | Projection linéaire à travers le même programme spectral. |
| `documents/unite-temoin-2026-11-04/UnitLift.lean` | Unité, augmentation, budget et conservation d'une lecture annulant `1`. |
| `documents/unite-temoin-2026-11-04/SquarefreeReadout.lean` | Lecture effective de coefficients sans répétition dans `MvPolynomial`. |

Ces fichiers importent uniquement Mathlib. Leur contrôle conserve les
hypothèses figurant dans chaque énoncé ; il ne les transforme pas en résultats
inconditionnels sur le compilateur complet. Le rapport enregistre les sorties
Lean, les imports et les empreintes des sources, et échoue en présence d'une
erreur, d'un avertissement, de `sorryAx` ou d'une preuve remplacée par un
`sorry`, `admit` ou axiome déclaré dans ces sept fichiers.

Les axiomes standards que Lean affiche dans ses audits, tels que
`propext`, `Classical.choice` et `Quot.sound`, sont distincts d'un axiome
ajouté pour supposer un résultat du projet. Les sorties complètes de ces
audits restent dans le rapport JSON.

## Provenance de l'environnement historique

Les rapports historiques ont utilisé Lean `4.34.1`. L'environnement Mathlib
local provenait de l'archive du tag `v4.34.1`, téléchargée depuis
`https://codeload.github.com/leanprover-community/mathlib4/tar.gz/refs/tags/v4.34.1`.
Le rapport de bootstrap local enregistre l'empreinte SHA256 de cette archive :

```text
c586ce5d3f83f85903826b613347b81e9eb6da885ecbbf22f72b2a3197a2904e
```

Cette copie était une archive sans métadonnées Git : aucun identifiant de
commit Mathlib local n'est donc affirmé ici. La préparation Lake ci-dessus
fournit un environnement neuf résolu depuis le même tag. Les anciens scripts
qui référencent des chemins absolus Windows sont conservés pour la traçabilité ;
le point d'entrée `repro/run.py` n'en dépend pas.

Les fichiers Lean archivés peuvent être des dépendances, des versions
intermédiaires, des contre-exemples ou des candidats rejetés. Ce document ne
promet pas leur recompilation globale. La portée formalisée de chaque résultat
du papier est détaillée dans son annexe et dans les rapports associés.
