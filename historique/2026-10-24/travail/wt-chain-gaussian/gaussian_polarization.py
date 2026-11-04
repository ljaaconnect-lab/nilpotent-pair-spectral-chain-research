"""Exact exponential Gaussian polarization, including joint spectral readout.

For n>=3 there are 2**(n-3) regular rank-four-update Gaussian components.
Their specialized scalar observers use four accumulators, and neighboring
components share their row sums by Gray code. This is NOT polynomial in n.
"""
from fractions import Fraction
from dag import length,marked_inputs


def repeated_component_reader(h,b,c,dag):
    """Pf(K_h)/(n-2)!; exactly twelve scalar gates per column.

    It equals sum_(j!=k) b_j*c_k*product_(l!=j,k)h_l. This polynomial
    identity removes every rational parameter of the Gaussian at readout;
    no division by a value h_j is performed or hidden in a leaf.
    """
    e0=dag.const(1)
    eb=ec=ebc=dag.const(0)
    for hj,bj,cj in zip(h,b,c):
        next_ebc=dag.add(dag.add(dag.mul(hj,ebc),dag.mul(bj,ec)),dag.mul(cj,eb))
        next_eb=dag.add(dag.mul(hj,eb),dag.mul(bj,e0))
        next_ec=dag.add(dag.mul(hj,ec),dag.mul(cj,e0))
        e0=dag.mul(hj,e0)
        eb,ec,ebc=next_eb,next_ec,next_ebc
    return ebc


def build(n,labels,dag):
    b=marked_inputs(n,dag)
    outputs=[dag.const(0)]*length(n)
    slot=sum(labels)%length(n)
    if n==1:
        outputs[slot]=b[0][0]
        return outputs
    if n==2:
        outputs[slot]=dag.add(dag.mul(b[0][0],b[1][1]),dag.mul(b[0][1],b[1][0]))
        return outputs

    m=n-2
    scaled=[[value if i==0 else dag.mul(dag.const(1<<i),value)
             for value in b[i]] for i in range(m)]
    h=scaled[0].copy()
    for row in scaled[1:]:
        h=[dag.add(x,y) for x,y in zip(h,row)]
    positive=[[dag.mul(dag.const(2),value) for value in row] for row in scaled[:-1]]
    negative=[[dag.mul(dag.const(-2),value) for value in row] for row in scaled[:-1]]
    denominator=1<<((m-1)+m*(m-1)//2)
    previous=0
    total=None
    for index in range(1<<(m-1)):
        gray=index^(index>>1)
        if index:
            bit=(gray^previous).bit_length()-1
            increments=negative[bit] if gray>>bit&1 else positive[bit]
            h=[dag.add(x,y) for x,y in zip(h,increments)]
        value=repeated_component_reader(h,b[-2],b[-1],dag)
        weight=Fraction(-1 if gray.bit_count()%2 else 1,denominator)
        value=dag.mul(dag.const(weight),value)
        total=value if total is None else dag.add(total,value)
        previous=gray
    outputs[slot]=total
    return outputs


def gate_bound(n):
    if n==1:
        return 1
    if n==2:
        return 10
    m=n-2
    components=1<<(m-1)
    return 2*n*n+4*n*(m-1)-n-2+(13*n+2)*components
