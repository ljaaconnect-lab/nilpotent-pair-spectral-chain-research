# Atomic second-prefix blueprint — n76

The four frozen leaves concern two actual row insertions over every commutative ring and every natural n, including zero. They do not assert a closure for later prefixes.

The dependency is the independently compiled `ActualClosedSubsetTransfer.state`, whose seed is the empty subset and whose step sums over one erased column. Its actual polynomial coefficient invariant is reused from the verified object; this node never recompiles that dependency.

The dependency graph is acyclic:

1. B1 distributes the two finite row sums.
2. `erase_diagonal` uses `sum_erase_add` for a column already in H. B2 sums that equation and then applies B1.
3. `pair_exponent_iff` identifies a squarefree degree-two exponent with precisely two distinct inserted columns. `table_two_pair_expansion` applies the imported actual coefficient invariant to the product of the two linear row forms. Thus this is a statement about the actual seed/step table, rather than a response defined to equal the requested expression.
4. `table_two_zero_of_card_ne` proves that table entries vanish except at subsets of size two. `signed_response_eq_mass` therefore justifies the original signed summation: (-1)^(|U|+|J|)=(-1)^|J| for every nonzero term.
5. `powerset_pair_indicator` and finite-sum commutation give `table_two_mass`, summing precisely ordered pairs of distinct columns in H. B3 takes H=univ\J and invokes B2.
6. `complement_sum` recovers each H-sum from its initialized total and its J-sum. The initialized diagonal and total declarations are direct equalities of actual data. B4 proves that the query built from those data equals B3's actual signed response.

The initialized data are b, c, their pointwise product d_j=b_j*c_j, and the three totals. Initialization uses n scalar multiplications and 3*max(n-1,0) scalar additions. For a specified J of size m, the query uses 3*max(m-1,0) additions, three total-minus-subsum subtractions, one row-product multiplication, one diagonal subtraction, and multiplication by the known sign literal. Subtraction is compiled as multiplication by -1 followed by addition if the scalar model contains only + and *. A final known sign can be omitted for positive sign. No variable division or coefficient-extraction gate is used.

A specified subset query is linear in n. Evaluating an arbitrary future functional over all subsets, or closing all n prefixes with a polynomial number of states, remains a separate obligation. This artifact proves neither of those statements and carries root score zero.

The source and evaluator are frozen before the first compiler call. Every complete candidate invocation counts toward the cap of three, including failed calls and timeouts. Each round archives its exact source and actual compiler output. All declarations are explicitly audited using #print axioms; acceptance requires compiler exit zero and only propext, Classical.choice, Quot.sound. Final status is recorded in n76-strict-report.json.

Final verification: candidate 2 compiled with exit code zero after two total compiler invocations. All four fixed leaves and all 16 supporting declaration audits were accepted. The source SHA256 is `5dfd49a3b490f7a4d6cc289491fbb8a4f04484690dbbd33ae40fe5f9a909a321`; the compiled object SHA256 is `f75267e1ad930762ccbb9d34eaeb0e925d419d44c0dd51299040a481b743d4a3`. Candidate 1 remains archived with its rejected diagnostics. Candidate 2's warnings concern unused simp arguments and deprecated lemma aliases; no statement was weakened and no compiler call was spent on cosmetic cleanup.

In the literal +/* model, four subtractions cost eight gates. Apart from initialization, a specified query therefore costs at most `3*max(|J|-1,0)+10` gates, counting the row product and a possible multiplication by the known negative sign. The denominator of the local development score is the four frozen leaves. A score of 4/4 records these accepted identities, while `root_conjecture_verified=false` records that the conjecture remains open.
