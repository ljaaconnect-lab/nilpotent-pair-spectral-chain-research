# Reproduce the accepted n75 leaf

Use a fresh checkout of the recorded `arbor/n75` commit. The accepted source is
`AtomicFirstPrefix.lean`, SHA256
`2e4ce93c35638d5ec2f6e784dc511874352d4a753a5691d71448972e66c96cdf`.
The file is UTF-8 with LF newlines, protected by `.gitattributes -text`.

Use the absolute Lean 4.34.1 compiler specified in `compile_n75.py`. Apply all
three environment entries from `work/mathlib-environment.json`; prepend the
fresh checkout to LEAN_PATH using `os.pathsep`. Compile the source once with
`lean.exe -o AtomicFirstPrefix.olean AtomicFirstPrefix.lean`. Wait for the final
process exit. Expected exit is zero, with precisely six standard axiom audits
and no warnings. This new replay is a coordinator invocation, counted separately
from the seven n75 development invocations.

All three direct Mathlib imports and their source/compiled hashes are frozen in
`n75-dependency-provenance.json`. The only added dependency build is documented
in `n75-dependency-build.json`; no other proof cache or delivered source is needed.
The compiler needs the prepared Mathlib cache but must not mutate it.

`python verify_n75.py` is a static provenance audit, not a Lean invocation. It
rejects nonzero compilation, source/snapshot hash mismatches, absent audits,
unexpected axioms, forbidden proof placeholders, or non-LF accepted source.
The old failed snapshots are retained only as rejected compiler history.
