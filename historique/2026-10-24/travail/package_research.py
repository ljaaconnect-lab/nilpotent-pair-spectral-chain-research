"""Package immutable research records; this archive is not a solution claim."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from zipfile import ZIP_DEFLATED, ZipFile

work = Path(__file__).resolve().parent
repo = work / 'scalar-search'
refs = {
    'source_exacte': 'e59cbe84958d5d3968f45f5097a8b9150b910dd2',
    'normalisation_implicite': '2f1469d11038dc93af89dffda05a8eca3fb74fe0',
    'jets_et_mineurs_principaux': '00d55927fff7d1e7b05b1f68ee8b97ce3859a1d1',
    'remontee_et_newton': sys.argv[1],
}

def git(*args):
    return subprocess.check_output(['git', '-C', str(repo), *args])

readme = '''# Recherche sur la source scalaire P_A — 24 octobre 2026

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
'''

out = work.parent / 'outputs' / 'recherche_pa_2026-10-24.zip'
out.parent.mkdir(exist_ok=True)
manifest = {'general_polynomial_solution': False, 'commits': refs, 'sha256': {}}
with ZipFile(out, 'w', ZIP_DEFLATED) as archive:
    def add(name, data):
        archive.writestr(name, data)
        manifest['sha256'][name] = hashlib.sha256(data).hexdigest()
    add('LIRE_D_ABORD.md', readme.encode('utf-8'))
    for folder, ref in refs.items():
        names = git('ls-tree', '-r', '--name-only', ref).decode().splitlines()
        for name in names:
            if name.endswith(('.py', '.md', '.json', '.txt')):
                add(folder + '/' + name, git('show', ref + ':' + name))
    for name in ('ROOT_PROOFS.md', 'verify_subset_representations.py',
                 'verification.json', 'baseline-gate.json', 'projector-gate.json'):
        add('coordinateur/' + name, (work / name).read_bytes())
    for path in sorted((repo / '.arbor').rglob('*')):
        if path.is_file():
            add('arbre/' + path.relative_to(repo / '.arbor').as_posix(), path.read_bytes())
    archive.writestr('manifest.json', json.dumps(manifest, indent=2).encode())
with ZipFile(out) as archive:
    assert archive.testzip() is None
    for name, digest in manifest['sha256'].items():
        assert hashlib.sha256(archive.read(name)).hexdigest() == digest
print(json.dumps({'archive': str(out), 'files': len(manifest['sha256']) + 1,
                  'bytes': out.stat().st_size, 'general_polynomial_solution': False}))
