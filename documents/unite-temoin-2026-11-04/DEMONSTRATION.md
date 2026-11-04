# Ajout d'une unité au circuit partagé : résultat et portée exacte

4 novembre 2026. On conserve le préfixe natif, la forme linéarisée, le
produit partagé et le graphe des phases et de la vraie INTT. Le compilateur
de référence n'est pas modifié. La variante est construite par
`compile_with_unit.py` dans le même DAG, à partir des mêmes fils du préfixe.

## 1. Vérification préalable de la sortie scalaire annoncée

Pour n=2, Q=5, N=4, omega=2, d=(0,1), a_ij=0 et z=1, tous les B_ij
valent 1. Dans l'algèbre orientée :

\[
H=\gamma_2(q_0+q_1)^2=-2q_0q_1=2\widetilde\Omega.
\]

Le coefficient scalaire recherché est donc 2. Le représentant natif
H(a,z,x) s'annule en x=0 ; la vraie INTT renvoie donc zéro dans la case
cible. Ce fil inchangé ne calcule pas le coefficient recherché comme
polynôme en a,z indépendant de x. Ce contre-exemple réfute l'affirmation
sur les fils actuels, sans réfuter l'existence d'un autre circuit scalaire
polynomial pour la même architecture.

Le coût polynomial des représentants demeure établi. Il ne peut pas être
annoncé comme coût d'un coefficient que ces fils ne calculent pas encore.

## 2. L'élément ajouté : une seule porte d'addition

Posons H = gamma_n F_0, et insérons la porte

\[
\boxed{H^+=1+H.}
\]

Dans le suffixe déjà fusionné, on définit explicitement

\[
\widetilde W^+[f]=\omega^{fD_*}(1+H).
\]

L'orthogonalité de la NTT donne pour toute taille admissible :

\[
\boxed{\widetilde Z^+[k]=\delta_{k,k_*}(1+H),
\qquad k_*=D_*\bmod N.}
\]

Comme n>=1, F_0 est homogène de degré n dans les auxiliaires x. Alors
H(a,z,0)=0, d'où

\[
\boxed{\widetilde Z^+[k_*](a,z,0)=1.}
\]

Cela empêche l'annulation de toute la table de sortie. Les autres cases
restent nulles par le routage spectral. Les formes orientées en amont
restent naturellement nulles en x=0 ; l'ajout ne les modifie pas.

## 3. Préservation du coefficient recherché

Soit lambda la projection sur le coefficient de Omega dans l'algèbre
orientée. Pour n>=1, Omega a degré strictement positif et lambda(1)=0.
Par additivité :

\[
\lambda(1+\rho(H))=\lambda(\rho(H)).
\]

La nouvelle sortie orientée est delta_(k,k*) (1+Y Omega), dont le
coefficient supérieur est toujours Y. Elle diffère de la sortie totale
native delta_(k,k*) Y Omega par une unité connue dans la case cible.
La soustraction de cette unité restaure la sortie native, avec son
annulation en x=0.

Deux lectures restent donc distinctes :

\[
\operatorname{ev}_0(1+H)=1,
\qquad \lambda(1+\rho(H))=Y.
\]

La modification préserve l'information recherchée ; elle ne construit
pas son extraction en portes scalaires depuis a,z seuls. Le test n=2
ci-dessus donne désormais 1 en x=0, alors que le coefficient vaut 2.

## 4. Borne générale sur le même circuit partagé

La construction prépare H une seule fois. Elle ajoute la porte 1+H,
puis réutilise le même gabarit de phases et de papillons INTT. Le budget
théorique établi précédemment augmente donc d'une seule porte :

\[
\boxed{C^+_{\mathrm{rep}}(n)\le29n^3+1.}
\]

Le programme conserve les adresses de tous les ancêtres du cœur.
`DAG.substitute` construit les descendants modifiés dans le même dépôt
de portes ; seules les portes accessibles depuis les nouvelles sorties
sont comptées et exécutées. L'ancien suffixe de référence n'est pas
ajouté au budget du nouveau circuit. Il reste disponible pour les tests.

La majoration +1 concerne le gabarit avant simplification. Une comparaison
de deux DAG optimisés pourrait présenter une différence autre que 1 si
des simplifications changent. Dans les six cas testés, la différence
mesurée est effectivement 1 :

| n | Portes utiles initiales | Variante avec unité |
|---:|---:|---:|
| 1 | 12 | 13 |
| 2 | 73 | 74 |
| 3 | 121 | 122 |
| 4 | 330 | 331 |
| 8 | 1494 | 1495 |
| 16 | 6766 | 6767 |

Ces mesures vérifient l'implémentation. La borne générale vient du
décompte du gabarit partagé, et ne repose pas sur l'extrapolation du tableau.

## 5. Pourquoi l'annulation ne peut pas disparaître pour la même classe

Posons R=F_Q[a,z], P=R[x_0,...,x_(N-1)], et soit I l'idéal engendré par
les relations de convolution et de padding. Chaque générateur s'annule
en x=0 : les convolutions sont homogènes de degré 2, et le padding de
degré 1. Pour le morphisme epsilon=ev_0 : P -> R, on a donc

\[
I\subseteq\ker\epsilon.
\]

En effet, epsilon annule chaque générateur, donc toute somme de produits
de ces générateurs par des polynômes. Elle descend ainsi en un morphisme
d'augmentation de P/I vers R.

Si un candidat G représente exactement la même sortie que H, alors
G-H appartient à I. Par conséquent

\[
\epsilon(G)-\epsilon(H)=\epsilon(G-H)=0,
\qquad\boxed{G(a,z,0)=H(a,z,0)=0.}
\]

Ce résultat est général : changer de représentant de la même classe ne
peut pas empêcher l'annulation en zéro. L'ajout de l'unité est possible
précisément parce qu'il enrichit la sortie totale tout en conservant son
coefficient supérieur.

## 6. Vérification et limite du résultat

Les preuves algébriques sont dans `UnitLift.lean`, avec leur rapport dans
`lean-validation.json` : dix théorèmes acceptés par Lean 4.34.1, sans
avertissement ni preuve incomplète. Les hypothèses sur l'augmentation et sur lambda(1)
sont explicites dans Lean ; leur application à l'idéal natif est démontrée
dans les sections 3 et 5 ci-dessus. La compilation Python et son budget
ne sont pas entièrement formalisés dans ces lemmes.

`verify_unit_lift.py` contrôle les sorties, le partage du préfixe et les
bornes sur six tailles, avec entrées nulles, non nulles et aléatoires
reproductibles. Son rapport est `unit-lift-validation.json`.

Le résultat obtenu est une variante à sortie non nulle en x=0, de taille
polynomiale comme représentant, conservant le coefficient cible. La borne
générale d'un circuit scalaire fournissant ce coefficient depuis a,z
seuls n'est pas établie par cette modification.

La conservation générale par la lecture du coefficient, y compris son
indépendance du représentant dans le quotient, est démontrée dans
`LECTURE_CONSERVEE.md`. Cinq lemmes supplémentaires sur les coefficients
formels sont vérifiés dans `SquarefreeReadout.lean`.
