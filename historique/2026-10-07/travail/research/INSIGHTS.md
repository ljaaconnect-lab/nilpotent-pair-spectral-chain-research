# Arbor leaf n1: exact scalar circuit simulation

Artifact version: n1-explicit-dags-v1. The fixed hypothesis was that a real
scalar arithmetic DAG of at most 4 n^4 gates computes Hhat for n=2,3,4 and
matches the coefficient identity on the frozen development boundary, while
materialized expansion and subset-state DP have growing explicit costs.

The script `candidate.py` constructs the determinant with the section 7
Faddeev–LeVerrier recurrence and uses the section 14 Vandermonde factor. Every
interior node is an explicit fan-in-two addition or multiplication. Constants
p_ij = 1+a_ij^2 are calculated from the rational input and used as leaves, as
per the source circuit model. Their preprocessing is not part of the reported
gate count. Other leaves are 0,1,-1 and the rational recurrence constants.
Subtraction is encoded as multiplication by -1 followed by addition, so the
reported size is conservative relative to the source's one-gate subtraction
convention. Exponentiation uses an explicit binary squaring chain.

Every actual DAG gate is evaluated in the exact sparse polynomial ring
Q[t,z], with Fraction coefficients and pairs of nonnegative integer exponents.
There is no SymPy determinant, permanent, or hidden polynomial operation in
the counted DAG. Dead evaluated node values are released with a reference
count; this changes storage only. The reported gate-evaluation count equals
the DAG's gate count. Exponent pairs and rational arithmetic are evaluator
data structures, and their processing cost is distinct from scalar circuit
size. Taking a dictionary slice at exponent K after this evaluation is an
explicit expansion-based coefficient extractor, not a proposed compact
coefficient-extraction circuit.

## Development result

`python evaluate.py --split dev --output dev-report.json` exited with code 0.
Frozen score: 1.0 = 36/36 exact assertions. The evaluator hash recorded in the
report is
`2c393f62241c992bc816d717a2b15fe5f368e2c9064fa1b92f566020dc5dfa1c`.
The nine development cases are identity, cyclic-permutation and Vandermonde
input matrices for n=2,3,4. In all cases the full Hhat polynomial, extracted
central polynomial, index K and gate bound match the frozen independent
double-permutation oracle. The test boundary has not been accessed.

- n=2: K=3, actual Hhat gates=48 <=64, Hhat support=6, central support=2.
- n=3: K=26, actual Hhat gates=198 <=324, Hhat support=38, central support=6.
- n=4: K=255, actual Hhat gates=568 <=1024, Hhat support=578, central support=24.

The three input families have the same supports. Although some A entries are
zero, p_ij=1+a_ij^2 is always positive; identity inputs therefore do not induce
a sparse diagonal matrix of p_ij. The exact per-case operation counts, elapsed
evaluation times and live-term measurements are in `measurements.json`.

## Independent subset-state construction

`build_subset_dp` constructs another actual +/* DAG, now for the positive
coefficient polynomial P_A, using

    F[empty]=1
    F[S]=sum_{j in S} F[S without j] * p_(|S|-1,j) * z^(2^((|S|-1)*n+j))

The marked entries are shared nodes. For the complete state table, state count
is 2^n and transition count is n*2^(n-1). There is one multiplication per
transition and |S|-1 additions per nonempty state. Thus DP gates are
n*2^n-(2^n-1), and total gates including marked entries are
2*n^2-1+n*2^n-(2^n-1). This is a cost formula for this implementation; it is
not an arithmetic circuit lower bound for P_A.

- n=2: 4 states, 4 transitions, 5 DP gates, 12 total gates.
- n=3: 8 states, 12 transitions, 17 DP gates, 34 total gates.
- n=4: 16 states, 32 transitions, 49 DP gates, 80 total gates.

All nine resulting polynomials equal the central coefficient obtained by the
Hhat DAG. These finite cases check the algorithms; they do not demonstrate
polynomial asymptotic complexity, and small counts here do not rule out either
future polynomial algorithms or unavoidable exponential costs.

## Distilled insight and parent constraint

The determinant recurrence computes the signed, two-variable Hhat circuit in
polynomial gate size, but does not give a recurrence for its central
coefficient with polynomial state dimension. Its matrix entries are formal
polynomials, so replacing each formal operation by coefficient-array
operations incurs additional costs. The base-n index is K=n^n-1. This search
found no new fixed-dimension recurrence of the form u^T M^k v for central
extraction.

The observed full support counts are (n!)^2+2, consistent with the paper's
double-permutation formula: the z address distinguishes the first permutation
and the t label distinguishes the second for fixed first permutation. This
structural explanation is an informal consequence of the label injectivity
used in the source, not a Lean-verified theorem in this leaf. Explicit
materialization is factorial in output support, even though the circuit for
Hhat is small. Neither that materialization cost nor the subset DP gate
formula disproves Conjecture 1.5.

Path-adjustment constraint: do not score polynomial-size Hhat construction,
finite extraction checks, positive amplitudes, or a method-specific
exponential state table as proof or disproof of polynomial sign correction.
Further candidates must address coefficient extraction and uniform scalar
complexity separately from the already compact determinant recurrence.

## Reproduction

    python evaluate.py --split dev --output dev-report.json
    python candidate.py --all-dev --output measurements.json --dag dag-n2-identity.json
    python candidate.py --n 4 --family vandermonde --dag dag-n4-vandermonde.json

The JSON DAGs list actual topologically ordered nodes and the output index.
No Lean declaration is part of this leaf; its score is exact simulation
assertion pass fraction, not proof confidence.
