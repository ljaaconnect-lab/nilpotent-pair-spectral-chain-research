# Recherche sur la source scalaire P_A — 24 octobre 2026

STATUT : RÉSOLUTION GÉNÉRALE NON OBTENUE.

Cette archive conserve les constructions exactes, les preuves à portée
restreinte et les vérifications de six hypothèses. Elle n'est pas une preuve
de la conjecture 1.5, ni une preuve de son impossibilité.

Le document de référence est le PDF confirmé de 63 pages
annihilation_raccord_spectral_demonstrations.pdf, SHA256
ed1f05cd132305ec98ec4f195ae395123cc4ae68e1a137ac4a78898f4d5199f4.
Son raccordement B.18 est conservé. La source scalaire polynomiale manque.

La source exacte exécutable retenue est sur la branche locale best-verified,
commit e59cbe84958d5d3968f45f5097a8b9150b910dd2. Sa taille est
(n-1)2^n+2n^2-n : elle reste exponentielle. À n=8, elle utilise 1912 portes,
contre 1920 pour la référence initiale. Elle a passé 56 cas de développement
et 99 cas indépendants (autre graine, autre nombre premier, tailles 1 à 9).
Ces tests finis ne prouvent pas une borne polynomiale.

Après extraction :
  cd source_exacte
  python evaluate_dev.py

Chaque autre répertoire conserve les notes, scripts et sorties de sa branche
exacte. Les scripts symboliques utilisent SymPy. Certains calculs de contrôle
énumèrent volontairement de petits cas; ils ne sont pas des algorithmes
polynomiaux proposés. Aucun théorème nouveau n'a été certifié dans Lean.

Les progrès constructifs comprennent une normalisation implicite qui élimine
toute occupation avec un seul indice répété, ses corrections jusqu'au degré 5,
des représentations matricielles exactes des couches 2 et 3, une resommation
des poids de correction par sommes de Gauss, et des systèmes Newton exacts
aux petites tailles. Leurs prolongements examinés ne ferment pas le cas général.

Protocole de recherche : Arbor, arbre persistant, expériences isolées,
évaluateur de développement figé et contrôle indépendant avant promotion.
L'organisation du travail a utilisé Scientific Agent Skills; sa référence
a été ajoutée : Timothy Kassis, Vinayak Agarwal, Yuhuan He, Darshil Patel,
Aubrey M. Brueckner (2026), Scientific Agent Skills: A Library of Procedural
Knowledge for Research Agents. https://doi.org/10.48550/arXiv.2609.00065
(notice vérifiée le 24 octobre 2026, dernière révision 2 septembre 2026).
Cette référence concerne le protocole, pas la validité des résultats mathématiques.
