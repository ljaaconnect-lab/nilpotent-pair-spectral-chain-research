# n61 measured result and constructive frontier

Development score: **24/24 = 1.0** for the six predeclared assertions at each
n=2,3,4,5. The selected candidate is `shared_cofactor_matchings`. The score
measures exact finite validation, not conjecture completion. Neither the
generic cofactor compiler nor its gate bound has been universally certified
in Lean in this leaf. The independent n62 bridge has separate provenance.

The actual live generic circuits have these counted binary operations:

- n=2: 7 additions + 6 multiplications = 13 gates.
- n=3: 48 additions + 60 multiplications = 108 gates.
- n=4: 445 additions + 545 multiplications = 990 gates.
- n=5: 5175 additions + 5328 multiplications = 10503 gates.

Compiling all original prescribed entries `(1+a_ij^2)z^(2^(in+j))` adds
exactly 2n^2-1 multiplications, including all shared marker squarings. The
marked circuits therefore use **20,125,1021,10552** gates. All four marked
circuits were evaluated exactly in Q[z] against an independent permutation
oracle at the frozen rational matrix A_ij=(i+1)/(j+2). Formal z was preserved.
The same generic circuit was checked at arbitrary formal x_ij, rather than
inferring an identity from those numerical rational inputs.

Actual scalar DAGs, topology, counts and allowed-leaf provenance are saved as
`n61-generic-dag-nN.json` and `n61-marked-dag-nN.json`. Unreachable arithmetic
was eliminated structurally; allocated generic gates before liveness were
19,138,1230,14085. The live operations above are the actual final circuits,
not a count of differentiated or expanded monomials.

The universal integer matching preprocessing has these exact measurements:

- n=2: 2 final states, 2 distinct minors, 3 cached edge products; 1 attempted
  transition, 1 integer addition, 1 integer multiplication; coefficient bits 2.
- n=3: 13 final states, 11 distinct minors, 18 cached edge products; 42 attempted
  transitions, 15 integer additions, 14 integer multiplications; coefficient bits 3.
- n=4: 99 final states, 54 distinct minors, 122 cached edge products; 1326 attempted
  transitions, 201 integer additions, 221 integer multiplications; coefficient bits 4.
- n=5: 813 final states, 227 distinct minors, 949 cached edge products; 31190 attempted
  transitions, 3030 integer additions, 3119 integer multiplications; coefficient bits 5.

These integers depend only on the universal Euler projector list. No input
leaf is initialized with P_A or a coefficient of Hhat. Their general l1
bound `(1+n(n-1))^(n(n-1)/2)` supplies an informal polynomial bit-length
bound, even though enumerating the states does not have an established
polynomial construction cost. The minor constants have O(log n) bits;
the remaining marked constant leaves are prescribed p_ij. Source §1.5 allows
these leaves and separately requires polynomial uniform construction time.
That time requirement is still open for this construction.

Positive local cofactor identities were checked for every used matching,
including the empty matching and the full matchings. This supplies an exact
constructive decomposition into ordinary determinants and products. The
full scalar graph was then evaluated independently; these are distinct
checks, rather than treating the decomposition as a free contraction.

The two other frozen variants clarify where this implementation pays its
cost. The unsimplified four-specialization construction has seed costs
30,150,476,1170 and exact final generic costs
127,39933267,2258865300972646960551251,
1883867033886289599693693559587956291023529309711360800584979795.
The n=2 circuit was materialized and evaluated; larger counts use the
explicit recurrence G_next=4G+7 and are not claimed to be measured executions.

Shared row specializations produced valid live circuits of 19 and 1040 gates
at n=2,3. At n=4,5 this precisely frozen implementation reached its 200000-node
cap, after allocating 199977 and 199967 arithmetic gates. Completed row-stage
counts and specialization-cache sizes are retained in the reports. This is
a resource constraint on this variant, not a counterexample or a lower bound.
The selected cofactor construction stayed within the limit: full n=5 exact
validation took 37.49 seconds under the fixed 120-second bound.

The only evaluator adjustment normalized polynomial equality: a first n=2
report returned 5/6 because the actual SymPy Poly used domain QQ while the
oracle used ZZ. Both expressions were identical and the exact difference
was zero. The preserved v1 log/probe and v2 source freeze document the change
to a zero-difference comparison. The protocol, candidate source, denominator
and three variants were unchanged. The final report uses the v2 evaluator.

The next constructive proof obligation is a **uniform polynomial scalar
sharing scheme for the grouped Euler projectors or their complementary
cofactors**, preserving all formal entry markers. It must supply actual
add/mul gates, an explicit total bound including data construction, and
admissible constant provenance/bit lengths. The identities alone do not
provide that scheme. The explicit general upper bound in N61_DESIGN.md is
not a polynomial bound and must not be interpreted as a lower bound. No
new numerical experiment or impossibility claim is needed to state this gap.

Reproduction from this worktree:

    python validate_euler_identity.py --n 2
    python validate_euler_identity.py --n 3
    python validate_euler_identity.py --n 4
    python validate_euler_identity.py --n 5
    python evaluate_euler.py --mode validation --n 2
    python evaluate_euler.py --mode validation --n 3
    python evaluate_euler.py --mode validation --n 4
    python evaluate_euler.py --mode validation --n 5
    python evaluate_euler.py --mode diagnostic --n 2
    python evaluate_euler.py --mode diagnostic --n 3
    python evaluate_euler.py --mode diagnostic --n 4
    python evaluate_euler.py --mode diagnostic --n 5
    python evaluate_euler.py --mode aggregate

The selected API is `euler_compiler.build_cofactor(n) -> (graph,output)`
with formal x0..x(n^2-1), or `build_marked(A) -> (graph,output,metadata)`.
For the marked result, `graph.evaluate(output)` returns a sparse Fraction
dict keyed by `(0,z_exponent)` and exact evaluation statistics; `.gates`
and `.serialize(output)` describe the actual circuit. No held-out case
or shared Arbor state was read or written by this leaf.
