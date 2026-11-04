# Vérification du raccord de normalisation sur le circuit déjà borné

3 novembre 2026. Travail limité au point demandé : le certificat de
normalisation du circuit représentatif partagé, sans introduire de nouvel
opérateur, de nouvelle représentation ou de nouveau compilateur.

**Résultat : le certificat `normalized` est faux pour les sorties inchangées
du programme représentatif borné à 29n³.** Le présenter comme une simple
preuve encore manquante sur ces mêmes fils était incorrect. Le résultat
ci-dessous réfute cette instanciation précise. Il ne réfute ni la chaîne
orientée, ni la possibilité d'une normalisation compilée, ni une borne
polynomiale pour une autre réalisation de la même architecture.

## 1. Les deux énoncés à raccorder

On conserve les paramètres admissibles du projet : n>=1, Q premier,
n<N<=2n et N divisant Q−1, avec omega d'ordre N. L'algèbre orientée
retenue est le quotient commutatif

\[
A=\mathbf F_Q[q_0,\ldots,q_{n-1}]/(q_0^2,\ldots,q_{n-1}^2),
\qquad \widetilde\Omega=\gamma_n q_0\cdots q_{n-1}.
\]

Les relations de convolution et de padding sont sa présentation dans
les coordonnées Fourier x. Aucune relation supplémentaire n'est ajoutée.

Le programme existant construit, avec les formules déjà retenues,

\[
L_i(a,z,x)=\sum_{r<N}C_{ir}(a,z)x_{-r},\qquad
H(a,z,x)=\prod_{i<n}L_i(a,z,x),
\]
\[
c_k(a,z,x)=\operatorname{INTT}_N
\bigl[(\gamma_n\omega^{fD_*}H(a,z,x))_{f<N}\bigr][k].
\]

Sa correction et sa borne sont établies :

\[
\rho_x(c_k)=\mathcal Z_k,\qquad |c|\le29n^3.
\]

Le théorème [CertifiedScalarClosure](fermeture-native-2026-11-03/CertifiedScalarClosure.lean)
ne demande pas seulement cette interprétation dans le quotient. Son
hypothèse `normalized` appliquée à ces mêmes sorties demanderait

\[
\tag{Norm}
\forall a,z,x,k,\qquad
\sigma(c_k(a,z,x))\,\widetilde\Omega=\mathcal Z_k(a,z).
\]

Ici x est universellement quantifié comme entrée scalaire dans le contrat
Lean. Le label est fixe ; sigma est l'inclusion du corps des coefficients
dans l'algèbre orientée. La conclusion du théorème, si cette hypothèse
était vérifiée, utiliserait c(a,z,0) sans augmenter le nombre de portes.

## 2. Les sorties du programme s'annulent aux auxiliaires nuls

Pour chaque ligne, L_i(a,z,0)=0 par définition. Comme n>=1, le produit H
contient une forme et satisfait H(a,z,0)=0. La correction du signe et les
phases conservent zéro. L'INTT est une application linéaire, donc

\[
\boxed{\forall a,z,k,\quad c_k(a,z,0)=0.}
\]

Cette preuve concerne le programme complet, vraie INTT comprise. Plus
généralement, ses sorties sont homogènes de degré n en x, ou nulles.

En substituant x=0 dans (Norm), on obtiendrait nécessairement

\[
\boxed{\forall a,z,k,\quad \mathcal Z_k(a,z)=0.}
\]

Cette substitution vérifie une instance obligatoire du quantificateur
de (Norm). Elle n'est pas proposée comme nouvelle méthode de calcul de
la chaîne et ne remplace pas ses générateurs orientés par des scalaires.

## 3. Une entrée native non nulle, pour toute taille

Choisir les entrées autorisées a_ij=0 et z=1. Alors tous les B_ij valent un.
L'inversion Fourier déjà établie donne dans le quotient

\[
[L_i]=\sum_{j<n}q_j,\qquad
[H]=\left(\sum_{j<n}q_j\right)^n.
\]

Les seules relations q_j²=0 impliquent

\[
\left(\sum_{j<n}q_j\right)^n=n!\,q_0\cdots q_{n-1}.
\]

En effet, tous les termes répétant un générateur s'annulent ; les n!
ordres du produit de tous les générateurs donnent le même monôme.
C'est une identité algébrique utilisée dans la preuve, sans développement
à exécuter dans le circuit.

Le monôme q_0...q_(n−1) est non nul dans le quotient : le coefficient de
ce monôme vaut zéro dans chaque multiple d'un q_j², et donc dans tout
élément de l'idéal qu'ils engendrent. Il ne peut appartenir à cet idéal.
Puisque Q>N>n, n! est non nul et inversible dans le corps. Le label
Omega_tilde=gamma_n q_0...q_(n−1) est donc non nul.

La fusion des fréquences et l'INTT déjà retenues donnent, à k_*=D_* mod N,

\[
\boxed{\mathcal Z_{k_*}(a=0,z=1)=n!\,\widetilde\Omega\ne0.}
\]

Cette valeur contredit la conséquence de (Norm) en section 2. Le certificat
ne peut donc être prouvé sur les sorties inchangées du programme actuel,
pour aucune taille n>=1 sous les paramètres admissibles.

## 4. Témoin explicite à deux lignes

Prendre n=2, Q=5, N=4, omega=2 et d=(0,1), toujours avec a=0,z=1.
Les quatre coefficients C de chaque ligne sont (3,2,0,1) modulo cinq.
Les relations orientées donnent

\[
[H]=(q_0+q_1)^2=2q_0q_1,\qquad
\gamma_2=-1,\qquad \widetilde\Omega=-q_0q_1.
\]

La sortie native est ainsi

\[
\mathcal Z=(0,\ 2\widetilde\Omega,\ 0,\ 0).
\]

Le programme représentatif évalué en x=0 produit pourtant
(0,0,0,0). Le scalaire deux est non nul modulo cinq. Les données, la
linéarisation, le signe, les phases et la vraie INTT sont ceux du projet.

## 5. Une sélection d'autres fils existants ne suffit pas

Pour n>=2, on peut également exclure une simple sélection d'un autre fil
du même DAG comme coefficient terminal. Il ne s'agit pas d'une borne
inférieure pour les circuits qui pourraient être construits autrement.

Le programme a l'invariant structurel suivant :

- tout fil de degré positif en x s'annule en x=0 ;
- tout fil non nul de degré zéro en x est structurel ou dépend des données
  a_ij d'une seule ligne, avec éventuellement z.

La seconde assertion vient de la construction : les marqueurs ne dépendent
que de z ; chaque B et chaque NTT de coefficients utilisent une seule
ligne. Les multiplications entre lignes arrivent après introduction de x.
Les phases et l'INTT combinent alors seulement des termes de degré n.

Un fil de degré positif échoue déjà sur l'entrée de la section 3.
Pour un fil de degré zéro, choisir une autre ligne et changer un seul
a_ij de zéro à un, avec z=1 et les autres données inchangées. Ce fil garde
sa valeur. Le coefficient terminal, lui, passe de n! à
n!+(n−1)! : l'entrée B_ij choisie passe de un à deux, et les termes qui
l'utilisent sont au nombre de (n−1)!. Cette différence est non nulle
modulo Q. Le fil ne peut donc être le coefficient correct pour les deux
entrées.

L'obstacle porte ainsi aussi sur le `select` du lecteur existant, lorsqu'il
ne fait que choisir des fils du DAG actuel. Il ne concerne pas une
réorganisation arithmétique qui construirait réellement ces coefficients.

## 6. Portée et vérifications du programme

Le [vérificateur ciblé](raccord-normalisation-2026-11-03/verify_native_normalization_contract.py)
appelle le constructeur natif inchangé. Il contrôle l'homogénéité des fils,
leur annulation, l'origine dans une seule ligne des fils scalaires de
degré zéro, et les témoins légaux ci-dessus. Le
[rapport](raccord-normalisation-2026-11-03/native-normalization-witnesses.json)
couvre n=1,...,8 ; 4 019 fils sont contre-vérifiés comme candidats à une
simple sélection pour n>=2. Aucune table de sous-ensembles, dérivation,
récurrence R ou nouvelle primitive n'est utilisée.

Ces contrôles finis accompagnent les preuves générales des sections 2,
3 et 5 ; ils ne sont pas leur justification par extrapolation.

La borne 29n³ du représentant reste valide. Les identités de quotient et
de fusion restent valides. Les normalisations exactes générales connues
restent valides. **Ce qui est réfuté est leur identification à un
coefficient déjà présent sur les fils inchangés de ce programme.** Aucune
borne polynomiale scalaire générale n'est déduite de cette réfutation.

## 7. Vérification Lean du contrat précis

Le fichier [NativeNormalizationContract.lean](raccord-normalisation-2026-11-03/NativeNormalizationContract.lean)
contient dix théorèmes acceptés par Lean 4.34.1, sans avertissement,
sans `sorry` ni axiome ajouté. Le
[rapport de validation](raccord-normalisation-2026-11-03/native-normalization-contract-validation.json)
conserve la sortie du vérificateur, les empreintes et les hypothèses.

- `linear_row_zero`, `oriented_product_zero` et `spectral_output_zero`
  vérifient l'annulation pour tout n>0, tous les coefficients C et toute
  lecture spectrale linéaire, donc pour les poids de l'INTT retenue.
- `representative_normalized_forces_zero` prouve que le contrat universel
  (Norm) impose une sortie native nulle. `circuit_normalized_forces_zero`
  énonce aussi ce résultat pour les fils sélectionnés d'un `Circuit`
  existant, sous l'hypothèse explicite d'annulation de ces fils.
- `nonzero_native_rejects_normalized` donne la négation du contrat dès
  qu'une sortie native est non nulle.
- `q5_witness_arithmetic` vérifie les paramètres numériques du témoin
  n=2,Q=5,N=4 et son coefficient deux. `tag_two_ne_zero` montre que ce
  coefficient fois le label est non nul dès que le label est non nul.

Le label terminal non nul reste une hypothèse dans ces nouveaux théorèmes
Lean. La construction intégrale de la base du quotient et l'identité
générale n! q_top sont démontrées dans la section 3, pas formalisées dans
ce fichier. La formalisation porte sur les formules et le contrat ; elle
ne prétend pas vérifier la traduction de tout le constructeur Python
dans `Circuit`. Les contrôles séparés de la section 6 portent sur ce code.

Reproduction depuis la racine du projet :

```powershell
python -B documents/raccord-normalisation-2026-11-03/replay_native_normalization_contract.py
python -B documents/raccord-normalisation-2026-11-03/verify_native_normalization_contract.py
```
