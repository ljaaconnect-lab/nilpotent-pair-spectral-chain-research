"""Exploratory endpoint-local Gaussian ansatz; no correctness claim from fitting.

K[j,k] = delta[j,k] d(v_j) J2 + W(v_j) H W(v_k)^T,
where v_j=(1,r_j,s_j,q_j), W has v_j in each mode's own four
coordinates, and H is a constant skew 8x8 matrix. 32 rational unknowns
would give a polynomial homogeneous-coordinate construction if an exact
identity were found. Numerical non-convergence is not an impossibility proof.
"""
import itertools
import json
import numpy as np
from scipy.optimize import least_squares


def matchings(indices):
    if not indices:
        yield 1,[]
        return
    for j in range(1,len(indices)):
        for sign,pairs in matchings(indices[1:j]+indices[j+1:]):
            yield (-1)**(j+1)*sign,[(indices[0],indices[j])]+pairs


EDGES = list(itertools.combinations(range(8),2))
EDGE_INDEX = {edge:i for i,edge in enumerate(EDGES)}
TERMS = [(sign,[EDGE_INDEX[e] for e in pairs])
         for sign,pairs in matchings(tuple(range(8)))]


def dataset(rng,n):
    points = rng.integers(-2,3,size=(n,4,3)).astype(float)
    v = np.concatenate([np.ones((n,4,1)),points],axis=2)
    features = np.zeros((n,28,32))
    for edge,(u,w) in enumerate(EDGES):
        j,k = u//2,w//2
        if j==k:
            features[:,edge,:4] = v[:,j]
        for h,(p,q) in enumerate(EDGES):
            if p//4==u%2 and q//4==w%2:
                features[:,edge,4+h] += v[:,j,p%4]*v[:,k,q%4]
            if q//4==u%2 and p//4==w%2:
                features[:,edge,4+h] -= v[:,j,q%4]*v[:,k,p%4]
    target = np.zeros(n)
    for j,k,l in itertools.permutations(range(4),3):
        target += points[:,j,0]*points[:,k,1]*points[:,l,2]
    return features,target


def values_jacobian(parameters,features):
    entries = np.einsum('sep,p->se',features,parameters)
    values = np.zeros(len(features))
    edge_gradient = np.zeros(entries.shape)
    for sign,inds in TERMS:
        term = entries[:,inds]
        values += sign*np.prod(term,axis=1)
        for k,edge in enumerate(inds):
            others = [j for j in range(4) if j!=k]
            edge_gradient[:,edge] += sign*np.prod(term[:,others],axis=1)
    jacobian = np.einsum('se,sep->sp',edge_gradient,features)
    return values,jacobian


def run():
    rng = np.random.default_rng(2026102435)
    features,target = dataset(rng,160)
    test_features,test_target = dataset(rng,160)
    initial = np.zeros(32)
    initial[0]=1
    initial[3]=1
    initial[4+EDGE_INDEX[0,1]]=1
    initial[4+EDGE_INDEX[4,6]]=1/3
    initial[4+EDGE_INDEX[0,4]]=-1/3
    initial[4+EDGE_INDEX[1,6]]=2
    out = []
    for seed in range(3):
        x0=initial if seed==0 else rng.normal(0,0.4,size=32)
        result = least_squares(lambda x:values_jacobian(x,features)[0]-target,
                               x0,jac=lambda x:values_jacobian(x,features)[1],
                               max_nfev=250,ftol=1e-10,xtol=1e-10,gtol=1e-10)
        test_residual=values_jacobian(result.x,test_features)[0]-test_target
        record={'seed':seed,'training_l2':float(np.linalg.norm(result.fun)),
                'validation_l2':float(np.linalg.norm(test_residual)),
                'evaluations':result.nfev,'parameters':result.x.tolist(),
                'exact_construction':False}
        out.append(record)
        print(json.dumps(record),flush=True)
    return out


if __name__=='__main__':
    run()
