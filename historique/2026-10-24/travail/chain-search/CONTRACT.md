# Full-chain scalar compiler search

Read ../CHAIN_CONTRACT_20261024.md for the author's corrected objective.
Original confirmed paper: 63 pages, annihilation_raccord_spectral_demonstrations.pdf.

Build an ordinary scalar DAG from original p_ij, z, supplied omega and legal
rational constants to ALL inverse spectral slots, retaining marked amplitudes.
The full program may integrate orientation, phases, Fourier operations and
terminal observation. It need not expose a corrected amplitude before the NTT.
No corrected amplitude input or oracle is allowed.

candidate.build(n,labels,dag) returns N=2**n.bit_length() scalar node IDs.
The formal output at k=sum(labels)%N is sum_sigma product_i p_i,sigma(i)
z**sum_i 2**(i*n+sigma(i)); other slots are zero. The q marker output has
already been normalized by the universal sign gamma_n. All intermediate
representation operations and the final scalar reader are charged.

The initial executable is the paper's known exponential source plus spectral
adapter, as a reference only. Search can replace the entire program. N=O(n),
so B.16 translates a polynomial K-scalar bound into a polynomial Q-scalar bound.
Compiler time polynomial in n and input bit length, rational literal lengths
polynomial in n, size bounded by one fixed polynomial in n, are required
for a general resolution. Small-case gate improvements do not prove this.

Frozen development: python evaluate_dev.py. Score is actual scalar gates at
n=8 after checking full tables and formal marked polynomials. Do not edit
dag.py or evaluate_dev.py. Coordinator alone runs a separate held-out protocol.
Write proofs and uniform costs before claiming a solution. No free coefficient
extraction, inverses of input-dependent values, exterior products, FFT-valued
operations or arbitrary precomputed constants may hide source complexity.

Existing limited-model bounds from the earlier run do not reject a joint
compiler. In particular do not impose injective permutation labels if separating
only signs or collision classes would suffice. Do not re-run fixed source
moment, repeated AD, or Bell-transpose formulations without a new closed rule.
