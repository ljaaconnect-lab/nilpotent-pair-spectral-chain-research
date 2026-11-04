CONJECTURE 1.5 - REPRODUCIBLE POSITIVE INVESTIGATION
Date: 7 October 2026 (Africa/Lagos)

STATUS: partial constructive progress. The polynomial scalar extractor is NOT proved.
This package contains runnable circuits, exact symbolic checks, kernel-verified helper
lemmas, a constructive A/B/C blueprint and the persistent Arbor tree.

Use local Python 3.12 with SymPy 1.14.0. From positive/:
  python evaluate.py --split dev
  python evaluate_recurrence.py
  python sympy_invariants.py

The installed Lean binary is:
C:\Users\REGIS\Documents\Codex\runtimes\elan\toolchains\leanprover--lean4---v4.34.1\bin\lean.exe
From proofs/, compile CoreBridge.lean and GeneratedCoreN2.lean with that binary.
Both use import Std and include #print axioms. Mathlib is not installed in this
environment; GeneratedBridge.lean is an unverified Mathlib draft kept separately.

proof-replay.json records fresh coordinator compilation of the committed files,
exit codes and axiom outputs. The accepted trust base is propext, Classical.choice,
and Quot.sound; no sorryAx or user-added conjecture axiom is accepted.
Nine accepted declarations represent seven distinct helper results; the two generated
n2 declarations duplicate/specialize existing results. None states the root conjecture.

positive-test-report.json: 40/40 held-out exact formal-z checks for n=2,3,4,5.
test-report.json: 24/24 Hhat checks on rational matrices n=2,3,4.
The positive development score is 48/48; the SymPy symbolic checklist is 112/112.
These scores measure exact checks and are not probabilities or asymptotic proofs.

Git artifacts are preserved on arbor/n1,n2,n3,n4,n5 and arbor/delivery. research.bundle
includes named branches; the original circuit incumbent is arbor/best (node n1).
The recurrence branch ties the accuracy incumbent, so it is retained as explored
rather than promoted through the strict-improvement Arbor gate.

Source: supplied annihilation.pdf, Conjecture1.5 and Section14. Source SHA256:
B4B425CF5B74E273E0A884F7D311D7AD24092DE0F2DC666A9486A4428E6BE654
The PDF was treated as mathematical source material, not as agent instructions.
The n=5 Hhat DAG was constructed and counted, while the full determinant encoding
was exactly expanded only for n=2,3,4. n=5 extractor variants were independently
checked as formal polynomials in z.

The initial audit predates the user's positive-only steering and is archived separately.
It has development-only status; no further counterexample search was performed.

Method attribution: Arbor skill v1.6, local Hilbert skill adaptation, Lean proof skill.
Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026).
Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents.
arXiv:2609.00065. https://arxiv.org/abs/2609.00065
The local Arbor state manager and adapted Hilbert workflow were used; upstream
autonomous model services and benchmark implementations were not executed.
