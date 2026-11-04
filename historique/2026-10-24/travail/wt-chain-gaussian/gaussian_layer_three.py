"""A division-free four-coordinate realization of a third-layer Gaussian.

This is an exact, original-factor compiler for n=3 and a compact encoding of
the third paired layer for any number of columns. It is not an all-layer
fusion algorithm.
"""

from fractions import Fraction
from dag import marked_inputs, length
from pfaffian_scalar import pfaffian


class Jets:
    """Explicit ordinary scalar DAG for Q[t]/(t**(order+1))."""
    def __init__(self, dag, order):
        self.dag, self.order = dag, order

    def const(self, value):
        return (self.dag.const(value),) + (self.dag.const(0),)*self.order

    def deform(self, value):
        if not self.order:
            return self.const(1)
        return (self.dag.const(1), self.dag.sub(value,self.dag.const(1))) + \
               (self.dag.const(0),)*(self.order-1)

    def add(self, a, b):
        return tuple(self.dag.add(x,y) for x,y in zip(a,b))

    def neg(self, a):
        return tuple(self.dag.neg(x) for x in a)

    def sub(self, a, b):
        return self.add(a,self.neg(b))

    def mul(self, a, b):
        out = []
        for k in range(self.order+1):
            terms = [self.dag.mul(a[j],b[k-j]) for j in range(k+1)]
            v = terms[0]
            for term in terms[1:]:
                v = self.dag.add(v,term)
            out.append(v)
        return tuple(out)

    def inverse_deformed(self, a):
        """a=1+t*delta; explicit (-delta)**k, with no input inverse."""
        if not self.order:
            return self.const(1)
        negative_delta = self.dag.neg(a[1])
        coeff = [self.dag.const(1),negative_delta]
        for _ in range(2,self.order+1):
            coeff.append(self.dag.mul(coeff[-1],negative_delta))
        return tuple(coeff)

    def evaluate_at_one(self, a):
        value = a[0]
        for term in a[1:]:
            value = self.dag.add(value,term)
        return value


def third_layer_kernel(rows, dag, order=3):
    """Return (jet arithmetic, polynomial-jet antisymmetric matrix).

    The returned entries are tuples of ordinary DAG node IDs; no rational
    function or inverse is a hidden leaf. Every paired 6x6 Pfaffian equals
    the three-row permanent after evaluating its degree<=3 jet at t=1.
    """
    if len(rows) != 3 or len({len(row) for row in rows}) != 1:
        raise ValueError('three equally sized rows required')
    ring = Jets(dag,order)
    a,b,c = [[ring.deform(value) for value in row] for row in rows]
    inva = [ring.inverse_deformed(value) for value in a]
    r = [ring.mul(x,y) for x,y in zip(b,inva)]
    s = [ring.mul(x,y) for x,y in zip(c,inva)]
    n = len(a)
    zero,one = ring.const(0),ring.const(1)
    third,two = ring.const(Fraction(1,3)),ring.const(2)
    kernel = [[zero]*(2*n) for _ in range(2*n)]
    for j in range(n):
        for k in range(j+1,n):
            # Scale each x_j by a_j. The y_j scale is one.
            xx = ring.mul(ring.mul(a[j],a[k]),ring.sub(r[k],r[j]))
            yy = ring.mul(third,ring.sub(s[k],s[j]))
            kernel[2*j][2*k],kernel[2*k][2*j] = xx,ring.neg(xx)
            kernel[2*j+1][2*k+1],kernel[2*k+1][2*j+1] = yy,ring.neg(yy)
        for k in range(n):
            base = ring.sub(one if j==k else zero,third)
            xy = ring.mul(a[j],ring.add(base,ring.mul(two,ring.mul(r[j],s[k]))))
            kernel[2*j][2*k+1],kernel[2*k+1][2*j] = xy,ring.neg(xy)
    return ring,kernel


def build_three(labels, dag):
    """Complete three-row chain, from original p,z to every inverse slot."""
    if len(labels) != 3:
        raise ValueError('this construction establishes only layer three')
    ring,kernel = third_layer_kernel(marked_inputs(3,dag),dag)
    value = ring.evaluate_at_one(pfaffian(kernel,ring))
    outputs = [dag.const(0)]*length(3)
    outputs[sum(labels)%length(3)] = value
    return outputs


def build_four(labels, dag):
    """Exact fourth-row continuation as five Gaussian components.

    All parameters, interpolation, scalar observation, and inverse-slot
    routing are compiled. The component count does not have a proved
    polynomial closure under arbitrarily many further rows.
    """
    if len(labels) != 4:
        raise ValueError('four rows required')
    b = marked_inputs(4,dag)
    ring,kernel = third_layer_kernel(b[:3],dag,order=4)
    d = [ring.deform(value) for value in b[3]]
    weights = [Fraction(-25,12),4,-3,Fraction(4,3),Fraction(-1,4)]
    components = []
    for index,weight in enumerate(weights):
        updated = [row[:] for row in kernel]
        for j in range(4):
            value = ring.add(kernel[2*j][2*j+1],ring.mul(ring.const(index),d[j]))
            updated[2*j][2*j+1] = value
            updated[2*j+1][2*j] = ring.neg(value)
        components.append(ring.mul(ring.const(weight),pfaffian(updated,ring)))
    value = components[0]
    for component in components[1:]:
        value = ring.add(value,component)
    outputs = [dag.const(0)]*length(4)
    outputs[sum(labels)%length(4)] = ring.evaluate_at_one(value)
    return outputs
