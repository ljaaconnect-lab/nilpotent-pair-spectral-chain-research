# n57: actual dense scalar compiler and conditional theorem

Artifact version `n57-dense-scalar-compiler-v1`, branch `arbor/n57`, builds on
n40. The development protocol was fixed in `n57-protocol.json` before the first
Lean probe or positive evaluator run. The strict formal score is 4/4 = 1.0;
the separate finite Python score is 16/16 = 1.0. Neither score measures progress
on the missing target representation.

## Kernel-verified outcome

`MatrixScalarCompiler.lean` candidate 02 compiled with Lean 4.34.1 and the pinned
Mathlib environment: exit code 0, zero errors, no warnings or remaining goals.
The final source SHA-256 is
`6c2ad98a6eca9590430dcc973cec57daaa1d1e28c9009366fdb50df96fd5a69b`.
All 24 new theorem declarations were audited. Their only axioms are the standard
Lean axioms `propext`, `Classical.choice`, and `Quot.sound`; the final source
contains no placeholders or added axioms. Two full candidate compiles out of
20, four incremental probes, and one inherited dependency compile were used.

The accepted four obligations are:

1. `matrix_power_correct` adapts the n40 `MonoidData` to genuine Mathlib matrix
   multiplication and proves `compilePower (matrixMonoid r R) M k = M^k` for
   any semiring R, any r, any square matrix M and any natural exponent k.
2. `scalar_compiler_correct` proves the constructed scalar DAG evaluates to
   `sum_i u_i * (sum_j (M^k)_ij * v_j)`, also for any semiring and arbitrary
   supplied entries. It is a semantic proof through scalar sums, scalar dot
   products, dense products, each shared matrix instruction, its instruction
   sequence, matrix powers, and the final contraction.
3. `dense_product_gate_count` proves that the constructed dense product DAG
   has exactly `2*r^3-r^2` elementary scalar gates when r>=1.
4. `conditional_scalar_budget` proves
   `S + scalarCircuit(r,n^n-1).gates <= S + 4*r^3*n^2 + 3*r^2`
   with both r>=1 and n>=2 stated explicitly, and S an explicit input-cost
   parameter. Supplying subcircuits constructing M,u,v with cost at most S is
   a separate assumption when applying this to any external representation.

These proofs apply to polynomial coefficient semirings as well as rational
scalars. Formal z markers can remain in supplied entries; the compiler performs
only scalar additions and multiplications and uses free zero/one leaves.

## Circuit representation and actual scalar export

The Lean `Circuit` is a compositional DAG representation. Its elementary nodes
are scalar `add` and `mul`, each costing one gate. Wire maps only reference
existing input/output wires. Zero/one constants are leaves. A finite parallel
family explicitly contains one scalar subgraph per index, with the sum of its
gate counts charged. Sequential composition connects already constructed output
wires to later inputs, retaining shared outputs. This expands all matrix and
tensor operations into their scalar arithmetic before counting them.

`sumCircuit r` uses r-1 scalar additions for r>=1. `dotCircuit r` emits r scalar
products and that summation. `denseProduct r` emits one dot product per matrix
entry. The powering state has separate interfaces for the original matrix M
and the current matrix X. Each instruction preserves the original M through
wiring and computes X*X or X*M through one newly emitted dense scalar product.
The input M is never reconstructed or replaced by a target answer.

`dense_compiler.py` implements the schedule as an actual topologically ordered
SSA graph. Every M_ij,u_i,v_i has an explicit named input leaf, every arithmetic
node references prior scalar wire IDs, and a square uses the same current matrix
references on both operands. Four complete serialized graphs are in
`scalar-dags/n2-r2.json` through `scalar-dags/n5-r5.json`, including stage
boundaries, intermediate matrix output wires, and the final scalar output.

The universal theorem certifies the Lean circuit construction and its semantic
gate count. The Python SSA exporter is an independently executable implementation
of the same schedule. Its formal lowering equivalence to the Lean `Circuit`
syntax has not been proved; its exported graphs have the exact finite
validation below. This distinction is explicit in `n57-dev-report.json`.

## Measured evidence and derived counts

For r=n and n=2,3,4,5 respectively:

- K = 3,26,255,3124; shared matrix instructions J = 2,6,14,15.
- Actual scalar addition nodes: 11,116,687,1524.
- Actual scalar multiplication nodes: 22,174,916,1905.
- Actual total scalar gates: 33,290,1603,3429, excluding S.

The frozen 16 checks consist of four topology/full-count checks and twelve exact
evaluation agreements, using identity, cyclic-permutation, and explicit dense
integer matrices. The vectors are `u_i=i+1`, `v_i=2*i+1`. The oracle repeats a
matrix-vector update k times and then takes the dot product; it does not reuse
the scalar graph or binary matrix-power algorithm. Exact integer outputs are
compared before recording their bit lengths and hashes. No held-out boundary,
counterexample search, target-answer initialization, or optional dimension
experiment was used.

The kernel-verified exact general count is

    J*(2*r^3-r^2) + (2*r^2+r-1).

The dense multiplication term expands to r^3 scalar multiplications plus
r^2*(r-1) scalar additions. The final contraction expands to r matrix-vector
dot products followed by one dot product: r^2+r scalar multiplications and
r*(r-1)+(r-1) scalar additions. The separate addition/multiplication breakdown in the Python report
is measured from actual serialized nodes; the accepted Lean theorems derive
the exact total and conditional bound.

The n40 kernel theorem gives J<=2*n^2 at K=n^n-1. In n57, the complete scalar
construction and the inequalities for its product and contraction costs are
composed in Lean, yielding S+4*r^3*n^2+3*r^2 for all r>=1,n>=2. S includes every
gate in the supplied M,u,v construction. Gate counts alone do not account for
the bit-operation costs of large rational constants or values.

## Refinement constraints and remaining mathematical task

The first probes exposed a noncommutative matrix-power rewrite whose monoid
definition unfolded before its induction hypothesis, and an implicit finite
index in parallel circuit pattern matching. These were fixed by a direct
congruence proof and explicit pattern binders. Later compiler feedback required
the correct scalar summation prefix count, an explicit input-wire extensionality
lemma, and reduction of the two `Sum` injection cases before rewriting the
matrix-vector semantic lemma. Candidate 01 retained three such semantic
alignment errors and scored zero; candidate 02 closed them. Every failed source
snapshot and real error output is retained. No explicit `sorry` was used even
in new probes. Lean error-recovery audit output can contain `sorryAx` for failed
declarations; those attempts are rejected by the strict evaluator.

The unresolved target-specific lemma remains an explicit construction of M,u,v
with polynomial dimension r and polynomial initial scalar cost S, satisfying
`[t^K] Hhat_A(t,z) = u^T M^K v`, or an equivalent compact exact contraction.
This node verifies the conditional compiler needed after such a construction.
It does not establish that representation or resolve Conjecture 1.5.

## Reproduction

Use the prepared pinned Mathlib environment file, unchanged. `verify_dense.py`
applies all three entries `LEAN_PATH`, `LEAN_SRC_PATH`, and `LEAN_SYSROOT`, then
prepends this worktree and its local `proof-build/` directory to `LEAN_PATH`.
The only generated `.olean` is the inherited `PowerCompiler.lean` module in
that local directory; no shared Mathlib cache or Arbor state is edited.

    python verify_dense.py PowerCompiler.lean --kind dependency
    python verify_dense.py MatrixScalarCompiler.lean --kind candidate
    python evaluate_dense.py
    python report_dense.py

Compiler commands, exact source snapshots, audits and diagnostic output are
under `n57-logs/`. `n57-verification-history.json` records separate round counts.
`n57-python-report.json` records the frozen positive cases and measured gates.
`n57-dev-report.json` consolidates these records and graph hashes after checking
that the accepted source and protocol still match the actual evidence.
