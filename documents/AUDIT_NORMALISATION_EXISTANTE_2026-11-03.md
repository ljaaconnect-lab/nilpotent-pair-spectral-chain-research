# Normalisation générale : résultats déjà construits

3 novembre 2026. Vérification historique demandée par l'auteur avant toute
nouvelle construction. Le périmètre est celui des travaux du projet, sans
nouvelle recherche bibliographique.

**Conclusion : oui, des normalisations terminales exactes générales et des
circuits scalaires les réalisant depuis les données originales existaient
déjà.** L'affirmation antérieure « la normalisation générale reste à
construire », sans qualification de coût ni de représentation, était trop
large. Le raccord d'une telle normalisation à un budget scalaire polynomial
uniforme pour le même circuit reste non établi dans les résultats vérifiés.

## 1. Dans la forme linéarisée et la fusion des transports

[FUSION_LINEARISEE.md, section 2](../etudes/2026-11-01/linearisation-orientee-convolution/FUSION_LINEARISEE.md)
établit pour les lignes générales, avec les paramètres de corps admissibles,

\[
\lambda(F_f)=\omega^{fD_*}\lambda(F_0),\qquad
\mathcal Z[k]=\delta_{k,k_*}\lambda(F_0)\widetilde\Omega.
\]

Le degré terminal du quotient est de dimension un. La correction du signe
et la lecture INTT sont déjà raccordées à cette direction fixe. Cette
identité vaut pour toute taille et toute parenthésation des produits
orientés, par l'associativité. Elle ne fournit pas, à elle seule, un
circuit scalaire polynomial pour la coordonnée terminale.

La section 4 du même fichier raccorde déjà cette lecture aux différences :

\[
\lambda(F_0)=
\left[\prod_i(T_{v_i}-I)D_n\right](0),\qquad
T_yT_z=T_{y+z}.
\]

[RACCORD_NTT.md, sections 2–4](../etudes/2026-11-01/fusion-ntt/RACCORD_NTT.md)
donne aussi, pour toute longueur terminale n,

\[
\prod_j(T_{t_je_j}-I)1
=\left(\prod_jt_j\right)\mathcal I_{n-1}\cdots\mathcal I_0(1),
\]

puis l'observation par les horloges et l'INTT. Le texte distingue
explicitement cette identité générale du coût de son action scalaire.
La simple préparation compacte de F_0 conserve ses variables auxiliaires.

## 2. Des réalisations scalaires exactes étaient aussi disponibles

| Construction | Résultat déjà prouvé et construit | Portée du coût |
|---|---|---|
| [Insertion complète](../etudes/2026-11-01/fermeture-generale/INSERTION_GENERALE.md), sections 1–3 ; [circuit](../etudes/2026-11-01/fermeture-generale/circuit.py) | Loi à tout ordre, évaluation des horloges en portes scalaires, puis véritable INTT. Les seules données variables sont a,z. Le raccord précédent identifie cette valeur à celle des différences fusionnées. | Majorant O(N n(n+3)4^n+n²+N log N) pour cette réalisation. |
| [Fusion globale par polarisation](../etudes/2026-10-24/chaine-complete/construction_exacte_chaine.txt), sections 4–6 | Circuit exact général, phases comprises depuis les entrées, lecteur explicite à quatre accumulateurs par composante. Aucune amplitude fournie au programme. | Pour n≥3, coût depuis a,z : 4n²+4n(n−3)−n−2+(13n+2)2^(n−3). Petits cas traités séparément. |
| [Exécution du raccord existant](../etudes/2026-11-01/raccord-initialisation/EXECUTION_RACCORD_EXISTANT.md) ; [compilateur](../etudes/2026-11-01/raccord-initialisation/spectral/reprise-globale/shared_operator_dag.py) | Compilation des opérations en + et × ; après phases et INTT, seules a,z restent accessibles depuis les sorties. | Le partage est effectif ; la récurrence de coût démontrée ne donne pas un majorant polynomial uniforme. |

Pour la dernière réalisation, l'identité explicite est déjà écrite dans
[FUSIONS_ARCHITECTURE.md, section 2](../etudes/2026-11-01/fusion-double-log/FUSIONS_ARCHITECTURE.md) :

\[
\pi_n(L)G_B(s)=C_B\prod_js_j,\qquad
C_B=(\pi_n(L)G_B)(1,\ldots,1),
\]
\[
\mathcal Z[k]=\delta_{k,k_*}C_B\widetilde\Omega.
\]

Les lignes 102–104 y précisent que C_B est la racine réellement calculée,
et non une entrée. Cette réalisation requiert notamment Q>max(2,binom(n,2)).
Elle constitue un témoin historique d'existence, pas un calendrier imposé
à la compilation native recherchée. Ses coûts restent propres à cette
réalisation, conformément à la
[correction de périmètre](CORRECTION_PERIMETRE_BORNE_2026-11-03.md).

## 3. Cela satisfait bien le nouveau certificat Norm

Soit c_ancien(a,z) un des circuits complets exacts ci-dessus, dont les
sorties sont les coefficients scalaires de la table native. Définir

\[
c(a,z,x)=c_{\mathrm{ancien}}(a,z)
\]

consiste à ignorer les nouvelles entrées auxiliaires. Ce câblage ne crée
aucune porte arithmétique. Les identités de correction déjà démontrées
donnent directement

\[
\forall a,z,x,k,\quad
\sigma(c(a,z,x)_k)\widetilde\Omega=\mathcal Z(a,z)_k.
\]

Il s'agit exactement du certificat Norm de la note de fermeture. Sa
construction ne reçoit ni la sortie recherchée ni une amplitude en entrée.
L'existence générale exacte n'est donc pas une nouvelle obligation.

Les quantificateurs doivent cependant rester distincts, pour les tailles
et paramètres admissibles :

\[
\forall n\;\exists c_n:\quad\mathsf{Norm}(c_n,\mathcal Z_n)
\qquad\text{est déjà acquis par ces constructions.}
\]

\[
\exists K,d\;\forall n\;\exists c_n:\quad
\mathsf{Norm}(c_n,\mathcal Z_n)\ \land\ |c_n|\le Kn^d
\]

est l'énoncé supplémentaire qui n'a pas été retrouvé comme démontré.
Les preuves de normalisation et de taille doivent concerner le même
circuit. Le budget polynomial du représentant F_0(a,z,x) ne peut pas
être transféré à un autre circuit normalisé sans raccord de coûts.

Le certificat b·Omega_tilde=Z porte sur le terminal. Les représentations
des préfixes de degré k<n ne sont pas, en général, un scalaire unique
multiplié par le label terminal. Aucune nouvelle obligation de ce type
n'est imposée aux fusions intermédiaires.

## 4. Vérification Lean et portée exacte

Les sources anciennes ont été relues, ainsi que leurs contrats et rapports.
Un certificat historique général entièrement formalisé est également
présent :
[ActualClosedSubsetTransfer.lean](../etudes/2026-10-07/livrables/conjecture-1-5-closed-state/proofs/ActualClosedSubsetTransfer.lean)
prouve l'initialisation, la transition, l'invariant et la lecture des
entrées marquées. Son
[rapport n73](../etudes/2026-10-07/livrables/conjecture-1-5-closed-state/verification/n73-strict-report.json)
accepte 18 déclarations et correspond à l'empreinte du source conservé.
Le même fichier établit la dimension 2^n de cette référence exhaustive.
Ce témoin confirme l'existence générale exacte ; sa représentation et son
coût ne deviennent pas ceux de l'architecture compacte recherchée.

Deux rejeux indépendants ont été effectués sans modifier les archives :

```text
python -B etudes/2026-11-01/fusion-ntt/replay_lean.py
python -B etudes/2026-11-01/raccord-initialisation/dualite/replay_lean.py
```

Les sept théorèmes Fourier/différences et les quatre théorèmes affichés
du lecteur dual passent avec Lean 4.34.1, sans avertissement ni sorryAx.
Les empreintes des trois sources Lean correspondent aux rapports archivés ;
celles du compilateur shared_operator_dag.py et de son vérificateur
correspondent également au rapport conservé.

Ces vérifications portent sur les noyaux algébriques déclarés. Elles ne
formalisent pas intégralement les compilateurs historiques et ne prouvent
pas leur borne polynomiale. Les identités générales des chaînes complètes
sont démontrées dans les textes cités, avec leurs programmes et contrôles.

Le théorème récent CertifiedScalarClosure reste valide : il donne un
raccord conditionnel de normalisation et de budget. Ses hypothèses de
normalisation ne signifient pas que tous les travaux antérieurs en étaient
dépourvus. L'instanciation intégrale de ces anciens compilateurs dans son
nouveau type de circuit Lean est un travail distinct.

**État corrigé : normalisation exacte générale déjà construite ; raccord
de cette normalisation avec une borne scalaire polynomiale uniforme
sur le même circuit encore à établir.**

La [mesure ultérieure du même circuit partagé](COUT_MEME_CIRCUIT_2026-11-03.md)
fixe ce raccord quantitatif par une partition exacte des portes finales,
sans rouvrir l'existence de la normalisation.
