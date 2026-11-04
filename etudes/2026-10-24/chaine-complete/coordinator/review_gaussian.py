"""Coordinator checks of the exact, frozen Gaussian partial construction.

No fit is used. The permutation reference and recursive scalar Pfaffian are
independent of the submitted trace/jet reader. This does not test an all-n
polynomial compiler: none is submitted.
"""
from functools import lru_cache
from itertools import combinations, permutations
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
SNAPSHOT = HERE/'wt-gaussian-review'
if not SNAPSHOT.exists():
    SNAPSHOT = HERE.parent/'gaussian'
sys.path.insert(0, str(SNAPSHOT))
from dag import DAG, length, marked_inputs
from gaussian_layer_three import build_three, build_four, third_layer_kernel

PRIME = 786433
rng = random.Random(84702961)


def target(rows):
    return sum(prod(rows[i][j] for i,j in enumerate(perm))
               for perm in permutations(range(len(rows)))) % PRIME


def prod(values):
    out = 1
    for value in values:
        out = out * value % PRIME
    return out


def jetmul(a,b):
    return tuple(sum(a[i]*b[k-i] for i in range(k+1)) % PRIME
                 for k in range(len(a)))


def pfjet(matrix):
    order = len(matrix[0][0])
    @lru_cache(None)
    def recur(indices):
        if not indices:
            return (1,) + (0,)*(order-1)
        out = [0]*order
        for j in range(1,len(indices)):
            term = jetmul(matrix[indices[0]][indices[j]],
                          recur(indices[1:j]+indices[j+1:]))
            for k in range(order):
                out[k] = (out[k] + (-1)**(j+1)*term[k]) % PRIME
        return tuple(out)
    return recur(tuple(range(len(matrix))))


numeric, formal = 0, 0
counts = {}
for n,builder in [(3,build_three),(4,build_four)]:
    for case in range(5):
        labels = ([0]*n if case==0 else [-3*j-1 for j in range(n)]
                  if case==1 else [rng.randrange(-60,61) for _ in range(n)])
        dag = DAG()
        outputs = builder(labels,dag)
        counts[n] = dag.gates
        values = {('p',i,j):1+rng.randrange(-20,21)**2
                  for i in range(n) for j in range(n)}
        values['z'] = [0,1,PRIME-1,rng.randrange(PRIME),rng.randrange(PRIME)][case]
        marked = [[values['p',i,j]*pow(values['z'],1<<(i*n+j),PRIME) % PRIME
                   for j in range(n)] for i in range(n)]
        expected = [0]*length(n)
        expected[sum(labels)%length(n)] = target(marked)
        assert dag.evaluate_all(outputs,values,PRIME)==expected
        numeric += 1
        if n==3 and case==2:
            poly = {sum(1<<(i*n+j) for i,j in enumerate(perm)):
                    prod(values['p',i,j] for i,j in enumerate(perm))
                    for perm in permutations(range(n))}
            expected_poly = [{} for _ in range(length(n))]
            expected_poly[sum(labels)%length(n)] = poly
            assert dag.evaluate_polynomials(outputs,values,PRIME)==expected_poly
            formal += 1

# One constructed kernel must represent ALL triples of six columns.
dag = DAG()
b = marked_inputs(6,dag)
ring,kernel = third_layer_kernel(b[:3],dag,order=3)
flat = [coord for row in kernel for jet in row for coord in jet]
triple_checks = 0
for case in range(3):
    values = {('p',i,j):rng.randrange(-12,13)
              for i in range(6) for j in range(6)}
    values['z'] = [0,1,rng.randrange(2,PRIME)][case]
    observed = iter(dag.evaluate_all(flat,values,PRIME))
    numeric_kernel = [[tuple(next(observed) for _ in range(4))
                       for _ in range(12)] for _ in range(12)]
    for subset in combinations(range(6),3):
        modes = [mode for j in subset for mode in (2*j,2*j+1)]
        minor = [[numeric_kernel[i][j] for j in modes] for i in modes]
        rows = [[values['p',i,j]*pow(values['z'],1<<(i*6+j),PRIME)%PRIME
                 for j in subset] for i in range(3)]
        assert sum(pfjet(minor))%PRIME == target(rows)
        triple_checks += 1

result = {'commit':'3fa7c389ff85ef17640e8241f241849bfd578045',
          'numeric_full_table_checks':numeric,
          'formal_full_table_checks':formal,
          'all_triples_of_six_columns_checks':triple_checks,
          'charged_gate_counts':counts,
          'all_n_polynomial_fusion_proved':False}
(HERE/'gaussian-independent.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
