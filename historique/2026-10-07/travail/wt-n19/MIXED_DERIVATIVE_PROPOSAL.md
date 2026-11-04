# Arbor n19: positive rank-one and mixed-derivative contraction

This node supplies new positive constructions and concrete scalar circuits.
General arguments below are **UNVERIFIED by Lean** in this node. Exact generic
formal-weight and marked-z development checks do not establish an asymptotic
polynomial bound or resolve Conjecture 1.5. No counterexample generation,
general lower-bound work, held-out access, or shared Arbor-tree writes occurred.

## Explicit initialized rank-one chain

For X=diag(x_0,...,x_(n-1)), work in the commutative square-zero occupancy ring

`R=Q[B][x_0,...,x_(n-1)]/(x_0^2,...,x_(n-1)^2)`.

Define `A=I-XB`, `F=1/det(A)`, and `G=B*A^(-1)`. Initially all x are absent,
so **F=1 and G=B**: neither initial object contains the target permanent.
The inverse exists in this ring because every entry of XB lies in its nilpotent
occupancy ideal; a sufficiently high matrix power vanishes and a finite
geometric sum supplies the inverse.

Introduce one occupancy variable x_i at a time. The matrix changes by the
rank-one row update `A_new=A-x_i*e_i*B[i,:]`. Since x_i^2=0,

`(1-x_i*c)^(-1)=1+x_i*c`.

The determinant lemma and a direct inverse multiplication then give

`F_new=F+x_i*F*G_ii`,
`G_new[j,k]=G[j,k]+x_i*G[j,i]*G[i,k]`.

In these formulas all right-hand sides use the old G. Future updates at indices
larger than i only require j,k>i, so the implementation retains that submatrix
and discards completed rows/columns. This gives a chain of cheaply initialized
states with one scalar F and a shrinking future matrix G. It does not invoke
division as a gate; the updates are explicit binary scalar additions/products.

After all rows, the full squarefree coefficient of F equals the target generic
permanent. The master-identity interpretation from n16 is preserved. There is
also a direct cycle interpretation: G[j,k] coefficients enumerate paths from
j to k whose internal vertices are the processed occupancy labels; closing the
new path at i in the F update inserts the cycle containing i. Summing disjoint
processed occupancies builds all cycle covers, hence permutations, positively.

`build_rank_one_chain` emits a native arithmetic DAG in B and auxiliary x.
The exact gate count is

`S_rank(n)=3n+n(n-1)(2n-1)/2`.

Each stage spends three gates on F, and three per retained future G entry.
For n=2,3,4,5 this is **9,24,54,105** gates, compared with n16's explicit
Newton/reciprocal-table counts 30,129,404,1005. The new chain is a substantial
constructive simplification of the auxiliary recurrence circuit. The x
coefficient contraction remains a separately charged operation. The native
unprojected polynomial need not equal the reciprocal globally; its squarefree
jets are exactly the required ones.

## Mixed derivatives are dynamically compiled into actual scalar DAGs

For a subset S of distinct variables, the coefficient of x^S equals
`(partial_S f)(0)`; there is no factorial scale because every selected exponent
is one. At a scalar product gate the mixed Leibniz rule is

`partial_S(fg)(0)=sum_(T subset S) partial_T f(0)*partial_(S\T)g(0)`.

Each term and addition in this rule is a scalar circuit operation. The two
compilers emit explicit `ScalarDAG` nodes over generic B leaves and rational
constants, rather than merely treating jet multiplication as a scalar gate.

- The eager compiler propagates every structural squarefree coordinate through
  every source gate. Its additions and disjoint-mask products become actual
  scalar add/mul nodes. Every intermediate coordinate is available for audit.
- The demand compiler starts at the full mixed derivative of the final F,
  traverses its dependencies backward, and memoizes requested `(source,mask)`
  pairs. It omits only coordinates excluded by exact positive structural
  support. Its support sets are explicitly recorded and still cost search work;
  no symbolic zero oracle or uncharged projection is assumed.

Demand scalar DAGs for n=2 and n=5 are saved in `mixed-demand-n2-dag.json` and
`mixed-demand-n5-dag.json`, including every leaf, binary gate, and output index.

For n=2,3,4,5 the eager compiled scalar gate counts are **10,40,140,454**;
demand compiled counts are **8,30,102,324**. These are actual node counts.
The demand measurements are not extrapolated to a polynomial formula.

The eager constructor has the explicit algorithm-cost identity

`G_eager(n)=sum_(i=0)^(n-1) 2*3^i*(1+(n-i-1)^2)`
`          =2*3^n-n^2-n-2`.

To derive it, before stage i every F/G component has all 2^i positive structural
coordinates. A product of two such components has 3^i disjoint pairs and
3^i-2^i additions; multiplying by the new x_i costs 2^i further scalar products.
The old and x_i-bearing coordinates are disjoint, so the final update addition
copies them without an additional coefficient gate. Thus each updated F or G
component costs 2*3^i scalar gates, with 1+(n-i-1)^2 retained components.
The closed form follows by induction from
`G_eager(n+1)=3*G_eager(n)+2*(n^2+1)` and `G_eager(1)=2`.
This is a positive construction's cost, not a lower bound on alternative
circuits or a disproof of the root conjecture.

## Intermediate states are explicit and verified

After processing i variables, every F coefficient at occupancy S is the
principal permanent `per(B[S,S])`. Every future G[j,k] coefficient is

`sum_(orders of S) B[j,s_1]*B[s_1,s_2]*...*B[s_m,k]`,

with empty S giving B[j,k]. The evaluator verifies these formulas against
independent permutation/path sums at every stage for generic formal B, through
n=5. This validates the proposed chain's intermediate invariants, rather than
only its final scalar.

Each stage boundary retains `(1+(n-i)^2)*2^i` scalar jet coordinates, including
F and the future G submatrix. The observed peak boundary counts are
**5,10,20,40** at n=2,3,4,5. These figures are boundary-state counts; temporary
source gates and their jet coordinates are separately represented and counted
in `dev-mixed.json`. They are not a bound on total execution storage.

## Independent cycle factors and Bell partitions

A second constructive factorization organizes permutations by their cycles.
For each nonempty vertex set T define C(T) as the sum of weights of directed
cycles using exactly T, anchored at its least vertex to avoid overcounting.
Singleton cycles have the cheap initialization `C({i})=B_ii`.

`build_cycle_bell` computes larger C(T) with an explicit Hamiltonian-path table:
for anchor a=min(T), paths from a through a subset U ending at j follow

`L(U,j)=sum_(k in U\{j}) L(U\{j},k)*B[k,j]`,

with `L({j},j)=B[a,j]`, followed by closing each path with B[j,a]. All needed
scalar gates are emitted. Then the initialized Bell-partition recurrence is

`Q(empty)=1`,
`Q(S)=sum_(T subset S, min(S) in T) C(T)*Q(S\T)`.

The unique block containing min(S) selects a disjoint cycle set exactly once.
The final Q(full) is the generic permanent. Every coefficient, cycle, path, and
partition is built from B; no permanent appears in the initial state.

The cycle-factor constructor has gate count

`G_cycle(n)=(n-2)^2*2^(n-1)+n(n+1)/2-2` for n>=2.

Its Bell table uses `(3^n-1)/2` product terms and exactly
`G_Bell_table(n)=3^n-2^n` scalar gates including sums. Thus total Bell/cycle
counts at n=2,3,4,5 are **6,27,105,368**. The report separately records path,
cycle, partition state counts and transitions. This supplies a positive
factorization alternative whose contraction cost is fully charged.

## Original marked-polynomial scalar model

`build_marked_circuit(A, variant)` substitutes each generic weight leaf by
`(1+a_ij^2)*z^(2^(i*n+j))` in an actual inherited scalar Q[z] DAG. The p_ij are
permitted rational leaves and all marker powers are built through binary
squaring. Marker/entry construction adds exactly `2n^2-1` gates; no coefficient
operation remains inside the returned final circuit. Its construction process
has explicitly compiled the mixed derivatives into scalar nodes.

The complete marked circuits use the following gates for n=2,3,4,5:

- Demand chain: **15,47,133,373**.
- Eager chain: **17,57,171,503**.
- Cycle/Bell chain: **13,44,136,417**.

Additional development diagnostics instantiate Vandermonde A and compare all
three final Q[z] outputs with an independent marked permutation oracle. All
**12/12** formal-z checks passed. These diagnostics are separate from the
frozen generic-weight score and include no held-out instances.

## Frozen evidence and remaining constructive theorem

The frozen `positive-mixed-dev-v1` boundary is generic formal B at n=2,3,4,5,
with five assertions per n: eager output, demand output, Bell output, all F
prefix jets, and all future-G path jets. Its metric is exact assertion pass
fraction. The observed score is **20/20=1.0**, with evaluator SHA-256
`b139cb2c4f2d50a51d1a6246baa7f3376bb45ae880bbb06126c5ccbb7ad8057c`.
The evaluator was frozen before execution and never changed. Adding the
marked-instantiation production helper required a rerun of this same boundary;
both runs passed. No new Lean declaration was compiled in this node.

The rank-one route now has a compact, cheaply initialized auxiliary chain and
explicit contraction circuits with substantially lower finite gate counts than
n16. The remaining theorem must provide **polynomial scalar compression of its
mixed-derivative dependencies or cycle/Bell contraction**, with cheaply built
state coefficients and initial data, while preserving original marked weights.
One precise target is a polynomial family of scalar features closed under
`G[j,k] -> G[j,k]+x_i G[j,i]G[i,k]` and `F -> F+x_i F G[i,i]`, together with a
cheap final full-occupancy functional. Neither a ring-valued n^2 state count nor
an uncharged mixed derivative proves this compression.

Formal bridge sublemmas are nilpotent-unit inversion, the rank-one matrix and
determinant update identities over the intended ring, derivative/quotient
coefficient agreement, and the cycle/path invariants. Closing those sublemmas
would support the new construction; the polynomial contraction bound remains
an explicit additional obligation.
