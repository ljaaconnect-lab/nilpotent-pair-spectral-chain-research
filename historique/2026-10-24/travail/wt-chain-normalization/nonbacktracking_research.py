"""Two explicit polynomial-jet nonbacktracking research candidates.

Neither formula is installed as candidate.build without a target invariant.
All operations below are exact scalar rational operations. Matrix inverses
are only unit-series inverses; no input-dependent scalar division is used.
"""
from fractions import Fraction as Q
from itertools import combinations
import json
import schur_jet_helper as s
from verify_trace_correction import trace_constants, exp_jet, log_jet
from verify_trace_correction import matrix_product
from verify_trace_correction import trace_exponent, zero_diagonal_residual6
from verify_trace_correction import bouquet_series


def prod(jets,k):
    result=s.one(k)
    for jet in jets: result=s.mul(result,jet)
    return result


def determinant(matrix):
    n=len(matrix)
    if not n: raise ValueError('use the empty determinant explicitly')
    k=len(matrix[0][0])-1
    a=[[v[:] for v in row] for row in matrix]
    value=s.one(k)
    for i in range(n):
        assert a[i][i][0]==1
        pivot=a[i][i]
        value=s.mul(value,pivot)
        inv=s.inverse(pivot)
        for j in range(i+1,n):
            factor=s.mul(a[j][i],inv)
            for h in range(i+1,n): a[j][h]=s.add(a[j][h],s.neg(s.mul(factor,a[i][h])))
    return value


def det_one_minus(t,k):
    if not t: return s.one(k)
    return determinant([[s.add(s.one(k) if i==j else s.zero(k),s.neg(t[i][j]))
                         for j in range(len(t))] for i in range(len(t))])


def sqrt_unit(f):
    assert f[0]==1
    out=s.one(len(f)-1)
    for m in range(1,len(f)):
        out[m]=(f[m]-sum((out[j]*out[m-j] for j in range(1,m)),Q(0)))/2
    return out


def zeta_quotient(t,k):
    square=[[s.mul(v,v) for v in row] for row in t]
    return s.mul(det_one_minus(square,k),s.inverse(det_one_minus(t,k)))


def bass_determinant(u,n,k):
    """Exact weighted Ihara--Bass reduction, with every denominator a unit."""
    matrix=[[s.one(k) if i==j else s.zero(k) for j in range(n)] for i in range(n)]
    factors=[]
    for i,j in combinations(range(n),2):
        pair=s.mul(u[i,j],u[j,i])
        denominator=s.add(s.one(k),s.neg(pair))
        factors.append(denominator)
        inv=s.inverse(denominator)
        diagonal=s.mul(pair,inv)
        matrix[i][i]=s.add(matrix[i][i],diagonal)
        matrix[j][j]=s.add(matrix[j][j],diagonal)
        matrix[i][j]=s.neg(s.mul(u[i,j],inv))
        matrix[j][i]=s.neg(s.mul(u[j,i],inv))
    return s.mul(prod(factors,k),determinant(matrix))


def bass_quotient(u,n,k):
    square={e:s.mul(value,value) for e,value in u.items()}
    return s.mul(bass_determinant(square,n,k),s.inverse(bass_determinant(u,n,k)))


def edge_operator(weights,n,k):
    # All n(n-1) states are retained, even if a weight happens to vanish.
    edges=[(i,j) for i in range(n) for j in range(n) if i!=j]
    return [[weights[i,j,h] if j==g and h!=i else s.zero(k)
             for g,h in edges] for i,j in edges]


def matching_messages(b,k):
    n=len(b)
    monomer=[s.add(s.one(k),s.scale(s.shift(s.one(k)),b[i][i])) for i in range(n)]
    a={(i,j):s.scale(s.shift(s.shift(s.one(k))),b[i][j]*b[j][i])
       for i in range(n) for j in range(n) if i!=j}
    h={(i,j):s.one(k) for i,j in a}
    for _ in range(k+1):
        h={(i,j):s.inverse(s.add(monomer[i],s.sum_jets(
            [s.mul(a[i,v],h[v,i]) for v in range(n) if v!=i and v!=j],k))) for i,j in h}
    vertex=[s.add(monomer[i],s.sum_jets([s.mul(a[i,j],h[j,i])
                                       for j in range(n) if j!=i],k)) for i in range(n)]
    q={(i,j):s.mul(a[i,j],s.mul(h[i,j],h[j,i])) for i,j in a}
    z=s.mul(prod(vertex,k),s.inverse(prod([s.add(s.one(k),q[i,j])
                                         for i,j in combinations(range(n),2)],k)))
    return z,h,q


def formula_one(b,k):
    """Matching messages + directed loops + parity-correct dimer loops."""
    n=len(b)
    z,h,q=matching_messages(b,k)
    u={(i,j):s.scale(s.shift(h[j,i]),b[i][j]) for i,j in h}
    minus={key:s.neg(value) for key,value in q.items()}
    correction=s.add(bass_quotient(u,n,k),s.add(s.neg(sqrt_unit(bass_quotient(q,n,k))),
                                                sqrt_unit(bass_quotient(minus,n,k))))
    return s.mul(z,correction)


def gaussian_good_bethe(b,k):
    """Good density formed from Gaussian cavity messages and their Jacobian.

    It is exactly the original Good density on every bidirected forest,
    including arbitrary diagonal entries. The derivative messages here
    differentiate with respect to x, not the supplied w=t specialization.
    """
    n=len(b); edges=[(i,j) for i in range(n) for j in range(n) if i!=j]
    a={(i,j):b[i][j]*b[j][i] for i,j in edges}
    x=[s.shift(s.one(k)) for _ in range(n)]
    h={e:s.one(k) for e in edges}
    for _ in range(2*k+3):
        d=[s.add(s.one(k),s.scale(x[i],-b[i][i])) for i in range(n)]
        u={(i,j):s.scale(s.mul(x[i],x[j]),a[i,j]) for i,j in edges}
        denominator=[s.add(d[i],s.neg(s.sum_jets([s.mul(u[i,j],h[j,i])
                          for j in range(n) if i!=j],k))) for i in range(n)]
        x_new=[s.shift(denominator[i]) for i in range(n)]
        h_new={(i,j):s.inverse(s.add(d[i],s.neg(s.sum_jets([s.mul(u[i,v],h[v,i])
                    for v in range(n) if v!=i and v!=j],k)))) for i,j in edges}
        x,h=x_new,h_new
    d=[s.add(s.one(k),s.scale(x[i],-b[i][i])) for i in range(n)]
    u={(i,j):s.scale(s.mul(x[i],x[j]),a[i,j]) for i,j in edges}
    denominator=[s.add(d[i],s.neg(s.sum_jets([s.mul(u[i,j],h[j,i])
                  for j in range(n) if i!=j],k))) for i in range(n)]
    g=[s.inverse(v) for v in denominator]
    for i in range(n): assert s.mul(x[i],g[i])==s.shift(s.one(k))
    # h derivatives are an affine contraction with coefficients O(t^2).
    dh={(i,j,l):s.zero(k) for i,j in edges for l in range(n)}
    for _ in range(k+1):
        new={}
        for i,j in edges:
            for l in range(n):
                value=s.scale(s.one(k),b[i][i] if i==l else 0)
                for v in range(n):
                    if v==i or v==j: continue
                    direct=s.add(s.scale(x[v],int(i==l)),s.scale(x[i],int(v==l)))
                    value=s.add(value,s.scale(s.add(s.mul(direct,h[v,i]),
                                  s.mul(s.mul(x[i],x[v]),dh[v,i,l])),a[i,v]))
                new[i,j,l]=s.mul(s.mul(h[i,j],h[i,j]),value)
        dh=new
    jac=[]
    for i in range(n):
        row=[]
        for l in range(n):
            value=s.scale(s.one(k),b[i][i] if i==l else 0)
            for v in range(n):
                if v==i: continue
                direct=s.add(s.scale(x[v],int(i==l)),s.scale(x[i],int(v==l)))
                value=s.add(value,s.scale(s.add(s.mul(direct,h[v,i]),
                              s.mul(s.mul(x[i],x[v]),dh[v,i,l])),a[i,v]))
            dg=s.mul(s.mul(g[i],g[i]),value)
            row.append(s.add(g[i] if i==l else s.zero(k),s.mul(x[i],dg)))
        jac.append(row)
    q=prod(denominator,k)
    edge_factors=prod([s.add(s.one(k),s.neg(s.mul(u[i,j],s.mul(h[i,j],h[j,i]))))
                       for i,j in combinations(range(n),2)],k)
    f=s.mul(edge_factors,s.inverse(q))
    result=s.mul(f,s.mul(prod([s.mul(v,v) for v in g],k),s.inverse(determinant(jac))))
    return result


def nonbacktracking_trace_correction(b,k):
    n=len(b)
    beta=trace_constants(k); out=s.zero(k)
    for r in range(2,k+1):
        degree=k//r
        weights={(i,j):s.scale(s.shift(s.one(degree)),Q(b[i][j])**r)
                 for i in range(n) for j in range(n) if i!=j}
        logarithm=log_jet(bass_determinant(weights,n,degree))
        for length in range(1,degree+1):
            out[length*r]-=beta[length,r]*length*logarithm[length]
    return out


def scalar_schur_good(b,k):
    """Polynomial implementation; the imported permutation version is only a check."""
    n=len(b); x=[s.shift(s.one(k)) for _ in range(n)]
    for _ in range(k):
        r=s.resolvent(b,x)
        x=[s.shift(s.inverse(r[i][i])) for i in range(n)]
    r=s.resolvent(b,x)
    br=[[s.sum_jets([s.scale(r[a][j],b[i][a]) for a in range(n)],k)
         for j in range(n)] for i in range(n)]
    jac=[[s.add(r[i][i] if i==j else s.zero(k),s.mul(x[i],s.mul(r[i][j],br[j][i])))
          for j in range(n)] for i in range(n)]
    original=[[s.add(s.one(k) if i==j else s.zero(k),s.scale(x[i],-b[i][j]))
               for j in range(n)] for i in range(n)]
    numerator=prod([s.mul(r[i][i],r[i][i]) for i in range(n)],k)
    return s.mul(numerator,s.inverse(s.mul(determinant(original),determinant(jac))))


def formula_two(b,k):
    good=scalar_schur_good(b,k)
    gb=gaussian_good_bethe(b,k)
    matching,_,_=matching_messages(b,k)
    correction=exp_jet(nonbacktracking_trace_correction(b,k))
    return s.mul(good,s.mul(matching,s.mul(s.inverse(gb),correction)))


def first_residual6(b):
    n=len(b)
    assert all(b[i][i]==0 for i in range(n))
    b2=matrix_product(b,b); b3=matrix_product(b2,b)
    a=[[b[i][j]*b[j][i] for j in range(n)] for i in range(n)]
    a3=matrix_product(matrix_product(a,a),a)
    triangle_edge=[[b[i][j]*b2[j][i] for j in range(n)] for i in range(n)]
    return (sum(b3[i][i]**2 for i in range(n))
            -sum(v*v for row in triangle_edge for v in row)
            -2*sum(triangle_edge[i][j]*triangle_edge[j][i] for i in range(n) for j in range(n))
            +sum(a3[i][i] for i in range(n)))


def second_residual6(b):
    n=len(b)
    assert all(b[i][i]==0 for i in range(n))
    a=[[b[i][j]*b[j][i] for j in range(n)] for i in range(n)]
    a3=matrix_product(matrix_product(a,a),a)
    return Q(4,3)*sum(a3[i][i] for i in range(n))


def repair_degree_six(values,b):
    """Proven d=6 repair via the prior exact occupation identities, no permanent call."""
    assert len(values)>6 and all(b[i][i]==0 for i in range(len(b)))
    target6=(scalar_schur_good(b,6)[6]+trace_exponent(b,6)[6]
             -zero_diagonal_residual6(b))
    exponent=s.zero(len(values)-1)
    exponent[6]=target6-values[6]
    return s.mul(values,exp_jet(exponent))


def verify_gaussian_bass(b,k,phases):
    n=len(b)
    x=[s.scale(s.shift(s.one(k)),v) for v in phases]
    d=[s.add(s.one(k),s.scale(x[i],-b[i][i])) for i in range(n)]
    a={(i,j):s.scale(s.mul(x[i],x[j]),b[i][j]*b[j][i])
       for i in range(n) for j in range(n) if i!=j}
    h={e:s.one(k) for e in a}
    for _ in range(k+1):
        h={(i,j):s.inverse(s.add(d[i],s.neg(s.sum_jets([s.mul(a[i,v],h[v,i])
             for v in range(n) if v!=i and v!=j],k)))) for i,j in a}
    full=[s.add(d[i],s.neg(s.sum_jets([s.mul(a[i,j],h[j,i])
                                    for j in range(n) if i!=j],k))) for i in range(n)]
    pair={(i,j):s.mul(a[i,j],s.mul(h[i,j],h[j,i])) for i,j in a}
    q_bethe=s.mul(prod(full,k),s.inverse(prod([s.add(s.one(k),s.neg(pair[i,j]))
                                            for i,j in combinations(range(n),2)],k)))
    u={(i,j):s.scale(s.mul(x[i],h[j,i]),b[i][j]) for i,j in a}
    original=[[s.add(s.one(k) if i==j else s.zero(k),s.scale(x[i],-b[i][j]))
               for j in range(n)] for i in range(n)]
    exact=determinant(original)
    assert exact==s.mul(q_bethe,bass_determinant(u,n,k))
    return True


def exact_target(b,k):
    return [Q(s.principal_permanents(b,d)) if d<=len(b) else Q(0) for d in range(k+1)]


def report(values):
    return [str(v) if v.denominator!=1 else int(v) for v in values]


def main():
    cases={
        'weighted_tree':[[2,2,3],[1,-1,0],[1,0,4]],
        'directed_triangle':[[0,2,0],[0,0,3],[5,0,0]],
        'bidirected_triangle':[[0,2,3],[5,0,7],[11,13,0]],
        'bidirected_square_with_diagonal':[[1,2,0,3],[5,2,7,0],[0,11,3,13],[17,0,19,4]],
        'mixed_bouquet_2_3':[[0,2,3,0],[1,0,0,0],[0,0,0,5],[1,0,0,0]],
        'directed_bouquet_3_3':[[0,2,0,3,0],[0,0,5,0,0],[1,0,0,0,0],
                               [0,0,0,0,7],[1,0,0,0,0]],
        'legal_J4':[[1]*4 for _ in range(4)],
    }
    results=[]
    for name,b in cases.items():
        k=8
        target=exact_target(b,k)
        first=formula_one(b,k)
        second=formula_two(b,k)
        results.append({'name':name,'target':report(target),'formula_one':report(first),
                        'formula_two':report(second),
                        'first_error_one':next((i for i in range(k+1) if first[i]!=target[i]),None),
                        'first_error_two':next((i for i in range(k+1) if second[i]!=target[i]),None)})
        if name in ['weighted_tree','directed_triangle','bidirected_triangle','bidirected_square_with_diagonal']:
            assert first==target,(name,first,target)
        if name in ['weighted_tree','directed_triangle']:
            assert second==target,(name,second,target)
    # Independent edge-state determinant verifies the Bass reduction.
    b=cases['bidirected_triangle']; k=6; n=len(b)
    _,h,_=matching_messages(b,k)
    u={(i,j):s.scale(s.shift(h[j,i]),b[i][j]) for i,j in h}
    transitions={(i,j,v):u[j,v] for i in range(n) for j in range(n) for v in range(n)
                 if i!=j and j!=v and i!=v}
    assert bass_determinant(u,n,k)==det_one_minus(edge_operator(transitions,n,k),k)
    assert bass_quotient(u,n,k)==zeta_quotient(edge_operator(transitions,n,k),k)
    # Generic dense, asymmetric matrices test the proposed d=6 identities.
    from random import Random
    rng=Random(202610246)
    residuals=[]
    for n in [3,4,5]:
        b=[[0 if i==j else rng.randrange(1,4) for j in range(n)] for i in range(n)]
        first=formula_one(b,6); second=formula_two(b,6)
        target=exact_target(b,6)
        assert first[:6]==target[:6] and second[:6]==target[:6]
        assert first[6]==first_residual6(b)
        assert second[6]==second_residual6(b)
        assert repair_degree_six(first,b)==target
        assert repair_degree_six(second,b)==target
        assert verify_gaussian_bass(b,6,list(range(1,n+1)))
        residuals.append({'n':n,'first':int(first[6]),'second':int(second[6])})
    # Full-cycle phase factors are retained: column phases change activities.
    phase=[-2,3,5]
    phased=[[cases['bidirected_triangle'][i][j]*phase[j] for j in range(3)] for i in range(3)]
    assert formula_one(phased,8)==exact_target(phased,8)
    assert scalar_schur_good(phased,6)==s.schur_good_series(phased,6)
    legal6=formula_one([[1]*6 for _ in range(6)],6)[6]
    assert legal6==1800
    legal5=formula_two([[1]*5 for _ in range(5)],5)[5]
    assert legal5==60
    bouquet9=s.mul(bouquet_series([(3,10),(3,21)],9),
                    exp_jet(nonbacktracking_trace_correction(cases['directed_bouquet_3_3'],9)))[9]
    assert bouquet9==2*10*21*(10+21)==13020
    assert verify_gaussian_bass([[1,2,5],[10,1,2],[2,5,1]],8,[-2,3,5])
    print(json.dumps({'experiments':results,'bass_reduction_exact':True,
                      'generic_residual6_checks':residuals,'unicyclic_phase_check':True,
                      'gaussian_bass_general_checks':4,
                      'legal_J6_terminal_counterexample':{'observed':int(legal6),'target':720},
                      'legal_J5_formula_two_counterexample':{'observed':int(legal5),'target':120},
                      'formula_two_bouquet_degree_nine_error':int(bouquet9),
                      'uniform_polynomial_identity':False},indent=2))


if __name__=='__main__': main()
