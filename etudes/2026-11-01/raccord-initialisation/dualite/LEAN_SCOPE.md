# Portée de la vérification Lean du raccord dual

`DualReader.lean` utilise des occupations naturelles `Fin n → Nat`,
avec `collisions u = ∑ j, Nat.choose (u j) 2`. L'identité de collision
n'est pas une hypothèse : l'identité élémentaire de `choose` est prouvée
par induction, puis sommée sur les colonnes.

Les valeurs des monômes sont définies par le produit effectif
`monomialValue t u = ∏ j, t j ^ u j`. Pour toute fonction scalaire `p`,
le lecteur diagonal vaut `p (collisions u) * monomialValue t u`.
Le lemme `monomial_pullthrough` établit son passage à travers la
multiplication par un monôme d'occupation `u`, avec le lecteur décalé
par `collisions u + collisions v + overlap u v`.

La fonction `p` est arbitraire : on peut l'instancier par l'évaluation
du polynôme du projecteur sur l'entier de collision dans le corps voulu.
Le fichier ne définit pas la différentiation des polynômes multivariés,
ne formalise pas tout le compilateur et ne prouve pas une borne de
portes polynomiale. Il certifie le noyau combinatoire et monomial de la
loi duale écrite dans `RACCORD_DUAL.md`, pour tout nombre de colonnes et
toutes occupations.

Le fichier `replay_lean.py` recompile la source, contrôle son empreinte
avant et après, exige un code de retour nul, zéro avertissement et
l'absence de `sorryAx`. Le rapport `dual-lean-validation.json` conserve
les sorties de `#print axioms` et indique les limites de portée.
