"""Exact certificates for flag permanents and principal-minor repairs."""

import itertools
import json
import sympy as s


def permanent(a):
    if not a:
        return s.Integer(1)
    return sum(a[0][j]*permanent([row[:j]+row[j+1:] for row in a[1:]])
               for j in range(len(a)))


def branch_certificate(center):
    # Triple cycles containing vertex 1 have sum 2*center. All diagonal
    # entries are 1 and all opposite edge products are -1.
    radical = s.sqrt(center**2+1)
    roots = [-center+radical, -center-radical]
    out = []
    for bits in itertools.product(range(2), repeat=3):
        x,y,z = [roots[v] for v in bits]
        matrix = s.Matrix([[1,1,1,1],[-1,1,x,y],
                           [-1,-x-2*center,1,z],
                           [-1,-y-2*center,-z-2*center,1]])
        anchor = [s.simplify(matrix.extract((0,i,j),(0,i,j)).det())
                  for i,j in itertools.combinations(range(1,4),2)]
        triple = s.simplify(matrix.extract((1,2,3),(1,2,3)).det())
        det = s.simplify(matrix.det())
        assert anchor == [4+2*center]*3
        out.append({'choices':bits,'anchor_triples':[str(v) for v in anchor],
                    'triple_234':str(triple),'determinant':str(det)})
    return out


def layered_formula_checks():
    aa = s.symbols('a0:3', nonzero=True)
    bb = s.symbols('b0:3')
    cc = s.symbols('c0:3')
    diag = s.diag(*aa)
    layer2 = diag+s.ones(3,1)*s.Matrix([[bb[j]-aa[j]/2 for j in range(3)]])
    for i,j in itertools.combinations(range(3),2):
        assert s.expand(layer2.extract((i,j),(i,j)).det()-aa[i]*bb[j]-aa[j]*bb[i]) == 0
    rr = [bb[j]/aa[j] for j in range(3)]
    ss = [cc[j]/aa[j] for j in range(3)]
    u = s.Matrix([[1,rr[j]] for j in range(3)])
    v = s.Matrix([[-s.Rational(1,2),2*ss[j]] for j in range(3)])
    layer3 = diag*(s.eye(3)+u*v.T)
    result = layer3.det()+s.prod(aa)/2
    assert s.factor(result-permanent([list(aa),list(bb),list(cc)])) == 0
    # Continuation to layer four produces all seven nonempty row moments.
    rr4,ss4,qq4 = [s.symbols(f'{label}0:4') for label in ('r','s','q')]
    expected = sum(rr4[i]*ss4[j]*qq4[k]
                   for i,j,k in itertools.permutations(range(4),3))
    R,S,Q = map(sum,(rr4,ss4,qq4))
    RS = sum(rr4[i]*ss4[i] for i in range(4))
    RQ = sum(rr4[i]*qq4[i] for i in range(4))
    SQ = sum(ss4[i]*qq4[i] for i in range(4))
    RSQ = sum(rr4[i]*ss4[i]*qq4[i] for i in range(4))
    continued = R*S*Q-Q*RS-R*SQ-S*RQ+2*RSQ
    assert s.expand(continued-expected) == 0
    return {'layer_two_single_determinant':True,
            'layer_three_two_determinants':True,
            'layer_four_seven_moment_continuation':True}


if __name__ == '__main__':
    all_ones = branch_certificate(1)
    proper_only = branch_certificate(2)
    assert {v['determinant'] for v in all_ones} == {'20'}
    assert {v['triple_234'] for v in all_ones} == {'6','-10'}
    assert {v['triple_234'] for v in proper_only} == {'8','-72'}
    print(json.dumps({'all_ones_four_by_four':all_ones,
                      'proper_layers_counterexample':proper_only,
                      'layered_repairs':layered_formula_checks()},indent=2))
