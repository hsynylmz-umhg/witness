# Decisions

D001–D007 were retained and translated from the supplied scaffold. New decisions
record material scope/behavior choices made for the M0/first-M1 delivery.

| ID | Decision | Reason | Revisit condition |
|---|---|---|---|
| D001 | CLI first, small web UI later | Test the critical perception uncertainty first | After M4 |
| D002 | Match procedure step instances, not just part IDs | A part can appear in multiple operations | When implementing matching |
| D003 | Separate observed, missing_evidence and uncertain | Absence does not prove omission | Ground-truth calibration |
| D004 | 5 fps is only an experimental candidate | 1 fps can miss short movements; interpolation cannot recover them | Real 1/5/10 fps comparison |
| D005 | Historical API examples are not executable contracts | Endpoint, schema and parser assumptions can be wrong | Official contract plus appropriately authorized live checks |
| D006 | Defer coverage planner | Avoid expanding scope before core evidence works | M4 and time buffer |
| D007 | Later clips are separate sessions | They cannot prove historical occurrence/order | Permanent invariant |
| D008 | English for all project-authored material; preserve source originals | User language policy | Explicit user change |
| D009 | docs/RULES.md is authoritative; three thin tool entry points | Avoid conflicting instruction copies | Tool convention change |
| D010 | Preserve source media; no automatic deletion | Explicit retention choice and current rules supersede the historical deletion policy | User retention instruction |
| D011 | Archive superseded initial prompt/validator as inactive .txt references | Initial task is implemented; old validator wrongly forbids local .env and scans environments | No planned restoration |
| D012 | Do not integrate a provider parser while the documented Python vector fails | meta-sam-parser 0.1.0 decoder succeeds but its video line parser rejects the same documented payload | A compatible official version or independently verified corrected contract |
| D013 | Bound this offline slice to short local clips | Limit accidental resource use during the perception spike | Measured need to process longer videos |
| D014 | Sampling output is a reference plan only | Preserve original frame/PTS identity; avoid claiming provider sampling control | Implement verified extraction/upload mapping |
| D015 | Retain wider product vision without building optional channels now | Voice/cards/alternative providers/UI are later features, not prerequisites for an honest first slice | Future user-approved milestone |

Historical overclaims are corrected operationally: model masks are estimates,
image-plane axes are not exact physical rotation, missing evidence is not skipped,
and local hashes do not guarantee immutability. The original source stays unchanged.
Organizer deadlines/criteria and user/customer assertions remain unverified rather
than being copied into current facts. No product core was silently removed.

## Round 2 — appended decisions

| ID | Decision | Rationale and actual evidence | Revisit condition |
|---|---|---|---|
| D016 | Sampling FPS remains an experimental candidate; preserve legacy sample output and add sampling.json | With unchanged thresholds, 1/5/10 fps produced TP/FP/FN of 0/0/13, 10/1/3, 8/1/5. This is a coupled synthetic estimator experiment, not proof of a preferred real-media rate. Unknown source times remain null. | Held-out real-media event-recall comparison with calibrated time/rate thresholds |
| D017 | Correct the duplicated-marker diagnostic; use the pinned public codec and a strict documented line subset | The old diagnostic added an extra !. The unchanged official vector parses correctly in 0.1.0. SAM uses arithmetic-coded Base85, so fixed bits-per-symbol equality is inapplicable. Validate the actual packed envelope before raster allocation and decoded H*W length afterward; enforce a local pixel cap. The unsupported literal-length formula is an explicit scope correction, not an invented encoding. Only test helpers use the pinned internal reference encoder. | A verified provider/codec contract or supported public encoder changes |
| D018 | Implement a pure rotation/stop candidate state machine with all experiment thresholds in configuration | Use an inclusive 45-degree boundary, configured stationary tail, visibility/camera/identity/time gates, and witnessed/inferred/unwitnessed-tail outcomes. These describe visual candidates, not physical tightening. Current synthetic full-set precision 10/11, recall 10/13; clean 10/10. One wrong camera gate causes a false positive. This extends the offline risk spike without starting procedure/audit/UI scope. | Held-out real masks, IDs, camera and source-time measurements |
| D019 | Default-deny paid probing and reserve costs across sessions | Require a positive operator environment budget, --allow-paid, a positive configured cap, confirmed credits, local key and estimate strictly below remaining funds. One image request, zero retries, bounded timeout, shared locked ledger and session spend sidecar; unknown outcomes retain reserves. Costs after completion use published unit rates and are not account invoices. No paid request ran this round. | Explicit operator authorization and an actual bounded smoke test |
| D020 | Private operator materials are ignored and never linked by published paths | Original references and archived scaffold remain private and unchanged. The provenance baseline is immutable. Validate available private hashes; absent material in a fresh checkout emits one informational skip line. The archived scaffold is documented but not published. | Explicit operator policy change |

D017 supersedes D012's blocker inference; the historical failed diagnostic remains
recorded as a corrected error. Source-video-to-provider timing and real perception
quality remain unverified. D019's credit confirmation/config cap additionally retain
the pre-existing spending rules; environment and command flags alone do not bypass them.

## Round 3 — repair and offline audit decisions

| ID | Decision | Rationale and actual evidence | Revisit condition |
|---|---|---|---|
| D021 | Remove the risk-gate script's dependency on the test package and guard importability | D-001 did not reproduce in this checkout: `no exception; pytest tests/unit/test_workspace.py -q -x: 2 passed, 0 errors, 0 failed`. Pytest now makes the project root importable and a guard imports every package module and script. D-002 reproduced as `ModuleNotFoundError: No module named 'tests'`; the synthetic generator moved to `witness.synthetic`, which both tests and the standalone script import. | If a clean-checkout run produces a new import traceback, record its exact environment and stderr. |
| D022 | Reject 1 fps as this estimator's sampling candidate | Unchanged thresholds measured recall 0.000 at 1 fps and 0.769231 at 5 fps, with the same three abstentions at 5 fps. `candidate_sample_fps` is now 5.0; this remains a synthetic measurement, not a real-media optimum. | Measure labeled real-media recall at 5 fps, then 10 fps before threshold tuning if the 0.85 target is missed. |
| D023 | Fix an operator-authored procedure contract before any model call | The ten-part mock-panel procedure lets deterministic coverage/order/undocumented review run without inventing procedure output. The fixture is explicitly not model output. Its narrowly named `skipped` finding is a high-severity human-review coverage gap, not proof of physical omission or assembly correctness. | Verified procedure provider contract and instance-aware matching for repeated parts. |
| D024 | Keep PDF rendering optional and record an HTML fallback | The report uses optional local WeasyPrint only if available; absent or failed native rendering writes a named blocker and leaves self-contained HTML plus the hash chain. No PDF module is imported at startup and no unverified dependency was added. | A project-locked, reproducible offline PDF renderer is available and passes report rendering tests. |
