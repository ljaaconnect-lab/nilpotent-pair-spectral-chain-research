# Recherche de la borne polynomiale de toute la chaîne

Suite constructive : une [nouvelle compilation du même projecteur](../projection-avant-derivation/PROJECTEUR_COMPILE.md)
fusionne avant les dérivations suivantes. Elle produit la chaîne complète
en 472 portes pour n=6 et reconstruit le même préfixe en 630 portes.
Mise à jour : sa [propre preuve de croissance](../projection-avant-derivation/taille/CROISSANCE_PROJECTION.md)
établit désormais C_Y(n)>=2^(n/2) pour n puissance de deux >=4.
La reprise active utilise la [matrice linéarisée et la fusion spectrale](../linearisation-orientee-convolution/FUSION_LINEARISEE.md).
La preuve ci-dessous conserve sa portée sur le compilateur antérieur.

Le double logarithme est abandonné conformément à la consigne de l'auteur.
La réalisation globale par jets, déjà écartée, est également exclue de
cette reprise. Le circuit direct partagé sert de référence vérifiée ;
la recherche d'une autre compilation vise désormais à fusionner avant
la création des dérivées qu'il matérialise.
La cible reste le circuit complet depuis `a,z`, avec orientation, correction
universelle, annihilation et spectral, en portes scalaires ordinaires.
**La borne polynomiale générale n'est pas démontrée.**

**Nouvelle conclusion concernant le compilateur direct fixé.** La
[preuve de croissance du préfixe](si-direct/CROISSANCE_DAG_DIRECT.md)
établit `S_I^(1)(2m) >= binom(2m,m) >= 2^m` pour `m>=2`.
Sa taille ne peut donc pas être bornée polynomialement. Le résultat
compte des dérivées déjà créées et conservées par son partage syntaxique.
Il n'exclut pas une autre compilation scalaire de la même chaîne.

La [révision du décompte après fusion](BORNE_REVISEE_APRES_FUSION.md)
resserre maintenant la borne du circuit direct à
`C_chaîne <= S_I^(1) + 4n² - 3n + 2`, préparation de `B` comprise dans
`S_I^(1)`. Elle partage les sommes de lignes déjà calculées et ne réplique
pas le calcul spectral. Le composant lecteur antérieur, fusionné avec sa
lecture, coûte `2q` portes depuis les observations disponibles, au lieu de
leurs mises à jour successives ; leur production n'est pas gratuite.

La [fusion terminale à défaut quelconque](FUSION_TOUT_ORDRE.md) étend
la correction des derniers niveaux du lecteur existant.

Pour tout entier `0 <= R < n/2`, elle donne

\[
C_{\mathrm{chaîne}}\le S_{I_R}
+O\!\left((R+1)(R+2)^2 6^R n^{\lfloor R/2\rfloor+2}\right).
\]

Le terme ajouté est polynomial pour `R` fixé. En particulier, `R=2`
donne une correction en `O(n³)` depuis `B`. La preuve traite les valeurs
de collision partagées par plusieurs profils, notamment pour `n=6`.
`S_{I_R}` inclut la préparation des entrées et le préfixe restant ;
le même comptage s'applique à sa compilation directe. En effet, pour
`n=2m>=4` et `R<m`, le seuil est défini avec `b=n-R-1>=m>=2`.
Le profil de `m` blocs de taille deux respecte cette borne de bloc, donc
`tau_R>=m`. Les facteurs `1,...,m` restent ainsi les premiers facteurs du
préfixe, et les mêmes racines témoins sont conservées. Les autres
organisations globales ne sont pas couvertes par ce comptage.

La correction locale emploie des coefficients de petits produits marqués,
de degré borné par `R`. Elle ne développe pas le préfixe `S_{I_R}` en jets.
Elle ne fournit cependant aucune fermeture polynomiale générale de ce préfixe.

La démonstration a été relue indépendamment. Ses vérifications finies
sont conservées avec les sources dans ce dossier. Lean vérifie le lemme
combinatoire `2^m <= binom(2m,m)`, sans formaliser l'atteignabilité dans le
compilateur. Aucun théorème Lean de fermeture polynomiale générale n'a
été produit. Les preuves antérieures gardent leur portée antérieure.

La recherche n'a donc pas établi l'énoncé demandé
`C_chaîne(n) <= K n^c` avec `K,c` indépendants de `n`.
Elle n'établit pas non plus l'impossibilité d'un tel circuit.

Reproduction des vérifications numériques de la correction terminale :

```text
python outils/reproduire.py run fusion-terminale-generale
python outils/reproduire.py run recompte-fusion
python outils/reproduire.py run taille-prefixe-direct
python outils/reproduire.py run preuve-comptage-direct
```
