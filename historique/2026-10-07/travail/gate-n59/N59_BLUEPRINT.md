# Frozen n59 conditional criterion

`n59-protocol.json` fixes two principal obligations before proof attempts,
with 12 complete candidate compiles and separately counted probes/dependencies.
No new numerical experiment is planned. Accepted n40/n57 modules remain exact
dependencies and are compiled only into this worktree's local `proof-build/`.

1. Compose the actual supplied input circuit C with the accepted scalar circuit.
   Under the explicit equality C.eval(inputs)=inputData(M,u,v), prove the
   composed output is the matrix-power contraction and its gate count is
   C.gates+scalarCircuit.gates. This charges the actual initialization graph.
2. Define Pi(c,d) as X^c+4*X^(3*d+2)+3*X^(2*d) in Polynomial Nat, prove its
   evaluation formula, and use the accepted conditional dense compiler budget
   with explicit r>=1,n>=2,r<=n^d,C.gates<=S<=n^c.

An optional coefficient theorem may compose these results with an explicit
representation hypothesis H.coeff(n^n-1)=u^T M^(n^n-1) v. It must not introduce
that representation as an axiom or claim to construct it.

The remaining target obligations are separate: a source-model-admissible
constructor for M,u,v; its polynomial uniform running time; the provenance and
bounded bit lengths of rational constants and allowed parameter/input leaves;
and the exact representation equality preserving all formal z markers.
Boolean zero/one Circuit constants are cheap, but arbitrary rational/parameter
environment leaves require the original source model's admissibility proof.
The criterion here is a conditional scalar gate bound, not the original
Conjecture 1.5 without those construction and representation restrictions.
