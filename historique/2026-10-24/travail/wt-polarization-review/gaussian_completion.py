"""Full skew-matrix completion experiment for the fourth paired layer.

Every upper-triangular entry of the 2n by 2n skew kernel is free. Targets
are small, explicitly evaluated four-row permanents used only to test
existence; supplying such targets is not a compiler for general layers.
"""

import argparse
from itertools import combinations,permutations
import json
import time
import numpy as np
from scipy.optimize import least_squares


def matchings(indices):
    if not indices:
        yield 1,[]
        return
    for j in range(1,len(indices)):
        for sign,pairs in matchings(indices[1:j]+indices[j+1:]):
            yield (-1)**(j+1)*sign,[(indices[0],indices[j])]+pairs


class Completion:
    def __init__(self,n):
        self.n=n
        self.subsets=np.array(list(combinations(range(n),4)))
        self.edges=list(combinations(range(2*n),2))
        self.edge_index={edge:i for i,edge in enumerate(self.edges)}
        local_edges=list(combinations(range(8),2))
        local_index={edge:i for i,edge in enumerate(local_edges)}
        terms=list(matchings(tuple(range(8))))
        self.sign=np.array([v[0] for v in terms])
        self.terms=np.array([[local_index[edge] for edge in v[1]] for v in terms])
        self.scatter=np.array([[self.edge_index[2*ss[i//2]+i%2,2*ss[j//2]+j%2]
                               for i,j in local_edges] for ss in self.subsets])
        self.diagonal_slots=[self.edge_index[2*j,2*j+1] for j in range(n)]
        self.reference=np.array([
            (float(i//2==j//2)+23/4 if i%2==0 and j%2==1 else
             -23/4 if i%2==1 and j%2==0 else 0)
            for i,j in self.edges])
        self.last_x=None
        self.last_result=None

    def values_jacobian(self,x):
        if self.last_x is not None and np.array_equal(x,self.last_x):
            return self.last_result
        entries=x[self.scatter]
        terms=entries[:,self.terms]
        values=np.prod(terms,axis=2)@self.sign
        local_grad=np.zeros(entries.shape)
        for k in range(4):
            part=np.prod(terms[:,:,[j for j in range(4) if j!=k]],axis=2)*self.sign
            for edge in range(28):
                chosen=self.terms[:,k]==edge
                if np.any(chosen):
                    local_grad[:,edge]+=part[:,chosen].sum(axis=1)
        jac=np.zeros((len(self.subsets),len(self.edges)))
        jac[np.arange(len(self.subsets))[:,None],self.scatter]=local_grad
        self.last_x=x.copy()
        self.last_result=(values,jac)
        return values,jac

    def targets(self,b):
        return sum(np.prod(b[np.arange(4)[None,:],self.subsets[:,p]],axis=1)
                   for p in permutations(range(4)))

    def solve(self,target,start,max_nfev):
        then=time.monotonic()
        result=least_squares(lambda x:self.values_jacobian(x)[0]-target,start,
                             jac=lambda x:self.values_jacobian(x)[1],
                             method='trf',max_nfev=max_nfev,
                             ftol=1e-13,xtol=1e-13,gtol=1e-13)
        singular=np.linalg.svd(self.values_jacobian(result.x)[1],compute_uv=False)
        return result,{
            'l2_residual':float(np.linalg.norm(result.fun)),
            'max_residual':float(np.max(np.abs(result.fun))),
            'target_l2':float(np.linalg.norm(target)),
            'nfev':result.nfev,'njev':result.njev,'status':result.status,
            'jacobian_rank_1e8_relative':int(np.sum(singular>singular[0]*1e-8)),
            'smallest_singular':float(singular[-1]),
            'distance_to_base':float(np.linalg.norm(result.x-self.reference)),
            'elapsed_seconds':time.monotonic()-then}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--n',type=int,default=10)
    parser.add_argument('--seed',type=int,default=2026102440)
    parser.add_argument('--evaluations',type=int,default=250)
    parser.add_argument('--steps',default='0.01,0.03,0.1,0.3')
    parser.add_argument('--jitter',type=float,default=1.0)
    parser.add_argument('--control',choices=['none','gaussian'],default='none')
    parser.add_argument('--no-rescale',action='store_true')
    parser.add_argument('--output',default='completion_results.json')
    args=parser.parse_args()
    problem=Completion(args.n)
    rng=np.random.default_rng(args.seed)
    direction=rng.integers(-3,4,size=(4,args.n)).astype(float)/3
    control_direction=(rng.normal(size=len(problem.edges)) if args.control=='gaussian' else None)
    base_value,base_jac=problem.values_jacobian(problem.reference)
    assert np.max(np.abs(base_value-24))<1e-9
    singular=np.linalg.svd(base_jac,compute_uv=False)
    record={'n':args.n,'seed':args.seed,'constraints':len(problem.subsets),
            'kernel_parameters':len(problem.edges),'direction':direction.tolist(),
            'base_jacobian_rank':int(np.sum(singular>1e-7)),
            'full_free_skew_kernel':True,'is_proof':False,'control':args.control,'steps':[]}
    current=None
    previous_t=None
    for t in map(float,args.steps.split(',')):
        if current is None:
            current=problem.reference+t*args.jitter*rng.normal(size=len(problem.edges))
        elif not args.no_rescale:
            current=problem.reference+(t/previous_t)*(current-problem.reference)
        target=(problem.targets(1+t*direction) if args.control=='none' else
                problem.values_jacobian(problem.reference+t*control_direction)[0].copy())
        current_result,step=problem.solve(target,current,args.evaluations)
        current=current_result.x
        step['t']=t
        step['scaled_distance_to_base']=step['distance_to_base']/abs(t)
        record['steps'].append(step)
        print(json.dumps(step),flush=True)
        with open(args.output,'w',encoding='utf8') as handle:
            json.dump(record,handle,indent=2)
        np.savez(args.output+'.npz',kernel=current,direction=direction)
        previous_t=t


if __name__=='__main__':
    main()
