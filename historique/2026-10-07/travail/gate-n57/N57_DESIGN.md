# Frozen n57 design

The four obligations and the positive finite evaluator are fixed in
`n57-protocol.json` before the first evaluator or Lean probe. The compiler takes
every M,u,v entry as an explicit input leaf. Their construction cost S remains
an independent hypothesis.

The formal scalar DAG representation has elementary add/mul gates, free wiring
and zero/one leaves, parallel finite gate families, and sequential composition.
Composition connects existing output wires to later inputs and evaluates the
earlier graph once; wire fan-out duplicates references rather than computations.
A concrete scalar SSA exporter implements the same schedule.

The dense product emits r products per output cell and sums them with r-1
additions. A state interface keeps the original matrix and current matrix as
shared wires; each binary instruction emits one dense product, preserving the
original matrix without recomputation. The last contraction first computes Mv,
then the dot product with u, charging every scalar gate.

The Matrix adapter proves the monoid operation really is Mathlib matrix
multiplication. Scalar circuit semantics will be proved through dense dot
products, matrix products, instruction sequences, matrix powers, and the final
contraction. Counting wiring/composition as zero does not grant a free matrix or
tensor operation: every dense product is expanded to scalar gates before its
count is derived.

For J binary instructions and r>=1, the exact intended count is

    J*(2*r^3-r^2) + 2*r^2+r-1.

The n40 accepted theorem gives J<=2*n^2 for K=n^n-1,n>=2. This leads to the
conditional bound S+4*r^3*n^2+3*r^2. Establishing a target representation with
polynomial r and polynomial S is a separate unresolved mathematical task.

The finite evaluator uses exact input matrices on its fixed dimensions, with an
independent repeated matrix-vector oracle. Its measured evidence and the
universal kernel-verified statements are scored and reported separately.
