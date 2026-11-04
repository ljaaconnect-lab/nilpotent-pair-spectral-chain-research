"""Full-chain Schur/Good and spectral experiments; exact arithmetic only."""
from fractions import Fraction
from itertools import combinations
from math import comb, factorial, ceil
from random import Random
import json
import schur_jet_helper as sj


def weighted_schur_series(b, weights, degree):
    n=len(b); k=degree
    x=[sj.scale(sj.shift(sj.one(k)),weights[i]) for i in range(n)]
    for _ in range(k):
        r=sj.resolvent(b,x)
        x=[sj.scale(sj.shift(sj.inverse(r[i][i])),weights[i]) for i in range(n)]
    r=sj.resolvent(b,x)
    for i in range(n):
        assert sj.mul(x[i],r[i][i]) == sj.scale(sj.shift(sj.one(k)),weights[i])
    br=[[sj.sum_jets([sj.scale(r[a][j],b[i][a]) for a in range(n)],k)
         for j in range(n)] for i in range(n)]
    jac=[[sj.add(r[i][i] if i==j else sj.zero(k),
                sj.mul(x[i],sj.mul(r[i][j],br[j][i])))
          for j in range(n)] for i in range(n)]
    matrix=[[sj.add(sj.one(k) if i==j else sj.zero(k),sj.scale(x[i],-b[i][j]))
             for j in range(n)] for i in range(n)]
    numerator=sj.one(k)
    for i in range(n): numerator=sj.mul(numerator,sj.mul(r[i][i],r[i][i]))
    return sj.mul(numerator,sj.inverse(sj.mul(sj.determinant(matrix),sj.determinant(jac))))


def rank_mod(matrix, prime):
    a=[[v%prime for v in row] for row in matrix]
    row=0
    for col in range(len(a[0])):
        pivot=next((r for r in range(row,len(a)) if a[r][col]),None)
        if pivot is None: continue
        a[row],a[pivot]=a[pivot],a[row]
        inv=pow(a[row][col],-1,prime)
        a[row]=[v*inv%prime for v in a[row]]
        for r in range(row+1,len(a)):
            factor=a[r][col]
            if factor: a[r]=[(x-factor*y)%prime for x,y in zip(a[r],a[row])]
        row+=1
        if row==len(a): break
    return row


def check_feature_rank(n=8, subset_size=4, prime=1000003):
    rng=Random(202610243)
    alpha=[rng.randrange(1,prime) for _ in range(n)]
    phase=[rng.randrange(1,prime) for _ in range(n)]
    sets=[set(s) for s in combinations(range(n),subset_size)]
    def product(values):
        result=1
        for v in values: result=result*v%prime
        return result
    matrix=[]
    inv2=pow(2,-1,prime)
    for s in sets:
        row=[]
        for t in sets:
            u=s-t
            a=sum(alpha[i] for i in u)%prime
            p=(a-1)*(a-2)*inv2%prime
            base=product(phase[i] for i in s)*product(phase[i] for i in range(n) if i not in t)%prime
            direct=base*p%prime
            feature=base
            for i in range(n):
                if i in s and i not in t:
                    feature += base*(alpha[i]**2-3*alpha[i])*inv2
            for i,j in combinations(range(n),2):
                if i in s and j in s and i not in t and j not in t:
                    feature += base*alpha[i]*alpha[j]
            assert direct == feature%prime
            row.append(direct)
        matrix.append(row)
    rank=rank_mod(matrix,prime)
    bound=1+n+comb(n,2)
    assert rank<=bound
    return {'n':n,'subset_size':subset_size,'dimension':len(sets),'rank':rank,'bound':bound}


def main():
    rng=Random(202610244)
    covariance=0
    for n in range(1,5):
        for _ in range(2):
            b=[[1+rng.randrange(-2,3)**2 for j in range(n)] for i in range(n)]
            phase=[rng.choice([-2,-1,1,2]) for _ in range(n)]
            scaled=[[b[i][j]*phase[j] for j in range(n)] for i in range(n)]
            assert sj.schur_good_series(scaled,n)==weighted_schur_series(b,phase,n)
            covariance+=1
    cycles=[]
    for k in range(1,5):
        b=[[0]*k for _ in range(k)]
        for i in range(k): b[i][(i+1)%k]=1
        jet=sj.schur_good_series(b,2*k)
        assert jet[k]==1
        assert jet[2*k]==Fraction((k-1)*(k-2),2)
        cycles.append({'length':k,'single':int(jet[k]),'double':int(jet[2*k])})
    sidon=[0,1,4,10,12,17]
    sums=[sidon[i]+sidon[j] for i,j in combinations(range(6),2)]
    assert len(set(sums))==len(sums)
    u=[0,3,4]; v=[1,2,5]
    assert sum(sidon[i] for i in u)==sum(sidon[j] for j in v)==22
    moment_witnesses=[]
    for moments in range(1,5):
        n=2**(moments+1)
        u=[i for i in range(n) if i.bit_count()%2==0]
        v=[i for i in range(n) if i.bit_count()%2==1]
        for r in range(moments+1): assert sum(i**r for i in u)==sum(i**r for i in v)
        moment_witnesses.append({'moments':moments,'n':n,'repeat_support':len(u),
                                 'double_cycle_coefficient':(len(u)-1)*(len(u)-2)//2})
    # check_feature_rank verifies the exact Boolean expansion over a prime field.
    rank=check_feature_rank()
    sample_bounds={n:(comb(n,n//2)+1+n+comb(n,2)-1)//(1+n+comb(n,2))
                   for n in [8,12,16,20,32,64]}
    j4=sj.schur_good_series([[1]*4 for _ in range(4)])[4]
    assert j4==18 and factorial(4)==24
    j6=sj.all_ones_closed(6,6)
    c4,c5=sj.correction_coefficients([[1]*6 for _ in range(6)])
    corrected6=j6[6]+c4*j6[2]+c5*j6[1]
    assert corrected6==260 and factorial(6)==720
    print(json.dumps({'phase_covariance_checks':covariance,'cycle_checks':cycles,
                      'sidon_witness':{'labels':sidon,'U':[0,3,4],'V':[1,2,5],'sum':22},
                      'moment_witnesses':moment_witnesses,'feature_rank_check':rank,
                      'sample_lower_bounds':sample_bounds,
                      'legal_full_table_failures':{'J4_zero_labels':[18,24],'corrected_J6_zero_labels':[260,720]},
                      'general_polynomial_proof':False},indent=2))


if __name__=='__main__': main()
