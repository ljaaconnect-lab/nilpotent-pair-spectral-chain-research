# n40: verified shared binary powering

Artifact version: `n40-shared-binary-power-v1`. Boundary: `B_dev-formal-power-compiler`.

The final `PowerCompiler.lean` kernel-verifies all three obligations fixed in
`n40-obligations.json` before the first probe. Candidate 03 returned exit code 0,
zero errors, and dev score 3/3 = 1.0. Three complete candidate rounds were used
out of the fixed budget of 16; 27 incremental/library probes are recorded
separately. No held-out boundary was read.

## Constructive plan and its interpretation

`MonoidData` supplies an arbitrary type, identity, multiplication, associativity,
and both identity laws. This is exactly the data required for a monoid, without
commutativity. The element `a` is explicitly supplied. The proof never takes a
permanent, coefficient, or unknown target value as input.

The plan for exponent 0 or 1 is empty. For k > 1 it recursively computes the
plan for floor(k/2), then appends one `square` instruction, followed by one
`multiplyBase` instruction when k is odd. Interpretation starts from `a` when
k > 0 and returns the identity directly when k = 0. Each instruction uses one
multiplication. A square references the same previous value twice; it does not
duplicate the already constructed subcircuit.

`power_plan.py` exports this convention as actual SSA nodes: supplied identity
and base leaves, then a new multiplication node per instruction, with references
to prior nodes. `power-dag-examples.json` contains complete serialized plans for
k = 0, 1, 2, 3, 26, 255, 3124. The central exponents for n = 2, 3, 4, 5 require
respectively 2, 6, 14, 15 shared multiplications. These finite counts illustrate
the construction; the Lean bound is universal.

## Informal blueprint of the accepted proof

1. `run_append` identifies the interpretation of concatenated instruction
   lists with sequential execution, using `List.foldl_append`.
2. `power_add` derives a^(j+k) = a^j * a^k by natural induction and associativity.
   Its final proof term uses no axioms.
3. `positive_plan_correct` uses strong recursion on k. The recursive call is
   legal because floor(k/2) < k. The even branch squares a^(k/2); the odd branch
   also multiplies the result by the supplied base. `omega` discharges the
   integer exponent identities. `binary_plan_correct` handles k = 0 separately.
4. `binary_plan_logarithmic` uses the same recursion and the defining equation
   for `Nat.log2`: each recursive stage adds at most two instructions while
   log2(k) = log2(floor(k/2)) + 1 for k >= 2.
5. `central_exponent_log_bound` proves n <= 2^n, hence n^n <= 2^(n*n), and
   combines K = n^n - 1 < 2^(n*n) with `Nat.log2_lt`. The n >= 2 hypothesis
   supplies K != 0.
6. `central_plan_gate_bound`, outside the three-obligation denominator,
   composes the two accepted bounds to prove the actual plan length is at most
   2*n^2 when its exponent is K.

There are no remaining goals, placeholders, custom axioms, or unproved lemmas
in the accepted source. Its SHA-256 is
`c66d703e08237358eb992905106e01cb040d27314d42053030821f335450c863`.
The seven printed declaration audits use only the standard Lean axioms
`propext`, `Quot.sound`, and, for the logarithm/exponent comparison and its
composed helper, `Classical.choice`. The exact per-declaration audit is in
`n40-dev-report.json` and `power-logs/candidate-03/stdout.log`.

## Scalar matrix compilation, conditional on explicit initial data

Suppose an actual r-by-r matrix M and vectors u,v have been constructed over
the scalar coefficient algebra, with r >= 1. Let S include every gate used to
construct M, u, and v, preserving all formal z markers. A dense matrix product
uses r^3 scalar multiplications and r^2*(r-1) scalar additions, hence
2*r^3-r^2 scalar gates. This charges every tensor/matrix operation through
scalar additions and multiplications.

Let J be the actual instruction count of the shared binary plan. Constructing
M^K and then contracting u^T M^K v costs at most

    S + J*(2*r^3-r^2) + (2*r^2+r-1).

The contraction term comes from a matrix-vector product with r^2
multiplications and r*(r-1) additions, followed by a dot product with r
multiplications and r-1 additions. A requested fixed matrix entry needs no
final contraction. `dense_scalar_cost` in `power_plan.py` implements these
explicit conventions. Identity constants and already supplied leaf inputs are
free leaves in the usual arithmetic-circuit model; initialization costs are
always assigned to S.

The accepted universal helper gives J <= 2*n^2 for K = n^n - 1. Since
2*r^3-r^2 <= 2*r^3 and 2*r^2+r-1 <= 3*r^2 when r >= 1, the resulting upper
bound is

    S + 4*r^3*n^2 + 3*r^2.

Consequently, the additional assumptions r <= n^d and S <= n^c would give

    n^c + 4*n^(3*d+2) + 3*n^(2*d).

The scalar arithmetic accounting in this section is an explicit conditional
construction, not an additional Lean theorem in the frozen metric. Rational
constant bit lengths and a bit-operation implementation require their own
cost accounting when interpreting scalar gate size as runtime.

## Remaining constructive sublemma

The research target still needs an explicit M,u,v satisfying

    [t^K] Hhat_A(t,z) = u^T M^K v,

with a proved polynomial bound on r and a polynomial-cost scalar construction
of every initial datum from the original rational entries and formal z. An
equivalent compact exact contraction could supply that data. None of r, S, or
this representation identity is established here. The initial base remains
explicit and arbitrary; the verified powering ingredient does not solve
Conjecture 1.5.

## Error constraints and reproducibility

Compiler errors are retained in `power-logs/` together with snapshots of the
exact attempted source. Broad recursive `simp` encountered a recursion-depth
failure in candidate 01; its replacement unfolds only the needed equation.
An earlier exploratory simplification timed out at the fixed 60-second limit;
the additive-power lemma was then written as a direct induction proof term.
Opaque list lengths were exposed with the specific `List.length_cons` and
`List.length_nil` lemmas before `omega`. These repairs constrain the accepted
implementation instead of suppressing diagnostics or increasing resource
limits.

Probe 01's initial harness failed on cp1252 output encoding. Its compiler exit
was not preserved and remains unknown; it earns no score. The harness was
changed to explicit UTF-8. Probe 02's old error counter missed Lean's
`error(lean.unknownIdentifier)` spelling; the nonzero exit and original output
remain visible, and later runs use a corrected regex. Archived probe sources
can contain temporary `sorry` skeletons and are diagnostic evidence only.
`PowerProbe.lean` is a library-name discovery probe containing an unresolved
name, not a deliverable proof. Only the accepted final source and its successful
compiler record count as solved obligations.

From this worktree, use the existing pinned Lean executable:

    python verify_power.py PowerCompiler.lean --kind candidate
    python power_plan.py
    python report_power.py

The verifier saves a new source snapshot, compiler output, axiom audit, strict
score, and candidate budget usage. The report command only summarizes existing
compiler evidence and checks that its source hash still matches. No Lake build,
Mathlib cache mutation, shared Arbor-state write, or network operation is used.
