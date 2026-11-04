# N75: elementary first-prefix bridge

The original uniform scalar-circuit conjecture is unchanged and remains open.
The six leaves are proved sequentially, A4 first. No coefficient query, arbitrary
linear functional, matrix determinant, or normalization is a free scalar gate.

## Exact dependency graph

A4 depends on the actual principal submatrix of `-I + u*1ᵀ`, indexed by
`{j // j ∈ J}`, Mathlib's rank-one determinant identity over a commutative ring,
and determinant under matrix negation. It includes `J = ∅`.
A1 partitions the sum of the explicitly supplied vector `b` into `J` and its
complement; `h := total b` is calculated from that vector.
A2 uses an actual coefficient array for the square-zero product `q_j*q_J`:
it has a unit coefficient at `insert j J` only when `j ∉ J`, and zero elsewhere.
The post-insertion signed functional has one external minus sign; thus the
unit term has sign `-(-1)^(|J|+1) = (-1)^|J|`.
A3 sums these one-column responses with weights `b_j`, then applies A1.
A5 uses only the explicit local condition `∀j, h*u_j=b_j`, distributes `h`
across the finite sum, and combines A4 with A3.
A6 sums A5 against arbitrary supplied coefficients `f_J`. This is semantic
linearity, and computing that sum for arbitrary f has no polynomial cost claim.

The graph is acyclic: A4 and A1 and A2 are independent; A3 ← A1,A2;
A5 ← A3,A4; A6 ← A5.

## Resource and normalization boundary

Data are exactly `b` and its calculated total `h`; no desired output is initialized.
A single response query uses the finite sum over J, subtraction through rational
-1 and addition, then multiplication by the known index sign. This gives an
explicit +/* arithmetic expression with linearly many operations in n when b
and h are already scalar circuit outputs. This descriptive count is not a new
Lean circuit-complexity theorem. No variable inverse is a permitted leaf.

The condition `h*u=b` is a local algebraic premise. Its existence and division-free
scalar compilation for arbitrary inputs, especially `h=0`, are separate required
obligations. No global or second-prefix closure is claimed by A1–A6.

## Verification discipline

At most eight Lean invocations total, including dependency builds, probes, and
retries. The shared window already used seven invocations. Every run has a frozen
source snapshot, source hash, exact environment, final exit code, and axiom output.
Only standard `propext`, `Classical.choice`, `Quot.sound` may occur. No B_test,
.arbor, or outputs access. All accepted declarations will be audited before freeze.
