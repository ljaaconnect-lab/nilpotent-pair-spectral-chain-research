# n72 — finite positive pole-functional synthesis

The three frozen root grids have distinct rational poles and denominator degree n².
For every permutation σ, qσ is the polynomial whose factors are all unselected
edge poles; its degree is n²−n. A linear functional ℓ satisfying ℓ(qσ)=sgn(σ)
would give ℓ(D det(Bij/(t−θij)))=per(B), by determinant expansion.

Positive exact SymPy synthesis evaluated every permutation for n=2,3,4,5.
The functional exists on each n=2,3 development grid (six fits in total).
None of the three frozen grids produced a functional at n=4 or n=5.
These are constraints on the chosen grids only, not a disproof or a lower bound
for the conjecture. No numerical matrix counterexamples were generated.

Even a development fit needs an all-n analytic construction with polynomial
preprocessing; factorial enumeration and rational row reduction are not that
constructor. The determinant rational expression also needs a division-free
scalar compilation. Coefficient-array gates and literal bits must be charged.
No full root circuit was isolated, no held-out boundary was opened, and no Lean
compiler was invoked in this node. Root score is 0/4 obligations closed.
