# Cadre corrigé après relecture intégrale — 24 octobre 2026

Vérification ciblée du raccord, 3 novembre 2026 :
[certificat sur les fils du circuit déjà borné](RACCORD_NORMALISATION_MEME_CIRCUIT_2026-11-03.md).
Le certificat `normalized` est faux pour les sorties inchangées du
représentant : elles s'annulent en x=0, alors que la sortie native vaut
n! Omega_tilde pour a=0,z=1. Le présenter comme une preuve simplement
manquante sur ces fils était incorrect. Ce résultat ne réfute pas les
normalisations exactes connues ni une compilation polynomiale de la même
architecture. Il exclut cette identification précise des représentants
aux coefficients, ainsi que la simple sélection d'un autre fil existant
pour n>=2. La borne générale scalaire reste non démontrée.

Inventaire des démonstrations, 3 novembre 2026 :
[preuves des bornes polynomiales de chaque élément](INVENTAIRE_DEMONSTRATIONS_POLYNOMIALES_2026-11-03.md).
Les démonstrations générales, programmes formalisés, implications de coût
et hypothèses terminales sont distingués. Les groupes du prototype R sont
exclus. Treize rapports acceptés correspondent aux sources et dépendances
contrôlées ; aucun nouveau théorème ni rejeu Lean n'est annoncé.

Inventaire corrigé, 3 novembre 2026 :
[retrait des groupes ajoutés au périmètre](INVENTAIRE_COMPLET_2026-11-03.md).
G=2^n−1, s_k et W décrivent le prototype récursif R, pas les objets de
l'architecture retenue. Leurs coûts restent dans un inventaire expérimental
séparé. Le constructeur compact retient n vecteurs C, n formes, n−1
produits et une INTT partagée. Son budget polynomial de représentants
reste valide ; la borne scalaire depuis a,z doit concerner la compilation
conjointe, sans lui imposer les groupes du prototype.

Réanalyse du quotient, 3 novembre 2026 :
[convolutions, fusion et compilation scalaire conjointe](REANALYSE_QUOTIENT_2026-11-03.md).
La fusion des fréquences vaut dans tout le quotient, avant lecture.
Une réduction expérimentale exacte à tout ordre donne un compilateur
scalaire d'essai, avec fusion de la préparation et vraie INTT. Ses groupes
de lignes ne sont pas des objets imposés par l'architecture. Contrôles des deux
variantes jusqu'à n=6, 72 instances numériques et 12 tables en z formel.
Huit théorèmes Lean certifient la normalisation n=2,N=4 et un cœur scalaire
de trois portes. La preuve générale de correction est écrite ; la borne
polynomiale de J reste non démontrée. Aucun lecteur supplémentaire n'est
reporté après ce coût et aucun majorant du candidat n'est une borne
inférieure pour l'architecture.

Tentative de clôture, 3 novembre 2026 :
[contrôles ciblés de la fusion et de la lecture](TENTATIVE_CLOTURE_2026-11-03.md).
Deux réductions examinées perdent l'information nécessaire : la seule
direction cumulée et la spécialisation q=1 ne distinguent pas deux entrées
légales dont les sorties valent 26 et 18 modulo 97. Le programme natif et
sa vraie INTT sont utilisés dans le contrôle. Cela ne réfute pas une autre
compilation partagée ; la borne générale de J reste non démontrée.

Coût sur le même circuit, 3 novembre 2026 :
[mesure entière et obligation quantitative fixée](COUT_MEME_CIRCUIT_2026-11-03.md).
Chaque porte utile est identifiée et comptée une seule fois dans un même
DAG, vraie INTT comprise. Les 17 mesures concernent le programme actuel
de représentants, qui conserve x. Pour une réalisation scalaire normalisée,
P désigne sa préparation et T ses ancêtres de sortie :
C_total=|T∩P|+|T\P|<=10n³+J. J englobe conjointement fusion, normalisation
et spectral. Le seul objectif quantitatif restant est J<=kappa n^e pour
cette même famille de circuits exacts. Il n'est pas établi par la mesure
des représentants ; aucun autre coût de lecture n'est ajouté après J.

Audit historique de normalisation, 3 novembre 2026 :
[certificats exacts généraux déjà construits](AUDIT_NORMALISATION_EXISTANTE_2026-11-03.md).
Les identités terminales de la forme linéarisée et des différences fusionnées
étaient acquises, ainsi que plusieurs compilateurs scalaires exacts depuis
a,z. L'existence d'un normalisateur exact général n'est donc plus une
obligation. La question restante porte sur le raccord de son certificat
et d'un budget polynomial uniforme pour le même circuit partagé.

Fermeture native, 3 novembre 2026 :
[états partagés et lecture terminale certifiée](FERMETURE_NATIVE_2026-11-03.md).
Une suite arbitraire d'extensions conserve les anciens fils et additionne
exactement les portes des nouveaux blocs. La correction est transportée
par l'interprétation dans l'algèbre orientée. Si les fils de coefficient
portent un certificat terminal avec le label Omega_tilde, un lecteur
explicite supprime les auxiliaires à coût inchangé. Le raccord à la borne
(K0+AK)n^max(a,b+c), pour n>=1, est vérifié sur une famille entière.
25 théorèmes Lean formalisent ces règles. Le théorème de lecture garde
la normalisation comme hypothèse ; des réalisations exactes générales
antérieures satisfont déjà cette propriété, mais le raccord à leur budget
scalaire polynomial uniforme n'est pas encore démontré.

Induction native, 3 novembre 2026 :
[preuve récurrente des coûts, des préfixes et du raccord](INDUCTION_CHAINE_NATIVE_2026-11-03.md).
L'induction porte sur les étapes d'une instance de taille n fixée.
La règle S_(i+1)<=S_i+K n^c, uniformément en i, est formalisée dans Lean.
Le programme partagé des préfixes est également vérifié, sémantique et
n−1 portes de multiplication comprises. Son invariant conserve les
représentants en a,z,x. La propriété terminale « sorties scalaires depuis
a,z seuls » ne découle pas de la seule récurrence sur la taille et reste
à établir pour la compilation globale.

Composition native, 3 novembre 2026 :
[raccord des bornes individuelles de bout en bout](COMPOSITION_BORNES_NATIVES_2026-11-03.md).
Le circuit orienté complet admet la borne 17n², ou 7n² après fusion
spectrale en routage. Un circuit partagé de représentants linéarisés
de toutes les sorties est construit en au plus 29n³ portes, vraie INTT
incluse, ou 18n³+1 après routage. Il conserve les variables auxiliaires x.
Contrôles jusqu'à n=8, sans filtre différentiel ni moments. Le raccord
des bornes est valide dans ces représentations ; le passage à des sorties
scalaires depuis a,z seuls n'est pas couvert par les contrats acquis.
L'INTT demeure la lecture terminale et aucune amplitude préalable n'est
imposée. Voir la note pour la distinction exacte entre les interfaces.

Correction du périmètre, 3 novembre 2026 :
[produits orientés, fusion et redondance du filtre auxiliaire](CORRECTION_PERIMETRE_BORNE_2026-11-03.md).
Le décompte 2^{O(n log n)} de la reprise précédente concerne une variante
différentielle ajoutée : il ne mesure pas les objets nécessaires à la
compilation conjointe recherchée. Dans le quotient orienté, rho L=0,
donc rho pi_h(L)=rho ; les h filtres sont redondants dans ce quotient.
L'identité est aussi établie dans la forme linéarisée, et l'effacement
de toute liste de filtres après projection est formalisé dans Lean.
La recherche conserve directement produits orientés, fusion et INTT,
sans imposer moments, familles de dérivées ou amplitude scalaire préalable.
La borne polynomiale complète n'est pas déduite de cette correction.
Le prototype et ses majorants sont conservés dans leur périmètre propre :
[variante différentielle linéarisée](BORNE_CIRCUIT_PARTAGE_2026-11-03.md).

Instruction de l'auteur : étudier la chaîne entière de collision orientée,
correction universelle et calcul spectral. Ne pas imposer le calcul direct
d'une amplitude scalaire P_A avant la couche spectrale.

Les 63 pages de annihilation_raccord_spectral_demonstrations.pdf ont été
relues en ordre dans cette reprise, corps principal, références et B.1–B.11.
SHA256 : ed1f05cd132305ec98ec4f195ae395123cc4ae68e1a137ac4a78898f4d5199f4.
Les pages 38 et 55 ont aussi été inspectées visuellement.

## Objet et invariant

Les feuilles de données sont A ou p_ij=1+a_ij², z et les constantes de
champ autorisées. L'adressage w_ij=2^((i−1)n+j−1) reste formel.
L'orientation attachée à chaque colonne est q_j=x_j y_j :
q_j²=0 et q_i q_j=q_j q_i. Le signe global est
gamma_n=(−1)^(n(n−1)/2), avec q_[n]=gamma_n·Omega_tilde.

Une forme directe de la chaîne est :

  P_i[t] = sum_{j:d_j=t mod N} B_ij q_j;
  A_i[f] = NTT(P_i)[f] = sum_j B_ij q_j omega^(f d_j);
  W[f] = gamma_n product_i A_i[f];
  Z[k] = INTT(W)[k].

La cible formelle est

  Z[k] = delta_(k,k*) · (sum_sigma product_i p_i,sigma(i) z^E(sigma))
                        · Omega_tilde,
  k* = (sum_j d_j) mod N.

Le symbole P_A désigne le coefficient de cette sortie; il n'est pas une
feuille ni un intermédiaire scalaire obligatoire. La préparation des
marqueurs, la fusion des facteurs orientés, les phases et les transformées
peuvent être compilées ensemble, dans un ordre réorganisé et avec partage.
Une lecture scalaire, si elle est requise, peut n'apparaître qu'en sortie.
Son implantation fait alors partie du coût total.

## Ce que le texte établit

1. Le premier filtre à orientation simple se compile par déterminant
   signé en O(n^4) portes scalaires, sans développement des monômes.
2. La double orientation conserve les amplitudes et adresses et rassemble
   les signes en gamma_n. Elle ne remplace pas B par son carré.
3. Les entrées naturelles du spectre sont les sommes de termes B_ij q_j
   groupés par d_j, définition 13.10 et proposition B.22.
4. Le §B.1 dit explicitement que V_A=gamma_n F_A=P_A Omega_tilde est la
   valeur d'un fil existant et que P_A n'est ni constante ajoutée ni oracle.
5. La phase commune omega^(f D*) permet de déplacer la modulation après
   le filtre. C'est une identité de réorganisation du DAG.
6. Le circuit raccordé de B.1–B.4 a, avec p comme feuilles, au plus
   4n²+n−2+epsilon_n+B(N) portes dans l'algèbre agrandie,
   B(N)=2N log2 N+3N−3 pour N puissance de deux, N>=2.
   La préparation depuis A ajoute 2n² portes. Avec n<N<=2n,
   ce compte est polynomial. Cette borne est déjà prouvée dans le papier.
7. B.11/B.18 donnent un compilateur aval scalaire lorsque la coordonnée
   initiale est exposée. C'est une construction suffisante à coût additif;
   elle n'impose pas cette interface à toute autre compilation globale.
8. B.19 donne une équivalence de complexité des SORTIES : un circuit
   scalaire pour la table permet de sélectionner P_A sans porte nouvelle.
   Il ne dit pas que P_A doit avoir été calculé avant le spectre.

## Cible de la suite

Précision de l'auteur, 1 novembre 2026 : inventer un nouveau circuit
d'opérateurs ; une réénumération exponentielle des signes ou des
sous-ensembles ne répond pas à la demande. La taille de la description
d'un opérateur ne vaut pas encore borne du coût scalaire de son action.
La compilation globale doit traiter cette action, la fusion et la lecture.

Construire et borner une compilation GLOBALE de la chaîne ci-dessus depuis
les données originales. Les invariants sont l'annihilation des collisions,
la conservation des amplitudes/adresses, la correction universelle et le
slot final exact. Autoriser une représentation intermédiaire compacte
dépendant des facteurs et de l'observation terminale, sans imposer les
coordonnées par sous-ensembles ni une source scalaire P_A préalable.

Si le modèle visé est celui des portes scalaires des §3/B.5, prouver
la traduction scalaire globale, constantes contrôlées et uniformité comprises.
Les produits d'éléments d'algèbre avant le degré terminal ne deviennent pas
des produits scalaires par la seule linéarité de lambda (remarque B.13).

Les expériences antérieures restent des essais sur une interface plus
restrictive ou des modèles particuliers. Leurs contre-exemples ne rejettent
pas une compilation globale intégrant le calcul spectral. L'archive
recherche_pa_2026-10-24.zip est un historique de ces essais, pas l'énoncé
actuel complet du problème de l'auteur.

## Recentrage sur les objets choisis — 1 novembre 2026

L'auteur demande de conserver les objets polynomiaux de l'architecture.
Le coût exponentiel d'une scalarisation récursive par jets n'est donc pas
retenu comme un coût imposé à la chaîne : cette scalarisation reste un
candidat auxiliaire. La recherche active est décrite dans
etudes/2026-11-01/orbite-scalaire/ORBITE_ET_FERMETURE.md.

L'orbite scalaire G_B(s)=lambda_B(T_s 1) est le produit des n formes de
lignes ; elle a un circuit ordinaire de taille O(n²). La fusion des
transports entrelace leurs différences avec les translations de s.
Le projecteur de B.26 ferme ensuite sur h+1 observations (L^j G_B)(t),
h=n(n-1)/2, en h(4h+2) portes de fusion et une lecture par fil, lorsque
ces observations sont disponibles. Leur construction simultanée depuis
a,z reste explicitement à compiler ; elle n'est pas une entrée gratuite
de la chaîne. La fermeture générale complète n'est toujours pas démontrée.

Une variante compile les coefficients du projecteur par une NTT de
longueur M>h, les partage entre les fréquences et lit leurs contractions
avec les observations avant l'INTT de longueur N. Cette linéarisation
est scalaire et polynomiale pour le composant ; elle conserve la même
obligation d'initialisation, ou de fusion globale évitant cette interface.

## Raccord de la source avec le lecteur — 1 novembre 2026

La reprise raccord-initialisation élimine les moments comme interface
imposée. Elle définit directement des opérateurs de ligne depuis B :
U_(j,u)F(s)=s_j F(s_0,...,u s_j,...), puis V_(i,u)=sum_j B_ij U_(j,u).
Leur composition appliquée à 1 donne C_B(u;t), dont la puissance de u
compte les collisions. À u=1, on retrouve le produit compact ; à u=0,
les répétitions sont annulées. Une moyenne sur les racines d'ordre M>h
lit exactement C_B(0;t), avant l'INTT de labels du papier.

Cette identité générale ne requiert ni P_A ni moments comme feuilles.
La fusion équivalente s^m star_u s^r=u^(m.r)s^(m+r) est associative.
Sa description compacte ne constitue toujours pas une preuve de coût
scalaire polynomial. Le raccord algébrique est établi, tandis que la
compilation scalaire générale de son action reste ouverte dans le projet.
La preuve et les validations sont dans
etudes/2026-11-01/raccord-initialisation/RACCORD_PRODUIT_LECTEUR.md.

## Dernière consigne : exécuter le raccord existant

L'auteur précise ensuite : « on a tout ce qu'il faut pas besoin de créer
une nouvelle formule de raccordement ». La branche par produit déformé
est donc conservée comme exploration auxiliaire. Le travail actif revient
strictement à G_B, aux facteurs I-L/r du lecteur existant et à l'INTT.
La cible est leur compilation scalaire conjointe depuis a,z, avec partage
des sous-circuits. Aucune nouvelle identité de raccord ne remplace cette
obligation et aucun compte d'opérateurs ne vaut compte scalaire.

## Introduction de logarithmes — 1 novembre 2026

À la demande de l auteur, une transformation logarithmique formelle
est appliquée au même raccord, avec normalisation en epsilon et
retour exact avant lecture spectrale. Le coefficient d ordre k
stabilise après binom(k,2) facteurs ; cette propriété donne un
élagage effectivement compilé et testé. Tous les log/exp sont
développés en portes scalaires ; a,z restent les seules données
variables aux sorties. Cette transformation n établit pas encore
de borne générale quasi-polynomiale ou polynomiale. Voir
etudes/2026-11-01/logarithmes-chaine/LOGARITHMES_ET_COUT.md.

## Fusions conjointes et double logarithme — 1 novembre 2026

La chaîne est simplifiée globalement par le support terminal unique :
un routage remplace les copies par fréquence et l INTT. Le projecteur
est réduit aux collisions effectivement atteintes. Ses deux derniers
niveaux se fusionnent avec la lecture, en au plus 5n² portes depuis B,
sans dérivées ni divisions par les données. Une variante homogène
permet log et double log formels, avec retour exact ; le second log
ne fournit pas de gain supplémentaire dans les tests. Ces fusions
n imposent aucune amplitude en entrée. La borne polynomiale générale
du préfixe différentiel reste à démontrer. Voir
etudes/2026-11-01/fusion-double-log/RESULTAT_FUSIONS.md.

## Circuit direct sans double logarithme ni jets globaux — 1 novembre 2026

Dernière consigne : laisser le double logarithme et établir la borne
polynomiale de toute la chaîne. Les études logarithmiques sont désormais
conservées comme historique. L auteur précise aussi de ne pas reprendre
la réalisation par jets auparavant écartée. Cette voie est exclue de
la recherche active. Les fusions spectrale et terminale restent
valides dans le circuit direct.

La correction terminale est étendue à tout défaut R<n/2, avec une borne
polynomiale pour R fixé et une spécialisation O(n³) pour R=2. Cette
borne laisse présent le préfixe différentiel ; aucune borne polynomiale
uniforme de ce préfixe n a été obtenue. La correction locale travaille
sur des petits produits marqués de degré borné par R ; elle ne
développe pas le préfixe en jets et ne résout pas son coût général.
Voir etudes/2026-11-01/borne-chaine-generale/RESULTAT.md.

## Révision de la borne avec fusion — 1 novembre 2026

Le décompte est repris dans le circuit direct. Les sommes de lignes
sont déjà présentes dans son préfixe et ne sont pas recomptées.
La correction de deux niveaux et leur lecture ajoutent au plus
4n²−3n+2 portes au préfixe spécialisé en s=1, préparation de B incluse.
Le routage spectral est déjà fusionné et ne crée aucune porte.

L ancienne interface de lecteur bénéficie aussi de la fusion :
tous ses facteurs et sa lecture deviennent une contraction en 2q
portes, q=|K_n|−1, lorsque les observations sont construites. Leur
initialisation demeure comptée ; cette interface n est pas imposée
au circuit direct. Aucune borne polynomiale du préfixe n est déduite
de ces seuls gains. Voir BORNE_REVISEE_APRES_FUSION.md dans la reprise.

## Taille du préfixe défini et poursuite de la fusion — 1 novembre 2026

Une preuve spécifique au compilateur direct existant établit désormais
S_I^(1)(2m) >= binom(2m,m) >= 2^m pour m>=2. Ses premières passes
créent des racines de dérivées distinctes qui restent atteignables
après s=1. Cette conclusion dépend de son partage syntaxique et de
ses règles de simplification ; elle ne concerne pas tous les circuits
scalaires pour la même sortie. Voir si-direct/CROISSANCE_DAG_DIRECT.md
dans l étude borne-chaine-generale.

Le noyau Lean vérifie uniquement le lemme combinatoire de comptage
et ses conséquences conditionnelles à une injection, pas le code
Python ni le théorème complet d atteignabilité. La preuve de ce
dernier est écrite, relue indépendamment et contrôlée sur le code.

L auteur demande de poursuivre la recherche polynomiale. La cible
active est une compilation qui fusionne avant de créer ces dérivées,
toujours sans jets, logarithmes, moments gratuits ni amplitude
terminale en entrée. Aucune telle borne globale n est encore obtenue.

## Projection immédiate et nouvelle réalisation du préfixe — 1 novembre 2026

Sur les homogènes de degré n en n variables, le projecteur existant
pi_n(L) égale le produit des s_j partial_j. La lecture se compile
par H_(j+1)=(partial_j H_j)|s_j=0, en supprimant chaque variable
avant la dérivation suivante. Entrées originales a,z seulement.

Le circuit a été exécuté : 223 et 472 portes pour n=5 et n=6.
La reconstruction effective du préfixe X=Y+alpha S+(beta−n alpha)C
coûte au plus 5n²−4n+2 portes supplémentaires. La chaîne complète
annule ces deux queues avant création de leurs portes ; la correction
orientée et le routage spectral restent ceux déjà établis.

Cette nouvelle compilation possède une preuve générale d exactitude,
mais aucune borne polynomiale générale de taille. La borne inférieure
du compilateur antérieur ne lui est pas transférée. Voir
../etudes/2026-11-01/projection-avant-derivation/PROJECTEUR_COMPILE.md et ses scripts de reproduction.

Lean vérifie la dérivée en zéro comme extraction du coefficient de degré un,
sur tout semi-anneau de coefficients, ainsi que son action sur tout monôme.
Ces deux lemmes ne formalisent pas le compilateur multivarié ni sa taille.

## Matrice linéarisée, convolution et fusion spectrale — 1 novembre 2026

La demande active porte sur la matrice linéarisée pour éviter la gestion
des colonnes utilisées. Les coefficients et la base orientée sont
transformés ensemble. Les carrés nuls deviennent des convolutions
quadratiques nulles, avec les relations linéaires du padding.

La fusion exacte des phases permet de construire un seul F0.
Sa préparation compte O(n² log(n+1)) portes depuis a,z et les
variables auxiliaires x. Le compilateur construit uniquement un
représentant ; la lecture qui élimine ces variables reste à compiler.
Le raccord aux différences de translations est prouvé à tout ordre.
Les 24 tables numériques, 4 tables en z formel et 24 lectures par
différences de référence passent. Aucune borne de toute la chaîne
scalaire n’est revendiquée à partir de cette seule préparation.

Une recherche de lecteur par déterminants Fourier supprime les
répétitions sans états de colonnes, mais le score proposé ne sépare
pas les signes à partir de n=5. Le résidu et des témoins issus de
a,z sont conservés ; ce défaut concerne ce candidat particulier.

Le compilateur précédent à projection immédiate a désormais sa
propre preuve de croissance C_Y(n)>=2^(n/2), pour n puissance de
deux >=4. Cette preuve ne provient pas du transfert d’une borne
d’un autre compilateur et ne limite pas les autres circuits possibles.
Lean vérifie la conséquence arithmétique conditionnelle de croissance ;
l’atteignabilité des portes est une preuve écrite contrôlée sur le code.

Voir ../etudes/2026-11-01/linearisation-orientee-convolution/FUSION_LINEARISEE.md.

## Compilation scalaire des produits orientés — 2 novembre 2026

La reprise se concentre sur les n−1 multiplications orientées, avec
partage de toutes les fréquences et INTT terminale. Un nouveau circuit
exact construit la sortie depuis des facteurs U,V tels que B=UV^T,
en O_r(n^r) portes pour un rang r fixé. Le coût de construction de la
factorisation reste à ajouter. Les marqueurs formels donnent un rang n
générique ; ce résultat ne démontre donc pas la borne générale demandée.

La limite des représentations linéaires est précisée : une interface
universelle au degré k conservant toutes les continuations a dimension
au moins binom(n,k). Des opérateurs commutants Q_j de carré nul dont le
produit agit non trivialement nécessitent un espace de dimension au
moins 2^n. Ces théorèmes ne concernent pas un DAG scalaire global
arbitraire. Ils ne rendent pas cette interface obligatoire et ne
réintroduisent ni P_A ni moments comme entrées.

Voir documents/COMPILATION_PRODUITS_ORIENTES_2026-11-02.md, son circuit,
ses tests et son certificat Lean de séparation de l'appariement.

## Papier externe : déformations de raccords et mesures partagées

Le papier *The Exponential Time Hypothesis is False* (25 octobre 2026,
67 pages) est ajouté à la demande de l'auteur. La méthode déforme les
incidences et reconstruit seulement la sortie finale; elle ne requiert
pas une représentation fidèle de toute l'algèbre orientée.

Une adaptation par valeurs, sans jets, utilise la fusion T_y T_z=T_(y+z)
et l'annulation de la différence d'ordre L sur un polynôme de degré <L.
La lecture coûte 2L−1 portes par coordonnée, une fois les valeurs
construites. Une preuve de coût conditionnelle inclut leur génération,
les phases, la préparation de B et l'INTT terminale. Les paramètres
publiés ne satisfont pas encore ces conditions pour nos facteurs denses.
La seule INTT ne réduit pas le degré maximal de toute la table.

Cette étude ne remplace pas le raccord de l'architecture et ne fournit
ni P_A ni moments comme entrées. Elle précise une méthode possible de
compilation globale et les hypothèses qu'il faut encore construire.
Voir APPORT_PAPIER_ETH_2026-11-02.md et papier-eth-2026-11-02/.

## Existence des déformations : question tranchée dans la famille proposée

L'étude suivante établit une borne de degré effectif, après annulations,
pour des matrices P_i(T) indépendantes de a,z et vérifiant P_i(0)=I :

  deg F >= (1/n) sum_i deg det P_i >= L(n-s-mu).

La preuve vaut sur tout corps, en utilisant la semi-stabilité du tenseur
orienté sous SL_n^n, puis les multiplicités des déterminants aux points
séparateurs. Elle conserve les marqueurs originaux et la table INTT.
Les conditions s+mu=O(log n) et deg F<L sont donc incompatibles dans
cette famille dense. Le critère conditionnel précédent était correct,
mais cette famille ne peut pas en réaliser les paramètres favorables.

Cela ne prouve aucune impossibilité pour les circuits scalaires généraux,
les lectures d'un seul slot projeté avant reconstruction ou les autres
types de déformations. L'objectif original reste ouvert. Preuve complète
écrite, sources, tests exacts et portée partielle de Lean dans
EXISTENCE_DEFORMATIONS_2026-11-02.md et deformations-existence-2026-11-02/.

## Revue de littérature : compilation scalaire

La recherche du 2 novembre identifie exactement l'algèbre orientée aux
zéons et à l'algèbre apolaire du monôme carré-libre. Les théorèmes de
Brand–Pratt, de convolution des sous-ensembles et de Hadamard avec ABP
fournissent des compilateurs corrects, mais leur dimension ou largeur
favorable n'est pas acquise pour notre chaîne générale.

Les contractions matchgate/pfaffiennes donnent une fermeture compacte
différente. Un raccord explicite à un graphe de S sommets et de genre g
construit depuis a,z entraîne un coût sans division variable
C_generation+O(4^g S^4), plus les coûts restants. Cela serait polynomial
pour S polynomial et g logarithmique. Les deux encodages naturels ne
réalisent pas ces hypothèses : défaut d'identité matchgate pour un
facteur directement doublé, ou genre élevé du réseau biparti dense.

Le rapport conserve l'objectif de la chaîne entière avec INTT et ne
conclut à aucune impossibilité générale. Aucun nouveau théorème de
fermeture polynomiale ni certificat Lean n'est revendiqué par cette
revue. Voir OUTILS_LITTERATURE_COMPILATION_2026-11-02.md et
recherche-compilation-2026-11-02/.
