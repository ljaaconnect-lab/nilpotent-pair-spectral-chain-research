# N38: indexed assignment and occupation labels

`LabelBridge.lean` contains thirteen new accepted declarations. It imports
the earlier audited core digit encoding and general-ring sparse pairing.
Both imports were built locally from their unchanged source, with compiler
evidence recorded separately. No earlier n2 pairing was introduced as a new
claim or counted as a new lemma.

The actual indexed label is

`indexedLabel base xs = (xs.mapIdx (fun i d => d.val * base^i)).sum`.

The shifted identity proves that starting at position k multiplies the
recursive digit encoding by base^k. Its proof explicitly identifies the
mapIdx shift functions by addition associativity and commutation, then uses
power succession and distributivity. Consequently the zero-start indexed
sum equals the earlier recursive encoding. Its fixed-length injectivity
therefore transfers to the actual indexed power sum.

The digit bound is `encodeDigits base xs < base^xs.length` when base>0.
The proof bounds each step d+base*tail using d<base and tail<top. The positive
base binder is preserved; no weaker digit bound is silently substituted.
It yields `indexedLabel base xs <= base^xs.length-1`.

For any function f : Fin length -> Fin base, the assignment label uses
`List.ofFn f`. It is injective for base>0 and satisfies
`assignmentLabel base length f <= base^length-1`. A separate accepted
identity states exactly

`assignmentLabel base length f
 = (List.ofFn (fun i => (f i).val * base^i.val)).sum`.

Thus the connection is to an explicit finite indexed sum, not to an unnamed
encoding assumed equivalent to the paper's labels. Setting base=length=n
gives the base-n labels used for assignments, and restriction to permutations
preserves injectivity. The determinant's permutation enumeration and signs
still require their own checked specialization.

The accepted occupation selector uses natural count values explicitly:

For n>0, any length and count : Fin length -> Nat with count(i)<=n,
if `sum_i count(i)*(n+1)^i = sum_i (n+1)^i`, then every count(i)=1.

Counts are converted to Fin(n+1) using exactly the supplied bound. The label
equality implies equality with the all-one digit function. An additional
assumption sum_i count(i)=n is unnecessary for this stronger selector, and
was not used as a substitute for the required count bound. Specializing
length=n gives the selector needed by the Gram/occupation construction.

Finally, a duplicate-free list of finite assignments maps to a duplicate-free
list of these indexed labels. `indexed_assignment_pairing` applies the
earlier general-ring sparse-product theorem with K=base^length-1; the label
bound and distinctness are proved, while signs in {1,-1} are explicit
remaining premises. It returns the actual sparse-product coefficient at K
equal to the sum of the weights. It is valid over any R with
Lean.Grind.CommRing R, allowing polynomial-valued weights after the ring
instance and interpretation are supplied in a checked specialization.

All 24 actual compiler invocations are retained: 22 candidate rounds and two
local dependency builds. Final round 24 has exit 0 and all thirteen explicit
axiom audits contain only propext, Classical.choice, Quot.sound. Earlier
unsolved goals and failed broad-grind attempts are retained as real logs.
No final declaration uses sorryAx or a custom axiom. The strict audit matches
current source bytes and dependency source bytes to those compiler logs.

The Mathlib Polynomial interpretation remains a separate target. Mathlib
cache preparation was controlled by the parent; this node did not modify
the installation or consume a candidate round on unavailable modules. TLS
failures observed during this proof window were subsequently corrected by
the parent, who reported cache downloads and decompression with zero failures.
The available cache still needs an independent import test. In particular this
node does not identify sparse lists with Mathlib Polynomial R, prove the
general determinant/Vandermonde identities, or establish a polynomial-size
scalar extractor. The original Conjecture 1.5 remains unchanged and unproved.
