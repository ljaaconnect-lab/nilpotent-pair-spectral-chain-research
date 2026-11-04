# Borne affinée du DAG différentiel partagé

Date : 2026-11-03.

## Portée

Cette note analyse le programme existant
[shared_operator_dag.py](../../etudes/2026-11-01/raccord-initialisation/spectral/reprise-globale/shared_operator_dag.py).
Elle ne change ni le générateur, ni le projecteur, ni le lecteur. Elle n'introduit aucun tableau de jets dans le compilateur.

Le décompte porte sur les portes scalaires binaires \(+\) et \(\times\), avant la substitution des phases. Les simplifications par zéro/un, les constantes et l'internement sont ceux du code. Le budget logiciel d'allocation est supposé suffisamment grand pour achever la construction ; il n'est pas une borne mathématique.

Le résultat est une borne supérieure du circuit construit. Il ne donne aucune borne inférieure et **ne démontre pas une taille polynomiale en \(n\)**.

## Résultat

Pour \(n\ge2\), après \(r\) facteurs du projecteur, poser
\[
B_{n,r}=6n^2-2+r(3n+2),
\qquad
A_n=\sum_{k=0}^{n} n^k(2^{k+1}-1).
\]
Le nombre \(S_r\) de portes actives du graphe satisfait
\[
\boxed{S_r\le B_{n,r}A_n\le4B_{n,r}(2n)^n.}
\]

En particulier, avec \(h=\binom n2\),
\[
\boxed{S_h=O\!\left(n^3(2n)^n\right)=2^{O(n\log(n+1))}.}
\]
Cette borne améliore le majorant local itéré \((9n+1)^h\). Elle est polynomiale dans le nombre de facteurs \(r\) à \(n\) fixé, mais exponentielle en \(n\log n\) dans la borne affichée.

Le cas \(n=1\), sans facteur, se traite directement par le générateur initial.

## 1. Portes sources et homogénéité syntaxique

Appelons **portes sources** les portes arithmétiques demandées hors des appels récursifs à la méthode derivative, avant substitution spectrale. Il est permis de compter plusieurs demandes du même nœud : cela ne peut qu'augmenter le majorant.

La préparation de \(B_{ij}\) et du générateur
\[
G_B(s)=\prod_i\sum_jB_{ij}s_j
\]
demande au plus \(6n^2-2\) portes sources.

Chaque étape
\[
H\longmapsto H-\frac1a L(H),
\qquad L=\frac12\sum_j s_j^2\partial_j^2
\]
ajoute hors dérivation au plus \(3n+2\) portes : \(n\) carrés, \(n\) produits par les dérivées secondes, \(n-1\) additions, une multiplication par \(1/2\), puis un produit par \(-1/a\) et une addition. D'où \(B_{n,r}\).

Toutes les portes sources sont syntaxiquement homogènes en \(s\), de degré au plus \(n\). Les amplitudes et les marqueurs ont degré zéro en \(s\), les lignes degré un, et le produit complet degré \(n\). Une dérivée abaisse le degré d'une unité lorsqu'elle n'est pas nulle ; les facteurs \(s_j^2\) le rétablissent avant la somme définissant \(L\). Les carrés seuls ont degré deux, autorisé puisque \(n\ge2\).

Il s'agit d'une homogénéité de la construction, pas d'un degré obtenu après des annulations hypothétiques. La dérivation d'un graphe de degré zéro en \(s\) s'arrête exactement dans le code : tous ses majorants de degrés par variable sont nuls. Ainsi un mot de plus de \(n\) dérivations appliqué à une source ne crée pas de nouvelle porte arithmétique utile.

## 2. Gabarit local de Leibniz

Fixons une porte source \(g\) et un mot ordonné \(w=(j_1,\ldots,j_k)\) de dérivations.

Pour compter les portes propres à cette source, traitons provisoirement ses deux opérandes et toutes leurs dérivées comme des fils atomiques. Il s'agit seulement d'un dispositif de preuve : leurs vrais sous-circuits restent comptés, à leur provenance respective.

Si \(g=u+v\), le gabarit local de \(\partial_wg\) contient au plus une addition.

Si \(g=uv\), la règle de Leibniz non regroupée donne \(2^k\) termes, un pour chaque affectation de chaque lettre de \(w\) au premier ou au second opérande. Les lettres affectées à un opérande conservent leur ordre. Chaque terme est un produit
\[
(\partial_{w_1}u)(\partial_{w_2}v).
\]
L'arbre binaire de somme possède au plus \(2^k-1\) additions. Le nombre de positions arithmétiques du gabarit est donc au plus
\[
2^k+(2^k-1)=2^{k+1}-1.
\]
Cette présentation ne regroupe pas les mots mixtes qui commutent : le facteur \(n^k\) ci-dessous les compte tous séparément.

Le programme suit exactement les règles de somme et de produit qui produisent ces gabarits. Les zéros, les uns et les constantes peuvent supprimer des positions ; l'internement peut en identifier. Aucune de ces opérations n'en ajoute.

## 3. Couverture des dérivées de nœuds intermédiaires

Le point nécessaire au comptage est que les dérivées des nœuds déjà produits ne doivent pas être traitées comme autant de nouvelles sources.

L'invariant porte sur **l'union de toutes les positions des gabarits non simplifiés**, et pas seulement sur les résultats actifs. Il couvre donc aussi les sous-expressions calculées puis rendues inaccessibles par une simplification ultérieure.

Chaque porte créée dans un appel à derivative possède une provenance : elle est une position interne d'un gabarit local \((g,w)\), pour une porte source antérieure \(g\). Toute nouvelle porte arithmétique propre à ce gabarit est syntaxiquement homogène de degré \(\deg(g)-|w|\). Si une simplification par zéro ou un renvoie un ancien opérande, celui-ci conserve sa provenance antérieure : son mot n'est pas réinitialisé. Les constantes nouvelles n'ajoutent aucune porte arithmétique.

Cette affirmation se prouve par induction sur les appels récursifs :

1. Dériver une porte source crée les positions de son gabarit de longueur un ; les dérivées de ses opérandes sont traitées récursivement.
2. Si le nœud dérivé est déjà une position du gabarit \((g,w)\), dériver cette position donne une sous-expression du gabarit **non simplifié** \((g,wj)\), même si cette sous-expression disparaît de son résultat réduit. En effet, différencier le gabarit complet visite chacune de ses positions de somme ou de produit et applique les mêmes règles.
3. Les dérivées des fils atomiques relèvent, à leur tour, de la provenance de ces fils. Un fil déjà dérivé prolonge son mot antérieur ; il ne devient pas une nouvelle source. Pour les opérandes d'une source, les nœuds sont antérieurs à cette source ; pour un fil déjà dérivé, sa provenance retourne à sa source antérieure. L'induction sur les appels et ces références antérieures est donc bien fondée. La longueur totale du mot reste contrôlée par le degré de sa propre source.
4. Une porte ajoutée hors dérivation est comptée comme nouvelle source ; cela couvre précisément les multiplications par \(s_j^2\) qui rétablissent le degré.

Pour une paire \((g,w)\) fixée, les fils représentant les dérivées ordonnées de ses opérandes sont déterminés par le cache (idx,j). Une position donnée du gabarit ne peut donc créer plusieurs nœuds arithmétiques différents au fil des demandes : une nouvelle demande retrouve ses prédécesseurs et son nœud interné.

L'ordre canonique des deux prédécesseurs, fixé dans add et mul par leurs identifiants, ne change pas ce raisonnement. Il ne permute pas l'ordre des lettres d'un mot de dérivation ; il partage seulement des sommes ou produits identiques par commutativité.

Les appels dont la dérivée s'annule syntaxiquement n'augmentent pas ce budget. Dans ce code, les zéros sont éliminés et les opérations entre constantes sont repliées. Les positions non simplifiées sont déjà comptées avant ces suppressions. Dès que \(|w|>\deg(g)\), une nouvelle porte propre à \((g,w)\) aurait un degré syntaxique négatif, impossible ; les dérivées arrivées aux constantes s'arrêtent. Cela justifie la coupure à \(|w|\le n\) pour l'union complète des portes créées, et non seulement pour les racines finales.

Il suffit donc de compter tous les gabarits de toutes les sources et tous les mots de longueur au plus \(n\). Il existe \(n^k\) mots de longueur \(k\), d'où
\[
S_r\le B_{n,r}\sum_{k=0}^{n}n^k(2^{k+1}-1).
\]

## 4. Simplification de la borne et raccord spectral

Comme \(n\ge1\),
\[
A_n\le2\sum_{k=0}^{n}(2n)^k\le4(2n)^n.
\]
Avec \(r=h=O(n^2)\), on a \(B_{n,h}=O(n^3)\), ce qui donne le résultat annoncé.

Pour le programme qui conserve toutes les fréquences, chaque substitution recopie au plus une porte par porte active. La préparation de \(B\) est partagée, mais même sans exploiter ce gain :
\[
C(n,N)\le
N B_{n,h}A_n+2N\log_2N+N.
\]
Cette expression couvre les substitutions et l'INTT radix deux déjà utilisées.

Si la fusion spectrale du projet est appliquée, une seule substitution \(s=1\) et le routage du fil final suffisent. Le facteur \(N\) de répétition disparaît alors :
\[
C_{\mathrm{fusion}}(n)\le B_{n,h}A_n.
\]
Cette dernière borne concerne la variante utilisant la fusion spectrale démontrée, pas le graphe non simplifié qui émet toutes les copies.

## 5. Corollaire pour la chaîne réellement linéarisée

Le programme [linearised_full_chain.py](linearised_full_chain.py) utilise les coordonnées de Fourier \(x_r\), \(0\le r<N\), et les \(n\) dérivations
\[
\delta_jx_r=\omega^{rj}\qquad(0\le j<n).
\]
Les dérivées des feuilles sont des constantes fournies, sans porte arithmétique nouvelle. Il reste donc \(n\) lettres possibles dans les mots de dérivation, et non \(N\).

Poser
\[
q_j(x)=\frac1N\sum_{r<N}\omega^{-rj}x_r,\qquad
L_x=\frac12\sum_{j<n}q_j(x)^2\delta_j^2.
\]
Les relations \(\delta_jq_k=\delta_{jk}\) pour les indices actifs suivent de l'orthogonalité Fourier. Le code applique ainsi le projecteur conjugué dans les coordonnées linéarisées, puis remplace \(x_r\) par \(\sum_{j<n}\omega^{rj}\), ce qui correspond à \(q_j=1\).

Avec \(\ell=\log_2N\), la préparation du représentant \(F_0\), coefficients compris, est majorée par
\[
P(n,N)=4n^2-2+2nN\ell+3nN.
\]
La préparation explicite des \(q_j(x)\) ajoute au plus \(2nN\) portes. Chaque facteur ajoute ensuite au plus \(3n+2\) portes sources. Le nombre pertinent est donc
\[
B^{\mathrm{lin}}_{n,N,r}=P(n,N)+2nN+r(3n+2).
\]
Toutes ces sources sont homogènes de degré au plus \(n\) en \(x\) pour \(n\ge2\). Les mêmes gabarits, la même provenance et la même coupure des mots donnent
\[
\boxed{S^{\mathrm{lin}}_r
\le B^{\mathrm{lin}}_{n,N,r}A_n.}
\]
Ce nombre peut majorer conjointement la racine projetée et les \(q_j\), comme dans le décompte du programme.

Le programme construit ensuite une seule lecture \(Y\), la multiplie par les phases, puis appelle une vraie INTT radix deux. La préparation des \(N\) valeurs de phase fois \(Y\) coûte au plus \(N\) portes et l'INTT au plus \(2N\log_2N+N\). Par conséquent
\[
\boxed{
C^{\mathrm{lin}}_{\mathrm{INTT}}(n,N)
\le B^{\mathrm{lin}}_{n,N,h}A_n+2N\log_2N+2N.}
\]
La sortie avec routage spectral simplifié relie \(Y\) au seul indice utile et zéro ailleurs ; ce câblage n'ajoute aucune porte :
\[
\boxed{C^{\mathrm{lin}}_{\mathrm{routage}}(n,N)
\le B^{\mathrm{lin}}_{n,N,h}A_n.}
\]
Pour les paramètres du programme \(n<N\le2n\), ces deux bornes sont de type \(2^{O(n\log(n+1))}\). Les portes sont toutes scalaires et les seules entrées d'exécution sont \(a,z\). Le cas \(n=1\) est direct et n'applique aucun facteur du projecteur.

## 6. Ce que l'affinement établit

La multiplication du coût par \(9n+1\) à chaque facteur constitue un majorant local correct mais trop grossier pour compter les dérivées déjà partagées. Un décompte global par sources et mots de dérivation évite de payer cette même fermeture à chaque étape.

La borne affichée contient toujours le facteur \(A_n\). La présence d'une borne \(2^{O(n\log n)}\) ne permet ni de conclure à une taille polynomiale, ni de conclure à une croissance exponentielle nécessaire. Elle améliore une borne supérieure générale pour le compilateur existant.

Cette preuve est écrite. Elle n'a pas été formalisée dans Lean et ne prétend pas certifier le code par extraction formelle. Elle ne s'appuie sur aucun ajustement empirique des tailles finies.

