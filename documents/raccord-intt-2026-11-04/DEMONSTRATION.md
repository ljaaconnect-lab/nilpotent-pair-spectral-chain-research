# Lecture de la case finale et partage du coût de l'INTT

4 novembre 2026. Architecture retenue : mêmes amplitudes B, mêmes formes
linéarisées, produit orienté, correction du signe, fusion et vraie INTT.
Ce texte n'ajoute aucun opérateur au circuit natif.

## 1. Ce que peut partager exactement le lecteur

Posons R = F_Q[a,z] et notons A l'algèbre orientée. La projection
lambda : A -> R extrait le coefficient de l'élément de base Omega.
C'est une application R-linéaire. Elle est définie mathématiquement ;
sa notation n'est pas une porte scalaire primitive.

Pour toute famille U_f dans A et tous coefficients K_kf dans R :

\[
\lambda\left(\sum_f K_{kf}U_f\right)
=\sum_f K_{kf}\lambda(U_f).
\tag{1}
\]

Preuve : appliquer l'additivité de lambda à la somme finie, puis
lambda(c U) = c lambda(U) à chaque terme. Pour
K_kf = N^{-1} omega^{-fk}, (1) est exactement la commutation avec l'INTT.

Considérons maintenant le programme partagé des papillons. Chaque porte
est une addition ou une multiplication par une constante du corps.
Si les fils d'entrée portent lambda(U_f), on peut exécuter le même
programme avec les mêmes références de fils. Par induction sur ses
portes, chaque fil scalaire est la projection du fil orienté correspondant :

- addition : lambda(u+v) = lambda(u)+lambda(v) ;
- produit par c : lambda(cu) = c lambda(u).

Le graphe des portes est inchangé. Une sélection de son fil de sortie
n'ajoute aucune porte. Donc, pour des coefficients d'entrée déjà calculés,

\[
\boxed{C_{\text{INTT et sélection}}\le 2N\log_2N+N.}
\tag{2}
\]

La preuve concerne le coût du suffixe linéaire, en préservant le partage.
Elle ne compte pas comme gratuitement disponibles les valeurs lambda(U_f).
Si un préfixe scalaire P les calcule, le même DAG prolongé a au plus
|P| + 2N log_2 N + N portes. Aucun second lecteur n'est exigé après l'INTT.

## 2. La fusion fournit une identité encore plus précise

Soit H = gamma_n F_0, et alpha_f = omega^{fD_*}. Le représentant retenu
à l'entrée de l'INTT est alpha_f H. La distributivité donne, dans
l'anneau ordinaire R[x] avant même le passage au quotient,

\[
\widetilde Z_k
=\left(\frac1N\sum_f\omega^{f(D_*-k)}\right)H
=\delta_{k,k_*}H,
\qquad k_*=D_*\bmod N.
\tag{3}
\]

L'orthogonalité utilisée ici suit des hypothèses déjà retenues :
N est inversible dans F_Q et omega est d'ordre N. Si k=k_*, la somme
vaut N ; sinon, en posant r=omega^{D_*-k}, on a r != 1, r^N=1 et
(1-r) sum_{f=0}^{N-1} r^f = 1-r^N=0, donc la somme est nulle.

En particulier :

\[
\boxed{\widetilde Z_{k_*}=\gamma_n F_0.}
\tag{4}
\]

La case finale conserve le même représentant. Sa projection vérifie
lambda(rho(tilde Z_{k_*})) = lambda(rho(gamma_n F_0)). La sélection
de la case est gratuite, mais (4) ne transforme pas cette projection
en fil scalaire déjà construit depuis a,z.

## 3. Pourquoi cette preuve ne s'étend pas automatiquement au produit

La commutation (1) est linéaire. La projection d'un coefficient n'est
généralement pas multiplicative. Exemple interne à notre algèbre, n=2 :
si lambda_top extrait le coefficient de q0*q1, alors

\[
\lambda_{\rm top}(q_0)=\lambda_{\rm top}(q_1)=0,
\qquad \lambda_{\rm top}(q_0q_1)=1.
\]

Ainsi, lambda_top(q0*q1) != lambda_top(q0)*lambda_top(q1).
La récurrence de projection des portes linéaires ne justifie donc pas
de projeter séparément les facteurs puis de conserver leurs portes
de multiplication ordinaires. Cela ne réfute pas une autre compilation
scalaire des produits orientés ; cela délimite cette preuve de partage.

## 4. Vérification du fil réel dans le programme existant

`check_final_case.py` appelle le compilateur natif inchangé avec
n=2, Q=5, N=4, omega=2, d=(0,1), a_ij=0 et z=1. On a B_ij=1,
gamma_2=-1 et k_*=1. Dans le quotient,

\[
(-1)(q_0+q_1)^2=-2q_0q_1=2\widetilde\Omega.
\]

Le coefficient natif attendu est donc 2. Le fil réel sélectionné après
la vraie INTT donne 0 pour x=(0,0,0,0), et 4 pour x=(1,1,1,1),
tandis que son représentant est toujours -F_0. Ces substitutions
testent le polynôme représentant ; elles ne sont pas une méthode
d'évaluation du quotient. Elles réfutent l'identification de ce fil
inchangé avec le coefficient scalaire indépendant de x.

## 5. Conclusion exacte pour la borne générale

Le partage de l'extraction avec les portes linéaires de l'INTT est
mathématiquement valide lorsque leurs entrées portent déjà les
coefficients correspondants. Son coût marginal de sélection est nul.
La preuve ne fournit pas le calcul de ces coefficients à partir des
produits orientés, et ne ferme donc pas à elle seule la borne générale
en portes scalaires depuis a,z. Le budget polynomial déjà démontré
pour le représentant en a,z,x reste inchangé.

Une compilation intégrée pourrait établir cette borne sans bloc de
lecture séparé. Il reste alors à construire et borner ses portes,
avec leur correction, sur le même DAG. Aucune borne inférieure générale
ni nécessité d'un coût exponentiel n'est affirmée ici.

## 6. Sources et vérification

Lean 4.34.1 a accepté les sept théorèmes, sans avertissement ni preuve
incomplète. Les axiomes utilisés ont été affichés et contrôlés.

- `INTTProjection.lean` : projection d'une somme, de chaque porte et
  d'un programme linéaire partagé ; sélection du même fil ; identité de
  la case fusionnée et équivalence de son indépendance aux auxiliaires
  avec celle du représentant d'entrée.
- `replay_intt_projection.py` : vérification par Lean et audit des axiomes.
- `validation.json` : résultat exact de cette vérification.
- `check_final_case.py` et `final-case-validation.json` : exécution du
  programme natif inchangé, sur le cas explicite décrit plus haut.

L'identité d'orthogonalité est démontrée ci-dessus ; dans les théorèmes
Lean de fusion, l'identité du noyau reste une hypothèse explicite.
La compilation complète des produits orientés n'est pas revendiquée.
