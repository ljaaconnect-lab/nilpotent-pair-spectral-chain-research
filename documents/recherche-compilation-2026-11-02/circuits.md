# Revue de littérature — compilation par circuits arithmétiques

Date : 2026-11-02. Branche : Baur–Strassen, VSBR, circuits multiplicativement disjoints, ABP et produit de Hadamard. Objet : obtenir un compilateur exact en portes scalaires ordinaires pour les produits orientés, lecteur terminal compris, depuis les entrées originales `a,z`.

## Conclusion de cette branche

Le raccord le plus directement utilisable est le théorème de fermeture du produit de Hadamard non commutatif d'Arvind–Joglekar–Srinivasan. Il fournit effectivement un compilateur polynomial lorsque le filtre des mots possède un petit programme de branchement algébrique (ABP). Une spécialisation aux produits de facteurs linéaires donne ci-dessous un décompte explicite en toutes les portes scalaires, avec coût par fréquence au plus `(2 n² + n) w² + 1`, après préparation des `B_ij`, pour un filtre de largeur `w`.

Ce résultat ne construit pas le filtre de largeur polynomiale qui manque dans notre architecture. Les autres théorèmes examinés transforment un circuit déjà donné ou utilisent une hypothèse de parcimonie. Aucun des résultats lus ne fournit, avec les seules hypothèses actuelles de notre chaîne, la compilation scalaire générale recherchée. Cette phrase délimite la revue effectuée ; elle ne prétend pas exclure un théorème ailleurs dans la littérature ni un autre circuit.

## Sources primaires retenues

| Référence et qualité | Résultat précis | Hypothèse à vérifier pour notre chaîne |
|---|---|---|
| [Baur–Strassen, *The complexity of partial derivatives*, TCS 22 (1983), §4, théorème 2](https://web.vu.lt/mif/s.jukna/tropical/Baur-Strassen.pdf). Article original complet, preuve constructive. | Un programme utilisant A additions/soustractions, S multiplications scalaires et M autres multiplications/divisions donne la fonction et toutes ses premières dérivées avec au plus 2A+M, 2S et 3M opérations respectivement. Coût total ≤4(A+S+M) dans leur convention. | Il faut déjà un circuit scalaire pour la fonction à différencier. Le lecteur de notre produit est une extraction mixte d'ordre n, et non l'ensemble des premières dérivées. |
| [Valiant–Skyum–Berkowitz–Rackoff, *Fast Parallel Computation of Polynomials Using Few Processors*, SICOMP 12 (1983), théorèmes 1–3](https://www.cs.tau.ac.il/~amnon/Classes/2015-PRG/Papers/VSBR83.pdf). Article original complet, quatre pages. | Circuit homogène de taille C : taille O(C³), profondeur O(log C log d). Circuit quelconque de degré réel d : taille O(C³ d⁶). Variante à degré formel D : taille O(C³), profondeur O(log C log D). Construction sans division, valable sur tout corps, et même sur des semi-anneaux. | C doit compter des portes scalaires déjà disponibles. Une multiplication dans l'algèbre nilpotente ne peut pas être comptée comme une seule porte scalaire. |
| [Malod–Portier, *Characterizing Valiant's algebraic complexity classes*, rapport original 2005, lemmes 2, 4, 5](http://denif.ens-lyon.fr/data/complexite_algebrique_lyon/2007/cours/RR2005-44.pdf), version publiée [J. Complexity (2008)](https://doi.org/10.1016/j.jco.2006.09.006). Prépublication des auteurs contenant les constructions. | Taille t et degré formel d donnent un circuit multiplicativement disjoint de taille ≤dt. Un circuit faiblement asymétrique de taille m se transforme en graphe de chemins/ABP à m+1 sommets. Le passage général vers un circuit faiblement asymétrique a une borne de type t^{O(log d)}, pas une borne polynomiale générale en t,d. | Il faut un petit circuit scalaire initial. Le fait qu'un produit de facteurs soit une formule compacte avant application du lecteur ne fournit pas une telle formule après le lecteur. |
| [Arvind–Joglekar–Srinivasan, *Arithmetic Circuits and the Hadamard Product of Polynomials*, FSTTCS 2009, théorèmes 4 et 10](https://drops.dagstuhl.de/storage/00lipics/lipics-vol004-fsttcs2009/LIPIcs.FSTTCS.2009.2304/LIPIcs.FSTTCS.2009.2304.pdf), [version longue, théorèmes 1 et 5](https://arxiv.org/pdf/0907.4006). Article et preuve primaire de la construction. | Sur tout corps, deux ABP non commutatifs de tailles s₁,s₂ donnent un ABP de taille O(s₁s₂) pour leur produit de Hadamard. Un circuit non commutatif de degré polynomial et un ABP donnent aussi un circuit de taille polynomiale pour ce produit. | Il faut un ABP de petite taille pour le filtre exact des mots correspondant à l'orientation et au lecteur. Le théorème concerne les mots non commutatifs ; il ne donne pas gratuitement une fermeture coefficient par coefficient des circuits commutatifs généraux. |
| [Kaski–Koivisto–Nederlof, *Homomorphic Hashing for Sparse Coefficient Extraction*, théorème 13](https://arxiv.org/html/1203.4063). Article original, construction et analyse probabiliste explicites. | Pour un circuit à entrées singleton sur F[Z₂ⁿ], avec caractéristique différente de 2 et support final de taille ≤S, extraction d'un coefficient en O*(S) opérations, avec succès au moins 1/2. | Nécessite une algèbre de groupe appropriée, une borne sur le support avant extraction et une maîtrise de l'erreur. La parcimonie de la sortie après annihilation ne justifie pas à elle seule ces hypothèses. Ne fournit pas directement notre identité déterministe exacte. |
| [Andrews–Wigderson, *Constant-Depth Arithmetic Circuits for Linear Algebra Problems*, version du 22 septembre 2025](https://arxiv.org/html/2404.10839v2), §1.2, définitions 2.1–2.4 et lemmes 2.5, 2.7. Prépublication originale des auteurs, modèle explicite. | Taille polynomiale, profondeur constante pour PGCD, résultant et problèmes de matrices structurées. Les entrées univariées sont données par leurs coefficients ; les degrés comptent dans la taille. Lemme 2.7 : extraction d'un coefficient univarié en O(sd), si circuit initial de taille s et degré d. | Il faudrait une réduction exacte de notre lecteur à un de ces problèmes de dimension et degré polynomiaux. Le modèle général autorise division et sélection par test de nullité. Le lemme 2.5 élimine les sélections si la sortie est une fonction rationnelle formelle ; les divisions restent à traiter. |

Les discussions de complexité étrangère à la demande présentes dans ces articles ne sont pas utilisées ici.

## Raccord concret : produit orienté et filtre ABP

Cette partie est notre spécialisation de la construction de Hadamard, avec décompte des portes ; ce n'est pas un nouveau théorème d'existence du filtre.

Introduisons un alphabet non commutatif `x_1,...,x_n` pour conserver l'ordre des facteurs, et posons

\[
F_f(x)=\prod_{i=1}^n\left(\sum_{j=1}^n B_{ij}\omega^{f d_j}x_j\right).
\]

Le coefficient du mot `x_{j_1}...x_{j_n}` est exactement le produit des amplitudes de ses facteurs. Notons `chi(j_1,...,j_n)` le poids imposé par les règles d'orientation et le lecteur terminal, correction universelle comprise si l'on choisit de l'intégrer dans ce poids.

Le filtre est

\[
G(x)=\sum_{j_1,\dots,j_n}\chi(j_1,\dots,j_n)x_{j_1}\cdots x_{j_n}.
\]

Supposons que `G` ait un ABP de `n+1` couches, de largeur au plus `w`, dont les arêtes portent des formes linéaires à coefficients constants :

\[
\sum_j c_{iuvj}x_j.
\]

Les coefficients `c` doivent être disponibles sans préencoder une amplitude dépendant des entrées. Définissons

\[
A_i^{(f)}(u,v)=\sum_{j=1}^{n}c_{iuvj}\omega^{f d_j}B_{ij}.
\]

Alors la sortie du produit de Hadamard, après substitution `x_j=1`, vaut

\[
Y_f=e_s^{\mathsf T}A_1^{(f)}\cdots A_n^{(f)}e_t.
\]

Cela se compile en portes scalaires en propageant un vecteur de largeur `w`. Aucun produit matriciel n'est traité comme une porte primitive. Chaque matrice n'est qu'une notation pour les connexions scalaires du circuit.

Pour des couches complétées artificiellement à largeur `w` :

- préparation des entrées `A_i` : au plus `n w² (2n−1)` portes, puisque les phases sont des constantes et chaque entrée est une somme de `n` multiples d'amplitudes ;
- propagation des états : au plus `2n w²` portes ;
- correction universelle éventuelle : au plus une multiplication scalaire.

D'où

\[
C_f\le (2n^2+n)w^2+1.
\]

Pour `N≤2n` fréquences,

\[
C_{\mathrm{chaîne}}
\le C_B+2n\bigl((2n^2+n)w^2+1\bigr)+C_{\mathrm{INTT}}.
\]

En particulier, `w≤K n^r` donnerait `C_chaîne=O(n^{3+2r})`, avec `C_B=O(n²)` et la transformée usuelle. **L'hypothèse `w≤K n^r` n'est pas établie ici.** Le produit de Hadamard fournit le raccord et sa borne, pas l'existence du petit filtre.

Le lecteur peut incorporer le slot utile dans `chi`, plutôt qu'exiger une représentation de toute la table. Cette latitude doit être utilisée avant de tenter d'établir une borne sur la largeur ; rien dans le théorème de fermeture ne garantit qu'elle suffise.

## Degré et modèle de coût : précautions indispensables

La préparation des amplitudes

\[
B_{ij}=(1+a_{ij}^2)z^{2^{(i-1)n+j-1}}
\]

se fait avec une chaîne partagée de carrés de `z`. Leur degré élevé ne suffit donc pas à prouver un coût élevé. Deux usages sont licites : compiler d'abord un circuit polynomial en amplitudes indépendantes `B_ij`, puis remplacer ces entrées par leurs circuits depuis `a,z` ; ou conserver explicitement ces sous-circuits partagés pendant la construction. Dans les deux cas, le coût des coefficients doit être compté.

Inversement, déclarer que le produit est de degré `n` en variables auxiliaires ne transforme pas une multiplication de l'algèbre `K[q_1,...,q_n]/(q_1²,...,q_n²)` en multiplication scalaire. Le nombre de coordonnées et la compilation du lecteur restent à traiter.

La variante de VSBR fondée sur le degré formel mérite une précision : elle peut garder une taille O(C³) même si le degré formel est exponentiel, puisque ce degré n'intervient alors que dans la profondeur via son logarithme. L'obstacle à son application directe est l'absence du circuit scalaire initial de taille C, et non une interdiction générale causée par `z`.

Le théorème de Baur–Strassen s'applique aux premières dérivées simultanées. L'itérer `n` fois donne au mieux une borne exponentielle via ce seul argument. Une borne de facteur constant pour un passage ne démontre donc pas une fermeture polynomiale à ordre variable. L'article est formulé sur un corps infini ; la construction par règle de chaîne, sans division lorsque le circuit initial est sans division, fonctionne aussi pour les polynômes formels sur un corps fini. Cette extension ne change pas la question de l'ordre de dérivation.

Les décomptes ABP doivent également inclure les étiquettes d'arêtes. Le nombre de sommets de l'ABP n'est pas à lui seul le nombre de portes si une étiquette contient une longue forme linéaire ou un sous-circuit. La borne explicite ci-dessus compte toutes les `n` contributions de chaque étiquette.

Le résultat récent d'Andrews–Wigderson ne remplace pas un degré `d` par `log d` : la borne O(sd) d'extraction univariée reste linéaire en `d`. Leur modèle de taille compte les fils, donc remplacer un arbre de sommes ou de produits de grande arité par des portes binaires conserve un coût polynomial. Il faut en revanche vérifier séparément l'élimination des divisions, et la caractéristique : leurs résultats sont établis en caractéristique zéro ou suffisamment grande ; par exemple le PGCD de deux polynômes de degré `d` demande une caractéristique au moins `2d+1`. Le retrait des sélections du lemme 2.5 repose sur l'identité rationnelle, valable sur les extensions du corps, et non sur une simple égalité ponctuelle sur un corps fini.

## Traçabilité de la recherche

Compétence Exa Search, fichiers `SKILL.md`, `references/searching.md`, `references/source-quality.md` et `references/patterns-papers.md` lus.

Cinq requêtes distinctes exécutées avec `numResults=10` :

1. Baur–Strassen : article original, premières dérivées, constante de coût.
2. VSBR : réduction de profondeur, taille et degré.
3. Malod–Portier : circuits multiplicativement disjoints, faible asymétrie et ABP.
4. Arvind–Joglekar–Srinivasan : Hadamard non commutatif et extraction.
5. VSBR ciblé : texte original 1983 et énoncé exact du théorème 3.

Les quatre premiers appels ont d'abord été refusés pour absence du champ obligatoire `objective`, non documenté dans l'exemple du skill ; aucun résultat n'avait été reçu. Ils ont été corrigés puis réexécutés.

- `sources_reviewed`, convention du skill additionnant tous les `numResults`, tentatives incluses : **90**.
- Résultats effectivement reçus et inspectés : **50** notices.
- URLs uniques après déduplication exacte de ces notices : **47**.
- Articles primaires retenus dans le tableau : **6**, dont Andrews–Wigderson lu directement sur l'URL transmise par la branche principale, sans recherche Exa supplémentaire.
- Lecture complémentaire non retenue : Gupta–Kamath–Kayal–Saptharishi, ECCC TR13-026, réduction à faible profondeur ; ne change pas l'hypothèse d'un circuit scalaire initial.
- La version longue arXiv de AJS a été lue avec l'outil web après que `web_fetch_exa` n'avait retourné que sa fiche bibliographique ; les pages 3 et 6–7 fournissent les constructions pertinentes.

Ces nombres décrivent l'exécution de la recherche. Ils ne signifient pas que 90 articles distincts ont été lus intégralement.
