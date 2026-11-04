from dag import marked_inputs

def build(n,dag):
    b=marked_inputs(n,dag)
    states={0:dag.const(1)}
    for mask in range(1,1<<n):
        i=mask.bit_count()-1
        terms=[dag.mul(b[i][j],states[mask^(1<<j)]) for j in range(n) if mask>>j&1]
        total=terms[0]
        for term in terms[1:]: total=dag.add(total,term)
        states[mask]=total
    return states[(1<<n)-1]
