"""Check scalar transport circuits against a separate finite geometric sum.

No result of these tests claims a compiler for the mixed coefficient or Z.
"""
import argparse
import hashlib
import json
from itertools import product
from math import comb
from pathlib import Path
import random
from transport import build_fusion

HERE = Path(__file__).resolve().parent


def marked_spectral_example():
    """An exact legal example: evaluating y=1 keeps a collision at target slot."""
    p, n, size, omega = 17, 3, 4, 4
    labels = [0,1,2]
    frequencies = []
    for f in range(size):
        row = {}
        for assignment in product(range(n), repeat=n):
            exponent = sum(1 << (i*n+j) for i,j in enumerate(assignment))
            phase = pow(omega,f*sum(labels[j] for j in assignment),p)
            row[exponent] = (row.get(exponent,0)+phase) % p
        frequencies.append(row)
    target_slot = sum(labels) % size
    value = {}
    for f,row in enumerate(frequencies):
        factor = pow(size,-1,p)*pow(omega,(-f*target_slot) % size,p) % p
        for exponent,coefficient in row.items():
            value[exponent] = (value.get(exponent,0)+factor*coefficient) % p
    value = {e:c for e,c in value.items() if c}
    wanted_exponents = [84,98,140,161,266,273]
    assert value == {e:1 for e in wanted_exponents+[146]}
    return {'n':n, 'a_entries':0, 'N':size, 'Q':p, 'omega':omega,
            'labels':labels, 'target_slot':target_slot, 'z_formal':True,
            'correct_exponents':wanted_exponents, 'extra_exponent_after_y_equals_one':146}


def matmul(a, b, p):
    d = len(a)
    return [[sum(a[i][k]*b[k][j] for k in range(d)) % p
             for j in range(d)] for i in range(d)]


def reference(xs, v, y, p):
    d = len(v)
    aggregate = [[sum(t*a[i][j] for t,a in zip(y,xs)) % p
                  for j in range(d)] for i in range(d)]
    power = [[int(i == j) for j in range(d)] for i in range(d)]
    inverse = [row[:] for row in power]
    for _ in range(1, d):
        power = matmul(power, aggregate, p)
        inverse = [[(a+b) % p for a,b in zip(row,other)]
                   for row,other in zip(inverse,power)]
    assert not any(x for row in matmul(power,aggregate,p) for x in row)
    ys = [matmul(inverse,a,p) for a in xs]
    w = [sum(inverse[i][j]*v[j] for j in range(d)) % p for i in range(d)]
    return [a[i][j] for a in ys for i in range(d) for j in range(i)]+w


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    rng = random.Random(2026110105)
    tests, records = 0, []
    for n in range(1, 9):
        d, q = n+1, n
        compiler, sequential, fused = build_fusion(d,q)
        records.append({'n':n, 'dimension':d, 'generators':q,
                        'state_scalars':compiler.state_size,
                        'gates_per_transport':2*(q+1)*comb(d+1,3),
                        'three_transports_and_parameter_sum':compiler.dag.gates})
        for p in (2,3,17,998244353):
            for _ in range(8):
                xs = [[[rng.randrange(p) if j < i else 0 for j in range(d)]
                       for i in range(d)] for _ in range(q)]
                v = [rng.randrange(p) for _ in range(d)]
                y, z = [[rng.randrange(p) for _ in range(q)] for _ in range(2)]
                inputs = {('A',j,i,k):xs[j][i][k] for j in range(q)
                          for i in range(d) for k in range(i)}
                inputs.update({('v',i):x for i,x in enumerate(v)})
                inputs.update({('y',j):x for j,x in enumerate(y)})
                inputs.update({('z',j):x for j,x in enumerate(z)})
                got = compiler.dag.evaluate_all(sequential+fused,inputs,p)
                want = reference(xs,v,[(a+b)%p for a,b in zip(y,z)],p)
                assert got == want+want, (n,p,got,want)
                tests += 1
    report = {'status':'passed', 'scalar_transport_fusion_cases':tests,
              'primes':[2,3,17,998244353], 'seed':2026110105,
              'records':records, 'mixed_coefficient_compiler':False,
              'general_polynomial_solution':False,
              'marked_spectral_example':marked_spectral_example(),
              'source_sha256':{name:hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                               for name in ('transport.py','verify_transport.py')},
              'scalar_dag_sha256':hashlib.sha256((HERE.parents[2]/
                'etudes/2026-10-24/chaine-complete/reference/dag.py').read_bytes()).hexdigest()}
    if args.write_report:
        (HERE/'transport-validation.json').write_text(
            json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
