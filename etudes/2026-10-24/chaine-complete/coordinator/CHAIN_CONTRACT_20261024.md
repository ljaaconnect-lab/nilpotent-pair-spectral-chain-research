# Cadre corrigé après relecture intégrale — 24 octobre 2026

Instruction de l'auteur : étudier la chaîne entière de collision orientée,
correction universelle et calcul spectral. Ne pas imposer le calcul direct
d'une amplitude scalaire P_A avant la couche spectrale.

Les 63 pages de annihilation_raccord_spectral_demonstrations.pdf ont été
relues en ordre dans cette reprise, corps principal, références et B.1–B.11.
SHA256 : ed1f05cd132305ec98ec4f195ae395123cc4ae68e1a137ac4a78898f4d5199f4.
Les pages 38 et 55 ont aussi été inspectées visuellement.

## Objet et invariant

Les feuilles de données sont A ou p_ij=1+a_ij², z et les constantes de
champ autorisées. L'adressage w_ij=2^((i−1)n+j−1) reste formel.
L'orientation attachée à chaque colonne est q_j=x_j y_j :
q_j²=0 et q_i q_j=q_j q_i. Le signe global est
gamma_n=(−1)^(n(n−1)/2), avec q_[n]=gamma_n·Omega_tilde.

Une forme directe de la chaîne est :

  P_i[t] = sum_{j:d_j=t mod N} B_ij q_j;
  A_i[f] = NTT(P_i)[f] = sum_j B_ij q_j omega^(f d_j);
  W[f] = gamma_n product_i A_i[f];
  Z[k] = INTT(W)[k].

La cible formelle est

  Z[k] = delta_(k,k*) · (sum_sigma product_i p_i,sigma(i) z^E(sigma))
                        · Omega_tilde,
  k* = (sum_j d_j) mod N.

Le symbole P_A désigne le coefficient de cette sortie; il n'est pas une
feuille ni un intermédiaire scalaire obligatoire. La préparation des
marqueurs, la fusion des facteurs orientés, les phases et les transformées
peuvent être compilées ensemble, dans un ordre réorganisé et avec partage.
Une lecture scalaire, si elle est requise, peut n'apparaître qu'en sortie.
Son implantation fait alors partie du coût total.

## Ce que le texte établit

1. Le premier filtre à orientation simple se compile par déterminant
   signé en O(n^4) portes scalaires, sans développement des monômes.
2. La double orientation conserve les amplitudes et adresses et rassemble
   les signes en gamma_n. Elle ne remplace pas B par son carré.
3. Les entrées naturelles du spectre sont les sommes de termes B_ij q_j
   groupés par d_j, définition 13.10 et proposition B.22.
4. Le §B.1 dit explicitement que V_A=gamma_n F_A=P_A Omega_tilde est la
   valeur d'un fil existant et que P_A n'est ni constante ajoutée ni oracle.
5. La phase commune omega^(f D*) permet de déplacer la modulation après
   le filtre. C'est une identité de réorganisation du DAG.
6. Le circuit raccordé de B.1–B.4 a, avec p comme feuilles, au plus
   4n²+n−2+epsilon_n+B(N) portes dans l'algèbre agrandie,
   B(N)=2N log2 N+3N−3 pour N puissance de deux, N>=2.
   La préparation depuis A ajoute 2n² portes. Avec n<N<=2n,
   ce compte est polynomial. Cette borne est déjà prouvée dans le papier.
7. B.11/B.18 donnent un compilateur aval scalaire lorsque la coordonnée
   initiale est exposée. C'est une construction suffisante à coût additif;
   elle n'impose pas cette interface à toute autre compilation globale.
8. B.19 donne une équivalence de complexité des SORTIES : un circuit
   scalaire pour la table permet de sélectionner P_A sans porte nouvelle.
   Il ne dit pas que P_A doit avoir été calculé avant le spectre.

## Cible de la suite

Construire et borner une compilation GLOBALE de la chaîne ci-dessus depuis
les données originales. Les invariants sont l'annihilation des collisions,
la conservation des amplitudes/adresses, la correction universelle et le
slot final exact. Autoriser une représentation intermédiaire compacte
dépendant des facteurs et de l'observation terminale, sans imposer les
coordonnées par sous-ensembles ni une source scalaire P_A préalable.

Si le modèle visé est celui des portes scalaires des §3/B.5, prouver
la traduction scalaire globale, constantes contrôlées et uniformité comprises.
Les produits d'éléments d'algèbre avant le degré terminal ne deviennent pas
des produits scalaires par la seule linéarité de lambda (remarque B.13).

Les expériences antérieures restent des essais sur une interface plus
restrictive ou des modèles particuliers. Leurs contre-exemples ne rejettent
pas une compilation globale intégrant le calcul spectral. L'archive
recherche_pa_2026-10-24.zip est un historique de ces essais, pas l'énoncé
actuel complet du problème de l'auteur.
