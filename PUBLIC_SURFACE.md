# Public Surface Policy

This repository publishes only the hplan runtime, skills, installer assets, and the verification material needed to operate them.

- Any `docs` or `.archive` directory at any depth is local/private only. It must not be added to Git or installer packages.
- The four public core-contract artifacts live only in `runtime/hplan-core/`.
- Product planning, internal design, progress notes, and archived material stay outside this public repository.
- If a new runtime dependency is needed, add the minimum executable or machine-readable artifact under an existing public runtime path; do not create a replacement public document folder.

`hplan-core` remains a separate local/private source. The vendored fixture and runtime snapshot here are immutable verification inputs, not a public `hplan-core` repository.
