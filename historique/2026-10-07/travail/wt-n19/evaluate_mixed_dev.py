"""Frozen positive mixed-derivative evaluator v1; generic B, n=2,3,4,5.

Five exact checks per n: eager chain, demand chain, Bell cycles, all F-prefix
jets, and all future-resolvent G-prefix jets. Score is an assertion fraction.
"""
import json
import hashlib
from pathlib import Path
from time import perf_counter
import sympy as sp
import mixed_derivative as md


def main():
    rows, passed, total = [], 0, 0
    for n in (2, 3, 4, 5):
        started = perf_counter()
        source, F, snapshots, construction = md.build_rank_one_chain(n)
        full = (1 << n)-1
        expected = md.permanent_on_subset(source.symbols, n, tuple(range(n)))
        eager, coordinates, eager_stats = md.compile_eager(source)
        eager_values = eager.evaluate()
        eager_output = coordinates[F][full]
        demand, demand_output, demand_stats = md.compile_demand(source, F, full)
        demand_values = demand.evaluate()
        bell, bell_output, bell_stats = md.build_cycle_bell(n)
        bell_values = bell.evaluate()
        layers = md.verify_layers(source, snapshots, coordinates, eager_values)
        checks = {'eager_permanent': sp.expand(eager_values[eager_output]-expected) == 0,
                  'demand_permanent': sp.expand(demand_values[demand_output]-expected) == 0,
                  'bell_permanent': sp.expand(bell_values[bell_output]-expected) == 0,
                  'all_F_prefix_jets': layers['all_F_prefix_coefficients_exact'],
                  'all_G_prefix_jets': layers['all_G_prefix_path_coefficients_exact']}
        passed += sum(checks.values())
        total += len(checks)
        if n in (2, 5):
            Path(f'mixed-demand-n{n}-dag.json').write_text(
                json.dumps(demand.serialize(demand_output), indent=2)+'\n')
        rows.append({'n': n, 'checks': checks, 'construction': construction,
                     'eager': eager_stats, 'demand': demand_stats,
                     'bell': {'scalar_gates': bell.gates, **bell_stats},
                     'layers': layers, 'generic_permanent_terms': len(sp.Poly(expected).terms()),
                     'seconds': perf_counter()-started})
    report = {'protocol': 'positive-mixed-dev-v1', 'split': 'dev',
              'score': passed/total, 'passed': passed, 'total': total,
              'evaluator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'artifact_sha256': hashlib.sha256(Path(md.__file__).read_bytes()).hexdigest(),
              'cases': rows,
              'scope': 'Exact generic formal-B finite checks; scalar jet gates charged; no Lean proof.'}
    Path('dev-mixed.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'score': report['score'], 'passed': passed, 'total': total,
                      'evaluator_sha256': report['evaluator_sha256'],
                      'cases': [{'n': row['n'], 'checks': row['checks'],
                                 'native_gates': row['construction']['native_gates'],
                                 'eager_gates': row['eager']['compiled_gates'],
                                 'demand_gates': row['demand']['compiled_gates'],
                                 'bell_gates': row['bell']['scalar_gates'],
                                 'peak_states': row['layers']['peak_retained_scalar_states'],
                                 'seconds': row['seconds']} for row in rows]}, indent=2))


if __name__ == '__main__':
    main()
