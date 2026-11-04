# Raccord dual exact du lecteur au produit compact

Cette note construit une loi qui pousse le lecteur dans les facteurs
initiaux, sans demander la table des moments comme entrée. Elle n'établit
pas une borne polynomiale pour la scalarisation de toute cette loi.

## 1. Une loi de transport du lecteur

Travailler sur un corps K de caractéristique différente de 2, et poser

\[
E_j=s_j\partial_{s_j},\qquad
L=\frac12\sum_jE_j(E_j-I),\qquad
\kappa(u)=\sum_j\binom{u_j}{2}.
\]

Tous les E_j commutent. Pour un multi-indice naturel u et tout polynôme F,

\[
E_j(s^u F)=s^u(E_j+u_jI)F,
\]

donc

\[
\boxed{L(s^u F)=s^u\bigl(L+\sum_j u_jE_j+\kappa(u)I\bigr)F.}
\]

On le vérifie également sur un monôme s^alpha, par l'identité entière

\[
\kappa(\alpha+u)=\kappa(\alpha)+\kappa(u)+\sum_j\alpha_ju_j.
\]

Par composition, pour tout polynôme scalaire p,

\[
p(L)(s^u F)=s^u p\bigl(L+u\cdot E+\kappa(u)I\bigr)F.
\]

Aucun choix particulier de p et aucune division par une donnée ne sont
nécessaires. Pour le projecteur de l'étude, prendre p=pi_n.

## 2. Le lecteur se pousse directement à travers un facteur de ligne

Soit ell_i(s)=sum_j B_ij s_j et t_j=omega^(f d_j). Définir

\[
\rho_{p,u}(F)=
\left[p\bigl(L+u\cdot E+\kappa(u)I\bigr)F\right](t).
\]

La loi précédente et la linéarité donnent

\[
\boxed{
\rho_{p,u}(\ell_iF)
=\sum_j B_{ij}t_j\,\rho_{p,u+e_j}(F).
}
\]

La valeur terminale, sans facteur restant, est

\[
\boxed{\rho_{p,u}(1)=p(\kappa(u)).}
\]

Cette paire de lois est un raccord exact entre les feuilles B,t et le
lecteur. Partir de u=0, F=G_B et p=pi_n. Les phases restent dans B_ij t_j ;
la table des fréquences peut être injectée dans l'INTT habituelle. Il n'y a
pas de coefficient terminal fourni comme entrée.

Une notation entièrement scalaire équivalente utilise des translations
commutantes tau_j sur les polynômes d'une variable vectorielle x :

\[
(\tau_j H)(x)=H(x+e_j),\qquad
\boxed{
(\pi_n(L)G_B)(t)=
\left[\prod_{i=0}^{n-1}
 \left(\sum_j B_{ij}t_j\tau_j\right)
 \pi_n(\kappa(x))\right]_{x=0}.
}
\]

L'entrée du lecteur dual pi_n(kappa(x)) possède elle-même un circuit
compact. La question restante est le coût scalaire de la composition et
de la lecture de ces translations pondérées. Une porte tau_j n'est pas
comptée comme une porte scalaire + ou fois.

## 3. La coproducte explique les corrélations à conserver

Pour tous F,G,

\[
L(FG)=(LF)G+F(LG)+\sum_j(E_jF)(E_jG).
\]

Le dernier terme couple les deux sous-produits. Sur un facteur linéaire,
L ell_i=0, ce qui donne la première observation par les contractions
binaires des lignes. Pour les ordres supérieurs, le transport dual
ci-dessus conserve exactement ces termes croisés au moyen de u dot E.

L'état des seuls moments de L ne ferme donc pas par multiplication des
facteurs. Exemple : à t=(1,1), les formes F=s_1 et G=s_2 ont les mêmes
valeurs de (L^r F)(t) et (L^r G)(t) pour tout r : 1 pour r=0 et 0 sinon.
Pourtant, après multiplication par s_1,

\[
(L(s_1F))(t)=1,\qquad (L(s_1G))(t)=0.
\]

Cet exemple réfute uniquement cette interface locale de moments. Il ne
prouve aucune impossibilité d'une compilation globale qui utilise les
facteurs complets et le lecteur ensemble.

## 4. Coût de la réalisation explicitement testée

Le vérificateur joint mémorise u pour exécuter la loi duale. À profondeur k,
il existe binomial(n+k-1,k) multi-indices possibles. Le nombre de transitions
jusqu'à n facteurs est

\[
T_n=n\sum_{k=0}^{n-1}\binom{n+k-1}{k}
=n\binom{2n-1}{n-1}.
\]

Chaque transition utilise une multiplication et chaque état additionne ses
n branches. Sans simplifications, la partie propagation a donc

\[
(2n-1)\binom{2n-1}{n-1}
\]

portes scalaires, hors préparation des B_ij t_j et constantes terminales.
Cette réalisation exacte n'est pas polynomiale. Ce coût appartient à ce
choix de scalarisation, et n'est pas attribué à l'architecture générale.
Les seules conditions de correction du projecteur sont Q>max(2,h) ; les
conditions NTT supplémentaires restent celles du projet.

Pour obtenir le circuit recherché, il faudrait remplacer cette
mémorisation par une loi de partage uniformément polynomiale, ou une
contraction globale équivalente dont toutes les portes scalaires sont
exposées. Cette note ne fournit pas encore cette loi.

## 5. Vérification

`verify_dual.py` vérifie :

- l'identité de décalage de kappa sur 2000 multi-indices indépendants ;
- le lecteur dual pour des polynômes p arbitraires et pour pi_n ;
- le raccord aux phases exactes et aux slots INTT ;
- l'exemple de non-fermeture locale des seuls moments.

La référence énumère les affectations et la loi duale mémorise les
multi-indices ; ce sont des vérifications finies, pas un compilateur
polynomial. Le rapport consigne cette portée et les empreintes sources.
