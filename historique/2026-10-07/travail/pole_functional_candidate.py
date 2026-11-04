"""Positive exact synthesis of a scalar functional on low-degree pole encodings.

The factorial development enumeration is never claimed as a root constructor.
"""
import hashlib
import itertools
import json
import time
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parent

def roots(n, variant):
    if variant == 'additive':
        return [[(n+1)*(i+1)+(j+1) for j in range(n)] for i in range(n)]
    if variant == 'squared_additive':
        return [[((n+1)*(i+1)+(j+1))**2 for j in range(n)] for i in range(n)]
    if variant == 'radix':
        return [[(n+1)**(i+1)+(j+1) for j in range(n)] for i in range(n)]
    raise ValueError(variant)

def complement_polynomial(theta, sigma):
    coeff = [1]
    for i, row in enumerate(theta):
        for j, x in enumerate(row):
            if j == sigma[i]:
                continue
            updated = [0] * (len(coeff)+1)
            for k, c in enumerate(coeff):
                updated[k] -= x*c
                updated[k+1] += c
            coeff = updated
    return coeff

def synthesize(n, variant):
    start = time.monotonic()
    theta = roots(n, variant)
    assert len({x for row in theta for x in row}) == n*n
    permutations = list(itertools.permutations(range(n)))
    data = [complement_polynomial(theta, s) for s in permutations]
    signs = [(-1)**sum(s[i]>s[j] for i in range(n) for j in range(i+1,n)) for s in permutations]
    width = n*n-n+1
    augmented = sp.Matrix([r+[s] for r,s in zip(data, signs)])
    reduced, pivots = augmented.rref()
    fits = width not in pivots
    functional = None
    if fits:
        functional = [sp.Rational(0)]*width
        for row, pivot in enumerate(pivots):
            functional[pivot] = reduced[row,width]
        assert all(sum(c*l for c,l in zip(row,functional)) == s for row,s in zip(data, signs))
    return {
        'variant': variant, 'n': n, 'degree': width-1,
        'development_permutations': len(permutations), 'exact_functional_found': fits,
        'functional': [str(x) for x in functional] if functional is not None else None,
        'initialization': 'Finite development RREF; not a uniform all-n constructor',
        'elapsed_seconds': time.monotonic()-start,
        'root_conjecture_verified': False,
    }

def main():
    protocol_path = ROOT / 'n72-protocol.json'
    frozen_path = ROOT / 'n72-source-freeze.json'
    frozen = json.loads(frozen_path.read_text(encoding='utf-8'))
    for filename, expected in frozen['sha256'].items():
        actual = hashlib.sha256((ROOT/filename).read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit('Source freeze changed: '+filename)
    protocol = json.loads(protocol_path.read_text(encoding='utf-8'))
    results = []
    for variant in protocol['candidate_variants']:
        for n in [2,3,4,5]:
            result = synthesize(n, variant)
            results.append(result)
            print(json.dumps(result), flush=True)
    report = {
        'node': 'n72', 'evaluated_candidate_variants': 3,
        'results': results, 'supporting_fit_count': sum(r['exact_functional_found'] for r in results),
        'dev_root_score': 0.0, 'root_obligations_closed': 0,
        'heldout_runs': 0, 'formal_compiler_invocations': 0,
        'source_freeze': frozen, 'root_conjecture_verified': False,
        'constraint': 'A positive root formula requires a polynomial-size coefficient functional satisfying all permutation identities, plus a charged uniform constructor. Finite RREF fits alone do not establish it.'
    }
    (ROOT/'n72-dev-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
