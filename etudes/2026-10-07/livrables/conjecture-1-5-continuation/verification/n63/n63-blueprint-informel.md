# Blueprint Informel — n63

The original root protocol is retained verbatim in `n63-original-protocol.json`. Before verification, the root explicitly confirmed that obligation 4 inherits the bound on f from obligation 3. This clarification and the original digest were added to `n63-protocol.json`; exact formal statements and their shared bound appear in `n63-formal-obligations.json`.

## Acyclic plan within three levels

The coefficient is the actual finite sum over S.powerset with exponent `S.card - T.card`; it is not a recursion or a reconstruction postulate.

The hardest branch first proves `coefficient_insert`: separating subsets according to membership of a fresh a splits the finite sum into shifted and unshifted functions. Subset membership justifies the natural-cardinality subtraction and absence of a from each old subset. Then induction on S, generalized over f, reconstructs f(S) from the zeta sum; the shifted induction instance cancels the unshifted one.

The bounded branch uses the triangle inequality for the finite integer sum. Each term has absolute value at most one because the sign has absolute value one and h_f bounds f on every subset. Cardinality of the powerset gives `2^S.card`. Casting the resulting inequality to natural absolute value and using `S.card <= n` gives the strict bound `2^(n+1)`.

No finite-size experiment substitutes for any of these quantified identities. The explicit coefficient, reconstruction, absolute bound and natural absolute bound are the four fixed score obligations. Any unresolved goal remains visible in the journal and final report. These helpers provide no polynomial representation or scalar correction circuit; the separate root score remains zero.

The 12-candidate limit applies to complete candidate attempts. Dependency builds and declaration-retrieval probes are counted separately. Every actual invocation retains command, environment, source snapshot, digest, exit code and diagnostics. The runner has an exclusive lock, and a returned session id must be resumed until its final exit code before a dependent invocation starts.

## Frozen result

The four named primary obligations are accepted, with helper score 4/4 and independent root score 0. The complete source compiled at candidate 11, invocation 11, with no dependency builds, probes or replays. All six theorem declarations have explicit axiom audits contained in `{propext, Classical.choice, Quot.sound}`. There are no unresolved obligations, placeholders or `sorryAx`. Two compiler style warnings report unused automatically included `DecidableEq α` variables; they are retained in the exact compiler log without changing the frozen statements.

The fresh-element recurrence closed at candidate 3 after introducing the pointwise powerset membership hypothesis before using `Nat.succ_sub`. The insertion branch of the general induction closed at candidate 5; the empty branch closed at candidate 6. The absolute-value bound needed the existing, cached `Mathlib.Algebra.Order.Ring.Abs` import, recorded as a dependency constraint from candidate 7. The natural absolute-value bound closed at candidate 9, with the shared h_f retained. Candidate 10 added the named definitional equality by `rfl` for the exact ledger interface.

After the four primary obligations closed, the root authorized one separate bonus, frozen in `n63-bonus-contract.json` before its compilation. `sign_coefficient_natAbs_bound` handles an arbitrary `q : Finset α → Nat` and the actual function `T ↦ (-1 : Int) ^ q(T)`. Its bound hypothesis is discharged by `abs_pow`; only `S.card <= n` remains. This supplies a specific bounded-sign-function application without altering the score denominator or establishing a polynomial representation or compression theorem.

`n63-strict-report.json` binds the accepted source, clarified protocol, original protocol, formal contract, bonus contract and prepared Mathlib modules to their SHA256 digests. It records all invocation exits and exact declaration statements. The original source and every failed attempt remain available for independent replay and audit.
