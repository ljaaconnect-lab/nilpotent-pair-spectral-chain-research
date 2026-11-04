# n77: complete scalar reference for the direct corrected polynomial

The objective is the complete PA(z)=Cn(DA(z)). Central t-coefficient
extraction is archived and is neither a computation step nor an objective
of this node. The fixed n77 protocol is preserved. No Lean invocation,
probe or build is allocated or run. The independently verified n73
subset recurrence and marked_target theorem supply the mathematical
reference; this Python lowering is not a new formally verified compiler.

The decomposition is concrete and contains no unknown answer input:

1. Initialize F(empty)=1. Leaves are p_ij=1+a_ij^2 and formal z, with the
   sole short literal 1. The p leaves are prescribed parameters, rather
   than arbitrary rational constants selected to encode an answer.
2. Construct z,z^2,z^4,... with n^2-1 shared scalar squarings. Construct
   b_ij=p_ij*z^(2^(i*n+j)) with n^2 scalar multiplications. No power node
   or implicit marker operation is left in the serialized circuit.
3. For each nonempty mask U, set k=card(U), use row k-1, and construct
   F(U)=sum_(j in U) b_(k-1,j)*F(U.erase j). Every erased child was
   computed earlier and is shared. A singleton still pays its product
   with F(empty)=1. A k-term sum uses exactly k-1 binary additions.
4. Output F(full). It computes the entire marked permutation sum,
   mathematically PA(z), including every original formal z marker.
   There is no Cn, determinant, derivative, division, coefficient, Wick
   or auxiliary-ring primitive among its circuit nodes.

All n>=1 are supported by the construction. n=1 has two actual gates:
one entry weight and the singleton product. Its state count is two.

## Exact scalar costs

The state count is 2^n and the transition edge count is n*2^(n-1).
The recurrence has one multiplication per edge and

    n*2^(n-1)-(2^n-1)

additions. Its complete generic gate count is (n-1)*2^n+1. Markers cost
2n^2-1 further gates, so the complete marked circuit has

    (n-1)*2^n+2n^2

gates. Every emitted node is charged, even a product by literal 1; no
constant folding is used. The full root is not closed by this exponential
construction. These are costs of this particular recipe, not lower
bounds on another possible circuit.

The serialized input names declare parameter provenance. In the exact
evaluator p is computed as 1+A_ij^2, and z receives the requested rational
specialization. Its literal audit checks that the only fixed rational
leaf is 1. Prescribed p bit lengths are recorded separately from fixed
literal bits. For an A input with bit length L, the displayed p operation
has O(L) bit length; it does not hide the output as a long literal.

The uniform Python construction is explicit, but its work and output
size are exponential because it emits the above states and gates. The
small z=-1,0,1 development interpretations do not establish a uniform
polynomial bit-time bound for arbitrary numerical evaluations.

## Frozen local development boundary

Before any numerical interpretation, candidate/evaluator/boundary/protocol
and this blueprint are hashed in n77-source-freeze.json. The evaluator
checks these hashes before constructing or interpreting a circuit.
It serializes n=1,2,3,4,5. It inspects node topology, every literal and
input, the actual shared square chain, every state transition, liveness,
and the counts of each scalar stage.

For n=2,3,4,5 it evaluates 36 exact Fraction cases: identity, Vandermonde
A_ij=(i+1)^j and cyclic permutation A, each at z=-1,0,1. Its independent
oracle explicitly sums permutations, multiplies prescribed p values and
uses the sum of original edge labels. It never calls the subset recurrence
or fills a circuit leaf with the oracle answer. Every emitted scalar gate
is interpreted in each development case.

Four local obligations are scored separately: scalar topology/init;
all-stage budgets; marked input/literal provenance; full terminal equality.
A 4/4 result only verifies this complete local raccord. Root score is
zero regardless of that result because no polynomial compression exists
in this artifact. No held-out data or shared Arbor state are accessed.

## Exact next constructive obligation

Construct an explicitly initialized polynomial-dimensional state and
charged scalar transitions/output that replace this subset representation
while preserving the COMPLETE PA(z)=Cn DA(z) for every n and rational A,
including all prescribed z markings. Bound the complete gates, allowed
literal bits and uniform constructor time. Provide the corresponding
formal connection to the existing target theorem. No initial or terminal
coefficient may be supplied as an unknown leaf. This is the missing
compression in the harness; no counterexample or lower-bound campaign
is inferred from the size of the current reference.

The theorem-to-Python schedule mapping is the cardinality slice
F(U)=state(B,card(U),U). Its recurrence matches n73's explicit state
equations and its full output matches marked_target. The existing Lean
semantics do not automatically certify this serialized Python DAG;
the present artifact documents that limitation and supplies reproducible
code checks rather than claiming a new kernel theorem.
