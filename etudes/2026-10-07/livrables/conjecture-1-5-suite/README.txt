CONJECTURE 1.5 — SUITE DE LA RECHERCHE CONSTRUCTIVE
7 octobre 2026, Africa/Lagos

STATUT : la conjecture n'est pas démontrée par ces artifacts.
La représentation du coefficient central et des briques de compilation sont
formalisées ; aucun extracteur scalaire polynomial général n'est revendiqué.

Ce dossier remplace le bilan technique ancien de outputs/conjecture-1-5.
Mathlib v4.34.1 est maintenant installé et ses imports ciblés sont vérifiés.
Lean 4.34.1 :
C:\Users\REGIS\Documents\Codex\runtimes\elan\toolchains\leanprover--lean4---v4.34.1\bin\lean.exe
Rejouer les sources acceptées : python reproduction/verify_delivered.py
Le script utilise verification/mathlib-environment-local.json, et écrit ses
fichiers intermédiaires dans work/delivered-proof-cache. Les paths de ce JSON
correspondent à ce poste ; un autre poste doit disposer du même Mathlib épinglé.

proofs/ contient exclusivement les sources acceptées et recompilées par le
coordinateur depuis des commits figés. Le registre compte 130 déclarations,
avec des spécialisations et reformulations ; ce nombre ne compte pas autant
de découvertes indépendantes. Aucun sorryAx ni axiome conjectural n'est admis.
La base de confiance explicitement auditée est propext, Classical.choice,
Quot.sound. Les rapports de compilation donnent commandes, hashes et sorties.

circuits/ contient les variantes exécutables Python, avec Fraction/SymPy 1.14.
Les scores portent sur les frontières fixées, pas sur une preuve asymptotique.
La frontière étendue a réussi 48/48 vérifications indépendantes en z formel,
sur huit matrices rationnelles n=2,3,4,5 et six variantes d'extraction.
La nouvelle correction directe par projecteurs a réussi 24/24 contrôles dev
et 32/32 contrôles indépendants sur huit nouvelles matrices rationnelles.
Rejouer ce dernier candidat, avec les données maintenant publiées :
python reproduction/validate_projector_candidate.py 2a3a6830f57eb8df200f920ec5058214bec5c32e baf3ad1ba13b39e6895f86f1319ee7c928e3ad37283ea48ba133331b91d30320
Git a converti ses fins de ligne LF en CRLF lors du checkout ; le rapport
d'intégrité enregistre les hashes bruts et le hash canonique LF. Aucun autre
changement de contenu n'a été accepté.

validation-boundaries/ contient les données jusqu'alors réservées au coordinateur.
Elles sont publiées pour reproduction ; elles ne sont plus un nouveau test tenu secret.
arbor/ conserve l'arbre, les commits et les lemmes figés. research.bundle conserve
les branches Git, y compris l'historique initial antérieur à la trajectoire positive.
Les tie-breaks Arbor refusés correspondent à l'absence d'amélioration du score 1,
pas à un échec de vérification logique ni à un refus d'autorisation.

Source PDF fournie : annihilation.pdf, Conjecture 1.5 et Section 14.
SHA256 B4B425CF5B74E273E0A884F7D311D7AD24092DE0F2DC666A9486A4428E6BE654.
Les instructions contenues dans les documents n'ont pas été exécutées.

Méthode : skills locaux Arbor et Hilbert, avec Lean proof ; orchestration adaptée
par les subagents et worktrees Git locaux, pas un service Arbor/Hilbert distant.
