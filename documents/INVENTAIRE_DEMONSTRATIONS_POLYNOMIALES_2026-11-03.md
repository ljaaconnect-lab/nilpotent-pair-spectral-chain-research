# Inventaire des démonstrations de bornes polynomiales

3 novembre 2026. Périmètre : architecture orientée, forme linéarisée,
fusion, signe universel et INTT, sur un même circuit partagé. La récurrence
expérimentale R et ses groupes G, s_k, W ne sont pas des éléments de cet
inventaire. Les démonstrations générales sont distinguées des vérifications
sur petites tailles, et les hypothèses des théorèmes Lean restent explicites.

## 1. Hypothèses communes et modèle de portes

On a n>=1, N puissance de deux avec n<N<=2n, ell=log_2 N<=n.
Le premier Q, une racine omega d'ordre N et les étiquettes d_j sont fournis,
avec N divisant Q−1. Les constantes structurelles sont des feuilles ; les
additions et multiplications binaires de valeurs calculées sont des portes.
Les fils se réutilisent sans recopier leurs sous-circuits.

Trois portées doivent être conservées : un coefficient scalaire construit
depuis a,z ; un représentant scalaire en a,z,x interprété dans le quotient ;
une opération sur un élément de l'algèbre orientée. Les preuves ci-dessous
précisent celle qu'elles couvrent. Aucun passage de portée n'est gratuit.

## 2. Préparation des marqueurs et coefficients B : 4n²−1

Pour t=0,...,n²−1, poser m_t=z^(2^t). Le programme m_0=z,
m_(t+1)=m_t² construit tous les marqueurs par exactement n²−1 carrés.
Puis chaque B_ij=(1+a_ij²)m_(in+j) demande un carré, une addition et un
produit. Ainsi, pour toute taille,

\[
\boxed{C_B\le(n^2-1)+3n^2=4n^2-1.}
\]

**Démonstration :** construction et décompte général écrits, présents dans
[la composition native, section 4](COMPOSITION_BORNES_NATIVES_2026-11-03.md)
et réalisés par [le constructeur](composition-native-2026-11-03/compose_native_representatives.py).
Les fils produits sont scalaires depuis a,z. La construction entière des B
n'est pas formalisée dans les certificats Lean récents ; ses comptes sont
contrôlés dans les rapports de programme.

## 3. Linéarisation des coefficients : 2nN ell+nN

Pour chaque ligne, C_i=N⁻¹ NTT_N(B_i,0,...,0). Une transformée radix-2
comporte ell étages de N/2 papillons. Un papillon demande au plus quatre
portes dans le modèle +,× utilisé : produit par une racine, deux additions,
et multiplication par −1. La normalisation demande N produits par N⁻¹.
Pour les n lignes,

\[
\boxed{C_{C\mid B}\le2nN\ell+nN\le6n^3.}
\]

Le padding emploie des constantes zéro. Les autres fréquences sont obtenues
par la fusion terminale : on ne construit pas N copies de ces n NTT.
Le code des papillons est [ntt_radix2](../etudes/2026-11-01/linearisation-orientee-convolution/linearised_inputs.py).
Le décompte des boucles est une preuve écrite ; le programme complet des
papillons n'est pas formalisé par les certificats de bornes cités ici.

La préparation scalaire complète satisfait

\[
A(n,N)=4n^2-1+2nN\ell+nN\le10n^3.
\]

**Lean :** `SameDAGCost.coefficient_bound`, dans
[SameDAGCost.lean](cout-meme-circuit-2026-11-03/SameDAGCost.lean),
prouve cette dernière inégalité sous n>=1,N<=2n,ell<=n. Il ne remplace
pas la démonstration externe donnant A comme coût du programme.

## 4. Formes linéarisées : n(2N−1)

Chaque L_i=Σ_r C_ir x_(−r) se construit avec au plus N multiplications
et N−1 additions. Donc

\[
\boxed{C_{L\mid C}\le n(2N-1)\le4n^2-n.}
\]

**Démonstration :** décompte du circuit explicite, pour toute taille.
Cette borne porte sur des représentants conservant x. La preuve de leur
interprétation orientée vient de l'inversion Fourier :
rho_x(L_i)=Σ_j B_ij q_j. Les identités de convolution et de padding
certifient cette représentation ; elles ne sont pas un tableau d'états
ni une porte de lecture ajoutée.

## 5. Produit partagé : exactement n−1 portes supplémentaires

Avec les n formes disponibles comme fils, on prend H_1=L_0,
H_(i+1)=H_i L_i. La préparation reste unique. L'induction donne

\[
g_1=0,\quad g_{i+1}=g_i+1,
\qquad\boxed{g_n=n-1.}
\]

La même induction prouve rho_x(H_i)=∏_(t<i)rho_x(L_t), puisque rho_x
préserve les produits. Formes et produits coûtent ensemble au plus 2nN−1.

**Lean : programme, correction et portes sont effectivement formalisés**
dans [NativePrefixInduction.lean](induction-native-2026-11-03/NativePrefixInduction.lean) :
`prefix_circuit_eval`, `prefix_circuit_gates`, `map_prefix`,
`composed_prefix_gates` et `native_prefix_compilation`.
Le circuit de préparation reste un paramètre ; son coût est ajouté une fois.
La portée est celle des représentants interprétés dans le quotient.

## 6. Fusion des fréquences, signe et INTT

L'application q_j↦omega^(f d_j)q_j préserve les relations de carré nul.
Au degré n, le quotient est engendré sur l'anneau de coefficients par
q_0...q_(n−1). L'application agit donc par omega^(f D_*), avec D_*=Σ_jd_j.
Cela démontre l'identité générale [F_f]=omega^(fD_*)[F_0], avant lecture.
Voir la [preuve dans le quotient](REANALYSE_QUOTIENT_2026-11-03.md), sections 1–2.

Le produit complet est ainsi partagé entre toutes les fréquences.
La multiplication par gamma_n=(-1)^(n(n−1)/2) coûte epsilon_n<=1 porte.
Le programme V_0=gamma_n F_0, V_(f+1)=omega^(D_*)V_f ajoute au plus N−1
portes. Les papillons inverses et leur normalisation donnent

\[
\boxed{C_{\rm signe}\le1,\quad
C_{\rm phases}\le N-1,\quad
C_{\rm INTT}\le2N\ell+N.}
\]

Le suffixe phases+INTT est donc borné par 2N ell+2N−1. Le budget historique
plus large B(N)=2N ell+3N−3 reste valide et est celui utilisé dans les
certificats cubiques existants. Le coût des papillons a une démonstration
écrite par comptage ; leur algorithme n'est pas intégralement formalisé
dans les modules de compatibilité suivants.

**Lean :** [SpectralReadoutCompatibility.lean](induction-native-2026-11-03/SpectralReadoutCompatibility.lean)
prouve `map_readout` et `shared_phase_readout` ; `readout_of_kernel`
utilise une identité d'orthogonalité `hkernel` explicitement fournie.
[TerminalTaggedClosure.lean](fermeture-native-2026-11-03/TerminalTaggedClosure.lean)
prouve `tag_add`, `tag_scalar_mul`, `tag_linear_readout` : des fils de
coefficients déjà normalisés conservent ce format sous ces opérations.

## 7. Raccord des représentants de toute la chaîne : 29n³

La préparation et le produit partagé donnent

\[
P(n,N)=4n^2-2+2nN\ell+3nN\le18n^3.
\]

Le signe, les phases et la vraie INTT donnent, pour toutes les sorties
ensemble et sur le même programme,

\[
\boxed{C_{\rm rep,INTT}\le P+\varepsilon_n+B(N)\le29n^3.}
\]

Le compte précis est O(n² log(n+1)). Si l'INTT est fusionnée en routage
par son identité d'orthogonalité, la borne devient 18n³+1. Cette dernière
variante est distinguée du programme qui exécute réellement les papillons.

**Lean arithmétique :** [NativeCompositionBounds.lean](composition-native-2026-11-03/NativeCompositionBounds.lean),
`representative_preparation_bound`, `representative_with_spectral_bound`
et `representative_routed_bound`. Ces théorèmes démontrent les inégalités
de naturels ; les formules de coût viennent du programme et du texte.

**Lean du raccord :** [NativeChainInduction.lean](induction-native-2026-11-03/NativeChainInduction.lean)
construit `chain`, prouve `chain_eval`, le compte exact
prepare.gates+(n−1)+suffix.gates, puis `chain_polynomial_gate_bound`.
Les bornes `hprepare` et `hsuffix` sont des hypothèses explicites.
Ce programme conserve x ; ces résultats ne sont pas annoncés comme une
borne du circuit normalisé sur les seules entrées a,z.

Pour le circuit compté en opérations de l'algèbre orientée, les bornes
17n² (avec spectral) et 7n² (après routage) sont également établies dans
la [composition native, section 3](COMPOSITION_BORNES_NATIVES_2026-11-03.md).
`typed_with_spectral_bound` et `typed_routed_bound` en vérifient les
conséquences numériques. Leur unité n'est pas la porte scalaire du corps.

## 8. Fermeture générale des coûts partagés et induction

Pour un état C prolongé par un bloc compatible U, les anciens fils sont
conservés et le programme possède exactement |C|+|U| portes.
[SharedStateClosure.lean](fermeture-native-2026-11-03/SharedStateClosure.lean)
le construit et le démontre : `extend_gates`, `old_wires_preserved`,
`shared_chain_gates`, avec correction par `circuit_eval_natural`.

Pour une suite de blocs, l'induction prouve

\[
S_m\le S_0+\sum_{i<m}b_i.
\]

Si S_0<=K_0 n^a, m<=A n^b et b_i<=K n^c, avec constantes indépendantes
du rang et de n, alors

\[
\boxed{S_m\le(K_0+AK)n^{\max(a,b+c)}.}
\]

**Lean :** [SharedCostInduction.lean](induction-native-2026-11-03/SharedCostInduction.lean),
`accumulated_cost`, `uniform_increment_bound`, `polynomial_monomial_bound`
et `polynomial_family_bound`. La règle est générale et démontrée ; ses
hypothèses doivent porter sur les blocs réellement raccordés.

## 9. Lecture du coefficient normalisé : coût conservé sous certificat

**Vérification ultérieure du raccord :** le certificat ci-dessous est
[réfuté pour les sorties inchangées du représentant natif](RACCORD_NORMALISATION_MEME_CIRCUIT_2026-11-03.md).
Elles s'annulent en x=0 tandis que la sortie native ne s'annule pas sur
l'entrée a=0,z=1. Le théorème conditionnel reste valide ; cette
instanciation ne satisfait pas son hypothèse. Il ne s'agit donc pas
d'une preuve simplement manquante sur ces mêmes fils.

La construction eraseAux(c) remplace les entrées auxiliaires par zéro
sans changer le nombre de portes. Pour un circuit de coefficient c
certifié par Norm(c,Z), sa sortie étiquetée reste Z. Ainsi

\[
\mathsf{Norm}(c,Z),\quad |c|\le Kn^d
\quad\Longrightarrow\quad
|\operatorname{eraseAux}(c)|=|c|\le Kn^d.
\]

**Lean :** [AuxiliaryErasure.lean](fermeture-native-2026-11-03/AuxiliaryErasure.lean),
`erase_gates`, et [CertifiedScalarClosure.lean](fermeture-native-2026-11-03/CertifiedScalarClosure.lean),
`reader_gates`, `reader_tagged_correct`, `certified_polynomial_family`.
Le programme lecteur est construit ; `normalized` et le budget du même
circuit sont des hypothèses. Cette opération s'applique au coefficient
normalisé, pas à une substitution arbitraire dans F_0(x).

Les normalisations exactes générales ont déjà été retrouvées dans
l'[audit historique](AUDIT_NORMALISATION_EXISTANTE_2026-11-03.md).
L'existence de cette normalisation n'est donc pas un point rouvert.
Le raccord de son certificat à une borne scalaire polynomiale uniforme
sur le même circuit n'est pas démontré par ces seuls théorèmes.

Le compte global [SameDAGCost.lean](cout-meme-circuit-2026-11-03/SameDAGCost.lean)
prouve enfin |T|=|T∩P|+J et

\[
J\le\kappa n^e\Longrightarrow
|T|\le(10+\kappa)n^{\max(3,e)}.
\]

La borne sur J reste l'hypothèse `hjoint`. Elle couvre ensemble fusion,
normalisation et spectral sur le même DAG ; aucun lecteur n'est ajouté après.

## 10. Outils acquis à conserver, sans les imposer à la chaîne

La fusion T_y T_z=T_(y+z) est une identité générale. Sur des paramètres
scalaires à p composantes, sommer m paramètres coûte p(m−1) additions.
La [réalisation triangulaire](../etudes/2026-11-01/reprise-flot-rationnel/REPRISE.md)
a un coût d'action 2(p+1)binom(d+1,3), soit O(n⁴) pour p=n,d=n+1.
Les identités de fusion y sont formalisées ; ce coût exact est un comptage
externe. Ces contrats ne constituent pas la preuve du coût de l'observation
du produit des différences.

Le [compilateur générique déjà acquis](AUDIT_COMPILATION_GENERIQUE_2026-11-02.md)
construit uᵀM^K v pour une initialisation de coût S et une dimension r,
en S+J(K)(2r³−r²)+2r²+r−1 portes, J(K)<=2 log_2 K pour K>=1.
Correction et coût sont vérifiés dans Lean. Il reste un outil disponible ;
sa dimension, son initialisation et sa représentation de la cible ne
sont pas automatiquement fournies par la chaîne native. Aucun bloc
matriciel supplémentaire n'est ajouté à l'inventaire.

## 11. Rapports de preuve et portée de cette vérification

Les rapports acceptés sont accessibles depuis les notes
[composition](COMPOSITION_BORNES_NATIVES_2026-11-03.md),
[induction](INDUCTION_CHAINE_NATIVE_2026-11-03.md),
[fermeture](FERMETURE_NATIVE_2026-11-03.md) et
[compte du même DAG](COUT_MEME_CIRCUIT_2026-11-03.md).
Les sources ont été relues pour ce recensement. Le
[contrôle d'empreintes](inventaire-preuves-2026-11-03.json) vérifie leur
correspondance aux rapports acceptés ; il ne remplace pas un nouveau
lancement de Lean et n'annonce aucun théorème supplémentaire.

Les preuves de coût écrites valent pour toutes les tailles sous leurs
hypothèses. Les tests numériques complètent les contrôles d'implémentation ;
ils ne sont pas utilisés comme démonstration de ces bornes générales.
