"""New clock/Jordan operator ansatz; NOT a valid general-chain compiler.

Every operation is compiled to the ordinary scalar DAG.  The quartic
counterterm makes the construction exact through order four, but the
general closure is not established and fails already at order five.
"""
from fractions import Fraction as F
from pathlib import Path
from math import factorial
import importlib.util

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('operator_scalar_dag',ROOT/'etudes/2026-10-24/chaine-complete/reference/dag.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class Algebra:
    def __init__(self,dag,d):
        self.dag,self.d=dag,d
        self.constants={}
        self.z=self.c(0)
        self.o=self.c(1)
    def c(self,x):
        x=F(x)
        if x not in self.constants:self.constants[x]=self.dag.const(x)
        return self.constants[x]
    def plus(self,a,b):
        if a==self.z:return b
        if b==self.z:return a
        return self.dag.add(a,b)
    def times(self,a,b):
        if a==self.z or b==self.z:return self.z
        if a==self.o:return b
        if b==self.o:return a
        return self.dag.mul(a,b)
    def zero(self):return [[self.z]*self.d for _ in range(self.d)]
    def identity(self):return [[self.o if i==j else self.z for j in range(self.d)] for i in range(self.d)]
    def add(self,*xs):
        out=self.zero()
        for x in xs:
            out=[[self.plus(out[i][j],x[i][j]) for j in range(self.d)] for i in range(self.d)]
        return out
    def scale(self,x,c):
        c=self.c(c)
        return [[self.times(c,v) for v in row] for row in x]
    def sub(self,x,y):return self.add(x,self.scale(y,-1))
    def mul(self,x,y):
        out=self.zero()
        for i in range(self.d):
            for j in range(self.d):
                out[i][j]=self.z
                for k in range(self.d):
                    out[i][j]=self.plus(out[i][j],self.times(x[i][k],y[k][j]))
        return out
    def comm(self,x,y):return self.sub(self.mul(x,y),self.mul(y,x))
    def jordan(self,x,y):return self.scale(self.add(self.mul(x,y),self.mul(y,x)),F(1,2))


def quartic(xs,a):
    p=a.add(*xs)
    p2=a.add(*(a.mul(x,x) for x in xs))
    pp=a.mul(p,p)
    t1=a.add(*(a.comm(x,a.comm(x,a.sub(pp,a.add(a.mul(x,p),a.mul(p,x),p2)))) for x in xs))
    t2=a.sub(a.add(*(a.mul(a.comm(x,p),a.comm(x,p)) for x in xs)),
             a.add(*(a.mul(a.comm(x,y),a.comm(x,y)) for x in xs for y in xs)))
    t3=a.add(*(a.sub(a.mul(a.mul(x,a.mul(a.sub(p,x),a.sub(p,x))),x),
                         a.mul(a.mul(a.sub(p,x),a.mul(x,x)),a.sub(p,x))) for x in xs))
    return a.scale(a.add(t1,a.scale(t2,-2),a.scale(t3,2)),F(1,24))


def build(n,labels,prime=998244353,generator=3,correct4=True,from_a=True):
    N=1 << n.bit_length()
    if prime<=max(n,3) or (prime-1)%N:raise ValueError('Need Q>max(n,3), N dividing Q-1')
    omega=pow(generator,(prime-1)//N,prime)
    if pow(omega,N,prime)!=1 or pow(omega,N//2,prime)==1:raise ValueError('wrong root order')
    dag=mod.DAG()
    a=Algebra(dag,n+1)
    if from_a:
        raw=[[dag.inp(('a',i,j)) for j in range(n)] for i in range(n)]
        p=[[a.plus(a.o,a.times(x,x)) for x in row] for row in raw]
    else:p=[[dag.inp(('p',i,j)) for j in range(n)] for i in range(n)]
    z=[dag.inp('z')]
    for _ in range(n*n-1):z.append(a.times(z[-1],z[-1]))
    b=[[a.times(p[i][j],z[i*n+j]) for j in range(n)] for i in range(n)]
    frequency=[]
    for f in range(N):
        xs=[]
        for j in range(n):
            x=a.zero()
            phase=a.c(pow(omega,f*labels[j],prime))
            for i in range(n):x[i+1][i]=a.times(b[i][j],phase)
            xs.append(x)
        r4=quartic(xs,a) if correct4 and n>=4 else a.zero()
        u=[a.identity()]
        w=[a.identity() for _ in xs]
        for r in range(1,n+1):
            rhs=a.add(*(a.jordan(x,wj) for x,wj in zip(xs,w)))
            if correct4 and r>=4:rhs=a.add(rhs,a.jordan(r4,u[r-4]))
            ur=a.scale(rhs,F(1,r))
            u.append(ur)
            w=[a.sub(ur,a.jordan(x,wj)) for x,wj in zip(xs,w)]
        frequency.append(a.times(a.c(factorial(n)),u[n][n][0]))

    def inverse(values):
        m=len(values)
        if m==1:return values
        e,o=inverse(values[::2]),inverse(values[1::2])
        lo,hi=[],[]
        for j in range(m//2):
            t=a.times(a.c(pow(omega,(-j*(N//m))%N,prime)),o[j])
            lo.append(a.plus(e[j],t))
            hi.append(a.plus(e[j],a.times(a.c(-1),t)))
        return lo+hi
    outputs=[a.times(a.c(F(1,N)),x) for x in inverse(frequency)]
    return dag,outputs,{'n':n,'N':N,'gates':dag.gates,'matrix_dimension':n+1,
                        'quartic_repair':correct4,'general_validity':False}
