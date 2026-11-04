# Borne générale démontrée pour le compilateur partagé

Cette note analyse le compilateur gelé `shared_operator_dag.py`, sans
changer le produit \(G_B\), le projecteur \(\pi_n(L)\), ni la lecture.
Elle donne une borne valable à tout ordre. **Cette borne n'est pas
polynomiale en \(n\)** ; aucune borne polynomiale ne se déduit des seuls
comptages prouvés ci-dessous. Il ne s'agit pas d'une borne inférieure
pour ce compilateur, et encore moins pour les autres circuits possibles.

## 1. Coût d'une dérivation première et seconde partagées

Soit \(F\) donné par un DAG scalaire comportant \(S\) portes actives
\(+\) et \(\times\). Fixer une variable \(s_j\). La mémoïsation
de la dérivée par paire (nœud, variable) ne dérive qu'une fois chaque
nœud nécessaire.

Pour une addition, la première et la seconde dérivées demandent chacune
au plus une addition. Pour un produit \(F=UV\), écrire

\[
F'=U'V+UV',
\qquad
F''=(U''V+U'V')+(U'V'+UV'').
\]

La première ligne ajoute au plus trois portes au-delà des dérivées
des enfants. La seconde ajoute au plus six portes : trois produits
distincts et trois additions, car le nœud \(U'V'\) est partagé.
Les dérivées des enfants sont déjà comptabilisées à leurs propres
nœuds. Les entrées et les constantes ne créent aucune porte de dérivée.

Une induction topologique sur le DAG donne donc :

\[
\boxed{\text{portes nouvelles pour }(\partial_jF,\partial_j^2F)
       \ \le\ 9S.}
\]

Le compilateur peut faire mieux grâce aux zéros, aux uns, aux constantes,
aux bornes de degrés et aux nœuds déjà présents dans le cache. Toutes
ces opérations diminuent la création ou l'accessibilité des portes ;
elles n'invalident pas la borne supérieure. Les partager entre plusieurs
variables ne peut pas augmenter le total \(9nS\).

## 2. Récurrence des facteurs du lecteur existant

Soit \(S_r\) le nombre de portes actives du DAG de

\[
H_r=\prod_{k=1}^{r}(I-L/k)G_B,
\qquad 0\le r\le h=\binom n2,
\]

avant substitution des phases. Ce nombre inclut la préparation des
\(B_{ij}\) depuis \(a,z\). La source satisfait

\[
S_0\le(4n^2-1)+(2n^2-1)=6n^2-2.
\]

Après les dérivées secondes, former
\(L(H_r)=\tfrac12\sum_j s_j^2\partial_j^2H_r\)
ajoute au plus \(3n\) portes : \(n\) carrés, \(n\) produits,
\(n-1\) additions et un produit par \(1/2\). Le produit par
\(-1/(r+1)\) puis l'addition de \(H_r\) ajoutent deux portes.
Il en résulte la récurrence démontrée

\[
\boxed{S_{r+1}\le(9n+1)S_r+3n+2.}
\]

Poser \(a_n=9n+1\), \(b_n=3n+2\). Par induction sur \(r\),

\[
\boxed{
S_r\le a_n^r(6n^2-2)
      +b_n\frac{a_n^r-1}{9n}.
}
\]

La fraction désigne la somme géométrique entière
\(1+a_n+\cdots+a_n^{r-1}\), pas une division exécutée dans le
circuit de données. Pour \(r=0\), cette somme est nulle.

Cette borne est volontairement supérieure au coût observé : elle ne
suppose aucune identité supplémentaire entre dérivées distinctes. Elle
ne transforme pas en théorème le ralentissement empirique de la
croissance après les premiers facteurs à \(n\) fixé.

## 3. Chaîne entière et observation finale

Pour chaque fréquence, substituer les constantes \(s_j=\omega^{fd_j}\)
ne crée pas plus de portes que le DAG substitué. Même en ignorant tout
partage entre fréquences, les \(N\) sorties spectrales se compilent
donc avec au plus \(NS_h\) portes. L'INTT radix-2 ajoute au plus
\(2N\log_2N+N\) portes suivant la convention du projet. Ainsi

\[
\boxed{
\begin{aligned}
C(n,N)\le{}&N\left[
(9n+1)^h(6n^2-2)
+(3n+2)\frac{(9n+1)^h-1}{9n}
\right]\\
&+2N\log_2N+N.
\end{aligned}}
\]

Les paramètres admissibles \(Q,\omega,N\) et les labels sont fournis,
avec \(Q>\max(2,h)\) et une racine d'ordre exact \(N\), puissance
de deux. Une fois ces paramètres fournis, les puissances et inverses
de constantes nécessaires ont une préparation polynomiale. Aucune
génération uniforme polynomiale des premiers ou des racines n'est
revendiquée. La borne ci-dessus compte les portes dépendant des données
et la transformée ; la préparation des constantes reste séparée.

## 4. Ce que cette preuve laisse ouvert

Une borne polynomiale générale exigerait un invariant supplémentaire
qui contrôle les **portes nouvelles non partagées**, par exemple une
borne \(S_{r+1}-S_r\le p(n,r)\) avec \(p\) polynomial, établie
pour les DAG réellement produits. La présence de \(h+1\) observations
ou de \(h\) facteurs du lecteur ne fournit pas cet invariant.

Le compilateur actuel ne normalise pas ses nœuds modulo toutes les
identités différentielles de \(G_B\). Sa mémoïsation identifie les
opérations structurellement égales et les mêmes dérivées de nœuds ;
elle ne permet donc pas, à elle seule, de remplacer la récurrence
prouvée par une récurrence additive polynomiale.

**Conclusion précise :** la correction algébrique du compilateur et
une borne générale de sa chaîne entière sont démontrées par les
inductions précédentes. La borne générale polynomiale demandée ne
l'est pas. Les essais finis et la forme compacte du lecteur ne sont
pas utilisés comme substituts à cette preuve manquante.
