# n64 result and constructive boundary

Score: **7184/7184 = 1.0**, development only. All compatible partial matchings
were enumerated for n=2,3,4,5 (7,34,209,1546), with four assertions per matching.
The assertions compare the unchanged n61 recurrence, independent Boolean
Möbius sum, local Pfaffian, principal Pfaffian of the one fixed port matrix,
and the actual scalar trace recurrence evaluated gate by gate.

The new constructive identity is

    c(S)=Pf K[ports(S) union dummyPorts],

for one fixed K of order 2n^2+2. Its entries are 0,+/-1 and depend only on
the universal edge order and column order. Selection now changes indices,
not a family of entry formulas based on selected ranks. The proof and exact
matrix are in N64_BLUEPRINT.md. The identity is informally derived and
finitely checked; this leaf does not claim a universal Lean theorem.

Each scalar trace-Pfaffian compiler is an explicit binary DAG with formal
upper-entry input leaves. Lower skew entries cost negation multiplications,
shared matrix powers use dense binary add/mul gates, and every division by
2k is a rational-literal multiplication. The terminal q_m is constructed
directly by its recurrence. No Pfaffian, determinant, derivative or extraction
primitive is charged as a free operation. Exact template measurements:

- Order2: 1 addition + 5 multiplications = 6 gates.
- Order4: 55 additions + 84 multiplications = 139 gates.
- Order6: 378 additions + 475 multiplications = 853 gates.
- Order8: 1378 additions + 1612 multiplications = 2990 gates.
- Order10: 3655 additions + 4117 multiplications = 7772 gates.
- Order12: 8001 additions + 8808 multiplications = 16809 gates.

The compiler count formula for d=2m is

    G(d)=16m^4-20m^3+11m^2-m+floor(m/2).

This is an exact count of this implementation, independently audited from
the actual graph nodes. The generic polynomial semantics of the recurrence
has not been Lean-certified here. Finite evaluations use SymPy matching
expansion as an independent validation oracle, while the scalar graph
interpreter executes each counted gate over Fraction.

The paired coefficient matrix for |S|=k has order 2k+2, so evaluating ONE
coefficient through this compiler uses G(2k+2) gates. The local matrix has
order k+1 (odd k) or k+2 (even k). Enumerating all S remains a different cost.
The Möbius formula gives |c(S)|<=2^|S|: at most n+1 bits for its absolute
integer numerator, with a fixed encoding overhead for its sign/denominator.
Measured maximum magnitude bit lengths at n2..5 were 2,3,4,5.

Validation reused values for equal relative column-order patterns only after
constructing and comparing both concrete matrices for every matching. The
distinct pattern counts were 4,10,34,154. This is finite validation reuse,
not a claim that a polynomial number of patterns covers general n. Total
actual scalar gate evaluations in the four runs were 2141,20915,227915,
2347355. Timings were approximately 0.09,0.23,1.56,12.30 seconds, all below
the frozen 120-second per-run limit. No candidate repair was required.

The protocol extension and source hashes were frozen before the first test
in n64-source-freeze-v1.json. The protocol SHA256 is
`df1339dc3b95dc35ecf29413bdd5a7603f0d6314ee0b73d1755c48bac7e5f8a0`;
pfaffian_coefficients.py SHA256 is
`1bd0c45b3273065b2718bcea6dbca5f64ede5e85353d7f145cc8dcbd6e3634c7`.
The inherited n61 euler_compiler.py has a different raw-byte hash in this
fresh worktree because Git checked its LF text out with CRLF; it was not
edited. Its n61 mathematical recurrence and source provenance are unchanged.

The precise remaining constructive obligation is summing the paired
principal coefficients together with the incidence determinant factors,
while retaining a_e and b_e together for each selected edge. The explicit
full Okada master and its algebraic reduction are recorded, with collaborator
provenance and informal status, in blueprint-pfaffian-aggregation.md. The
full unsynchronized contraction equals n^n times the product of row sums.
Its edge-sign average supplies the intended projection, but correlation by
column signs returns exactly the earlier n15 character construction. This
is an exact preserved reduction, not a new polynomial circuit.

Thus this leaf closes the matching-dependent rank description at the
informal and finite-validation level and charges the individual Pfaffian
compiler. It leaves the synchronized global scalar contraction, its uniform
construction bound and its complete Lean verification unresolved. No
counterexample/lower-bound campaign was conducted and no held-out case was
accessed. Shared Arbor state and outputs were not modified.

Reproduction in this worktree:

    python evaluate_pfaffian.py --n 2
    python evaluate_pfaffian.py --n 3
    python evaluate_pfaffian.py --n 4
    python evaluate_pfaffian.py --n 5
    python evaluate_pfaffian.py --aggregate

Public functions in pfaffian_coefficients.py:

- fixed_port_matrix(n): the single K, independent of S.
- principal_ports(n,matching): both ports per edge and the dummy ports.
- principal(K,indices): the selected explicit skew matrix.
- local_matrix(column_order): the equivalent local matrix.
- trace_circuit(d): (DAG,output), generic upper skew entry input leaves.
- evaluate_trace(graph,output,matrix): exact Fraction value and actual gates evaluated.
- mobius_coefficient(n,matching): independent finite validation expression.

These helpers support the coordinator's fresh held-out fixtures without
reading them inside this leaf. The root conjecture is not declared proved.
