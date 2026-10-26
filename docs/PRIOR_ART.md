# Sources, licenses and permissions

| Source | Version / reference | Use and license/permission status |
|---|---|---|
| User's WITNESS project document | 19 October 2026; held privately by the operator | Historical design source, preserved unchanged; no public redistribution performed |
| User's context-kit ZIP | Hash and file inventory in docs/TOOLING.md | Workspace convention reference; scripts/settings/templates not installed; original ZIP preserved |
| Prior scaffold references to BASLA/competition guide | Not present in this workspace | Not inspected; no current competition/eligibility verification claimed |
| NumPy | Locked 2.5.4 on this runtime | Installed numerical dependency; BSD-3-Clause project license, bundled component notices remain in distribution |
| pytest | Locked 9.1.1 | Test dependency, MIT |
| Ruff | Locked 0.17.2 | Lint/format dependency, MIT |
| setuptools | Locked 84.2.1 | Build/development dependency, MIT |
| meta-sam-parser | Pinned runtime 0.1.0; official repository linked in API_VERIFICATION | Public mask codec and diagnostic; SAM License, not assumed to be MIT/Apache. Package notices remain in .venv |
| FFmpeg | Installed 8.0.1 essentials Gyan build | External executables, not redistributed; build license depends on compile options |
| SYNTHETIC probe/mask/test-pattern fixtures | This task | Authored/generated locally; no captured private media. Codec vector is quoted from official Python README and attributed in the diagnostic |

All transitive versions and artifact hashes are in uv.lock; installed distributions
retain their own notices. [Official SAM library repository](https://github.com/meta-models/meta-sam)
and [its license](https://github.com/meta-models/meta-sam/blob/main/LICENSE) are the
sources for that runtime package. No third-party implementation source was vendored
or patched. Dependency license labels are attribution, not a legal compatibility
opinion. The user has not selected a license for WITNESS itself. Future real media
requires permission for the hardware and people shown. Historical costs, user/market
claims and API snippets were not imported as established facts.

Round 2's test-only encoder calls the pinned package's private reference encoder;
production imports only public APIs. The small attributed lossless conformance
vector comes from the official library's compact conformance example, not a WITNESS
live response. No third-party implementation source was copied or patched. All new
mask/track fixtures are labeled SYNTHETIC. No public release was performed.
