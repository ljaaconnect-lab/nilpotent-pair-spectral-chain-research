from sonder_jordan import *
import sympy as sp

def corrected(q,K):
    u=[{():F(1)}];w=[{():F(1)} for _ in range(q)];r4=correction4(q)
    for r in range(1,K+1):
        rhs=add(*(jordan(j,w[j]) for j in range(q)))
        if r>=4:rhs=add(rhs,scale(add(mul(r4,u[r-4]),mul(u[r-4],r4)),F(1,2)))
        v=scale(rhs,F(1,r));u.append(v)
        w=[add(v,scale(jordan(j,w[j]),-1)) for j in range(q)]
    return u

def derivative(p,images):
    out=defaultdict(F)
    for word,c in p.items():
        for k,j in enumerate(word):
            for replacement,a in images[j].items():
                out[word[:k]+replacement+word[k+1:]]+=c*a
    return {w:c for w,c in out.items() if c}

if __name__=='__main__':
    q=4
    u=corrected(q,5)
    rhs=scale(add(expected(q,5),scale(u[5],-1)),5)
    r4=correction4(q)
    p={(j,):F(1) for j in range(q)}
    xx=[{(j,j):F(1)} for j in range(q)]
    xp=[add(mul({(j,):F(1)},p),mul(p,{(j,):F(1)})) for j in range(q)]
    columns=[derivative(r4,xp),derivative(r4,xx)]
    words=sorted(set(rhs).union(*(set(c) for c in columns)))
    A=sp.Matrix([[c.get(w,0) for c in columns] for w in words])
    b=sp.Matrix([rhs.get(w,0) for w in words])
    print({'equations':len(words),'rank':A.rank(),'augmented_rank':A.row_join(b).rank(),'solutions':str(sp.linsolve((A,b)))})
