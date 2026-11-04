"""Add one unit to the shared corrected core, retaining the native INTT graph.

The new output represents delta_(k,k*) * (1 + Y*Omega). Its top coefficient
is unchanged, but evaluation at zero auxiliary coordinates returns 1, not Y.
The original compiler and the original output roots remain available.
"""
from __future__ import annotations

from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT / 'documents/composition-native-2026-11-03'))
from compose_native_representatives import compile_native_representatives


def compile_with_unit(n, Q, N, omega, labels, budget=1_000_000):
    original = compile_native_representatives(n, Q, N, omega, labels, budget)
    dag = original['dag']
    core = original['corrected']
    prefix = dag.reachable([core])
    lifted_core = dag.add(dag.one, core)
    # Substitute one internal wire; all ancestors remain the SAME existing nodes.
    # This copies only the affected spectral descendants into the same DAG store.
    outputs = dag.substitute(original['outputs'], {core: lifted_core})
    spectra = dag.substitute(original['spectra'], {core: lifted_core})
    reachable = dag.reachable(outputs)
    assert prefix <= reachable
    assert dag.count([lifted_core]) == dag.count([core]) + 1
    bound = original['metadata']['true_INTT_bound'] + 1
    assert dag.count(outputs) <= bound <= 29 * n**3 + 1
    assert dag.derivative_calls == dag.collision_operator_calls == 0
    metadata = {
        'n': n, 'Q': Q, 'N': N, 'omega': omega,
        'target': original['metadata']['routing_index'],
        'added_core_gates': 1,
        'shared_prefix_preserved': True,
        'original_useful_gates': dag.count(original['outputs']),
        'lifted_useful_gates': dag.count(outputs),
        'bound': bound, 'cubic_bound': 29 * n**3 + 1,
        'native_intt_constructions': dag.intt_calls,
        'spectral_suffix_method': 'Same native INTT topology with the shared core wire replaced',
        'exact_oriented_output_preserved': False,
        'top_coefficient_preserved': True,
        'output_at_zero_auxiliary_target': 1,
        'scalar_a_z_only_output_constructed': False,
    }
    return {'original': original, 'dag': dag, 'lifted_core': lifted_core,
            'spectra': spectra, 'outputs': outputs, 'metadata': metadata}


if __name__ == '__main__':
    import json
    sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(compile_with_unit(2, 5, 4, 2, [0, 1])['metadata'], indent=2))
