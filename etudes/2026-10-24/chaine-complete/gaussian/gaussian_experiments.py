"""Exact Gaussian fusion, parity, and joint terminal-reader experiments."""

from fractions import Fraction
from functools import lru_cache
from itertools import product, permutations
import json
import random
import sympy as s
from dag import DAG,length
from pfaffian_scalar import route_terminal_component
from gaussian_layer_three import build_three,build_four


def pf(a):
    @lru_cache(None)
    def rec(indices):
        if not indices:
            return 1
        first = indices[0]
        return sum((-1)**(j+1)*a[first][indices[j]]
                   *rec(indices[1:j]+indices[j+1:]) for j in range(1,len(indices)))
    return rec(tuple(range(len(a))))


def gaussian(a):
    m = len(a)
    out = {}
    for mask in range(1<<m):
        if mask.bit_count()%2:
            continue
        inds = [i for i in range(m) if mask>>i&1]
        coeff = pf([[a[i][j] for j in inds] for i in inds])
        if coeff:
            out[mask] = coeff
    return out


def exterior_mul(a,b):
    out = {}
    for left,x in a.items():
        for right,y in b.items():
            if left & right:
                continue
            inversions = sum((right & ((1<<i)-1)).bit_count()
                             for i in range(left.bit_length()) if left>>i&1)
            mask = left | right
            out[mask] = out.get(mask,0)+(-1)**inversions*x*y
    return {key:val for key,val in out.items() if val}


def paired(a,n):
    return {mask:val for mask,val in a.items()
            if all(((mask>>(2*j))&3) in (0,3) for j in range(n))}


def fusion_check(rng,n=3):
    def kernel():
        a = [[0]*(2*n) for _ in range(2*n)]
        for i in range(2*n):
            for j in range(i+1,2*n):
                a[i][j] = rng.randrange(-3,4)
                a[j][i] = -a[i][j]
        return a
    a,b = kernel(),kernel()
    expected = exterior_mul(paired(gaussian(a),n),paired(gaussian(b),n))
    observed = {}
    for signs in product((-1,1),repeat=n-1):
        signs = signs+(1,)
        k = [[signs[i//2]*a[i][j]*signs[j//2]+b[i][j]
              for j in range(2*n)] for i in range(2*n)]
        for mask,val in paired(gaussian(k),n).items():
            observed[mask] = observed.get(mask,0)+Fraction(val,1<<(n-1))
    observed = {key:val for key,val in observed.items() if val}
    assert observed == expected
    return {'modes':2*n,'twirl_components':1<<(n-1),'exact_identity':True}


def leakage_check():
    a1,a2,b1,b2,u,v = s.symbols('a1 a2 b1 b2 u v')
    a = [[0,a1,1,0],[-a1,0,0,0],[-1,0,0,a2],[0,0,-a2,0]]
    b = [[0,b1,0,0],[-b1,0,0,1],[0,0,0,b2],[0,-1,-b2,0]]
    kernel = [[u*a[i][j]+v*b[i][j] for j in range(4)] for i in range(4)]
    direct = s.Poly(s.expand(pf(kernel)),u,v).coeff_monomial(u*v)
    assert s.expand(direct-(a1*b2+a2*b1-1)) == 0
    signs = [-1,-1,1,1]
    changed = [[u*signs[i]*a[i][j]*signs[j]+v*b[i][j]
                for j in range(4)] for i in range(4)]
    twirled = s.Poly(s.expand((pf(kernel)+pf(changed))/2),u,v).coeff_monomial(u*v)
    assert s.expand(twirled-(a1*b2+a2*b1)) == 0
    # All-ones row factors, labels (0,1), N=4, omega=i: the unwanted
    # unpaired recombination lands in the same inverse spectral slot.
    w = s.I
    bad_frequency = [w**f for f in range(4)]
    good_frequency = [2*w**f for f in range(4)]
    bad_slots = [s.simplify(sum(w**(-f*k)*bad_frequency[f] for f in range(4))/4)
                 for k in range(4)]
    good_slots = [s.simplify(sum(w**(-f*k)*good_frequency[f] for f in range(4))/4)
                  for k in range(4)]
    assert bad_slots == [0,1,0,0] and good_slots == [0,2,0,0]
    return {'naive_fusion_mixed_coefficient':str(direct),
            'twirled_coefficient':str(twirled),
            'naive_complete_table':[str(v) for v in bad_slots],
            'correct_complete_table':[str(v) for v in good_slots]}


def scalar_reader_checks(rng):
    checks = 0
    gates = {}
    prime = 65537
    for n in range(1,7):
        d = DAG()
        zero = d.const(0)
        kernel = [[zero]*(2*n) for _ in range(2*n)]
        for i in range(2*n):
            for j in range(i+1,2*n):
                kernel[i][j] = d.inp(('K',i,j))
                kernel[j][i] = d.neg(kernel[i][j])
        labels = [(-1)**j*(j+1) for j in range(n)]
        outputs = route_terminal_component(kernel,labels,d)
        gates[n] = d.gates
        for _ in range(6):
            vals = {('K',i,j):rng.randrange(-7,8) for i in range(2*n)
                    for j in range(i+1,2*n)}
            aa = [[0]*(2*n) for _ in range(2*n)]
            for i in range(2*n):
                for j in range(i+1,2*n):
                    aa[i][j] = vals['K',i,j]
                    aa[j][i] = -aa[i][j]
            target = pf(aa) % prime
            expected = [target if k==sum(labels)%length(n) else 0 for k in range(length(n))]
            assert d.evaluate_all(outputs,vals,prime) == expected
            checks += 1
    return {'numeric_complete_table_checks':checks,'gates_including_kernel_signs':gates,
            'is_original_factor_compiler':False}


def normalized_third_kernel(r,sval,a=None):
    n = len(r)
    if a is None:
        a = [1]*n
    kernel = [[0]*(2*n) for _ in range(2*n)]
    for j in range(n):
        for k in range(j+1,n):
            xx = a[j]*a[k]*(r[k]-r[j])
            yy = (sval[k]-sval[j])/3
            kernel[2*j][2*k],kernel[2*k][2*j] = xx,-xx
            kernel[2*j+1][2*k+1],kernel[2*k+1][2*j+1] = yy,-yy
        for k in range(n):
            xy = a[j]*((1 if j==k else 0)-s.Rational(1,3)+2*r[j]*sval[k])
            kernel[2*j][2*k+1],kernel[2*k+1][2*j] = xy,-xy
    return kernel


def third_layer_checks(rng):
    r = s.symbols('r0:3')
    sval = s.symbols('s0:3')
    actual = s.expand(pf(normalized_third_kernel(r,sval)))
    expected = sum(r[j]*sval[k] for j in range(3) for k in range(3) if j!=k)
    assert s.expand(actual-expected)==0
    for n in range(1,7):
        r = [s.Integer(rng.randrange(-3,4)) for _ in range(n)]
        sval = [s.Integer(rng.randrange(-3,4)) for _ in range(n)]
        target = 1-s.Rational(n,3)+(2-n)*sum(x*y for x,y in zip(r,sval))+sum(r)*sum(sval)
        assert s.expand(pf(normalized_third_kernel(r,sval))-target)==0

    labels = [-2,5,1]
    dag = DAG()
    outputs = build_three(labels,dag)
    prime = 65537
    for trial in range(12):
        p = [[rng.randrange(0,8) for _ in range(3)] for _ in range(3)]
        z = 0 if trial==0 else rng.randrange(0,prime)
        inputs = {('p',i,j):p[i][j] for i in range(3) for j in range(3)}
        inputs['z']=z
        terms = [s.prod(p[i][j]*pow(z,1<<(i*3+j),prime)
                        for i,j in enumerate(perm)) for perm in permutations(range(3))]
        target = int(sum(terms))%prime
        assert dag.evaluate_all(outputs,inputs,prime)==[target,0,0,0]
    for _ in range(2):
        inputs = {('p',i,j):rng.randrange(1,6) for i in range(3) for j in range(3)}
        expected = {}
        for perm in permutations(range(3)):
            exponent=sum(1<<(i*3+j) for i,j in enumerate(perm))
            expected[exponent]=int(s.prod(inputs['p',i,j] for i,j in enumerate(perm)))%prime
        assert dag.evaluate_polynomials(outputs,inputs,prime)==[expected,{},{},{}]
    return {'symbolic_paired_six_mode_identity':str(actual),
            'general_k_formula_checks':6,'original_input_numeric_full_table_checks':12,
            'original_input_formal_full_table_checks':2,'gates_three_row_compiler':dag.gates,
            'all_layer_fusion_established':False}


def fourth_layer_checks(rng):
    u=s.symbols('u')
    a=[s.Integer(rng.randrange(1,6)) for _ in range(4)]
    b,c,d=[[s.Integer(rng.randrange(-3,4)) for _ in range(4)] for _ in range(3)]
    kernel=normalized_third_kernel([x/y for x,y in zip(b,a)],
                                   [x/y for x,y in zip(c,a)],a)
    for j in range(4):
        kernel[2*j][2*j+1]+=u*d[j]
        kernel[2*j+1][2*j]-=u*d[j]
    polynomial=s.Poly(s.expand(pf(kernel)),u)
    expected=sum(a[p[0]]*b[p[1]]*c[p[2]]*d[p[3]] for p in permutations(range(4)))
    assert polynomial.coeff_monomial(u)==expected
    weights=[-s.Rational(25,12),4,-3,s.Rational(4,3),-s.Rational(1,4)]
    assert sum(weight*polynomial.eval(k) for k,weight in enumerate(weights))==expected
    dag=DAG()
    labels=[-3,2,6,5]
    outputs=build_four(labels,dag)
    for _ in range(3):
        p=[[rng.randrange(0,6) for _ in range(4)] for _ in range(4)]
        z=rng.randrange(1,65537)
        inputs={('p',i,j):p[i][j] for i in range(4) for j in range(4)}
        inputs['z']=z
        target=sum(s.prod(p[i][j]*pow(z,1<<(i*4+j),65537)
                          for i,j in enumerate(perm)) for perm in permutations(range(4)))
        target=int(target)%65537
        assert dag.evaluate_all(outputs,inputs,65537)==[0,0,target,0,0,0,0,0]
    return {'diagonal_jet_polynomial':str(polynomial.as_expr()),
            'target':str(expected),'interpolation_weights':list(map(str,weights)),
            'components_for_one_step':5,'exact_identity':True,
            'original_input_numeric_full_table_checks':3,'gates_four_row_compiler':dag.gates,
            'polynomial_count_after_all_rows_proved':False}


def affine_feature_witness():
    r=[3,1,1,3]
    sval=[1,3,5,7]
    choices=[[5,1,7,3],[3,7,1,5]]
    grams=[]
    values=[]
    triples=[]
    for t in choices:
        features=s.Matrix([[1,r[j],sval[j],t[j]] for j in range(4)])
        grams.append(features.T*features)
        values.append(sum(r[i]*sval[j]*t[k] for i,j,k in permutations(range(4),3)))
        triples.append(sum(r[j]*sval[j]*t[j] for j in range(4)))
    assert grams[0]==grams[1] and values==[744,792]
    return {'r':r,'s':sval,'t_choices':choices,'common_gram':[[int(x) for x in row] for row in grams[0].tolist()],
            'triple_moments':triples,'target_permanents':values,
            'scope':'constant J plus U C U^T, endpoint-affine U, constant C; '
                    'no obstruction to data-dependent diagonal or nonlinear/global features'}


if __name__ == '__main__':
    rng = random.Random(2026102434)
    print(json.dumps({'unpaired_leakage':leakage_check(),
                      'parity_fusion':[fusion_check(rng,n) for n in range(1,5)],
                      'scalar_gaussian_reader':scalar_reader_checks(rng),
                      'single_gaussian_third_layer':third_layer_checks(rng),
                      'fourth_layer_diagonal_jet':fourth_layer_checks(rng),
                      'affine_feature_witness':affine_feature_witness()},indent=2))
