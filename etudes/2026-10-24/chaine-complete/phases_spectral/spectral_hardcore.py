"""Division-free full-table compilers for structurally banded marked inputs.

Entries outside the declared band are zero, so this is a constructive class
result rather than a candidate for the dense positive-input contract.
"""
from dag import length


def marked_band(n, width, dag):
    powers = [dag.inp('z')]
    for _ in range(n*n-1):
        powers.append(dag.mul(powers[-1], powers[-1]))
    return {(i, j): dag.mul(dag.inp(('p', i, j)), powers[i*n+j])
            for i in range(n) for j in range(max(0, i-width), min(n, i+width+1))}


def build_tridiagonal(n, labels, dag):
    """Two observable hard-core states per interior layer, original phases.

    For n>=2: exactly n^2+7n-8 scalar gates including binary marking.
    The phase indices are compile-time metadata of the occupied columns.
    All nonconstant scalar arithmetic is charged through dag.
    """
    if n < 1 or len(labels) != n:
        raise ValueError('Need n>=1 and exactly n column labels.')
    N = length(n)
    b = marked_band(n, 1, dag)
    main = b[0, 0]
    main_phase = labels[0] % N
    pending = b.get((0, 1))
    pending_phase = labels[1] % N if n > 1 else None
    for row in range(1, n):
        straight = dag.mul(b[row, row], main)
        close = dag.mul(b[row, row-1], pending)
        straight_phase = (main_phase+labels[row]) % N
        close_phase = (pending_phase+labels[row-1]) % N
        assert straight_phase == close_phase
        next_main = dag.add(straight, close)
        if row < n-1:
            next_pending = dag.mul(b[row, row+1], main)
            next_pending_phase = (main_phase+labels[row+1]) % N
        else:
            next_pending = next_pending_phase = None
        main, main_phase = next_main, straight_phase
        pending, pending_phase = next_pending, next_pending_phase
    assert main_phase == sum(labels) % N
    zero = dag.const(0)
    return [main if k == main_phase else zero for k in range(N)]


def build_banded(n, labels, dag, width=2):
    """Frontier quotient of the observable hard-core operator, fixed width.

    At layer k, columns below k-width are already occupied and columns at
    least k+width cannot yet be occupied. At most 2*width active bits remain.
    The resulting scalar size is O(n^2+n*(2*width+1)*binom(2*width,width)).
    """
    if n < 1 or width < 0 or len(labels) != n:
        raise ValueError('Invalid size, width or labels.')
    N = length(n)
    b = marked_band(n, width, dag)
    states = {0: (dag.const(1), 0)}
    for row in range(n):
        new = {}
        expired = (1 << max(0, row-width+1))-1
        for mask, (value, phase) in states.items():
            for column in range(max(0, row-width), min(n, row+width+1)):
                if mask >> column & 1:
                    continue
                target = mask | (1 << column)
                if target & expired != expired:
                    continue
                term = b[row, column] if row == 0 else dag.mul(value, b[row, column])
                target_phase = (phase+labels[column]) % N
                if target in new:
                    previous, old_phase = new[target]
                    assert old_phase == target_phase
                    term = dag.add(previous, term)
                new[target] = (term, target_phase)
        states = new
    assert set(states) == {(1 << n)-1}
    value, phase = states[(1 << n)-1]
    assert phase == sum(labels) % N
    zero = dag.const(0)
    return [value if k == phase else zero for k in range(N)]


def observable_graph(n, width):
    """Support-only elimination of states outside the root's cyclic component.

    Return (proper-subset vertices, edges), edge=(source,target,row,column).
    All parameters of the reduced operator are original marked cell values.
    """
    root = 0
    layers = [{root}]
    edges = []
    for row in range(n):
        new = set()
        expired = (1 << max(0, row-width+1))-1
        for mask in sorted(layers[-1]):
            for column in range(max(0, row-width), min(n, row+width+1)):
                if mask >> column & 1:
                    continue
                target = mask | (1 << column)
                if target & expired != expired:
                    continue
                new.add(target)
                edges.append((mask, root if row == n-1 else target, row, column))
        layers.append(new)
    return [mask for layer in layers[:-1] for mask in sorted(layer)], edges


def raw_graph(n, width=None):
    vertices = list(range((1 << n)-1))
    edges = []
    for mask in vertices:
        row = mask.bit_count()
        for column in range(n):
            if mask >> column & 1 or (width is not None and abs(row-column) > width):
                continue
            target = mask | (1 << column)
            edges.append((mask, 0 if row == n-1 else target, row, column))
    return vertices, edges
