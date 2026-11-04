CONJECTURE 1.5 — CONTINUATION n63 à n68, 7 octobre 2026
Ce dossier est un complément de conjecture-1-5-suite ; il ne prétend pas
résoudre la conjecture. Lire statut.txt pour distinguer preuve, calcul fini,
coût local et obligation de compression générale.

Reproduction sur ce poste, avec Python, SymPy 1.14 et Mathlib/Lean 4.34.1 :
python reproduction/verify_delivered.py
python reproduction/verify_local_pfaffian.py
Les scripts écrivent leurs rapports dans work/pfaffian-delivered-*, sans
modifier les sources livrées. Les chemins de l'environnement Mathlib sont
ceux de ce poste ; un autre poste doit fournir le même environnement épinglé.
La frontière publiée vérifie uniquement des identités locales positives.
Le manifeste SHA256 contrôle les bytes effectivement livrés, y compris
leurs fins de ligne. L'incident n64 explique la normalisation Git du protocole.

Les commits des branches nommées arbor/n63 à arbor/n68 sont conservés dans
research.bundle, l'arbre Arbor et verification. Le bundle Git est vérifié.
Les scores locaux sont distincts du score de preuve racine.
Les refus de merge au score égal 1 ne sont pas des refus d'autorisation.

Méthode : adaptations locales des skills Arbor, Hilbert et lean-proof,
subagents isolés dans des worktrees Git ; pas d'exécution d'un service distant.
Référence logicielle ajoutée, record arXiv courant consulté le 7 octobre 2026 :
Kassis, Timothy; Agarwal, Vinayak; He, Yuhuan; Patel, Darshil;
Brueckner, Aubrey M. (2026). Scientific Agent Skills: A Library of Procedural
Knowledge for Research Agents. arXiv:2609.00065, record courant v2.
https://doi.org/10.48550/arXiv.2609.00065

Référence mathématique consultée pour l'interface de sommation :
Okada, Soichi. Pfaffian Formulas and Schur Q-Function Identities.
Advances in Mathematics 353 (2019), 446–470, Lemma 3.1 et Theorem 3.4.
https://doi.org/10.1016/j.aim.2019.07.006
Ces théorèmes ne fournissent pas dans ce dossier la projection synchronisée.
Les dérivations du blueprint sont explicitement marquées informelles.

Nouvelle preuve autonome : proofs/HadamardPfaffian.lean (trois théorèmes).
Pour ne vérifier que ce nouveau source inchangé depuis le rejeu du commit :
python reproduction/verify_delivered.py --source HadamardPfaffian.lean
Les lemmes Möbius déjà livrés ont leur propre rapport de compilation.
Les quatre déclarations n67 incluent la définition gaussian4 auditée ;
le total de déclarations n'est pas un total de résultats indépendants.
positive-frontier contient les constructions partielles, leurs versions,
protocoles et contraintes. Le fichier LocalGadget.lean de ce dossier est
un brouillon non compilé conservé pour le contrôle du gel des sources ;
seuls les sources dans proofs sont des preuves acceptées. Aucun objectif
racine n'est clos.
