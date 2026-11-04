# Hilbert n39: fixed square-zero update obligations

The frozen boundary is `rank-one-obligations.json`: five complete declarations,
with sixteen complete candidate verification rounds. Tactic-level probes are
tracked separately. No successful declaration may contain `sorryAx` or depend
on a newly declared axiom. Supporting generic matrix identities do not change
the final target's ring, nilpotence, or two-sided inverse hypotheses.

The hardest product identity is attempted first. Its proof expands
`(A-x•U)*(G+x•(G*U*G))`. The linear term cancels using A*G=I; the quadratic
term contains x*x and vanishes. The reverse product uses G*A=I. These statements
hold for arbitrary U; taking U=uv^T gives precisely the requested rank-one
formula. Neither equality assumes an inverse operation is a circuit gate.

The scalar identity follows by normalizing the quadratic polynomial and using
x*x=0. The propagated formula for a left factor B follows from distributivity,
scalar centrality, and matrix associativity. It makes the inverse-update term
available to the n19 resolvent recurrence without changing its scalar model.

## Verified result

All five frozen declarations were accepted together by the pinned Lean 4.34.1
compiler in round 9, and were accepted again with the additional outer-product
bridge in round 12. Both accepted files returned exit code 0. The final file has
no incomplete goals, `sorry`, `admit`, `unsafe`, or new axiom declarations.
Every printed axiom audit contains only `propext`, `Quot.sound`, and, for the
matrix lemmas, `Classical.choice`. The fixed development score is 5/5 = 1.0;
this is an obligation pass fraction, not confidence in the root conjecture.

The additional accepted lemma `propagate_rank_one` gives the explicit formula

    B*(G + x*(G*(u v^T)*G))
      = B*G + x*((B*G)*u)*(v^T*G).

Here scalar multiplication of matrices is displayed by `*` for readability;
the Lean source distinguishes scalar multiplication `•` from matrix products.
The correction is a single outer product. Specializing `u` to the i-th basis
vector and `v` to the i-th row of B yields the intended future-entry update
`H[j,k] + x*H[j,i]*H[i,k]` for `H=B*G`. That basis-vector specialization is an
informal consequence, not an additional theorem proved in this artifact.

## Feedback constraints and scope

Exactly twelve complete candidate compiler rounds were consumed from the
sixteen-round budget. Rounds 1 and 2 timed out without diagnostics at 60 seconds;
after a genuine import probe, all three exported Lean environment fields were
supplied and the subprocess deadline was raised to 180 seconds. Rounds 3 and 5
exposed only the required additive cancellation identities. Round 10 exposed a
scoped-notation parser issue; round 11 exposed bottom-up `simp` rewrite order.
The final optional bridge uses qualified vector products and ordered `rw`.
Full compiler output, source hashes, and audits are in `rank-one-progress.json`.

No held-out data were accessed. No shared cache or Arbor tree was modified.
The original n19 evaluators and scripts are unchanged.

These results establish explicit algebra in a square-zero coefficient ring.
They do not make a matrix inverse, quotient-ring multiplication, coefficient
projection, residue, or diagonal an allowed costless scalar gate. The next
constructive obligations are to instantiate the update in the square-zero ring,
justify the determinant/reciprocal scalar update, and compile the complete
coefficient contraction into a polynomial-size scalar circuit with cheap
initialization. The present artifact proves none of these complexity claims.
