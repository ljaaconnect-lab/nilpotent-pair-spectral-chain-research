# Élimination adaptative par jets duaux

Ce candidat compile la lecture terminale de la chaîne \(\mathcal Z_Q\)
depuis les entrées originales. Il fournit une récurrence exacte sans
division. Son développement actuel en portes scalaires a un coût
exponentiel explicite ; la fermeture polynomiale générale reste à établir.

## État, mise à jour et lecteur

Pour tout anneau commutatif \(R\), appeler \(L_R(B)\) la somme des poids
des chemins terminaux qui utilisent chaque ligne et chaque colonne une
fois. C'est la spécification de l'observation, jamais une entrée du circuit.
Pour \(B=(\begin{smallmatrix}\alpha&r\\c&D\end{smallmatrix})\), former
dans \(R[\varepsilon]/(\varepsilon^2)\) la matrice plus petite
\(D+\varepsilon cr\). Si sa lecture récursive vaut
\(H_0+\varepsilon H_1\), alors
\[
\boxed{L_R(B)=\alpha H_0+H_1.}
\]
La base est \(L_R([b])=b\). La direction \(\varepsilon\) est nouvelle
à chaque élimination. Aucun pivot n'est inversé.

Preuve. Les chemins qui utilisent l'entrée \(\alpha\) contribuent
\(\alpha L_R(D)\). Chacun des autres utilise exactement une entrée
\(r_j\) de la première ligne et une entrée \(c_i\) de la première
colonne. Il correspond, de façon bijective, à un chemin sur la matrice
résiduelle dont l'unique facteur perturbé est
\(\varepsilon c_i r_j\). Le coefficient de \(\varepsilon\) rassemble
ces chemins une fois chacun. Les produits contenant deux perturbations
sont nuls. L'identité est donc valable sur tout anneau commutatif ;
l'induction s'applique aussi aux anneaux duaux successifs.

## Chaîne entière

Le compilateur prépare
\(B_{ij}=(1+a_{ij}^2)z^{2^{in+j}}\) par carrés successifs. À chaque
fréquence \(f\), il forme d'abord
\(B^{(f)}_{ij}=\omega^{fd_j}B_{ij}\), puis applique l'élimination
ci-dessus à cette matrice. L'identité terminale de
[RACCORD_NTT.md](../fusion-ntt/RACCORD_NTT.md) identifie cette lecture à
\(\lambda_B[\prod_j(T_{\omega^{fd_j}e_j}-I)1]\).
Une véritable INTT radix 2 agit ensuite sur toutes les fréquences.
La sortie est le coefficient de \(\widetilde\Omega\) dans
\(\mathcal Z_Q\) : la correction de signe universelle est déjà incluse.
Le circuit ne reçoit que \(a_{ij}\) et \(z\), avec les paramètres
structurels \(n,d_j,Q,\omega\).

## Coût réellement compilé

Un élément de profondeur duale \(k\) est un tuple de \(2^k\)
scalaires. Sans simplification, une addition coûte \(A_k=2^k\) portes,
et une multiplication coûte \(M_k=2\cdot3^k-2^k\), puisque
\(M_0=1\) et \(M_{k+1}=3M_k+A_k\).
Le cœur à dimension \(n\ge1\) coûte exactement
\[
\begin{aligned}
G_n&=\sum_{k=0}^{n-2}
 \left(((n-k-1)^2+1)M_k+A_k\right)\\
&=4\cdot3^{n-1}-3\cdot2^n+n+1.
\end{aligned}
\]
La somme vide donne bien \(G_1=0\). Chaque produit par une constante
est facturé. Pour \(N=2^{\lceil\log_2(n+1)\rceil}\), le coût total est
\[
\boxed{4n^2-1+N(n^2+G_n)+2N\log_2N+N.}
\]
Il comprend la préparation, les phases avant chaque élimination,
tous les jets dépliés, la lecture et l'INTT. La taille des constantes
et le coût binaire des opérations de corps ne sont pas assimilés à
des portes supplémentaires : il s'agit du modèle de portes scalaires
demandé.

La prochaine fermeture à construire doit compresser simultanément
l'état résiduel et le lecteur composé des jets, en préservant les
interactions mixtes. Le présent circuit donne un état, une mise à jour
et une lecture précis sur lesquels travailler, sans dissimuler leur coût.

## Vérification reproductible

Exécuter `python verify_schur.py`. Le vérificateur compare les sorties et
les fréquences à une expansion indépendante pour deux entrées par ordre
\(1\le n\le7\), puis compare les polynômes formels en \(z\) pour
\(n\le5\), sans réduction des exposants. L'expansion de vérification
n'est jamais appelée par le compilateur. Le rapport `validation.json`
enregistre les entrées, les coûts mesurés et les empreintes des sources.
Ces tests finis ne constituent pas une preuve de fermeture polynomiale.
