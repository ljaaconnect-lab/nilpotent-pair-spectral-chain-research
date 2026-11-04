"""Division-free scalar reader for a supplied antisymmetric kernel.

This is a charged implementation of the Gaussian terminal observer, not
an initializer or a solution of the missing Gaussian fusion problem.
"""

from fractions import Fraction


def pfaffian(kernel, dag):
    """Return Pf(kernel) using +,-,* and rational constants only.

    The pair order is (x1,y1,x2,y2,...), so Pf(J)=1 for the standard
    block-diagonal symplectic J. No inverses of data values are used.
    """
    m = len(kernel)
    if m % 2:
        raise ValueError('even dimension required')
    n = m // 2
    one = dag.const(1)
    if not n:
        return one
    # A=-J K: even rows are minus the following K row; odd rows the
    # preceding K row. This is a signed permutation, not a dense product.
    a = [[dag.neg(kernel[i+1][j]) if i % 2 == 0 else kernel[i-1][j]
          for j in range(m)] for i in range(m)]

    def total(values):
        result = values[0]
        for value in values[1:]:
            result = dag.add(result, value)
        return result

    def matmul(left, right):
        return [[total([dag.mul(left[i][k], right[k][j]) for k in range(m)])
                 for j in range(m)] for i in range(m)]

    traces = [None]
    power = a
    for r in range(1,n+1):
        if r > 1:
            power = matmul(power,a)
        traces.append(total([power[i][i] for i in range(m)]))
    coeff = [one]
    for k in range(1,n+1):
        terms = []
        for r in range(1,k+1):
            term = dag.mul(traces[r],coeff[k-r])
            if r % 2 == 0:
                term = dag.neg(term)
            terms.append(term)
        coeff.append(dag.mul(dag.const(Fraction(1,2*k)),total(terms)))
    return coeff[n]


def route_terminal_component(kernel, labels, dag):
    """Jointly compile this Gaussian component's inverse spectral table.

    Every mode-pair phase is carried by a congruence. Fourier orthogonality
    then routes its scalar top coefficient directly to sum(labels) mod N.
    A complete candidate must still construct all exact Gaussian components
    from the original row factors, with a proved polynomial count.
    """
    from dag import length
    n = len(labels)
    if len(kernel) != 2*n:
        raise ValueError('one mode pair per input column required')
    outputs = [dag.const(0)]*length(n)
    outputs[sum(labels) % length(n)] = pfaffian(kernel,dag)
    return outputs
