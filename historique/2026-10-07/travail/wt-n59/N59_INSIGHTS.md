# n59: verified conditional polynomial criterion

Artifact `n59-composed-polynomial-criterion-v1`. The protocol fixes two principal
obligations before attempts. Candidate 01 compiled with Lean 4.34.1, exit 0,
zero errors and no remaining goals. Strict development score: 2/2 = 1.0.
Four new declarations were audited; they use only the standard axioms
`propext`, `Classical.choice`, and `Quot.sound`. No new source contains a
placeholder or added axiom. Counters: one complete candidate out of twelve,
one probe, two exact dependency compiles. No numerical experiment or held-out
access was performed.

`ConditionalCriterion.lean` supplies an actual prefix `initial : Circuit I
(Inputs r)`. `composedCircuit` connects that graph to the n57 scalar circuit.
`compose_input_correct` proves its output equals the genuine matrix-power
contraction under the explicit input semantics equality, and its cost equals
`initial.gates + scalarCircuit.gates`. The graph's initialization is charged
once; its input and output wires remain shared by composition.

`Pi c d : Polynomial Nat` is the explicit natural-coefficient polynomial

    X^c + C(4)*X^(3*d+2) + C(3)*X^(2*d).

`Pi_eval` proves its evaluation is `n^c+4*n^(3*d+2)+3*n^(2*d)`. Its c,d
parameters are fixed independently of n. Mathlib's polynomial addition is
noncomputable, so the declaration carries that library marker. This is an
explicit three-term polynomial with an accepted evaluation formula; no unknown
target value or extraction procedure is used in its definition.

`polynomial_composed_budget` applies the accepted n57 dense compiler theorem
and natural-power monotonicity. Its assumptions are all visible:

    r>=1, n>=2, r<=n^d, initial.gates<=S, S<=n^c.

It proves the actual composed graph has at most `(Pi c d).eval n` scalar gates.
The coefficient helper `conditional_target_coefficient`, outside the two-item
score denominator, additionally concludes correctness for `H.coeff(n^n-1)`
only when `H.coeff(n^n-1)=u^T M^(n^n-1) v` is supplied as an explicit hypothesis.
That representation is a theorem argument, never an axiom or asserted discovery.

The remaining target requirements are the exact representation preserving every
formal z marker, source-model admissibility and provenance of the constructor's
rational/parameter leaves, uniform polynomial constructor runtime, and bounded
rational-literal bit lengths. Zero/one Boolean Circuit constants are cheap,
but arbitrary values assigned to environment leaves need the original model's
provenance justification. A scalar gate inequality does not supply those
restrictions or their bit-operation analysis. Conjecture 1.5 remains unresolved.

The sole probe exposed Mathlib's noncomputable polynomial addition requirement;
its real error and exact snapshot are retained. The complete candidate then
closed both obligations and both helpers. Accepted dependencies have the same
source hashes as n40/n57 and were compiled only into this worktree's ignored
`proof-build/`. All three supplied Mathlib environment entries are preserved.
No shared cache, Arbor state, or inherited evaluator was changed.

The final source SHA-256 is
`0d3de6f6475371f1226de953c7c707ff7b5abf31557715be195bdb125fab8189`.
Evidence is in `n59-logs/` and `n59-verification-history.json`; the consolidated
strict report and per-declaration audits are in `n59-dev-report.json`.
Reproduce from this worktree using:

    python verify_criterion.py PowerCompiler.lean --kind dependency
    python verify_criterion.py MatrixScalarCompiler.lean --kind dependency
    python verify_criterion.py ConditionalCriterion.lean --kind candidate
    python report_criterion.py
