"""Exact jets for the implicit Schur-self-energy/Good experiment.

These small tests use permutation determinants to stay independent of a
claimed fast determinant compiler. The note supplies the polynomial jet
compiler for the proposed scalar, whose target identity fails at n=4.
"""
from fractions import Fraction
from itertools import permutations, combinations
from math import factorial
from random import Random
import json


def zero(k): return [Fraction(0)] * (k+1)
def one(k): return [Fraction(1)] + [Fraction(0)] * k

def add(a,b): return [x+y for x,y in zip(a,b)]
def neg(a): return [-x for x in a]
def scale(a,c): return [x*c for x in a]

def mul(a,b):
    k=len(a)-1
    return [sum(a[j]*b[i-j] for j in range(i+1)) for i in range(k+1)]

def inverse(a):
    assert a[0] == 1
    result=[Fraction(1)]
    for i in range(1,len(a)):
        result.append(-sum(a[j]*result[i-j] for j in range(1,i+1)))
    return result

def shift(a): return [Fraction(0)] + a[:-1]

def matmul(a,b):
    n=len(a); k=len(a[0][0])-1
    return [[sum_jets([mul(a[i][r],b[r][j]) for r in range(n)],k)
             for j in range(n)] for i in range(n)]

def sum_jets(values,k):
    result=zero(k)
    for value in values: result=add(result,value)
    return result

def resolvent(b,x):
    n=len(b); k=len(x[0])-1
    # R_0=I, R_s=sum_{a=1}^s X_a B R_{s-a}; exact coefficient recurrence.
    coeffs=[[[Fraction(int(i==j)) for j in range(n)] for i in range(n)]]
    for s in range(1,k+1):
        coeffs.append([[sum(x[i][a]*b[i][r]*coeffs[s-a][r][j]
                           for a in range(1,s+1) for r in range(n))
                        for j in range(n)] for i in range(n)])
    return [[[coeffs[s][i][j] for s in range(k+1)] for j in range(n)] for i in range(n)]

def determinant(a):
    n=len(a); k=len(a[0][0])-1
    result=zero(k)
    for p in permutations(range(n)):
        inversions=sum(p[i]>p[j] for i in range(n) for j in range(i+1,n))
        value=scale(one(k),(-1)**inversions)
        for i,j in enumerate(p): value=mul(value,a[i][j])
        result=add(result,value)
    return result

def schur_good_series(b,degree=None):
    n=len(b); k=n if degree is None else degree
    x=[shift(one(k)) for _ in range(n)]
    for iteration in range(k):
        r=resolvent(b,x)
        x=[shift(inverse(r[i][i])) for i in range(n)]
    r=resolvent(b,x)
    for i in range(n): assert mul(x[i],r[i][i]) == shift(one(k))
    br=[[sum_jets([scale(r[a][j],b[i][a]) for a in range(n)],k)
         for j in range(n)] for i in range(n)]
    jac=[[add(r[i][i] if i==j else zero(k),mul(x[i],mul(r[i][j],br[j][i])))
          for j in range(n)] for i in range(n)]
    matrix=[[add(one(k) if i==j else zero(k),scale(x[i],-b[i][j]))
             for j in range(n)] for i in range(n)]
    numerator=one(k)
    for i in range(n): numerator=mul(numerator,mul(r[i][i],r[i][i]))
    result=mul(numerator,inverse(mul(determinant(matrix),determinant(jac))))
    return result

def permanent(b):
    total=0
    for p in permutations(range(len(b))):
        value=1
        for i,j in enumerate(p): value*=b[i][j]
        total+=value
    return total


def polynomial_power(p,n,k):
    result=one(k)
    padded=[Fraction(x) for x in p]+[Fraction(0)]*(k+1-len(p))
    for _ in range(n): result=mul(result,padded)
    return result


def all_ones_closed(n,k):
    # t=r(1+r)/(1+n r); Lagrange inversion for the exact Good scalar.
    numerator=mul(polynomial_power([1,n],1,k),polynomial_power([1,1],2*n,k))
    denominator=mul(polynomial_power([1,2],n-1,k),polynomial_power([1,2,n],1,k))
    g=mul(numerator,inverse(denominator))
    result=[Fraction(1)]
    derivative=[Fraction((i+1))*g[i+1] for i in range(k)]+[Fraction(0)]
    for m in range(1,k+1):
        psi=mul(polynomial_power([1,n],m,k),inverse(polynomial_power([1,1],m,k)))
        result.append(mul(derivative,psi)[m-1]/m)
    return result


def correction_coefficients(b):
    n=len(b); d=[b[i][i] for i in range(n)]
    a=[[b[i][j]*b[j][i] if i!=j else 0 for j in range(n)] for i in range(n)]
    r=[sum(row) for row in a]
    c4=sum(a[i][j]*d[i]*d[j] for i in range(n) for j in range(i+1,n))
    s2=sum(d[i]*a[i][j]**2 for i in range(n) for j in range(n))
    dar=sum(d[i]*a[i][j]*r[j] for i in range(n) for j in range(n))
    edge=sum(a[i][j]*d[i]*d[j]*(d[i]+d[j]) for i in range(n) for j in range(i+1,n))
    triangle=sum(d[i]*b[i][j]*d[j]*b[j][k]*b[k][i]
                 for i in range(n) for j in range(n) for k in range(n)
                 if i!=j and j!=k and k!=i)
    c5=dar-2*s2-edge+triangle
    return c4,c5


def principal_permanents(b,k):
    return sum(permanent([[b[i][j] for j in s] for i in s])
               for s in combinations(range(len(b)),k))


def main():
    rng=Random(202610242)
    tests=[]
    for n in range(1,6):
        for case in range(3):
            b=[[1+rng.randrange(-2,3)**2 for j in range(n)] for i in range(n)]
            observed=schur_good_series(b)[n]
            expected=permanent(b)
            c4,c5=correction_coefficients(b)
            if n<=3: assert observed==expected
            elif n==4: assert observed==expected-c4
            else: assert observed==expected-c4*sum(b[i][i] for i in range(n))-c5
            jets=schur_good_series(b,max(n,4))
            assert jets[4]+c4 == principal_permanents(b,4)
            if n==5:
                assert jets[5]+c4*jets[1]+c5 == expected
            tests.append({'n':n,'observed':int(observed),'permanent':expected,
                          'difference':int(observed-expected)})
    closed=[]
    for n in range(1,9):
        values=all_ones_closed(n,max(n,2))
        if n<=4:
            generic=schur_good_series([[1]*n for _ in range(n)],max(n,2))
            assert generic==values
        closed.append({'n':n,'coefficient':int(values[n]),'permanent':factorial(n)})
    assert closed[3]['coefficient']==18 and closed[3]['permanent']==24
    c4,c5=correction_coefficients([[1]*6 for _ in range(6)])
    j6=all_ones_closed(6,6)
    corrected6=j6[6]+c4*j6[2]+c5*j6[1]
    assert corrected6==260 and factorial(6)==720
    print(json.dumps({'random_checks':tests,'all_ones_closed':closed,
                      'degree_six_after_corrections':{'coefficient':int(corrected6),'permanent':720},
                      'candidate_target_identity':False,
                      'global_polynomial_proof':False},indent=2))

if __name__=='__main__': main()
