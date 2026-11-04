# Compilation scalaire du produit et du lecteur existants

Cette étude conserve exactement le raccord de
`orbite-scalaire/ORBITE_ET_FERMETURE.md`. Elle ne propose pas une nouvelle
formule de raccord. Le programme compile effectivement le produit compact,
l'action composée du projecteur et la lecture spectrale en un DAG de
portes scalaires ordinaires. **Aucune borne polynomiale générale de ce DAG
n'est établie.**

## 1. Opérations compilées

Les seules entrées de données sont \(a,z\). Les paramètres admissibles
de champ, les racines et les labels sont fournis. La source reste

\[
B_{ij}=(1+a_{ij}^2)z^{2^{in+j}},\qquad
H_0(s)=G_B(s)=\prod_i\left(\sum_jB_{ij}s_j\right).
\]

Le compilateur crée les carrés successifs de \(z\), puis les \(B_{ij}\)
et le produit des formes de lignes. Il applique ensuite, sans changer
le lecteur,

\[
H_r=H_{r-1}-r^{-1}L(H_{r-1}),\quad
L=\frac12\sum_j s_j^2\partial_j^2,
\quad 1\le r\le h=\binom n2.
\]

À la fin seulement, il remplace les variables \(s_j\) par
\(\omega^{fd_j}\), pour chaque fréquence \(f\), et émet les
papillons de l'INTT. Il n'utilise ni table de moments, ni valeur terminale
fournie, ni table d'occupations, ni grille de quadrature.

## 2. Partage réel du calcul

Chaque nœud est une constante, une entrée, une addition ou un produit.
Un dictionnaire unique identifie les opérations structurellement égales,
avec ordre canonique des deux opérandes commutatifs. Les zéros, les uns
et les opérations entre constantes sont simplifiés.

La dérivée d'un nœud \(v\) par rapport à \(s_j\) est mémorisée par
la paire \((v,j)\). La même dérivée réutilisée par plusieurs facteurs
du lecteur pointe donc vers les mêmes fils. Une borne du degré en chaque
\(s_j\) permet de retourner immédiatement zéro lorsque ce degré est
nul. Les degrés sont des métadonnées de compilation ; ce ne sont pas des
portes exécutées sur les données.

Les règles de compilation sont exactement

\[
\partial_j(F+G)=\partial_jF+\partial_jG,\qquad
\partial_j(FG)=(\partial_jF)G+F(\partial_jG).
\]

Elles créent uniquement des portes \(+\) et \(\times\). Aucune
porte « dériver », « substituer », « appliquer \(L\) » ou « lire un
coefficient » ne reste dans le circuit exécuté. La différentiation et
la substitution sont des opérations du compilateur qui produisent ce
circuit explicite.

Le décompte final parcourt les nœuds accessibles depuis toutes les sorties.
Les essais de dérivation devenus inutiles ne sont donc pas comptés comme
portes du circuit final. Ils restent comptabilisés séparément dans les
allocations du compilateur et la taille de son cache.

## 3. Correction du schéma

L'induction sur les nœuds établit que le DAG retourné par la fonction
`derivative(v,j)` représente bien \(\partial_jv\). La borne de degré
zéro autorise la simplification utilisée, et les autres cas appliquent
la linéarité et Leibniz. Deux applications donnent \(\partial_j^2v\).
La fonction `L` représente donc l'opérateur du lecteur existant.

L'induction sur \(r\) donne alors

\[
H_r=\left(\prod_{k=1}^{r}(I-L/k)\right)G_B.
\]

La substitution spectrale est effectuée après cette action : elle ne
remplace jamais une dérivation du polynôme par une dérivation de sa
valeur scalaire. L'INTT finale est la transformée déjà retenue par le
projet, avec la correction universelle \(\widetilde\Omega\).

Cette preuve écrite concerne le schéma de compilation. Aucune nouvelle
certification Lean du programme Python n'est revendiquée. Le programme
possède un plafond explicite d'allocation pour contrôler les ressources ;
dépasser ce plafond n'est pas présenté comme une impossibilité mathématique.

## 4. Portes observées et vérification

Les constantes admissibles de l'essai sont \(Q=97\),
\(N=2^{\lceil\log_2(n+1)\rceil}\), une racine d'ordre \(N\) obtenue
à partir de 5, et \(d_j=j\). Le compilateur vérifie l'ordre exact et
\(Q>\max(2,h)\). Cette expérience ne revendique pas un algorithme de
génération uniforme des premiers ou des racines.

| \(n\) | Source + projecteur, avant phases | Chaîne scalaire complète |
|---:|---:|---:|
| 1 | 4 | 8 |
| 2 | 34 | 65 |
| 3 | 178 | 434 |
| 4 | 1 020 | 4 441 |
| 5 | 8 613 | 35 131 |
| 6 | 62 578 | 242 471 |

Ces nombres sont les portes actives réellement présentes. Ils ne sont
ni une interpolation de complexité, ni une borne polynomiale générale.
À ordre \(n\) fixé, le cache partage une grande partie des dérivées
entre facteurs successifs du lecteur ; cela ne borne pas uniformément
leur nombre lorsque \(n\) varie.

`verify_shared_operator_dag.py` passe 48 tables numériques, huit pour
chacun des ordres \(1\) à \(6\). Huit autres tables, deux par ordre
de \(1\) à \(4\), exécutent exactement le même DAG sur des polynômes
en \(z\) et comparent chaque exposant de chaque slot. Les exposants de
\(z\) ne sont pas réduits modulo \(Q-1\) dans ces vérifications
formelles. Les énumérations de choix de colonnes et de permutations
appartiennent uniquement aux références indépendantes de test.

Le rapport `shared-operator-dag-validation.json` conserve les empreintes
des deux sources, les comptes après chaque facteur, les allocations et
les résultats. Par défaut, relancer le vérificateur laisse le rapport
inchangé ; `--write-report` le régénère.

**Résultat livré :** une compilation scalaire concrète et partagée du
raccord existant, avec une vérification directe depuis \(a,z\).
La fermeture polynomiale générale demandée reste à démontrer pour cette
compilation ou pour une autre organisation du même calcul.
