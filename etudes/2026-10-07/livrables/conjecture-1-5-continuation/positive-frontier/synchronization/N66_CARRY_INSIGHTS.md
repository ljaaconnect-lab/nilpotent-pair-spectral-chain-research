# n66 carry supplement v1 distilled insights

- One explicit skew matrix of order 2N+1 represents the complete native
  carry Gaussian family. No output-specific matrix is chosen.
- The actual native-to-grouped shuffle is sum_(i<j)y_i x_j. It changes
  the native Walsh-looking phase to |x||y|+binom(|y|,2). Consequently
  this coherent graded family has not produced ordinary Hadamard F',G'.
- Abstractly, C C^T=2^N I, and C applied twice to synchronized input
  ports changes their copy constraint to 2^m delta_(bF=bG). Both formulas
  include their required scales and final parity carry.
- The transformed abstract cap has four Gaussian component factors in
  a specified factor order. Its permutation to the F/G boundary order
  has the explicit remaining sign chi=sum_e s_e prefix_(aF+aG)_e+
  binom(|s|+1,2). A correct global routing must handle this sign together
  with the input shuffles, rather than dropping either.
- Actual one-component scalar DAGs have 18N+7 binary gates and only
  constant-length rational literals. Counts for N=2n², n2..5, are
  151,331,583,907. These are tensor-label evaluations, not B extraction.
- Supporting finite identities: 40/40. Original root obligations: 0/3.
  Supplement Lean compiles: 0. Universal reasoning remains unverified
  within this supplement; independent n67 local proofs are not claimed
  as new proofs here. Base n66 frozen files remain unchanged.
- Next constructive obligation: a single explicitly ordered contraction
  of the coherent carry families, the full F/G families, and the cap
  factors that yields the ordinary synchronized contraction with a
  polynomial scalar gate certificate. This interface is open.
