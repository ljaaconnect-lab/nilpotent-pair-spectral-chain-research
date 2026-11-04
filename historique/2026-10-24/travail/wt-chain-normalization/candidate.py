from dag import marked_inputs, length


def build(n, labels, dag):
    """Exact whole-table reference with the known character readout folded.

    This is still exponential. The Schur-Good research does not supply a
    valid general replacement, so this candidate only removes the redundant
    spectral tail from the complete known compiler.
    """
    b = marked_inputs(n, dag)
    states = {0: dag.const(1)}
    for mask in range(1, 1 << n):
        row = mask.bit_count() - 1
        if row == 0:
            states[mask] = b[0][mask.bit_length() - 1]
            continue
        terms = [dag.mul(b[row][j], states[mask ^ (1 << j)])
                 for j in range(n) if mask >> j & 1]
        total = terms[0]
        for term in terms[1:]:
            total = dag.add(total, term)
        states[mask] = total
    outputs = [dag.const(0)] * length(n)
    outputs[sum(labels) % len(outputs)] = states[(1 << n) - 1]
    return outputs
