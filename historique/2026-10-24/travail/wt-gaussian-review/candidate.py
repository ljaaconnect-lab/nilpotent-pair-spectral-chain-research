from dag import marked_inputs, spectral_tail


def build(n, labels, dag):
    """Known complete exponential reference, from original inputs to all slots.

    The baseline uses the paper's sufficient scalar interface. Candidates
    may replace this whole function by a joint orientation/spectral compiler.
    There is no corrected-amplitude input or oracle.
    """
    b = marked_inputs(n, dag)
    states = {0: dag.const(1)}
    for mask in range(1, 1 << n):
        i = mask.bit_count() - 1
        if i == 0:
            states[mask] = b[0][mask.bit_length() - 1]
            continue
        terms = [dag.mul(b[i][j], states[mask ^ (1 << j)])
                 for j in range(n) if mask >> j & 1]
        total = terms[0]
        for term in terms[1:]: total = dag.add(total, term)
        states[mask] = total
    return spectral_tail(states[(1 << n) - 1], labels, dag)
