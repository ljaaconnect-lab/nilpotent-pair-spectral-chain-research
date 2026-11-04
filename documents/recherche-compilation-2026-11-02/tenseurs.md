# Compilation par contractions, matchgates et représentations reconnaissables

Date : 2 novembre 2026. Branche de la recherche bibliographique sur la compilation globale en portes scalaires des produits orientés. Entrées conservées : a,z et constantes autorisées ; aucune amplitude terminale, matrice de moments ou table exponentielle ne devient une entrée gratuite.

## Résultat utile

L'outil positif le plus proche de notre besoin dans cette branche est la **fermeture des signatures matchgate, suivie d'une contraction par Pfaffiens**. Il traite une contraction globale avec une observation terminale, sans exposer les coordonnées par sous-ensembles. Il donne un vrai contrat de compilation en portes scalaires, y compris sans divisions par des expressions dépendant des données.

Toutefois, il exige des identités algébriques précises et une topologie contrôlée. La chaîne dense actuelle ne satisfait pas automatiquement ces hypothèses. Aucune source examinée ne donne une borne polynomiale générale applicable à nos produits orientés arbitraires par la seule relation q_j²=0, q_iq_j=q_jq_i ou par la présence d'une INTT.

## 1. Contrat positif : certificat matchgate de petit genre

Notons M la taille d'un réseau, en comptant ses sommets et ses ports. Au sommet v d'arité d_v, supposons donnée une signature sous forme canonique de Grassmann :

    T_v(theta) = C_v exp(theta^t A_v theta / 2)
                 integral Dmu exp(mu^t B_v theta).

Les données A_v,B_v,C_v doivent être calculées depuis les entrées originales par un circuit scalaire de coût C_gen. Leur existence abstraite, un accès aux coefficients d'une signature exponentielle ou une normalisation nécessitant des divisions variables ne suffisent pas.

Hypothèses du certificat :

1. Le réseau, son placement sur une surface orientable de genre g et l'ordre des ports sont explicitement donnés et uniformément constructibles.
2. Les paramètres canoniques ont les circuits de génération ci-dessus.
3. La contraction du réseau égale exactement l'observation terminale de la chaîne orientée, correction universelle et phases comprises.
4. Le corps a caractéristique différente de 2 ; les constantes nécessaires sont disponibles. C'est compatible avec le cadre NTT usuel modulo Q impair.

**Compilation sans divisions variables.**

Bravyi, théorème 3, remplace chaque signature canonique d'arité d_v par un gadget planaire de taille O(d_v²), dont les poids sont linéaires en ses paramètres. Le remplacement se fait dans un disque : il conserve le genre du réseau. Posons

    S = O(sum_v (1+d_v²)) = O(M²).

Galluccio–Loebl, théorème 3.10, exprime le polynôme de couplages du graphe ainsi construit comme une combinaison de 4^g Pfaffiens de matrices de taille S. Les orientations et les coefficients sont déterminés par le graphe et son placement, et non par les valeurs a,z. Les identités sont des identités polynomiales ; les coefficients de surface ne nécessitent que des divisions par des puissances de 2, donc par des constantes dans notre corps impair.

Mahajan–Subramanya–Vinay donnent une programmation dynamique pour chaque Pfaffien en O(S^4) opérations d'anneau. Elle utilise additions, soustractions et multiplications, sans division variable, et se déroule en circuit. Les soustractions se traduisent par multiplication par -1 et addition.

On obtient donc le contrat conservateur

    C_scalar <= C_gen + O(4^g S^4)
             <= C_gen + O(4^g M^8).

Pour des arités bornées, S=O(M), et le dernier exposant 8 devient 4. La génération des constantes de la topologie et l'uniformité du certificat restent à contrôler ; elles ne doivent pas dépendre d'une sortie inconnue.

En particulier, si M<=C_M n^a, g<=b log_2 n et C_gen=O(n^c0), alors

    C_scalar = O(n^c0 + n^(8a+2b)),

ou O(n^c0+n^(4a+2b)) pour les arités bornées. La préparation des B_ij et le traitement spectral polynomial s'ajoutent s'ils ne sont pas déjà inclus dans C_gen.

Cette borne est une **conséquence combinée** des trois sources ; elle n'est pas un énoncé mot pour mot d'un article. Elle constitue une cible de preuve précise : produire le certificat global, puis appliquer une compilation déjà démontrée.

**Attention au coût annoncé par Bravyi.** Son théorème 1 énonce, pour v sommets et une coupe planaire de m arêtes fournie,

    O((v+m)^6) + O(m^3) 2^(2g),

et, à degré borné,

    O((v+m)^3) + O(m^3) 2^(2g).

Ce résultat utilise un calcul arithmétique avec éliminations. Pour notre modèle strict de portes +,×, il ne faut pas annoncer sans justification que toutes les divisions variables disparaissent au même coût cubique. Le détour constructif ci-dessus par les gadgets et le Pfaffien sans division fournit une borne polynomiale plus conservatrice, mais adaptée au modèle demandé.

Sources primaires :

- Sergey Bravyi, *Contraction of matchgate tensor networks on non-planar graphs*, théorèmes 1, 2, 3, §4 : https://arxiv.org/pdf/0801.2989
- Anna Galluccio, Martin Loebl, *On the Theory of Pfaffian Orientations. I*, théorème 3.10 : https://www.combinatorics.org/ojs/index.php/eljc/article/download/v6i1r6/pdf/
- Meena Mahajan, P. R. Subramanya, V. Vinay, *A Combinatorial Algorithm for Pfaffians*, §7 et théorème 11 : https://eccc.weizmann.ac.il/report/1999/030/download/

## 2. Pourquoi la double orientation n'est pas automatiquement gaussienne

Cai–Gorenstein caractérisent les signatures matchgate par les identités quadratiques de matchgate, qui incluent la contrainte de parité. Bravyi donne leur représentation canonique compacte. Une simple parité paire et l'utilisation de variables de Grassmann ne suffisent donc pas.

Dans l'encodage direct de notre facteur orienté,

    A_i = sum_j b_j x_j y_j,

prenons seulement deux colonnes. Avec l'ordre (x_1,y_1,x_2,y_2), ses seules coordonnées non nulles sont

    T(1100)=b_1,    T(0011)=b_2.

L'identité matchgate à quatre ports demande

    -T(0000)T(1111) + T(1100)T(0011)
    -T(1010)T(0101) + T(1001)T(0110) = 0.

Elle se réduit ici à b_1 b_2=0, fausse pour les entrées formelles génériques. Dans nos variables d'origine, b_j=B_ij omega^(f d_j), le défaut est un monôme de phase non nul multiplié par

    (1+a_i1²)(1+a_i2²) z^(w_i1+w_i2),

donc il n'est pas identiquement nul.

Autre formulation, en caractéristique impaire : une 2-forme pure de signature matchgate doit être décomposable, tandis que

    (b_1 x_1y_1 + b_2 x_2y_2)^2
       = 2 b_1 b_2 x_1y_1x_2y_2 != 0.

Un changement linéaire inversible des générateurs de Grassmann conserve cette non-décomposabilité. La modulation spectrale, qui multiplie les b_j par des scalaires non nuls, conserve aussi ce défaut. La linéarisation de la base q n'est pas, en général, un changement linéaire des générateurs x,y : elle ne fournit pas à elle seule un théorème matchgate.

**Portée exacte :** ce calcul exclut l'identification directe de chaque facteur doublé à une seule signature gaussienne de cette représentation. Il n'exclut ni une représentation globale différente, ni une somme compacte de signatures, ni un réseau à variables auxiliaires conservant uniquement l'observation terminale. Il ne constitue aucune borne sur les circuits scalaires généraux.

Sources primaires :

- Jin-Yi Cai, Aaron Gorenstein, *Matchgates Revisited*, Theory of Computing 10 (2014), §§2–5 : https://theoryofcomputing.org/articles/v010a007/v010a007.pdf
- Bravyi, équation (2), théorème 2 et invariance sous changement de variables.

## 3. L'autre encodage : facteurs localement matchgate, topologie dense

Il faut distinguer l'échec précédent d'un autre encodage exact. On peut construire un réseau biparti avec un sommet par facteur de ligne, un sommet par colonne, et un indice binaire par incidence. Chaque sommet exige une occupation de poids de Hamming exactement un. Les poids B_ij et phases peuvent être placés sur les incidences.

Les signatures locales EXACT1, pondérées ou non, ont une fonction génératrice linéaire en variables de Grassmann. Ce sont bien des signatures matchgate (Bravyi, discussion suivant son théorème 3 et §4.3). Ici, le défaut est **global** : pour la matrice dense, le graphe d'incidence est K_(n,n).

La formule d'Euler donne pour un placement orientable de ce graphe biparti simple

    g >= (n-2)^2 / 4.

Preuve élémentaire : V=2n, E=n², toute face a au moins quatre côtés ; ainsi F<=E/2 et 2-2g=V-E+F<=2n-n²/2.

La borne 4^g ne devient donc pas polynomiale par l'application directe du théorème de genre à ce réseau. Ce n'est pas un argument de complexité absolu : c'est l'absence de l'hypothèse de petit genre dans cet encodage.

Les gadgets de croisement matchgate ne réalisent pas librement le croisement ordinaire sans signe. Leur signature introduit précisément un signe sur l'occupation double. La correction globale universelle de notre double orientation ne prouve pas que tous ces signes de croisement dépendant des configurations sont corrigés gratuitement.

La piste positive pertinente serait une **transformation globale exacte de réseau**, calculable depuis a,z, qui donne M polynomial et g logarithmique tout en satisfaisant les identités matchgate. La littérature fournit alors le compilateur final. Nous n'avons pas trouvé de théorème produisant cette transformation pour nos facteurs denses génériques.

## 4. Contraction générale à petite largeur : bon contrat, hypothèse manquante

Markov–Shi prouvent une simulation par contraction en

    T^O(1) exp(O(tw(G)))

pour leurs réseaux issus de portes d'arité bornée. Le paramètre fondamental des contractions est la largeur du graphe des arêtes L(G) :

    cc(G) = tw(L(G)).

Leur théorème 4.5 compare cette largeur à tw(G) lorsque le degré est borné. Il est donc incorrect de citer la seule largeur tw(G), sans arité ni dimension des liens, pour un réseau quelconque.

Pour un réseau de taille T, indices de dimension D constante et séquence de contraction de largeur w, le déroulement élémentaire donne un circuit scalaire

    T D^O(w)

après ajout de la génération des tenseurs. Si T est polynomial et w=O(log n), cela donne la borne voulue. Toutes les opérations de contraction sont des sommes et produits ; aucune division variable n'est requise.

Dans le réseau biparti dense ci-dessus, tw(K_(n,n))=n. On peut le voir sans hypothèse externe : les sacs formés des n sommets gauches et d'un sommet droit donnent la borne supérieure n ; contracter n-1 arêtes d'un couplage donne un mineur K_(n+1), d'où la borne inférieure n. Un simple remplacement de sommets par des arbres ou des gadgets qui préserve ce mineur ne ramène donc pas cette largeur à O(log n).

Un DAG de formule qui ressemble à un arbre n'est pas pour autant un réseau de petit coût : il faut compter la dimension de l'objet transporté par chaque fil. Transporter un élément de toute l'algèbre nilpotente dans un lien de dimension 2^n ne satisfait pas l'hypothèse de dimension constante.

Source primaire :

- Igor Markov, Yaoyun Shi, *Simulating quantum computation by contracting tensor networks*, propositions 3.5, 4.2, théorèmes 4.5–4.6 : https://arxiv.org/html/quant-ph/0511069

## 5. Hankel / automates pondérés : test exact d'une fermeture linéaire

Le théorème de Fliess donne, sur un corps K, l'équivalence entre rang fini du Hankel d'une série et représentation linéaire finie. Le rang du Hankel est la dimension minimale. C'est un outil rigoureux pour certifier un espace d'états observable suffisant, plus fin qu'une représentation fidèle de toute l'algèbre.

Si une représentation de dimension r est explicitement calculée depuis les données originales, une lecture alpha M_1 ... M_n beta se compile par vecteurs-matrices en O(n r²) portes scalaires, plus le coût de construction. Il n'est pas nécessaire de multiplier toutes les matrices entre elles.

Cependant, pour la série universelle qui lit le coefficient terminal de produits des q_j, l'appariement

    H(S,T)=lambda(q_S q_T)

sur les sous-ensembles vaut 1 exactement lorsque T est le complément de S, et 0 sinon. Ce sous-tableau est une matrice de permutation de taille 2^n. Au degré k fixé, la restriction entre degrés k et n-k a rang binom(n,k). Le quotient par toutes les continuations reste donc grand dans cette interface universelle.

Ce calcul est un test de la représentation linéaire considérée. Il ne s'applique pas à tout circuit scalaire global dépendant des facteurs et d'une seule lecture. Il ne faut pas transformer l'outil de Fliess en obligation de passer par cette interface.

L'apprentissage spectral et les factorisations approximatives de Hankel ne résolvent pas ce point : notre cible est une identité exacte sur des entrées formelles, et les valeurs du Hankel ne sont pas des données gratuites.

Source primaire directe de l'auteur :

- Michel Fliess, *Séries rationnelles positives et processus stochastiques*, Annales de l'I.H.P. 11 (1975), théorème 2.2 et corollaire, pp. 4–7 : https://www.numdam.org/item/AIHPB_1975__11_1_1_0.pdf

## 6. Synthèse opérationnelle

| Famille | Ce qui fournit réellement une compilation polynomiale | Ce qui manque pour notre chaîne générale |
|---|---|---|
| Matchgate / Pfaffien | Paramètres canoniques depuis a,z, réseau de taille poly(n), genre O(log n), lecteur exact | Certificat global ; le facteur doublé n'est pas localement gaussien et le réseau EXACT1 dense a grand genre |
| Contraction à petite largeur | Tenseurs explicitement générés, dimension des liens contrôlée, largeur O(log n) | Transformation exacte du réseau dense vers cette largeur |
| Hankel / automates pondérés | Représentation observable de dimension poly(n), initialisation incluse | Rang polynomial pour l'interface réellement utilisée ; l'interface universelle a rang 2^n |

Le meilleur outil positif de cette branche est donc un **théorème de compilation conditionnel déjà établi**, avec une cible structurelle précise, plutôt qu'une borne générale déjà applicable. Le travail mathématique nouveau serait de construire le certificat global qui satisfait ses hypothèses. Nous n'avons pas identifié une source supprimant ces hypothèses dans le cadre exact demandé.

## Journal de recherche et qualité

- Outil : Exa, compétences Search et références searching.md/source-quality.md lues.
- 10 appels de recherche : 4 appels avec numResults=8, puis 6 appels avec numResults=5.
- sources_reviewed = 62 selon la convention de la compétence (somme des numResults demandés, et non nombre de publications distinctes entièrement lues).
- 6 travaux primaires retenus, URL dédupliquées ci-dessus. Les versions arXiv et journal du même article ont été regroupées.
- Lecture complémentaire examinée puis remplacée par Fliess comme source de l'énoncé exact : Balle–Panangaden–Precup, LICS 2015, théorème 2, https://www.cs.mcgill.ca/~prakash/Pubs/lics_2015.pdf.
- Qualité : articles de recherche des auteurs des théorèmes, textes complets sur arXiv, journal scientifique, ECCC ou Numdam ; blogs, agrégateurs et sources secondaires non utilisés pour soutenir les conclusions.
- Les contre-tests à quatre ports, les calculs de largeur/genre pour K_(n,n), et la borne combinée C_gen+O(4^g M^8) sont nos applications explicites des théorèmes, distinguées des résultats cités.
- Aucun théorème nouveau de cette note n'est revendiqué comme vérifié dans Lean.

