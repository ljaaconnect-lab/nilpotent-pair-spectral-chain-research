"""Exact cycle-resummation and overlapping-cycle tests, with mixed phases.

This is a research verifier, not a claimed permanent compiler.  All its
arithmetic is rational.  The scalar jet cost is proved in the companion note;
the small independent Schur verifier uses permutation determinants.
"""
from fractions import Fraction as Q
from math import factorial
from random import Random
import json
import schur_jet_helper as sj
from verify_joint import weighted_schur_series


def binomial(z, k):
    value = Q(1)
    for j in range(k):
        value *= Q(z-j, j+1)
    return value


def log_jet(f):
    assert f[0] == 1
    result = sj.zero(len(f)-1)
    for m in range(1, len(f)):
        result[m] = f[m] - sum((j*result[j]*f[m-j] for j in range(1,m)),Q(0))/m
    return result


def exp_jet(f):
    assert f[0] == 0
    result = sj.one(len(f)-1)
    for m in range(1, len(f)):
        result[m] = sum(j*f[j]*result[m-j] for j in range(1,m+1))/m
    return result


def cycle_series(length, degree, weight=1):
    result = sj.one(degree)
    for r in range(1, degree//length+1):
        result[length*r] = weight**r * (-1)**r * binomial(length*(r-1)-1,r)
    return result


def trace_constants(degree):
    beta = {}
    for r in range(2, degree+1):
        for h in range(1, degree//r+1):
            g = [Q(1)] + [(-1)**j*binomial(h*(j-1)-1,j) for j in range(1,r+1)]
            target_log = Q((-1)**(r+1),r)
            discrepancy = target_log-log_jet(g)[r]
            beta[h,r] = discrepancy/h - sum(beta[h*d,r//d]
                for d in range(2,r+1) if r%d==0 and r//d>=2)
    return beta


def matrix_product(a,b):
    n=len(a)
    return [[sum(a[i][r]*b[r][j] for r in range(n)) for j in range(n)]
            for i in range(n)]


def trace_exponent(b, degree, weights=None):
    n=len(b)
    weights = [1]*n if weights is None else weights
    beta = trace_constants(degree)
    result = sj.zero(degree)
    for r in range(2,degree+1):
        a = [[(weights[i]*b[i][j])**r for j in range(n)] for i in range(n)]
        power = [[Q(int(i==j)) for j in range(n)] for i in range(n)]
        for h in range(1,degree//r+1):
            power=matrix_product(power,a)
            result[h*r] += beta[h,r]*sum(power[i][i] for i in range(n))
    return result


def bouquet_series(cycles, degree):
    """Each (h,c) denotes a cycle length and its weighted product c.

    All cycles share one vertex; their remaining vertices are disjoint.
    This includes a length-one loop at the common vertex.
    """
    rs=[]
    result=sj.one(degree)
    for h,c in cycles:
        s=sj.zero(degree)
        if h<=degree: s[h]=Q(c)
        r=sj.zero(degree)
        for _ in range(degree):
            one_r=sj.add(sj.one(degree),r)
            inverse_power=sj.one(degree)
            for _ in range(h-1): inverse_power=sj.mul(inverse_power,sj.inverse(one_r))
            r=sj.mul(s,inverse_power)
        rs.append(r)
        numerator=sj.one(degree)
        for _ in range(h): numerator=sj.mul(numerator,sj.add(sj.one(degree),r))
        denominator=sj.add(sj.one(degree),sj.scale(r,h))
        result=sj.mul(result,sj.mul(numerator,sj.inverse(denominator)))
    prefactor=sj.add(sj.one(degree),sj.sum_jets(rs,degree))
    return sj.mul(prefactor,result)


def bouquet_correction(cycles,degree):
    target=sj.one(degree)
    for h,c in cycles:
        if h<=degree: target[h]+=c
    return sj.mul(target,sj.inverse(bouquet_series(cycles,degree)))


def zero_diagonal_residual6(b):
    """Residual after the isolated-cycle trace correction, universally at d=6."""
    n=len(b)
    assert all(b[i][i]==0 for i in range(n))
    a=[[b[i][j]*b[j][i] for j in range(n)] for i in range(n)]
    r=[sum(row) for row in a]
    s=[sum(v*v for v in row) for row in a]
    a3=matrix_product(matrix_product(a,a),a)
    return (2*sum(x*y for x,y in zip(r,s))
            - Q(3,2)*sum(v**3 for row in a for v in row)
            + sum(a3[i][i] for i in range(n))
            - Q(1,2)*sum(r[i]*a[i][j]*r[j] for i in range(n) for j in range(n)))


def cycle_incidence_series(n, cycles, degree):
    """Unit-series message closure; exact when the cycle-incidence graph is a forest.

    The returned Bethe expression on a graph with loops is explicitly only a
    candidate. Each cycle is (tuple of its vertices, weighted edge product).
    No hidden enumeration of cycles occurs inside this routine.
    """
    incidence=[[] for _ in range(n)]
    activities=[]
    for c,(vertices,weight) in enumerate(cycles):
        for v in vertices: incidence[v].append(c)
        activity=sj.zero(degree)
        if len(vertices)<=degree: activity[len(vertices)]=Q(weight)
        activities.append(activity)
    m={(v,c):sj.one(degree) for c,(vs,_) in enumerate(cycles) for v in vs}
    for _ in range(degree+1):
        u={}
        for c,(vs,_) in enumerate(cycles):
            for v in vs:
                message=activities[c]
                for w in vs:
                    if w!=v: message=sj.mul(message,m[w,c])
                u[c,v]=message
        new_m={}
        for v,c in m:
            denominator=sj.one(degree)
            for d in incidence[v]:
                if d!=c: denominator=sj.add(denominator,u[d,v])
            new_m[v,c]=sj.inverse(denominator)
        m=new_m
    numerator=sj.one(degree)
    for v in range(n):
        factor=sj.one(degree)
        for c in incidence[v]: factor=sj.add(factor,u[c,v])
        numerator=sj.mul(numerator,factor)
    for c,(vs,_) in enumerate(cycles):
        selected=activities[c]
        for v in vs: selected=sj.mul(selected,m[v,c])
        numerator=sj.mul(numerator,sj.add(sj.one(degree),selected))
    denominator=sj.one(degree)
    for v,c in m:
        denominator=sj.mul(denominator,sj.add(sj.one(degree),sj.mul(u[c,v],m[v,c])))
    return sj.mul(numerator,sj.inverse(denominator))


def cycle_partition(n,cycles,degree):
    """Independent exponential verifier, not part of the proposed scalar rule."""
    result=sj.zero(degree)
    for mask in range(1<<len(cycles)):
        used=set(); weight=Q(1); valid=True
        for c,(vertices,value) in enumerate(cycles):
            if mask>>c&1:
                if used.intersection(vertices): valid=False; break
                used.update(vertices); weight*=value
        if valid and len(used)<=degree: result[len(used)]+=weight
    return result


def as_ints(values):
    assert all(v.denominator==1 for v in values)
    return [int(v) for v in values]


def main():
    degree=18
    beta=trace_constants(degree)
    cycle_checks=0
    for h in range(1,degree+1):
        for weight in [1,2,-3]:
            exponent=sj.zero(degree)
            for (k,l),value in beta.items():
                if k%h==0:
                    exponent[k*l]+=value*h*weight**(k*l//h)
            corrected=sj.mul(cycle_series(h,degree,weight),exp_jet(exponent))
            expected=sj.one(degree)
            if h<=degree: expected[h]=Q(weight)
            assert corrected==expected
            cycle_checks+=1
    # Two independent blocks preserve all mixed degrees, not just one target.
    disjoint=[(2,3),(3,-2),(4,5)]
    original=sj.one(degree); exponent=sj.zero(degree); expected=sj.one(degree)
    for h,c in disjoint:
        original=sj.mul(original,cycle_series(h,degree,c))
        block=sj.one(degree); block[h]=c; expected=sj.mul(expected,block)
        for (k,l),value in beta.items():
            if k%h==0: exponent[k*l]+=value*h*c**(k*l//h)
    assert sj.mul(original,exp_jet(exponent))==expected
    # Exact Schur determinant against the bouquet formula, retaining phases.
    bouquet_checks=[]
    cases=[([[0,2,3],[1,0,0],[1,0,0]], [(2,2),(2,3)]),
           ([[0,2,3,0],[1,0,0,0],[0,0,0,5],[1,0,0,0]],[(2,2),(3,15)]),
           ([[7,2,3],[1,0,0],[1,0,0]],[(1,7),(2,2),(2,3)])]
    for b,cycles in cases:
        k=8
        observed=sj.schur_good_series(b,k)
        assert observed==bouquet_series(cycles,k)
        target=sj.one(k)
        for h,c in cycles: target[h]+=c
        assert sj.mul(observed,bouquet_correction(cycles,k))==target
        bouquet_checks.append({'cycles':cycles,'degree':k,'jets':as_ints(observed)})
    phase=[-2,3,5]
    b=cases[0][0]
    phased_cycles=[(2,2*phase[0]*phase[1]),(2,3*phase[0]*phase[2])]
    assert weighted_schur_series(b,phase,8)==bouquet_series(phased_cycles,8)
    # The bouquet rule extends to an arbitrary forest of cycle blocks.
    cactus_cycles=[((0,1),2),((1,2),-3),((2,3),5)]
    cactus=cycle_incidence_series(4,cactus_cycles,12)
    assert cactus==cycle_partition(4,cactus_cycles,12)
    assert cactus[:5]==[1,0,4,0,10]
    # Directly compare to the original matrix's marked principal permanents.
    cactus_b=[[0,2,0,0],[1,0,-3,0],[0,1,0,5],[0,0,1,0]]
    for d in range(5): assert cactus[d]==sj.principal_permanents(cactus_b,d)
    cactus_good=sj.schur_good_series(cactus_b,8)
    cactus_corrector=sj.mul(cactus[:9],sj.inverse(cactus_good))
    assert sj.mul(cactus_good,cactus_corrector)==cactus[:9]
    # This natural message closure does not extend to cyclic incidence.
    triangle_cycles=[((0,1),1),((0,2),1),((1,2),1),
                     ((0,1,2),1),((0,2,1),1)]
    bethe=cycle_incidence_series(3,triangle_cycles,8)
    triangle_target=cycle_partition(3,triangle_cycles,8)
    assert bethe!=triangle_target
    # Generic loopless degree-six correction, with arbitrary entry signs.
    rng=Random(202610245)
    residual_checks=[]
    for n in range(2,5):
        for _ in range(3):
            b=[[0 if i==j else rng.randrange(-3,4) for j in range(n)] for i in range(n)]
            g=sj.schur_good_series(b,6)
            exponent=trace_exponent(b,6)
            assert exponent[:6]==sj.zero(5)
            residual=g[6]+exponent[6]
            assert residual==zero_diagonal_residual6(b)
            residual_checks.append({'n':n,'residual':int(residual)})
    star=cases[0][0]
    star_residual=zero_diagonal_residual6(star)
    assert star_residual==2*2*3+2*3*3==30
    dense=[[0,1,1],[1,0,1],[1,1,0]]
    assert sj.schur_good_series(dense,6)[6]+trace_exponent(dense,6)[6]==9
    # A small bouquet resummation is not a general matrix correction.
    # Keep the exact legal dense J6 test as a full-chain failure at zero labels.
    j6=sj.all_ones_closed(6,6)
    c4,c5=sj.correction_coefficients([[1]*6 for _ in range(6)])
    k6=trace_exponent([[1]*6 for _ in range(6)],6)[6]
    corrected=j6[6]+c4*j6[2]+c5*j6[1]+k6
    assert k6==-55 and corrected==205 and factorial(6)==720
    print(json.dumps({'cycle_checks':cycle_checks,'disjoint_cycle_jet_degree':degree,
        'nonzero_beta_through_degree_six':{str(key):str(value) for key,value in beta.items()
                                          if key[0]*key[1]<=6 and value},
        'bouquet_checks':bouquet_checks,'bouquet_phase_check':True,
        'cactus_degree_twelve':as_ints(cactus),
        'cyclic_incidence_candidate':{'observed':as_ints(bethe),
                                     'target':as_ints(triangle_target)},
        'loopless_residual_checks':residual_checks,
        'overlap_counterexamples':{'weighted_star_residual6':int(star_residual),
                                  'bidirected_triangle_residual6':9},
        'legal_J6_after_c4_c5_cycle_correction':{'observed':int(corrected),'target':720},
        'general_polynomial_proof':False},indent=2))


if __name__=='__main__': main()
