ANNIHILATION PAR COLLISION ORIENTÉE — PROJET CONSOLIDÉ
Regroupement du 2026-11-03 ; 105 pistes et tentatives recensées ; 11 versions de papiers retrouvées.

OUVRIR index.html pour naviguer et rechercher dans les essais.
Ce dossier est un projet local autonome, prêt à ouvrir comme dossier/projet dans Codex.

CADRE ACTUEL
Construire la chaîne entière en portes scalaires polynomiales depuis les
entrées originales, orientation et spectral ensemble, sans imposer P_A en
entrée. Le cadre corrigé est documents/CADRE_ACTUEL.md. Les formulations
antérieures centrées sur une source P_A sont conservées comme historique.

La résolution polynomiale générale n'est pas obtenue dans ces travaux.
Les preuves partielles, contre-exemples et scores restent attachés à leurs
hypothèses. « merged » dans les arbres signifie référence expérimentale
retenue, et ne signifie pas conjecture résolue. Les scores de campagnes
différentes ne sont pas directement comparables.

ARTICLE LATEX : ARCHITECTURE, GÉOMÉTRIE ET BORNES ÉTABLIES
output/pdf/architecture_orientee.pdf
Source autonome : output/pdf/architecture_orientee.tex
Onze pages, quatre figures vectorielles, preuves avec étapes intermédiaires,
coûts individuels et globaux, portée Lean en annexe. La construction scalaire
générale reste explicitement une conjecture, avec le critère quantitatif
sur le même graphe partagé. Compilation : output/pdf/README_article.md.

VÉRIFICATION DU RACCORD SUR LES FILS DU CIRCUIT BORNÉ
documents/RACCORD_NORMALISATION_MEME_CIRCUIT_2026-11-03.md
Le certificat normalized proposé est faux pour les sorties inchangées :
elles valent zéro en x=0, alors que la sortie orientée vaut n! Omega_tilde
pour a=0,z=1. La borne 29n³ reste celle des représentants. Le résultat
réfute cette instanciation, sans réfuter une normalisation compilée.
Dix théorèmes Lean acceptés ; label non nul gardé comme hypothèse formelle.
La preuve générale dans le quotient est écrite dans la note.

INVENTAIRE DES DÉMONSTRATIONS POLYNOMIALES
documents/INVENTAIRE_DEMONSTRATIONS_POLYNOMIALES_2026-11-03.md
Preuves générales de chaque bloc retenu, hypothèses et portée précise :
préparation, linéarisation, produits partagés, fusion, signe et INTT.
Distinction entre comptage écrit, programme Lean et implications numériques.
Règles de fermeture et lecture certifiée recensées. Treize rapports acceptés
et empreintes de 31 fichiers vérifiés, sans nouveau lancement de Lean.

INVENTAIRE CORRIGÉ : RETRAIT DES GROUPES AJOUTÉS
documents/INVENTAIRE_COMPLET_2026-11-03.md
G=2^n−1, s_k et W proviennent du prototype R ajouté, pas de l'architecture
retenue. Ils sont retirés de son inventaire. Le programme compact conserve
n vecteurs C, n formes, n−1 produits et une INTT partagée ; son budget de
représentants est polynomial. Les coûts du prototype R restent archivés
dans documents/INVENTAIRE_PROTOTYPE_R_2026-11-03.md. La compilation conjointe
en sorties scalaires depuis a,z garde la même cible de preuve quantitative.

RÉANALYSE DU QUOTIENT : CONVOLUTIONS ET COMPILATION CONJOINTE
documents/REANALYSE_QUOTIENT_2026-11-03.md
La fusion des fréquences est une identité avant lecture dans le quotient.
Réduction expérimentale exacte à tout ordre par convolutions, compilateur
scalaire d'essai avec préparation fusionnée et vraie INTT depuis a,z seuls.
Ses groupes de lignes ne sont pas imposés à l'architecture retenue. Les
mesures jusqu'à n=6 restent celles de cet essai. Huit théorèmes Lean
certifient le cas n=2,N=4, dont le cœur de trois portes. La borne
polynomiale générale de J reste non démontrée.

TENTATIVE DE CLÔTURE : FUSION ET LECTURE
documents/TENTATIVE_CLOTURE_2026-11-03.md
Deux simplifications testées sur le programme natif : direction cumulée
seule et spécialisation q=1. Contre-exemple légal à n=2, contrôlé avec la
vraie INTT et prolongé à n=2..8. La borne générale de J n'est pas obtenue ;
ces contrôles ne sont pas une impossibilité pour les circuits généraux.

MESURE DE TOUTE LA CHAÎNE SUR LE MÊME CIRCUIT PARTAGÉ
documents/COUT_MEME_CIRCUIT_2026-11-03.md
17 mesures du même programme natif avec vraie INTT, jusqu'à n=32,
par ensembles disjoints de portes utiles. Total des représentants :
330, 1494, 6766, 30558 portes pour n=4,8,16,32, avec auxiliaires x.
Pour le circuit normalisé, compte fixé : C_total=|T∩P|+J<=10n³+J.
J comprend ensemble fusion, normalisation et spectral. Une seule borne
reste visée : J<=kappa n^e sur la même famille exacte ; elle donnerait
K=10+kappa et d=max(3,e). Aucune borne générale de J n'est annoncée.

AUDIT DU CERTIFICAT DE NORMALISATION DÉJÀ CONSTRUIT
documents/AUDIT_NORMALISATION_EXISTANTE_2026-11-03.md
Normalisation terminale exacte générale retrouvée : identité dans la forme
linéarisée, raccord aux différences fusionnées et compilateurs scalaires
depuis a,z. L'existence exacte était déjà acquise. Le certificat et un
budget polynomial uniforme restent à raccorder pour le même circuit.
Rejeu propre des noyaux Lean Fourier/différences et du lecteur dual.

FERMETURE DES ÉTATS ET LECTURE TERMINALE CERTIFIÉE
documents/FERMETURE_NATIVE_2026-11-03.md
Fermeture des états partagés par extension, correction sémantique et coût
exactement additif. Lecteur explicite sans auxiliaires, de même taille,
sous certificat de normalisation du coefficient avec son label terminal.
Raccord à une famille de bornes polynomiales à exposants uniformes :
25 théorèmes Lean. Des normalisateurs exacts généraux existent déjà ;
leur raccord à un budget polynomial uniforme n'est pas obtenu par cette
seule induction.

INDUCTION SUR LA CHAÎNE NATIVE
documents/INDUCTION_CHAINE_NATIVE_2026-11-03.md
Récurrence additive vérifiée dans Lean, avec constantes et exposants
indépendants du rang. Preuve du programme partagé de préfixes : sens exact
et n−1 multiplications après une préparation commune. Raccord à la lecture
spectrale et borne des représentants ; les hypothèses d'initialisation
et de format terminal restent explicites. La sortie depuis a,z seuls
n'est pas obtenue par cette induction des représentants.

COMPOSITION DES BORNES : CHAÎNE NATIVE ET REPRÉSENTANTS LINÉARISÉS
documents/COMPOSITION_BORNES_NATIVES_2026-11-03.md
Raccord effectif depuis a,z : un seul produit linéarisé partagé, signe,
phases et vraie INTT. Borne générale 29n³ pour les représentants de toute
la table, 18n³+1 après fusion en routage. Contrôles n=1..8, 80 instances
numériques et 8 tables en z formel. Les auxiliaires x restent présents :
le résultat ne démontre pas encore la compilation scalaire depuis a,z seuls.
Le contrat exact de composition et le point non couvert sont explicités.
Cinq implications arithmétiques de comptage sont vérifiées dans Lean ;
leur portée est distinguée de la compilation et de l'élimination des x.

CORRECTION DU PÉRIMÈTRE : PRODUITS ORIENTÉS ET FUSION
documents/CORRECTION_PERIMETRE_BORNE_2026-11-03.md
La borne différentielle ci-dessous compte un prototype ajouté, pas les
objets imposés par l'architecture. Dans le quotient orienté, rho L=0 et
rho pi_h(L)=rho : les h filtres sont redondants. Preuve du même résultat
dans la forme linéarisée ; effacement de toute liste de filtres vérifié
dans Lean. Cela ne rend pas gratuite la compilation scalaire du quotient.

VARIANTE DIFFÉRENTIELLE : BORNE D'UN PROTOTYPE
documents/BORNE_CIRCUIT_PARTAGE_2026-11-03.md
Construction scalaire complète dans les coordonnées Fourier, vraie INTT
incluse ; contrôles jusqu'à n=6 dans deux corps. La borne des h compositions
sur l'état fermé était déjà polynomiale, hors initialisation. Nouveau
majorant du prototype : 2^{O(n log n)}, non retenu comme borne de l'architecture.
Cinq conséquences arithmétiques vérifiées dans Lean ; portée explicitée.

LITTÉRATURE : THÉORÈMES DE COMPILATION SCALAIRE
documents/OUTILS_LITTERATURE_COMPILATION_2026-11-02.md
Revue sur quatre axes : algèbres apolaires/zéons, Hadamard et ABP,
transposition, contractions matchgate/pfaffiennes. Décompte toutes
portes et hypothèses de chaque théorème. Aucun théorème vérifié ne
donne encore la borne générale sans construction supplémentaire.

EXISTENCE DES DÉFORMATIONS : BORNE SUR LE DEGRÉ EFFECTIF
documents/EXISTENCE_DEFORMATIONS_2026-11-02.md
Preuve en toute caractéristique : deg F >= L(n-s-mu) pour les
déformations linéaires d'incidences indépendantes des données.
Les petits groupes et mesures sont incompatibles avec deg F<L
dans cette famille précise. Aucune impossibilité générale de circuit.

APPORT DU PAPIER ETH : RACCORDEMENTS ET MESURES PARTAGÉES
documents/APPORT_PAPIER_ETH_2026-11-02.md
Lecture des 67 pages du papier externe fourni le 2 novembre.
Critère de compilation globale par valeurs, raccordé aux translations
et à l'INTT. Degré, configurations locales et valeurs des mesures sont
comptés explicitement. L'existence favorable est désormais exclue
dans la famille linéaire dense précise par la nouvelle reprise.

COMPILATION DES PRODUITS ORIENTÉS
documents/COMPILATION_PRODUITS_ORIENTES_2026-11-02.md
Circuit scalaire exact O_r(n^r) lorsqu'une factorisation de rang r fixé
est disponible ; partage spectral inclus, 96 instances vérifiées.
Les matrices marquées ont rang n en général : cette construction ne
démontre pas la borne générale. Portée des états linéaires précisée.

LECTURE FINALE : INTT ET COMPILATION CONJOINTE
documents/LECTURE_INTT_ET_MOMENTS_2026-11-02.md
L'INTT demeure la lecture terminale. Moments et matrice de lecture sont
des variantes auxiliaires, sans obligation de les matérialiser.
Aucune borne générale d'initialisation de tous les moments n'a été retrouvée.

CONSTANTES c ET d POUR LA VARIANTE PAR MOMENTS
documents/CONSTANTES_C_D_2026-11-02.md
d=2 pour le lecteur à observations, mis au format du compilateur n57.
La borne S<=n^c de son initialisation complète reste à démontrer.
Le couple c=5,d=2 du générateur compact ne fournit pas cette initialisation.

AUDIT CIBLÉ : COMPILATION GÉNÉRIQUE DÉJÀ ACQUISE
documents/AUDIT_COMPILATION_GENERIQUE_2026-11-02.md
Compilateur n57–n59 vérifié dans Lean : initialisation, puissance partagée
et lecture de uᵀM^K v en O(S+r³ log(K+1)+r²) portes scalaires.
Transport fusionné et dérivations également rétablis dans l'inventaire.

SCHÉMA ET ÉTAT DES PREUVES
documents/ARCHITECTURE_ET_COUTS_2026-11-02.md
Architecture après fusion, coûts établis et portée des vérifications.
Le lecteur composé est identifié comme le bloc restant à borner.

INVENTAIRE DES COÛTS
documents/INVENTAIRE_COUTS_2026-11-02.md
Chaque étape de la chaîne, les coûts locaux des opérateurs et le total
après fusion sont distingués, sans double comptage.

PARCOURS CONSEILLÉ
Dernière reprise : etudes/2026-11-01/linearisation-orientee-convolution/FUSION_LINEARISEE.md.
Matrice et orientation transformées ensemble, annihilation par convolution.
Toutes les fréquences fusionnent en un représentant auxiliaire F0.
Préparation O(n² log(n+1)) : 496, 628, 774 portes pour n=6,7,8.
Raccord exact à la loi T_y T_z=T_(y+z), sans table de colonnes utilisées
dans le compilateur de préparation. Lecture scalaire générale non résolue.
Le candidat de lecteur par déterminants réussit n=3,4, puis son filtre
échoue dès n=5 ; preuve et témoins dans le sous-dossier determinants/.

Étape précédente : etudes/2026-11-01/projection-avant-derivation/PROJECTEUR_COMPILE.md.
Projection immédiate exacte ; préfixe reconstruit avec un surcoût quadratique.
Une nouvelle preuve spécifique à ce compilateur établit désormais
C_Y(n)>=binom(n,n/2)>=2^(n/2) pour n puissance de deux >=4.
La conséquence arithmétique est vérifiée dans Lean, conditionnellement
à la borne inférieure ; le code du compilateur n’est pas formalisé.
Cette preuve ne s’applique pas à toutes les autres réalisations scalaires.

Étape précédente : etudes/2026-11-01/borne-chaine-generale/RESULTAT.md.
Le préfixe du compilateur direct fixé possède au moins binom(2m,m) portes
pour n=2m>=4. Preuve dans borne-chaine-generale/si-direct/.
Ce résultat ne borne pas la taille des autres circuits possibles.
Décompte révisé : borne-chaine-generale/BORNE_REVISEE_APRES_FUSION.md.
Préfixe direct + 4n²−3n+2 portes ; partage et routage vérifiés n=3..6.
Double logarithme et réalisation globale par jets écartés.
Correction terminale exacte à tout défaut R<n/2,
polynomiale pour R fixé ; O(n³) pour R=2. Le préfixe reste à borner.
La borne polynomiale de toute la chaîne n est pas obtenue.

Étape précédente : etudes/2026-11-01/fusion-double-log/RESULTAT_FUSIONS.md.
Fusion du spectral, des facteurs inutiles et de deux niveaux avec la lecture.
Correction terminale démontrée en au plus 5n² portes ; double log exécuté.
120 tables numériques, 192 jets et 9 tables z formel ; 4 identités Lean.
Borne polynomiale générale du préfixe différentiel non démontrée.

Étape précédente : etudes/2026-11-01/logarithmes-chaine/LOGARITHMES_ET_COUT.md.
Logarithmes formels dans le raccord existant, avec retour exact et élagage.
40 tables numériques, 200 jets intermédiaires et 3 tables z formel vérifiés.
Trois identités de conjugaison vérifiées dans Lean.
Borne quasi-polynomiale ou polynomiale globale non établie.

Étape précédente : etudes/2026-11-01/raccord-initialisation/EXECUTION_RACCORD_EXISTANT.md.
Le raccord choisi est conservé : G_B, facteurs I-L/r et INTT.
Un compilateur partagé les traduit en portes scalaires depuis a,z.
48 tables numériques n<=6 et 8 tables avec z formel n<=4 passent.
Le nombre général de portes n est pas encore borné polynomialement.
Les nouvelles formulations explorées restent seulement auxiliaires.

Étape précédente : etudes/2026-11-01/orbite-scalaire/ORBITE_ET_FERMETURE.md.
Retour aux objets polynomiaux choisis : l orbite scalaire G_B porte
les transports et leurs différences, avec entrelacement vérifié dans Lean.
Le projecteur global ferme sur h+1 observations, h=n(n-1)/2, en
h(4h+2) portes ; la lecture est un fil. Cette borne concerne le composant
une fois les observations disponibles : leur construction simultanée
depuis a,z reste à obtenir pour résoudre la chaîne générale.

Une variante applique la NTT aux coefficients du projecteur, les partage
entre toutes les fréquences, puis lit les observations avant l INTT finale.
La preuve et le compte sont dans LINEARISATION_PROJECTEUR.md.

Candidat auxiliaire : etudes/2026-11-01/fermeture-adaptative/ETAT_DIRECT.md.
Construction directe par élimination orientée sans division ; les phases
précèdent les éliminations et une véritable INTT termine la chaîne.
Le noyau algébrique est vérifié dans Lean ; 14 tables numériques et
5 tables avec z formel passent. État résiduel et lecteur se regroupent
dans un même résolvant. Le coût scalaire actuel demeure exponentiel.
La direction de réduction de lecture a été interrompue à la demande
de l auteur et reste uniquement dans l historique des études.

Étape précédente : etudes/2026-11-01/fusion-ntt/RACCORD_NTT.md.
La NTT porte sur les différences T_y-I. Le produit des n facteurs élimine
les répétitions au degré terminal, sans sélection finale de colonnes.
La formule est exacte à tout ordre ; des lemmes généraux sont vérifiés dans
Lean et 30 tables Z avec z formel sont contrôlées. Le coût scalaire de
l'action composée des différences n'est pas encore borné polynomialement.

Reprise précédente : etudes/2026-11-01/reprise-flot-rationnel/REPRISE.md.
Fusion rationnelle générale formalisée dans Lean et action des transports
compilée en portes scalaires polynomiales. 256 tests de fusion passent.
La sélection des colonnes distinctes reste à compiler : la résolution
polynomiale de la chaîne complète n'est toujours pas obtenue.

Étape précédente : etudes/2026-11-01/fermeture-generale/INSERTION_GENERALE.md.
Insertion complète avec identité exacte à tout ordre ; compilation scalaire
par dérivations et bandes de l’horloge. Six lemmes généraux vérifiés dans
Lean ; tests de la chaîne complète jusqu’à n=8. Le majorant actuel reste
O(n^3 4^n), donc la fermeture polynomiale générale n’est pas démontrée.
La correction quintique précédente reste dans lean-operateurs/.

1. sources/papiers/annihilation_raccord_spectral_demonstrations.pdf : papier confirmé.
2. documents/CADRE_ACTUEL.md : compréhension corrigée et objectif intégral.
3. documents/construction_exacte_chaine.txt : construction exacte actuelle et coût exponentiel.
4. etudes/2026-10-24/chaine-complete/ : noyaux gaussiens, polarisation,
   phases, corrections Schur–Good/Bass et réductions spectrales.
5. etudes/2026-10-24/source-scalaire/ : essais précédant le recentrage.
6. etudes/2026-10-07/livrables/ : formalisation Lean, convolutions,
   raccords, jets, préfixes, suffixes et états fermés.
7. catalogue.json / index.html : toutes les hypothèses, résultats et commits.

HISTORIQUE COMPLET
historique/ contient les instantanés des espaces de travail, les cas
non retenus, les rapports, les arbres et les messages publics disponibles
des deux conversations pertinentes. Les appels internes et le raisonnement
de l'assistant sont exclus de l'export des conversations.
Les versions des papiers sont conservées avec leurs noms et SHA256 ; leur
présence dans ce dossier n'affirme pas qu'elles ont toutes été relues ou
validées pendant ce regroupement.

historique/git/ conserve trois bundles Git autonomes. Pour explorer un
ancien état, cloner le bundle dans un nouveau dossier puis choisir le commit.
Les fichiers de travail non committés sont aussi conservés dans les
instantanés, indépendamment de ces bundles. Les originaux n'ont pas été déplacés.

VÉRIFICATION
  python outils/verifier_integrite.py
  python outils/reproduire.py run projection-immediate
  python outils/reproduire.py run prefixe-projete
  python outils/reproduire.py run preuve-projection
  python outils/reproduire.py run taille-prefixe-direct
  python outils/reproduire.py run preuve-comptage-direct
  python outils/reproduire.py run fusion-double-log
  python outils/reproduire.py run preuves-double-log
  python outils/reproduire.py run logarithmes
  python outils/reproduire.py run preuves-logarithmes
  python outils/reproduire.py run raccord-existant
  python outils/reproduire.py run preuves-raccord-dual
  python outils/reproduire.py run raccord-collisions
  python outils/reproduire.py run raccord-dual
  python outils/reproduire.py run raccord-contractions
  python outils/reproduire.py run orbite-scalaire
  python outils/reproduire.py run projecteur-ntt
  python outils/reproduire.py run observateur-collisions
  python outils/reproduire.py run preuves-orbite
  python outils/reproduire.py run schur-jet
  python outils/reproduire.py run preuves-schur-jet
  python outils/reproduire.py run resolvant-partage
  python outils/reproduire.py run fusion-ntt
  python outils/reproduire.py run preuves-fusion-ntt
  python outils/reproduire.py run transport-rationnel
  python outils/reproduire.py run preuves-transport
  python outils/reproduire.py run insertion-complete
  python outils/reproduire.py run preuves-insertion
  python outils/reproduire.py run lean-operateurs
  python outils/reproduire.py run preuves-operateurs
  python outils/reproduire.py run operateurs-horloge
  python outils/reproduire.py run ntt-walsh
  python outils/reproduire.py list
  python outils/reproduire.py smoke
Les deux tests smoke rejouent des circuits exacts de la chaîne complète.
Ils ne prouvent pas une borne polynomiale.

Les quatre dépendances Python expérimentales sont consignées dans
requirements.txt. Les vérificateurs de base utilisent la bibliothèque
standard ; les expériences symboliques, numériques et CP-SAT utilisent
respectivement SymPy, NumPy/SciPy et OR-Tools.

LEAN
Les sources .lean, lean-toolchain, manifestes Lake et rapports de compilation
historiques sont conservés. Les bibliothèques Mathlib, exécutables et caches
compilés ne sont pas dupliqués. Rejouer une compilation Lean exige l'outil
et les dépendances indiqués dans les README et scripts de chaque livraison.
Le regroupement n'a pas relancé les milliers de compilations/essais anciens.

POUR REPRENDRE
Travailler dans travail/ ou sur une nouvelle branche Git. Garder les essais
historiques intacts, noter le cadre, les entrées, la fusion, le lecteur et
le coût total de chaque nouvelle représentation. Aucune impossibilité
générale n'est déduite des modèles restreints qui ont échoué.

STOCKAGE
Le projet complet est stocké sur D:\Codex\Projets\annihilation-collision-orientee.
Un accès par jonction est fourni depuis le dossier outputs de la conversation.
Les originaux de recherche restent à leurs emplacements précédents.
