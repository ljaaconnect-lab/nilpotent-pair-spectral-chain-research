# Conjugaison logarithmique algébrique

Fichier : `LogConjugation.lean`.

Le terme « logarithmique » désigne la relation algébrique `D H = H v`.
Le fichier n'introduit aucune fonction logarithme analytique, aucun logarithme
discret et aucune porte logarithme. Il travaille dans un anneau commutatif
arbitraire. `D` est un morphisme additif accompagné de la règle de Leibniz,
c'est-à-dire une dérivation additive.

Pour `D H = H v`, l'identité vérifiée est

\[
(D^2-D)(HF)
=H\{D^2F+(2v-1)DF+(Dv+v^2-v)F\}.
\]

La somme finie permet de l'appliquer à

\[
L=c\sum_j(D_j^2-D_j),
\]

avec un scalaire arbitraire `c`. Pour le lecteur du projet, on prend
`D_j=s_j ∂_j` et `c=1/2` dans un corps de caractéristique différente de deux.
Cette substitution est une interprétation mathématique du théorème ;
l'implémentation des dérivations d'Euler n'est pas formalisée dans ce fichier.

Enfin, si `L(HF)=H A(F)`, le facteur du lecteur se réécrit exactement

\[
(I-r^{-1}L)(HF)=H\bigl(F-r^{-1}A(F)\bigr).
\]

Dans le théorème, `rInv` est simplement un scalaire fourni. Aucune inversion
de données n'est exécutée pour cette égalité. Les trois théorèmes sont
`conjugate_second_order`, `conjugate_finite_sum` et `conjugate_reader_factor`.

Les hypothèses `D_j H = H v_j` sont explicites. Le fichier ne prouve pas
qu'un `v_j` existe dans l'anneau choisi pour tout `H`. Si `H` est inversible,
on peut prendre `v_j=H^{-1}D_j H`. Pour un produit dont certains facteurs
s'annulent, une division numérique ordinaire ne satisfait pas cette
construction ; la régularisation formelle doit être traitée séparément.

Le résultat réécrit l'opérateur et son facteur de lecture en une expression
algébrique. Il ne borne pas le coût de toutes les dérivées qui apparaissent
lors d'une composition répétée. Il ne prouve donc ni fermeture polynomiale
ni fermeture quasi-polynomiale de la chaîne complète.

Reproduction :

```powershell
python -X utf8 etudes/2026-11-01/logarithmes-chaine/lean/replay_lean.py --write-report
```

Le script refuse un code de retour non nul, un avertissement, `sorryAx`,
ou une modification du fichier pendant le contrôle. Le rapport conserve
le SHA-256 du fichier et les sorties de `#print axioms`.
