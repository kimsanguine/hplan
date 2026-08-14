# Pinned hplan-core renderer fixture

This directory is an immutable, minimal vendor snapshot of `hplan-core` commit
`3055f65e52991e226cc1aabd6fa0f31071aa99d7` (2026-08-14). It contains only the
three neutral contracts and the renderer/validator required for deterministic
adapter parity in this repository's CI.

`hplan-core` remains private and local. CI must not invent a clone URL or
silently skip the renderer check. The validation workflow sets
`HPLAN_CORE_ROOT` to this fixture and runs the real pinned renderer against all
four adapter artifacts. A local release check can instead set `HPLAN_CORE_ROOT`
to a live hplan-core checkout; that comparison detects fixture or adapter drift.

Do not hand-edit individual fixture files. Refresh all five files and
`PROVENANCE.json` together from one approved local hplan-core commit, then run
the byte-parity test. There is no hplan-core clone URL for this repository.
