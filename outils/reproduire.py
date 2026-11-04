"""Commandes de reproduction depuis le dossier consolidé."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JOBS={
 'preuve-preparation-linearisee':('etudes/2026-11-01/linearisation-orientee-convolution/lean','replay_preparation_bound.py'),
 'canaux-determinants':('etudes/2026-11-01/linearisation-orientee-convolution/determinants','verify_determinant_channels.py'),
 'fusion-matrice-linearisee':('etudes/2026-11-01/linearisation-orientee-convolution','verify_fused_linearised.py'),
 'matrice-linearisee':('etudes/2026-11-01/linearisation-orientee-convolution','verify_linearised_inputs.py'),
 'preuve-croissance-projection':('etudes/2026-11-01/projection-avant-derivation/taille/lean','replay_growth.py'),
 'taille-projection':('etudes/2026-11-01/projection-avant-derivation/taille','verify_block_roots.py'),
 'preuve-projection':('etudes/2026-11-01/projection-avant-derivation/lean','replay_projection.py'),
 'prefixe-projete':('etudes/2026-11-01/projection-avant-derivation','verify_prefix_projection.py'),
 'projection-immediate':('etudes/2026-11-01/projection-avant-derivation','verify_direct_projection.py'),
 'taille-prefixe-direct':('etudes/2026-11-01/borne-chaine-generale/si-direct','verify_derivative_roots.py'),
 'preuve-comptage-direct':('etudes/2026-11-01/borne-chaine-generale/lean','replay_direct_dag_counting.py'),
 'recompte-fusion':('etudes/2026-11-01/borne-chaine-generale','verify_fused_cost_review.py'),
 'fusion-terminale-generale':('etudes/2026-11-01/borne-chaine-generale','verify_terminal_fusion.py'),
 'fusion-double-log':('etudes/2026-11-01/fusion-double-log','verify_fused_circuit.py'),
 'preuves-double-log':('etudes/2026-11-01/fusion-double-log/lean','replay_lean.py'),
 'logarithmes':('etudes/2026-11-01/logarithmes-chaine','verify_log_circuit.py'),
 'preuves-logarithmes':('etudes/2026-11-01/logarithmes-chaine/lean','replay_lean.py'),
 'raccord-existant':('etudes/2026-11-01/raccord-initialisation/spectral/reprise-globale','verify_shared_operator_dag.py'),
 'raccord-ad-inverse':('etudes/2026-11-01/raccord-initialisation/dualite','ad_compilation.py'),
 'raccord-action-globale':('etudes/2026-11-01/raccord-initialisation/moments/reprise-globale','verify_global_action.py'),
 'raccord-collisions':('etudes/2026-11-01/raccord-initialisation/spectral','verify_collision_spectrum.py'),
 'raccord-dual':('etudes/2026-11-01/raccord-initialisation/dualite','verify_dual.py'),
 'raccord-contractions':('etudes/2026-11-01/raccord-initialisation/moments','verify_moment_contractions.py'),
 'raccord-chirp':('etudes/2026-11-01/raccord-initialisation/spectral','verify_chirp_contraction.py'),
 'raccord-rationnel':('etudes/2026-11-01/raccord-initialisation/moments','verify_rational_contractions.py'),
 'preuves-raccord-dual':('etudes/2026-11-01/raccord-initialisation/dualite','replay_lean.py'),
 'projecteur-ntt':('etudes/2026-11-01/orbite-scalaire','verify_spectral_projector.py'),
 'orbite-scalaire':('etudes/2026-11-01/orbite-scalaire','verify_orbit_bridge.py'),
 'observateur-collisions':('etudes/2026-11-01/orbite-scalaire','verify_collision_observer.py'),
 'preuves-orbite':('etudes/2026-11-01/orbite-scalaire','replay_lean.py'),
 'schur-jet':('etudes/2026-11-01/fermeture-adaptative','verify_schur.py'),
 'preuves-schur-jet':('etudes/2026-11-01/fermeture-adaptative','replay_lean.py'),
 'resolvant-partage':('etudes/2026-11-01/fermeture-adaptative','verify_shared_resolvent.py'),
 'fusion-ntt':('etudes/2026-11-01/fusion-ntt','verify_bridge.py'),
 'preuves-fusion-ntt':('etudes/2026-11-01/fusion-ntt','replay_lean.py'),
 'transport-rationnel':('etudes/2026-11-01/reprise-flot-rationnel','verify_transport.py'),
 'preuves-transport':('etudes/2026-11-01/reprise-flot-rationnel','replay_lean.py'),
 'insertion-complete':('etudes/2026-11-01/fermeture-generale','verifier.py'),
 'preuves-insertion':('etudes/2026-11-01/fermeture-generale','replay_lean.py'),
 'lean-operateurs':('etudes/2026-11-01/lean-operateurs','verifier.py'),
 'preuves-operateurs':('etudes/2026-11-01/lean-operateurs','replay_lean.py'),
 'operateurs-horloge':('etudes/2026-11-01/operateurs-horloge','verifier.py'),
 'ntt-walsh':('etudes/2026-11-01/linearisation-mod-Q','verifier.py'),
 'reference':('etudes/2026-10-24/chaine-complete/reference','evaluate_dev.py'),
 'gaussian':('etudes/2026-10-24/chaine-complete/gaussian','evaluate_dev.py'),
 'phases':('etudes/2026-10-24/chaine-complete/phases_spectral','verify_phase_chain.py'),
 'cycles':('etudes/2026-10-24/chaine-complete/normalization','verify_trace_correction.py'),
 'residu6':('etudes/2026-10-24/chaine-complete/normalization','verify_residue6.py'),
 'hardcore':('etudes/2026-10-24/chaine-complete/phases_spectral','verify_spectral_hardcore.py')}
def run(name):
 folder,script=JOBS[name]
 p=subprocess.run([sys.executable,'-X','utf8',script],cwd=ROOT/folder,text=True,encoding='utf-8',capture_output=True)
 print(p.stdout,end='')
 if p.returncode:
  print(p.stderr,file=sys.stderr);raise SystemExit(p.returncode)
 return json.loads(p.stdout) if name in ('reference','gaussian') else {'exit_code':0}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('commande',choices=['list','run','smoke']);p.add_argument('essai',nargs='?',choices=list(JOBS));a=p.parse_args()
 if a.commande=='list':
  for k,(folder,script) in JOBS.items():print(k,':',folder+'/'+script)
 elif a.commande=='run':
  if not a.essai:p.error('préciser un essai')
  run(a.essai)
 else:
  results={name:run(name) for name in ['reference','gaussian']}
  assert results['reference']['score']==1912 and results['gaussian']['score']==3670
  print(json.dumps({'relocation_verified':True,'general_polynomial_proof':False},indent=2))
