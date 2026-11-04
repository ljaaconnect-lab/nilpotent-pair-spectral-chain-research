# Conservation générale de la valeur par la lecture native

4 novembre 2026. On conserve l'orientation, le changement de base de
Fourier, les relations de convolution et de padding, la fusion des
fréquences et l'INTT. L'unité ajoutée au cœur partagé est celle de
`compile_with_unit.py`. Aucun résultat recherché n'est fourni en entrée.

## 1. Construction de la lecture dans les coordonnées de l'architecture

Soit R=F_Q[a,z], avec n>=1, n<=N, N inversible et omega d'ordre N.
Notons P_x=R[x_0,...,x_(N-1)] et P_q=R[q_0,...,q_(n-1)] les anneaux
polynomiaux avant passage au quotient. Les symboles q de P_q sont les
coordonnées d'orientation déjà présentes, et ne sont pas de nouvelles
entrées du programme.

Le changement de base définit un morphisme R-linéaire et multiplicatif :

\[
\Phi:P_x\longrightarrow P_q,
\qquad \Phi(x_r)=\sum_{j<n}\omega^{rj}q_j.
\]

Pour q_* = q_0...q_(n-1), définissons explicitement

\[
\boxed{\Lambda(F)=\gamma_n[q_*]\Phi(F).}
\tag{1}
\]

La notation [q_*] désigne le coefficient de ce monôme. Elle définit
mathématiquement la lecture, sans la compter comme une porte scalaire.
La construction utilise le changement de base de notre architecture.

## 2. La lecture annule toutes les relations, y compris leurs multiples

Les générateurs de l'idéal natif I sont

\[
g_s=\frac1N\sum_r x_rx_{s-r},
\qquad h_j=\frac1N\sum_r\omega^{-rj}x_r\quad(n\le j<N).
\]

L'orthogonalité donne

\[
\begin{aligned}
\Phi(g_s)
&=\sum_{j,l<n}\omega^{sl}q_jq_l
  \left(\frac1N\sum_r\omega^{r(j-l)}\right)\\
&=\sum_{j<n}\omega^{sj}q_j^2,
\qquad \Phi(h_j)=0\quad(n\le j<N).
\end{aligned}
\tag{2}
\]

Soit maintenant A un polynôme quelconque de P_x. Chaque monôme de
Phi(A) q_j^2 a un exposant au moins 2 en q_j. Le monôme q_* a exposant
exactement 1 en chaque q_j. Donc

\[
[q_*]\bigl(\Phi(A)q_j^2\bigr)=0.
\]

Par (2), Lambda(A g_s)=0 et Lambda(A h_j)=0. Par additivité, Lambda
annule toute combinaison polynomiale des générateurs, c'est-à-dire
l'idéal entier I. Ainsi

\[
\boxed{F-F'\in I\ \Longrightarrow\ \Lambda(F)=\Lambda(F').}
\tag{3}
\]

Ceci prouve que la lecture est bien définie sur le quotient et que
toute normalisation exacte dans ce quotient conserve la valeur lue.
On ne suppose pas un certificat de normalisation scalaire sur les
fils inchangés pour obtenir (3).

## 3. Calibration de l'orientation et raccord depuis les entrées

Pour j<n, posons pi_j(x)=N^{-1} sum_r omega^(-rj) x_r. On a
Phi(pi_j)=q_j. Le label terminal possède le représentant

\[
\Omega_x=\gamma_n\prod_{j<n}\pi_j(x),
\qquad \Phi(\Omega_x)=\gamma_n q_*.
\]

Comme gamma_n^2=1, (1) donne Lambda(Omega_x)=1. Puisque n>=1,
q_* n'est pas le monôme constant, donc Lambda(1)=0. La lecture est
bien celle du coefficient suivant le label Omega retenu dans le projet.

Les coefficients C_ir et les formes L_i sont ceux du circuit existant :

\[
C_{ir}=\frac1N\sum_{j<n}B_{ij}\omega^{rj},
\qquad L_i=\sum_r C_{ir}x_{-r}.
\]

En développant seulement cette identité linéaire,

\[
\Phi(L_i)=\sum_{j<n}B_{ij}q_j.
\tag{4}
\]

Par multiplicativité de Phi, pour H=gamma_n product_i L_i :

\[
\Lambda(H)
=\gamma_n^2[q_*]\prod_i\sum_{j<n}B_{ij}q_j
=[q_*]\prod_i\sum_{j<n}B_{ij}q_j.
\tag{5}
\]

L'expression de droite décrit le coefficient obtenu par le produit
orienté natif et la correction universelle du signe. C'est une égalité
de spécification, pas une nouvelle voie de calcul imposée au programme.
Les B sont toujours construits depuis les entrées originales a,z.

## 4. Fusion, unité et lecture INTT : théorème général

La fusion déjà établie dans le quotient signifie
F_f - omega^(fD_*) F_0 appartient à I. Par (3), remplacer F_f par
omega^(fD_*) F_0 conserve sa lecture. On n'utilise pas une fausse
égalité entre ces deux polynômes ordinaires.

L'unité ajoutée conserve elle aussi la valeur :

\[
\Lambda(1+H)=\Lambda(H).
\tag{6}
\]

Avec le cœur partagé H^+=1+H, les sorties ordinaires du programme sont

\[
\widetilde Z^+[k]
=\frac1N\sum_f\omega^{-fk}\omega^{fD_*}(1+H).
\]

La lecture est R-linéaire. En utilisant (6), puis l'orthogonalité :

\[
\begin{aligned}
\Lambda(\widetilde Z^+[k])
&=\frac1N\sum_f\omega^{f(D_*-k)}\Lambda(1+H)\\
&=\left(\frac1N\sum_f\omega^{f(D_*-k)}\right)\Lambda(H)\\
&=\delta_{k,k_*}\Lambda(H),\qquad k_*=D_*\bmod N.
\end{aligned}
\]

On obtient donc, pour toutes les entrées formelles a,z et toute taille
admissible :

\[
\boxed{\Lambda(\widetilde Z^+[k])
=\Lambda(\widetilde Z[k])
=[\widetilde\Omega]\mathcal Z[k].}
\tag{7}
\]

En particulier, la case cible conserve exactement la valeur recherchée.
Toutes les opérations de cette preuve sont celles de notre architecture.

## 5. Ce que le théorème affirme sur le calcul

La conservation de la valeur par la lecture du coefficient est démontrée
généralement. La lecture est indépendante du représentant, traverse le
suffixe spectral et ignore l'unité ajoutée. L'évaluation x=0 est une
autre application : elle renvoie 1 sur la case enrichie, alors que
Lambda renvoie le coefficient recherché.

La borne 29n^3+1 concerne le circuit partagé des représentants. La
notation [q_*] dans (1) n'est pas déclarée gratuite et sa compilation
en portes scalaires avec un budget polynomial général reste à établir.
Le théorème (7) ferme la correction mathématique de la lecture ; il ne
constitue pas à lui seul une nouvelle borne de complexité pour ce lecteur.

## 6. Formalisation

Les théorèmes `spectral_unit_readout_preserved`,
`spectral_unit_readout_formula` et `spectral_unit_readout_routed` de
`UnitLift.lean` formalisent la conservation et le routage pour tout
lecteur R-linéaire annulant l'unité. L'identité du noyau spectral est
une hypothèse explicite. Les étapes (1)-(4) construisent ici le lecteur
natif et justifient ces propriétés dans notre quotient.

`SquarefreeReadout.lean` traite les coefficients des multiples des
carrés utilisés dans l'étape (2). Les rapports séparés indiquent les
énoncés effectivement acceptés par Lean et leur portée exacte.

Résultat de vérification : dix théorèmes de `UnitLift.lean` et cinq de
`SquarefreeReadout.lean` acceptés par Lean 4.34.1, sans avertissement ni
preuve incomplète. Le changement de base Fourier complet et le raccord
de son idéal au lecteur sont démontrés dans ce texte ; ils ne sont pas
annoncés comme intégralement formalisés dans ces quinze lemmes.
