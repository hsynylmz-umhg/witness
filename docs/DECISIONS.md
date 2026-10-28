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

## Round 4 — amendments and decisions

**D021 amendment (round 4).** The original row stays as written. Its evidence line held only in
the agent's environment. On the operator machine the same `tests/unit/test_workspace.py` run
gave **1 passed, 2 errors**, with this traceback:
`_pytest/pathlib.py:175: in find_prefixed / for x in os.scandir(root) / PermissionError:
[WinError 5] Erişim engellendi: '<home>\AppData\Local\Temp\pytest-of--HSYN-'`.
The cause was pytest's temp root and cache directory, not imports. D021's import guard and the
D-002 fix remain valid. Its claim that D-001 did not reproduce is superseded by D025.

| ID | Decision | Rationale and actual evidence | Revisit condition |
|---|---|---|---|
| D025 | Keep pytest's temp and cache roots inside the project | `addopts` gains `--basetemp=.tmp/pytest` and `cache_dir = ".tmp/.pytest_cache"`; `.tmp/` is ignored. `tests/conftest.py` creates the parent of `--basetemp`, because pytest does not, and a fresh checkout otherwise failed with `FileNotFoundError`. Config was chosen over setting `PYTEST_DEBUG_TEMPROOT` from Python because the temp factory can exist before conftest import. Evidence: the WinError 5 traceback above; after the fix, the round-4 full run had 0 errors. A guard test asserts that the base temp lies inside the repository root. `--basetemp` resolves against the working directory, so pytest must run from the repo root. Running it elsewhere fails the guard instead of passing silently. | Pytest changes `--basetemp` semantics, or the suite has to run from another directory |
| D026 | Keep both 94-degree `GT=0` camera cases and their labels | Audit in `docs/RISK_GATE.md`. `camera_jitter_94_stop` contains no genuine rotation (12-degree sinusoid, unstable-camera flag on every sample, recorded rotation 0), so it is a correct negative outside the recall denominator. `unflagged_camera_rotation_94_stop` produces a sampled track identical to `clean_94_stop` and differs only by label: a deliberate adversarial gate-trust case whose FP is unavoidable for any estimator using these inputs. No numbers changed and no re-run used new labels. | Later round: rename the jitter case so it drops `94_stop`, and add a positive case with real rotation under flagged jitter |
| D027 | Paid probing stays refused while credits are absent | With `WITNESS_MAX_SPEND_USD` unset, `.venv/Scripts/witness.exe sam probe --image artifacts/smoke/nonexistent.png --allow-paid` printed `PENDING: WITNESS_MAX_SPEND_USD is not set; no API request sent.` and exited **2**. No `spend.json` exists in the workspace. Spend USD 0.00. | Credits confirmed and the operator sets an explicit budget |

## Round 5 — first real footage

| ID | Decision | Rationale and actual evidence | Revisit condition |
|---|---|---|---|
| D028 | First real footage: what it measured and what it did not prove | The operator's key in `docs/REAL_MEDIA.md` was committed before measurement and was not edited. ffprobe 8.0.1 measured both clips: h264/yuv420p 1920x1080, nominal 30/1 but **VFR** (frame intervals 30.0 to 153.8 ms), **no rotation metadata**, PTS origin 0, 7227 and 4310 decoded frames, 240.9 s and 143.7 s. The existing `witness ingest` refused both with `Video exceeds the configured short-clip duration or frame limit.` (exit 2, limit `max_duration_seconds = 120.0`), so no session, build or finding exists for either clip. No threshold, limit, label or decoder changed. Measured: the files' timing properties, and the fact that the ingest guard holds on real files. Not proved: anything about detection, coverage or ordering on real footage. Even with a passing build, two clips of one scene, filmed by one operator under one camera and one light, could not show that the method generalises. Offline the pipeline also has no step that turns frames into events, so a build could only list all ten slots as unobserved. | An operator decision on the proposals below |

Proposed, not adopted (round 5 records them and implements neither):

- **P-028a — real clips versus the 120 s ingest limit.** The limit has no documented rationale. Options: an
  operator-approved `--config` override per real session, recorded in its manifest, or a
  segmenting ingest that keeps original PTS. Trimming or re-encoding the source files stays excluded.
- **P-028b — no offline observation step.** `build` reads `events.json`, which only a model
  path would write, and that path is NOT_RUN. A real clip can therefore never reach the
  audit offline. The next real-media round needs either an authorised model run within the
  D019 budget or a hand-labelled `events.json`, clearly marked as human annotation.
- **P-028c — procedure mismatch.** `mock_panel_v1.json` describes hex-driver rotation on M4
  fasteners. The footage shows pencil marks in printed boxes, and that needs its own
  operator-authored procedure.

## Round 6 — round-5 proposals resolved, deterministic box extractor

Written before either real clip was run through the extractor; results follow in the D029
measurement line below and in `docs/REAL_MEDIA.md`.

- **P-028a resolved: `max_duration_seconds` 120 -> 300** (`config/defaults.toml` and the
  `IngestConfig` default). The real clips are genuinely 240.9 s and 143.7 s long, so the 120 s
  limit was doing its job on files that really are long. It had been calibrated against
  synthetic clips and never exercised on real footage. Raising it alone changes nothing:
  without an event source (P-028b), an ingested real clip still builds to ten `skipped`
  findings. The frame limit (20000) is unchanged. The configuration hash in
  `docs/RISK_GATE.md` changes because the file changed; the gate numbers do not.
- **P-028b resolved: adopt the deterministic box extractor (D029).** No hand-written
  `events.json`, no model call; the model path stays `NOT_RUN`.
- **P-028c resolved: new procedure `data/procedures/panel_boxes_v1.json`**, left beside
  `mock_panel_v1.json`, which is unchanged because the synthetic corpus and the risk gate rest
  on it. The new file uses the existing step schema (action `mark_box`, tool `pencil`) and adds
  a top-level `sheet` layout. Numbering was read off the first frame: box 1 is the near-left
  box and numbers run up each column (1/2, 3/4, up to 9/10). That differs from the round-6
  prompt's "left-to-right from the bottom row".

| ID | Decision | Rationale and actual evidence | Revisit condition |
|---|---|---|---|
| D029 | Deterministic pencil-mark extractor for the ten-box panel | `src/witness/perception/boxes.py`, run by `witness boxes --session --video --procedure`. It verifies the video's SHA-256 against the session, decodes planned samples once with ffmpeg as 960x540 gray, finds the sheet (Otsu threshold, largest 4-connected bright component, at least 5% of the frame, else it raises) and the ten printed box interiors as enclosed bright components (else it raises), and measures each box's mean luminance relative to that frame's paper white (90th percentile of sheet pixels). Rule: down when the 1 s trailing median falls 8% below the first-second baseline; marked when the final down run reaches the end of the clip and lasts at least 3 s; onset is the first sample of that run. The 8% margin comes from paper and pencil (graphite at most ~60% of paper reflectance, smallest visible mark taken as a quarter of the interior, so a 10% drop, less 20% slack), not from these clips. Events reuse the only existing evidence-id contract, session-local `event-N` / `evidence-N` with a still at `evidence/evidence-N.png`, and every event carries both. Per-box frame indices and ratios go to `box_marks.json`, because the `events.json` schema does not admit extra keys. No homography: boxes are located as pixel regions, and the residual perspective error is measured per session. A deterministic extractor run on two clips of one scene demonstrates the loop end to end. It does not show the extractor generalises to other sheets, lighting, cameras or operators. Three SYNTHETIC tests pin it, including a hand that crosses a box and leaves without producing an event. | A second scene, or any change to the margin or persistence, which needs a new decision |

**D029 measurement (round 6, after the rule above was fixed).** Clean clip: ingest exit 0,
1205 samples, perspective residual 0.1017 uv, 3 events (BOX_01, BOX_07, BOX_10), build with 7
`skipped` findings and 0 order findings; the hash chain recomputes. Expected was 10 marks and
no findings. Skipped clip: ingest exit 0, then `witness boxes` exit 2 with `Expected 10
printed boxes inside the sheet, found 11.` (an edge sliver of paper). No events and no build;
the key expected 9 marks plus the 3/4 order discrepancy. Per-box final/baseline ratios on the
clean clip are 0.907-0.957, so light whole-box hatching dims a box less than the 8% margin
assumed, and onsets near the margin are not mark times. Nothing was tuned. Details are in
`docs/REAL_MEDIA.md`.

Proposed, not adopted (round 6 records them and implements neither; each needs footage that
is not the answer key, because tuning on these two clips would make the key a training set):

- **P-029a — reject components that touch the frame border** as box candidates. This is
  geometric and outcome-independent, but it was found by looking at a failure, so it is a new
  rule version, not a correction.
- **P-029b — the mark margin's physical premise failed.** Measured drops of 4-9% from light
  hatching sit at or under the 8% margin. Either the operator's mark becomes a defined dense
  fill, which is a protocol change for new footage, or the margin is re-derived from a
  calibration sheet shot separately. Lowering it on these clips is excluded.
- **P-029c — product claim if neither converges.** If a re-derived rule still cannot separate
  marks on held-out footage, narrow the claim to verifying a supplied event log rather than
  perceiving marks from pixels. This is an operator decision.

## Round 7 — the last perception round

Written before either real clip was run through rule v2. The measurement follows in D030.

**D029 amendment (round 7): measure texture, not brightness.** Rule v1 measured mean luminance,
which cannot separate a pencil from a hand: both make a box darker. Pencil hatching adds
high-frequency structure (dark strokes, light gaps), and a hand adds a flat, smooth darkening.
The round-6 margin was not set too high; it measured the wrong property. Rule v2
(`panel_boxes_rule_v2`, docstring of `src/witness/perception/boxes.py`) replaces the luminance
test with a texture ratio: mean absolute first difference in the eroded box window, divided by
the same quantity on the eroded paper margin in the same frame (cancelling exposure drift),
normalised by the box's own first-second baseline (cancelling the printed digit). A box is
marked when its 1 s trailing median ends at or above **RISE = 2.0** and the final run at or
above **RELEASE = 1.5** lasts at least 3 s. Onset is the first sample of that run, which fixes
the round-6 bug where onset was the last sample to cross the line. RISE comes from the
contrast of graphite strokes against paper noise; "at least double" is a stated judgement
call. Windows exclude 4 px of outline and sheet edge. With rule v2 the SYNTHETIC hand test (a
flat darkening resting on box 3 to the end, plus light 4% hatching on box 1) yields only BOX_01.
The same three tests fail when run against the saved v1 brightness extractor. No other
constant changed, and none will change after the measurement.

- **P-029a resolved: adopted.** Candidates whose bounding box comes within 2 px of a frame edge
  are not boxes: the sheet sits inside the frame, so an edge-touching region is a cut-off
  sliver. This is a correctness fix against the defect round 6 recorded, not a tuning knob.
- **P-029b resolved: calibration footage is ruled out for time.** No calibration sheet and no
  further clip will be shot. If the texture measure fails on these two clips, the limitation is
  the corpus (two clips, one scene, one operator) and it is recorded as such.

| ID | Decision | Rationale and actual evidence | Revisit condition |
|---|---|---|---|
| D030 | Close the perception line: **the claim narrows to verifying an event log, and the perception gap is stated in the submission** | Rule v2 was run once on each clip, unchanged. Clean: 9 of 10 marks, onsets in step order, 1 `skipped` finding (BOX_09 at 1.91x, under RISE 2.0); the key expects 10 and none. Skipped: 10 marks where the key expects 9. BOX_06 is a false positive caused by the sheet sliding about 25 px under the pencil, while the masks stay fixed from the first frame. BOX_09/BOX_10 onsets came before their strokes. Findings were 3 `order_discrepancy` (BOX_03 correct for the 3/4 swap, BOX_06 and BOX_09 spurious) and no `skipped` box 6; the key expects skip(6) plus order(3/4). Both reports were built and both hash chains recompute. The texture measure does separate pencil from a flat hand on SYNTHETIC frames, and recovers most real marks with correct order on the clean clip. On this footage, though, it does not reliably separate a real mark from sheet motion and a pencil hovering above a box. So the submission must not claim perception of marks from pixels. The product claim is the deterministic, evidence-linked verification of an event log: coverage, ordering, evidence ids and a recomputable hash chain. The extractor is shown as a measured demonstration with its misses. Two clips from one scene support neither a positive nor a negative generalisation. | None for perception: round 7 was the hard stop. Re-registration per frame would be the first change if perception is ever reopened |

## Round 8 — sheet registration, one change

Written before either real clip was run through rule v3. The outcome follows as the D030
amendment and D031.

**D029 amendment (round 8): follow the sheet.** Round 7 measured the sheet sliding about +25 px
horizontally across the skipped clip and about +3 / +8 px across the clean clip, while the rule-v2
box masks stayed fixed in the first frame. In the skipped clip blank box 6 rose to 4.23x its
baseline, and the last frame shows it blank, so that detection was geometry, not pencil. Clean
BOX_09 ended at 1.91x, under RISE 2.0; whether drift caused that is a hypothesis this round
tests, not a fact. Rule v3 (`panel_boxes_rule_v3`, docstring of
`src/witness/perception/boxes.py`) estimates each sample's integer translation of the sheet by
phase correlation of the Hann-tapered sheet crop against the first sample, searched strictly
inside half the smallest box pitch, and moves every box mask and the paper mask by it. One new
constant: the correlation peak must exceed **2.0x** the best value outside 2 px of it, or
extraction raises with the frame index. Per-sample dx, dy, peak and peak ratio are stored in
`box_marks.json`. The texture constants are unchanged: RISE 2.0, RELEASE 1.5, 3 s persistence,
4 px window margins, 2 px frame border. On SYNTHETIC frames, a 60 px sheet slide makes fixed
masks lose BOX_04, BOX_09 and BOX_10, and registration recovers all nine marks. A 25 px slide
of the SYNTHETIC sheet does not reproduce the real 4.23x, because its 3 px outlines carry too
little texture, so the test uses the larger slide. A frame-border test now pins P-029a, and a
noise frame and a lens-cap frame each raise the registration error.

**D030 amendment (round 8): the narrowing stands.** The round-7 decision above is unchanged.
Outcome of the one registration change: rule v3 was run once on each clip, unchanged, and
refused both. Clean: frame 1558 (t=52.033 s), correlation peak 0.1470 against a runner-up of
0.0746 (1.97x, needed more than 2.0x). Skipped: frame 1733 (t=57.814 s), 0.1328 against
0.0689 (1.93x). No events were produced, so the extractor matches the key on neither clip. A
diagnostic replay of the same computation without raising (not a result) shows registration
does follow the sheet when the peak is clear: skipped-clip shifts climb to +22 px confident
and +29 px at the last frame, against round 7's independent +25 px. But 245 of 1205 clean and
229 of 719 skipped samples fall at or below 2.0, mostly late in each clip as marks
accumulate. The round-7 BOX_09 hypothesis stays untested. Both `_03` reports were built over an
absent event log (10 `skipped` each) because the run script did not stop on the exit-2
refusal; they are not a measurement. Details are in `docs/REAL_MEDIA.md`, "Round 8 measurement".

| ID | Decision | Rationale and actual evidence | Revisit condition |
|---|---|---|---|
| D031 | **The perception line is closed and frozen.** The product claim is the one D030 states: deterministic, evidence-linked verification of an event log. Rule v3 stays in the code as the extractor, refusing loudly on these clips; no constant moves | Rule v2 (round 7) produced events but placed fixed masks on a drifting sheet. Rule v3 (round 8) follows the drift where the correlation is clear, and refuses where it is not, which on this footage is about a fifth of the samples. Lowering 2.0 would trade a loud refusal for masks that may sit wherever the pencil shadow is, which is the failure this round existed to remove. The latest real-clip events from any extractor remain the round-7 rule-v2 outputs (`artifacts/real_clean_02/`, `artifacts/real_skipped_02/`, produced by the code at tag `r7`), shown in the submission as a measured demonstration with their misses next to the key. Two clips from one scene, one operator and one sheet are a demonstration, not a generalisation claim, in either direction. | None. No round 9 and no further constant. The remaining time goes to the demo |
