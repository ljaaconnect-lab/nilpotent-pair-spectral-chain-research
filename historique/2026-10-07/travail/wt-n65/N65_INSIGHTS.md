# n65 distilled insight

The bounded inversion spectrum supplies a genuine constant-coefficient
recurrence of order D+1, D=n(n-1)/2, but it does not construct its initial
jets J0..JD. The written scalar initializer constructs only J0 and J1 by
complementary minors and charges every gate. Its polynomial count is a
partial result, explicitly unexecuted and unverified in this leaf.

The inverse-coordinate operator L in N65_BLUEPRINT.md is an exact informal
transition for F_k=J_k/det(X). It exposes a further requirement for any proposed
compression: a polynomial state map must intertwine the full differential
operator on every reachable function. A variable-coefficient basis relation
cannot be powered as an ordinary matrix without accounting for derivatives
of those coefficients. A constant-coefficient invariant basis with cheap
evaluations would also suffice; no such basis was supplied.

Falling-jet generating factors recover exactly the n61 partial-matching
cofactor expansion. This preserves the constructive identities while leaving
the number of scalar cofactor states unresolved. No repeated baseline test,
Hankel regression, counterexample campaign or lower-bound search was run.

Strict score: null because no complete eligible polynomial candidate was
isolated under the frozen three-obligation evaluator. This is an audited
research boundary, not a proof that a positive construction cannot exist.
Formal compiler attempts/probes: zero; the shared Hilbert budget is preserved.
No .arbor, outputs or held-out files were read or written.

Artifact files: initial_jets.py, N65_BLUEPRINT.md, n65-dev-report.json,
n65-source-record.json. The initializer API is build_initial_jets(n,A=None),
returning a two-output scalar DAG and exact-construction metadata. It must
not be advertised as a complete target compiler or companion initialization.
