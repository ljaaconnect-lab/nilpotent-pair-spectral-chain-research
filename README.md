# Nilpotent-Pair Spectral Chain — Research Archive

**Auteur : TSIGBE Comlan Alain.** État de l'archive : 4 novembre 2026.

Ce dépôt rassemble les tentatives de recherche sur l'annihilation par collision orientée, la linéarisation sur un corps fini, la fusion spectrale et la lecture finale. Il conserve les preuves Lean, les scripts, les contre-exemples, les rapports de validation et les états historiques, avec leurs chemins d'origine.

**Le manuscrit actuel et son PDF sont exclus de ce dépôt, conformément au choix de l'auteur.** Les anciens papiers présents dans `sources/papiers/` sont des pièces historiques de la recherche. Le [tableau des références internes](REFERENCE_MAP.md) donne les chemins des documents cités dans le manuscrit actuel.

## État scientifique

- La chaîne native et la conservation de la lecture dans le quotient sont décrites et démontrées dans les notes actuelles.
- La borne de **29 n³ portes** concerne le circuit partagé de représentants en `a,z,x` ; sa variante avec unité est bornée par **29 n³ + 1**.
- La compilation scalaire générale sur les seules entrées `a,z` reste ouverte. Les implications conditionnelles, les observations numériques et les tentatives anciennes gardent leur portée propre.

Les mentions historiques `merged`, `closed`, `proved` ou les scores de campagnes doivent être lues avec les hypothèses de leur dossier et de leur rapport. Elles ne constituent pas un certificat global de résolution.

## Commencer par ces fichiers

| Objet | Accès |
|---|---|
| Cadre actuel | [documents/CADRE_ACTUEL.md](documents/CADRE_ACTUEL.md) |
| Inventaire des bornes et de leur portée | [INVENTAIRE_DEMONSTRATIONS_POLYNOMIALES_2026-11-03.md](documents/INVENTAIRE_DEMONSTRATIONS_POLYNOMIALES_2026-11-03.md) |
| Compilateur natif de représentants | [compose_native_representatives.py](documents/composition-native-2026-11-03/compose_native_representatives.py) |
| Conservation de la lecture | [LECTURE_CONSERVEE.md](documents/unite-temoin-2026-11-04/LECTURE_CONSERVEE.md) |
| Variante avec unité | [compile_with_unit.py](documents/unite-temoin-2026-11-04/compile_with_unit.py) |
| Preuves Lean récentes | [UnitLift.lean](documents/unite-temoin-2026-11-04/UnitLift.lean), [SquarefreeReadout.lean](documents/unite-temoin-2026-11-04/SquarefreeReadout.lean) |
| Reproduction portable | [REPRODUCIBILITY.md](REPRODUCIBILITY.md) |
| Références du manuscrit vers l'archive | [REFERENCE_MAP.md](REFERENCE_MAP.md) |
| Catalogue de 105 pistes historiques | [catalogue.json](catalogue.json) |
| Index des fichiers Lean | [publication/proofs.json](publication/proofs.json) |
| Index des tentatives et dossiers | [publication/attempts.md](publication/attempts.md) |
| Empreintes des fichiers publiés | [publication/manifest.json](publication/manifest.json) |

## Organisation

| Dossier | Contenu |
|---|---|
| `documents/` | Notes de synthèse, noyaux Lean récents, compilateurs et rapports |
| `etudes/` | Études datées, expériences, preuves et livrables successifs |
| `historique/` | États intermédiaires, pistes abandonnées ou corrigées, archives Git |
| `travail/` | Sources et matériaux de travail conservés, sans caches de compilation |
| `sources/` | Papiers historiques, extractions textuelles et références bibliographiques |
| `archives/` | Cinq ensembles ZIP historiques, avec ceux des livrables dans `etudes/` |
| `outils/` | Outils historiques et contrôle du manifeste de publication |
| `repro/` | Nouveaux points d'entrée portables pour les contrôles récents |
| `publication/` | Index, empreintes, correspondance des références et périmètre de l'export |

Le [README.txt](README.txt), l'[index HTML historique](index.html) et les manifestes anciens sont conservés comme documents datés. Ils peuvent mentionner des chemins locaux, des fichiers temporaires exclus ou des versions de papiers antérieures. Pour l'état publié, utiliser ce README, les notes actuelles et le manifeste de `publication/`.

## Reproduire les contrôles récents

Avec Python 3, depuis la racine du dépôt :

```sh
python -B outils/verifier_publication.py
python -B repro/run.py smoke
python -B repro/run.py unit
```

Ces contrôles récents utilisent la bibliothèque standard Python. Le fichier historique `requirements.txt` décrit des dépendances supplémentaires d'autres campagnes ; elles ne sont pas toutes nécessaires au noyau récent.

Pour Lean, suivre [REPRODUCIBILITY.md](REPRODUCIBILITY.md). La configuration portable fixe **Lean 4.34.1** et le tag **mathlib v4.34.1**. Le rejeu ciblé couvre sept modules récents ; il ne prétend pas reconstruire automatiquement chaque candidat ou état historique de l'archive.

## Intégrité et historique

Les fichiers copiés depuis le projet conservent leurs contenus et leurs chemins. `publication/source-export.json` décrit cet export ; `publication/manifest.json` couvre l'état publié. Les archives `.bundle` conservent les historiques Git embarqués. Le dépôt de publication commence par un instantané explicite de ces matériaux.

Le périmètre exclut le papier actuel, les sorties temporaires, les caches Python/Lean, les exports redondants et la copie d'un livre tiers. Les références bibliographiques de ce livre sont conservées sans redistribuer son PDF.

## Citation et droits

Utiliser le bouton GitHub **Cite this repository** ou le fichier [CITATION.cff](CITATION.cff). Pour une preuve précise, citer aussi le chemin et le commit ou le tag utilisé. Le tag de l'instantané est `research-2026-11-04`.

Les mentions et licences présentes dans les sous-dossiers conservent leur portée ; aucune licence globale supplémentaire n'est attribuée à l'ensemble des travaux. Voir [NOTICE.md](NOTICE.md).
