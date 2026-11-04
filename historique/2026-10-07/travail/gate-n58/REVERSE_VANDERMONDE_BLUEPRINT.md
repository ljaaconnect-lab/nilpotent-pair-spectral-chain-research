# n58 exact reverse Vandermonde

The six obligations in `reverse-obligations.json` were frozen before candidate
proof attempts. All statements quantify over arbitrary n and `CommRing R`,
with no domain, field, characteristic, injectivity, or positivity hypothesis.
They include n=0 and n=1 without separate restrictions.

## Accepted identity and proof route

For every v:Fin n→R, the complete Lean source verifies

    det(fun i j => v_i^(n-1-j)) = product_{i<l}(v_i-v_l).

The pinned Mathlib source defines `projVandermonde a b` with entries
`a_i^j * b_i^(Fin.rev j).val`, and proves its determinant is
`product_{i<l}(a_l*b_i-a_i*b_l)`. Specializing `a_i=1`, `b_i=v_i`
gives exactly the desired orientation and descending exponents. Natural
subtraction normalization verifies `(Fin.rev j).val = n-1-j.val`.
The proof keeps the difference order v_i-v_l directly through this projective
specialization. It introduces no unproved permutation-sign lemma and invokes
no column-reversal sign approximation.

The following frozen identities are all accepted:

- Exact descending matrix = `projVandermonde (const1) v`.
- Generic reverse Vandermonde determinant.
- `(t^(n^i))^(n-1-j) = t^(n^i*(n-1-j))`.
- Polynomial specialization at `v_i=t^(n^i)` for arbitrary t:Polynomial R.
- Exact subtraction `(n-1)*n^i-j*n^i = n^i*(n-1-j)` for all natural n,i,j.
- Determinant identity with these complementary subtraction exponents.

## Actual paper-entry interface

Three requested bridge statements are verified outside the frozen denominator:
`unit_monomial_pow`, `paper_monomial_matrix_eq`, and `paper_monomial_det`.
They certify coefficient-one monomials as powers of Polynomial.X, the entire
raw monomial matrix as the typed complementary power matrix, and its exact
determinant product.

The inspected accepted n55 definitions are

    baseLabels n i j = j.val * n^i.val
    baseCaps n i = (n-1) * n^i.val
    reverseMatrix r c i j = Polynomial.monomial (c i-r i j) 1.

Their composition unfolds to the literal left matrix of
`paper_monomial_matrix_eq` and `paper_monomial_det`. This artifact proves that
raw matrix and determinant formula. It does not import the named n55 module;
the coordinator can combine the modules by unfolding these definitions.

## Actual compiler evidence

Round 12 compiled the final file with Lean 4.34.1 and exit code 0. All six
frozen obligations and all three additional bridge declarations were accepted
together. Every axiom audit is a subset of the agreed standard trust base
`propext`, `Classical.choice`, and `Quot.sound`; the subtraction theorem uses
only `propext`. No declaration contains an unfinished goal, placeholder, or new
axiom. The fixed development score is 6/6=1.0, an exact obligation pass fraction.

Twelve complete candidate compiles were used from the twenty-round budget,
with one import/name probe separately. Rounds 8–10 isolated Matrix.of/Equiv.refl
wrapper reduction in the extra interface theorem. Explicit `rfl` after the
already verified algebraic simplifications closed that definitional goal.
The full actual diagnostics, hashes, and audits are in `reverse-progress.json`.
`reverse-report.json` checks final source and frozen protocol hashes before
distilling acceptance. File attributes preserve the frozen byte hashes across
Windows checkouts. No cache dependency was downloaded or built. No held-out
data were accessed, and no shared cache or Arbor state was modified.

The resulting determinant formula is an exact algebraic interface to the
paper polynomial. Polynomial-size scalar central-coefficient extraction remains
a separate constructive theorem; no coefficient, residue, or projection is
introduced as a free circuit gate.
