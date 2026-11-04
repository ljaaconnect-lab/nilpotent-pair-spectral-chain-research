"""Gauge-fixed, bounded first-jet continuation of full skew completions."""
import argparse
import json
import time
import numpy as np
from scipy.optimize import least_squares
from gaussian_completion import Completion


def gauge_kernel(problem,vector):
    """Local SL2 gauge, regular near the prescribed all-ones kernel."""
    n=problem.n
    matrix=np.zeros((2*n,2*n))
    for value,(i,j) in zip(vector,problem.edges):
        matrix[i,j],matrix[j,i]=value,-value
    transform=np.eye(2*n)
    c=23/4
    for j in range(1,n):
        block=matrix[:2,2*j:2*j+2]
        canonical=np.array([[0,c],[-np.linalg.det(block)/c,0]])
        right=np.linalg.solve(block,canonical)
        assert abs(np.linalg.det(right)-1)<1e-8
        transform[2*j:2*j+2,2*j:2*j+2]=right.T
    matrix=transform@matrix@transform.T
    return np.array([matrix[i,j] for i,j in problem.edges])


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--n',type=int,default=10)
    parser.add_argument('--seed',type=int,default=2026102440)
    parser.add_argument('--steps',default='0.3,0.1,0.03')
    parser.add_argument('--evaluations',type=int,default=800)
    parser.add_argument('--bound',type=float,default=25)
    parser.add_argument('--control',action='store_true')
    parser.add_argument('--output',default='regular_completion_results.json')
    args=parser.parse_args()
    p=Completion(args.n)
    rng=np.random.default_rng(args.seed)
    direction=rng.integers(-3,4,size=(4,args.n)).astype(float)/3
    fixed={p.edge_index[0,2*j] for j in range(1,args.n)} | \
          {p.edge_index[1,2*j+1] for j in range(1,args.n)} | \
          {p.edge_index[0,2*j+1] for j in range(1,args.n)}
    free=[i for i in range(len(p.edges)) if i not in fixed]
    h=rng.normal(0,0.1,size=len(free))
    true_h=rng.normal(size=len(p.edges)) if args.control else None
    record={'n':args.n,'seed':args.seed,'bound':args.bound,'control':args.control,
            'all_skew_entries_modulo_regular_SL2_gauge':True,
            'fixed_gauge_parameters':len(fixed),'free_parameters':len(free),
            'direction':direction.tolist(),'steps':[],'is_existence_proof':False}
    for t in map(float,args.steps.split(',')):
        if args.control:
            true_kernel=p.reference+t*true_h
            gauged=gauge_kernel(p,true_kernel)
            target=p.values_jacobian(true_kernel)[0].copy()
            assert np.max(np.abs(p.values_jacobian(gauged)[0]-target))<1e-8
            h=(gauged-p.reference)[free]/t+rng.normal(0,0.05,size=len(free))
        else:
            target=p.targets(1+t*direction)
        def kernel(x):
            k=p.reference.copy()
            k[free]+=t*x
            return k
        def fun(x):
            return (p.values_jacobian(kernel(x))[0]-target)/t**4
        def jac(x):
            return p.values_jacobian(kernel(x))[1][:,free]/t**3
        started=time.monotonic()
        result=least_squares(fun,h,jac=jac,bounds=(-args.bound,args.bound),
                             max_nfev=args.evaluations,
                             ftol=1e-12,xtol=1e-12,gtol=1e-12)
        h=result.x
        residual=result.fun*t**4
        singular=np.linalg.svd(jac(h)*t**3,compute_uv=False)
        item={'t':t,'l2_residual':float(np.linalg.norm(residual)),
              'max_residual':float(np.max(np.abs(residual))),
              'scaled_residual_order4':float(np.linalg.norm(result.fun)),
              'h_l2':float(np.linalg.norm(h)),'h_linf':float(np.max(np.abs(h))),
              'nfev':result.nfev,'status':result.status,
              'jacobian_rank_relative_1e8':int(np.sum(singular>singular[0]*1e-8)),
              'seconds':time.monotonic()-started}
        record['steps'].append(item)
        print(json.dumps(item),flush=True)
        with open(args.output,'w',encoding='utf8') as handle:
            json.dump(record,handle,indent=2)


if __name__=='__main__':
    main()
