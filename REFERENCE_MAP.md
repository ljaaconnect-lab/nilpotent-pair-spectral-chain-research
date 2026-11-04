# Correspondance des références internes du manuscrit

**Auteur : TSIGBE Comlan Alain — état du 4 novembre 2026.**

Le manuscrit actuel n'est pas inclus. Ce tableau permet de retrouver les sept références internes et les principaux fichiers de vérification auxquels il renvoie. Les clés sont celles de sa bibliographie LaTeX. Les chemins sont conservés à l'identique.

| Clé | Référence | Fichier dans le dépôt |
|---|---|---|
| `papier` | Annihilation, raccord spectral et démonstrations — papier historique | [sources/papiers/annihilation_raccord_spectral_demonstrations.pdf](sources/papiers/annihilation_raccord_spectral_demonstrations.pdf) |
| `composition` | Composition des bornes de l'architecture native | [documents/COMPOSITION_BORNES_NATIVES_2026-11-03.md](documents/COMPOSITION_BORNES_NATIVES_2026-11-03.md) |
| `inventaire` | Inventaire des démonstrations de bornes polynomiales | [documents/INVENTAIRE_DEMONSTRATIONS_POLYNOMIALES_2026-11-03.md](documents/INVENTAIRE_DEMONSTRATIONS_POLYNOMIALES_2026-11-03.md) |
| `fusion` | Un seul produit linéarisé pour toutes les fréquences | [etudes/2026-11-01/linearisation-orientee-convolution/FUSION_LINEARISEE.md](etudes/2026-11-01/linearisation-orientee-convolution/FUSION_LINEARISEE.md) |
| `raccord` | Vérification du raccord de normalisation sur le circuit déjà borné | [documents/RACCORD_NORMALISATION_MEME_CIRCUIT_2026-11-03.md](documents/RACCORD_NORMALISATION_MEME_CIRCUIT_2026-11-03.md) |
| `lecture` | Conservation générale de la valeur par la lecture native | [documents/unite-temoin-2026-11-04/LECTURE_CONSERVEE.md](documents/unite-temoin-2026-11-04/LECTURE_CONSERVEE.md) |
| `unite` | Unité témoin et conservation du coefficient terminal | [documents/unite-temoin-2026-11-04/DEMONSTRATION.md](documents/unite-temoin-2026-11-04/DEMONSTRATION.md) |

## Fichiers complémentaires

- [Compilateur représentatif natif](documents/composition-native-2026-11-03/compose_native_representatives.py).
- [Ajout de l'unité au même cœur partagé](documents/unite-temoin-2026-11-04/compile_with_unit.py).
- [Lecture spectrale et programme partagé : INTTProjection.lean](documents/raccord-intt-2026-11-04/INTTProjection.lean).
- [UnitLift.lean](documents/unite-temoin-2026-11-04/UnitLift.lean) et son [rapport historique](documents/unite-temoin-2026-11-04/lean-validation.json).
- [SquarefreeReadout.lean](documents/unite-temoin-2026-11-04/SquarefreeReadout.lean) et son [rapport historique](documents/unite-temoin-2026-11-04/squarefree-validation.json).
- [Critère quantitatif sur un même graphe : SameDAGCost.lean](documents/cout-meme-circuit-2026-11-03/SameDAGCost.lean).

Pour des liens immuables, remplacer `blob/main/` par `blob/research-2026-11-04/` ou par `blob/<commit>/` dans les URL GitHub.
