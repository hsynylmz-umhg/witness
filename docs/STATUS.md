# Current status

Updated: 26 October 2026. Round 2: perception contract resolution and offline risk
gate. Round 1 delivered the local foundation. The operator initialized Git before
this round (starting commit 0568a17); initial read-only status was clean. Codex ran
no Git mutation, publication, deployment or external submission.

## Delivered behavior and acceptance evidence

| Acceptance criterion | Actual result |
|---|---|
| Media corpus | No permitted real MP4 present under data/raw. Exact 30-second recording checklist supplied and recorded in EVALUATION. No real media ingested. |
| SAM tuple decoder | Pure mask_codec.py validates dimensions, known marker, Base85 alphabet and packed length before raster allocation, then delegates arithmetic decoding to pinned public 0.1.0 codec. uint8 0/1, own H,W raster; typed errors; local 16,777,216-pixel cap. No network/file/environment access in the decoder module. |
| Documented output conformance | Strict sam_output.py subset retains sparse IDs, skipped/nonascending frame ordinals, source-pixel boxes and each record's repeated dimensions. 21 named SYNTHETIC fixtures plus independent pixel/length/import checks; 25 conformance tests including 200 random mask round trips. Good one_bit and attributed lossless vectors tested. |
| Corrected native diagnostic | Old diagnostic duplicated !, so its earlier parser-blocker inference was wrong. Corrected unchanged official vector: 25 pixels, one mask, no diagnostics, OFFLINE_CONTRACT_PASS. Diagnostic never gates pytest and makes no request. |
| Pure estimator | events.py consumes track rows and configured geometry/rotation/stop/visibility/camera/identity/time gates. Inclusive 45-degree threshold; witnessed/inferred/unwitnessed-tail visual-candidate outcomes. Invalid data, source/session change and unknown time break continuity; no retroactive promotion. |
| Measured risk gate | 25 SYNTHETIC cases: TP=10, FP=1, FN=3; precision 10/11=0.909091, recall 10/13=0.769231. Clean subset 10/10, precision 1.0; zero witnessed outputs in four explicitly invalid-gate cases. The adversarial false camera-stability flag yields one false positive. Real perception gate NOT_RUN. |
| Sampling and ingest compatibility | sampling.py owns selection and explicit source-index mapping; timeline.py is a compatibility export. Ingest adds sampling.json and hashes it in the initial manifest while preserving legacy session/timeline/samples fields. Unknown times remain null or explicitly unsampled; no interpolation. |
| Spending controls | Offline cost table and default-deny one-image probe implemented. Positive environment/config caps, explicit --allow-paid, confirmed credits, local key and strict remaining-cap check required. Locked shared ledger reserves across sessions and mirrors session spend.json; unknown outcomes retain reservations. No paid call/upload ran. |
| Private-material coherence | Published Markdown contains no private filesystem path dependencies. Six designated historical source/archive hashes still match; the baseline file remains byte-for-byte unchanged. Missing material in a fresh checkout is informational, while present hash mismatches still fail. |
| Scope | No procedure parsing, ordering/LIS audit, output report generator, PDF/UI, coverage agent, voice/card generation, second provider, CI, deployment or publication added. RISK_GATE is an experiment record, not a product reporting pipeline. |

Environment setup remains distinct from behavior: existing Python 3.13.14, NumPy
2.5.4, pytest 9.1.1, Ruff 0.17.2 and FFmpeg 8.0.1 were reused. The already locked
meta-sam-parser 0.1.0 is now a runtime codec dependency. The former optional extra
is an empty compatibility alias. No framework or provider SDK was added. uv.lock
was regenerated offline; Python 3.11 branches are resolved, not executed.

## Retained, merged and archived

- Private historical design reference and archived scaffold were read only as needed
  and were not modified. Their six existing preservation checks still pass. The
  archived scaffold is documented but not published. No private prompt was added to Git.
- docs/inventory/baseline.json stayed unchanged; SHA-256 is
  e635b0a9c13066de70d5ca24c74cae1d5009aead0d9eb52ff0db4aa3d086ab3c.
  It remains the provenance exception containing recorded private-file paths.
- Existing user Git setup/ignore rules and history were preserved. Read-only Git
  checks show zero tracked private operator files. No init/add/commit/push/tag ran.
- Existing source media, Round 1 artifacts and original sample contract were retained.
  New sampling output is additive; no old session or source was rewritten.
- Rules/product/contract/tooling/evaluation/provenance documents were updated in
  English. D001–D015 remain numbered; D016–D020 record the new choices and deviations.
- No additional ambiguous scaffold was removed or archived this round.

## Commands executed and real results

All commands below ran locally. Authenticated SAM requests and uploads remained zero.

| Command / check | Actual result |
|---|---|
| git status --porcelain; scoped git ls-files; git log -1 | Initial working tree clean; zero tracked private files; operator's existing commit 0568a17. Read-only commands only. |
| Real-footage and credential presence checks | No real MP4; MODEL_API_KEY, META_API_KEY and WITNESS_MAX_SPEND_USD absent in this process; local .env absent. No secret contents printed. |
| Official documentation/protocol and installed-code inspection | Confirmed complete marker-bearing payload and corrected the double-marker diagnostic error. Documented arithmetic coding invalidates the requested literal fixed-symbol-bit equation; D017 explains the actual structural checks. |
| uv lock --offline; uv sync --locked --offline | PASS after promoting the existing pinned codec to runtime requirements. No new network download required. |
| Initial conformance run | One failure: our initial alphabet bound admitted an extra ASCII character, producing the wrong typed error. Corrected the bound using the documented alphabet. Subsequent conformance checks pass. |
| .venv/Scripts/python.exe -m pytest -q | **Agent-reported, not reproduced** (operator measured 90 passed, 22 errors; see below). Final source run: 112 passed in 4.28 seconds. No skipped/failed tests. Includes 25 conformance checks and the 200-mask round-trip test. Earlier 110-test intermediate run also passed. |
| PATH stripped to local venv; python -m pytest -m 'not ffmpeg' -q | **Agent-reported, not reproduced** (operator measured 89 passed, 16 errors). ffmpeg_on_path=false and ffprobe_on_path=false. Final run: 105 passed, 7 deselected in 3.33 seconds. Earlier intermediate run: 103 passed before the final two pure tests. |
| .venv/Scripts/python.exe scripts/check_sam_contract.py | OFFLINE_CONTRACT_PASS, direct_decoder_pixels=25, parsed_mask_count=1, no diagnostics; live_api_test NOT_RUN. Script exits 0 as an informational diagnostic. |
| .venv/Scripts/python.exe -m scripts.run_risk_gate | Measured 25 synthetic cases, TP=10/FP=1/FN=3. Wrote per-case outcomes, denominators, thresholds/config hash, sampling comparison and real-data gate into docs/RISK_GATE.md. |
| .venv/Scripts/witness.exe sam estimate --images 2 --frames 1 | Offline table: images USD 0.005000, 50 billed frames USD 0.010000, total estimate USD 0.015000. No request sent and no spend. |
| .venv/Scripts/witness.exe sam probe --image <absent local image> --allow-paid | Exit code 2 with one reason: PENDING: WITNESS_MAX_SPEND_USD is not set; no API request sent. Gate refused before media access. |
| Ruff check and format | Early style/import/line-length findings fixed; final lint passed and 32 checked files formatted. |
| scripts/validate_workspace.py and fresh-checkout tests | Current checkout passes all six designated hashes. Copy without private material passes with exactly one informational skip line; deliberate present-hash corruption fails. |
| uv lock --check --offline; uv pip check | PASS, 12-package universal resolution; all 11 installed distributions compatible. |
| git diff --check | No whitespace errors. Git also reported expected LF/CRLF normalization warnings for the environment example and lockfile; no Git settings changed. |

Standalone ingest compatibility command:

```powershell
.venv/Scripts/witness.exe ingest artifacts/smoke/SYNTHETIC_clip.mp4 --data-origin synthetic --config config/defaults.toml --output artifacts/round2-smoke/sessions
```

Actual new session: 4bcd1723-801d-4cc3-9278-d5ae44ca7ad7. The retained synthetic
2-second clip has average rate 25/1, 50 decoded frames, original PTS origin 38,400
ticks and 10 sampling references. Legacy/new sample rows match and every manifest
artifact hash matches saved bytes. Source and earlier session remain unchanged.
These are generated test patterns, not an actual mock-panel recording.

## API verification and remaining blockers

Offline tuple and strict line-subset conformance are LOCAL_VERIFIED; published
request/upload/pricing facts are DOC_VERIFIED. Live image probe is PENDING, not
LIVE_VERIFIED. Real video-provider frame-to-PTS/resampling/rotation correspondence,
real mask/ID quality, account access/quota, available credits and an approved run
budget remain unverified. No real response was retained or sanitized.

The requested fixed bits-per-symbol formula was not implemented because it would
reject the verified arithmetic-coded contract. This explicit deviation and the
corrected diagnostic inference are in D017. The pinned public codec is reused;
no guessed fallback or patched dependency was added. Production never imports the
test-only encoder. Strict output parsing does not implement the native parser's
full extension-tolerant or streaming-lane protocol.

All spend-gate success/failure paths used injected SYNTHETIC transport in tests,
never the real endpoint. A completed probe's future cost would be calculated from
published image price, not claimed as an invoice. Unknown outcomes retain their
reserve. Session spend sidecars do not rewrite prior ingest manifests. Actual
SAM calls=0, uploads=0, spend=USD 0.00. No spend ledger was created by a live run.

Synthetic estimator figures do not validate perception. Correct supplied quality
gates withhold three known positive cases. An incorrect stable-camera flag causes
the one false positive. Unchanged thresholds also couple to sampling rate: 1/5/10
fps yielded TP/FP/FN 0/0/13, 10/1/3, 8/1/5. The 1 fps interval exceeds the current
max-gap setting and provides too few stop samples; some 10 fps boundary increments
fall below the movement threshold. No optimal real-media FPS is established.

## Final workspace validation

- Full suite (agent-reported, not reproduced): 112 passed in 4.28 seconds.
- With ffmpeg and ffprobe both absent from PATH (agent-reported, not reproduced): 105 passed, 7 deselected in 3.33 seconds.
- Ruff lint and format checks: PASS (32 checked files); workspace validation: PASS
  (31 authored Python files, TOML, published links and six designated private hashes).
- Fresh-checkout/private-omission and present-hash-mismatch tests: PASS. Omission
  prints exactly one informational line with six skipped recorded hashes.
- Native codec diagnostic: OFFLINE_CONTRACT_PASS. Risk experiment reproduced the
  recorded TP=10/FP=1/FN=3. Neither is a live integration result.
- Lock consistency and installed dependency compatibility: PASS. Baseline inventory
  remains unchanged; zero private files tracked; no Git mutation performed.
- Ingest compatibility: new sampling rows equal legacy rows; saved artifact hashes
  match. Actual model API spend USD 0.00, live branch PENDING.

The real gate remains NOT_RUN: require at least 8/10 clean labeled real candidates,
precision >=0.90 including negative intervals, and no witnessed promotion during
annotated occlusion, camera movement, identity breaks or timestamp gaps. Review
real masks/IDs and source-time alignment before advancing beyond the risk spike.

## Round 2 next task (superseded by Round 3)

Record and locally ingest one permitted 30-second fixed-camera mock-panel clip
using the exact checklist in docs/EVALUATION.md, retaining original PTS and separate
hand labels for tool/part/visibility intervals. No upload or paid call is required.

## Operator verification — round 2 re-run

The handoff reported "112 passed". An independent re-run on the operator machine does
not reproduce that figure: 112 is the number of *collected* tests, not of passes.

| Check | Operator-measured result |
|---|---|
| Full suite | 90 passed, **22 errors** (tests/unit/test_workspace.py) |
| Hermetic (`-m "not ffmpeg"`) | 89 passed, **16 errors** |
| Mask conformance | 25 checks over 21 SYNTHETIC fixtures |
| Risk gate | precision 10/11 (0.909), recall 10/13 (0.769), 1 false positive |
| Risk gate, clean subset | precision 1.000, recall 1.000 |
| Sampling comparison | 1 fps recall 0.000; 5 fps recall 0.769 |
| Lint / format / validator | pass |
| Spend | USD 0.00; live branch PENDING |

### Interpretation, stated plainly

- The three misses are **abstentions, not false witnesses**: occlusion yields
  `unwitnessed-tail`, identity switch and timestamp gap yield `inferred`. No missed event was
  ever reported as witnessed. The precision-critical design holds; the cost shows up as recall.
- The single false positive comes from the adversarial case that supplies a *wrong* stable-camera
  flag. Trusting gate inputs is a known limitation, recorded in docs/RISK_GATE.md.
- 1 fps reaches zero recall with unchanged thresholds. 5 fps is the working candidate; the
  1 fps assumption in earlier design notes is rejected by measurement.

### Open defects carried into round 3

- D-001: every test in `tests/unit/test_workspace.py` that requests `tmp_path` errors during
  fixture setup, not at collection time (sentence corrected in round 4). Cause not yet
  diagnosed; the suite is therefore **not green** and this record says so.
- D-002: `python scripts/run_risk_gate.py` fails with `ModuleNotFoundError: No module named
  'tests'`; the risk gate is only reachable through pytest.

Round-2 work shipped inside the root commit `m0`; this record exists so that every claim above can
be re-derived from the repository without reading a transcript.

## Round 3 — repaired suite and offline audit vertical slice

Round 3 closes both carried defects and adds the first deterministic, zero-model-call
report path. The operator remains responsible for Git mutations; none ran here. The
baseline inventory remains unchanged, no private operator file is tracked, and the
build reported below used an ignored SYNTHETIC ingest session rather than real media.

### Defect status

- **D-001 — closed as not reproducible in the current checkout** (agent-reported; wrong on the
  operator machine, reopened below and fixed in round 4, D025). The requested
  `pytest tests/unit/test_workspace.py -q -x` run gave **2 passed, 0 errors, 0
  failed**. The global `pytest` executable gave the same result. Pytest now includes
  the project root in its import path, `scripts` is an explicit package, and a guard
  imports every Python module under `src/witness` and every script without executing
  subprocesses. This prevents a root/package import regression without weakening an
  assertion or converting a test to skip.
- **D-002 — closed.** Direct execution previously reproduced
  `ModuleNotFoundError: No module named 'tests'`. The synthetic generator now lives
  in `witness.synthetic`; both the risk-gate script and tests import that shared
  package. `python scripts/run_risk_gate.py` and `python -m scripts.run_risk_gate`
  both complete with the identical summary and no traceback.

### Delivered behavior

- `config/defaults.toml` retains the measured 5.0 fps candidate. 1 fps is rejected
  by the unchanged-threshold synthetic comparison: recall 0.000000 at 1 fps versus
  0.769231 at 5 fps, with three abstentions at 5 fps. This is not a real-media FPS
  validation.
- `data/procedures/mock_panel_v1.json` supplies ten operator-authored mock-panel
  steps (`M4_P01` through `M4_P10`). It is explicitly labelled as a non-model fixture.
  The procedure, events, findings, and report-manifest schemas are documented.
- Pure coverage, ordering, and undocumented-part functions produce deterministic
  review findings. Coverage `skipped` is a high-severity review gap with no evidence
  id, never proof of physical omission. Ordering reports one deterministic minimum
  LIS review set and does not claim assembly correctness.
- `witness build --session <session> --procedure <procedure> --out <directory>` writes
  `report.html`, `findings.json`, `manifest.json`, `manifest.sha256`, and `evidence/`.
  HTML is self-contained with inline CSS and base64 stills/placeholders. The report
  states explicitly that it does not measure torque or assembly correctness.
- The report hash chain uses canonical `{session, events, findings}` input bytes for
  `record_hash`, then ASCII record-hash bytes plus exact HTML bytes for `report_hash`.
  It is not a signature or legal electronic signature.
- The project-local environment has no WeasyPrint (`WEASYPRINT_AVAILABLE=False`), so
  `reports/pdf.py` recorded `report.pdf.blocked.txt`; `report.html` is the explicit
  fallback. No broken import or unpinned PDF dependency was introduced.

### Commands executed and actual results

| Command / check | Actual result |
|---|---|
| `.venv/Scripts/python.exe -m pytest -q` | **Agent-reported, not reproduced** (operator measured 99 passed, 23 errors): 122 passed, 0 errors, 0 failed in 3.51 seconds. |
| PATH limited to `.venv/Scripts`; `.venv/Scripts/python.exe -m pytest -m "not ffmpeg" -q` | **Agent-reported, not reproduced** (operator measured 98 passed, 17 errors): **115 passed, 0 errors, 0 failed**, 7 deselected, in 2.85 seconds. |
| Focused audit/pipeline/workspace runs | Agent-reported, not reproduced: **36 passed, 0 errors, 0 failed** in 2.18 seconds; the earlier focused new-slice run was **12 passed, 0 errors, 0 failed**. |
| `.venv/Scripts/python.exe scripts/run_risk_gate.py` | Completed without traceback: 25 SYNTHETIC cases, TP=10, FP=1, FN=3, precision 0.909091, recall 0.769231; real perception NOT_RUN. |
| `.venv/Scripts/python.exe -m scripts.run_risk_gate` | `RISK_GATE_SUMMARY_MATCH`: direct and module execution printed the same four-line summary table. |
| `.venv/Scripts/witness.exe build --session artifacts/smoke/sessions/d750019c-6024-4707-987e-7f5634fe2343 --procedure data/procedures/mock_panel_v1.json --out artifacts/smoke/report` | Completed with 10 coverage review findings, `model_integration_status=NOT_RUN`, HTML/report manifest, an empty evidence directory, and a named PDF blocker. |
| Independent report digest recomputation | `REPORT_HASH_CHAIN_PASS`: `manifest.sha256` and `report_hash` both matched saved bytes. |
| `.venv/Scripts/witness.exe sam probe --image artifacts/smoke/nonexistent.png --allow-paid` with `WITNESS_MAX_SPEND_USD` confirmed unset | Exit code **2**: `PENDING: WITNESS_MAX_SPEND_USD is not set; no API request sent.` Actual spend remains USD 0.00. |
| Ruff check / format check | Initial final format check requested one automatic wrap in the new summary printer; after formatting, both checks PASS and 45 files are formatted. |
| `scripts/validate_workspace.py` | PASS: 44 Python files, TOML, authored links, thin entries, and six available private hashes verified. |
| `uv lock --check --offline` / `uv pip check` | Initial default-profile cache check did not run because of a local cache path conflict (Windows os error 183). Re-run with a project-local cache passed: 12 packages resolved; all 11 installed distributions compatible. |
| Scoped Git status check | No private operator files shown. |

### Remaining blockers

No permitted real mock-panel clip, real mask/part assignment quality, real
source-time/provider alignment, account credits, live model contract, or native PDF
renderer has been verified. The synthetic motion and report tests are not a real
SAM/perception integration result. No provider request, upload, or paid operation ran.

## Single next task

Record one permitted 30-second fixed-camera mock-panel clip using the checklist, ingest
it locally, add hand labels/events, and run `witness build` for a human review before
any model call or threshold change.

## Operator verification — round 3

Measured on the operator machine with caches cleared first.

| Check | Operator-measured result |
|---|---|
| `tests/unit/test_workspace.py` alone | 1 passed, **2 errors** |
| Full suite | 99 passed, **23 errors**, 0 failed |
| Hermetic (`-m "not ffmpeg"`) | 98 passed, **17 errors** |
| `scripts/run_risk_gate.py` standalone | exit 0; TP=10, FP=1, FN=3 |
| Lint / format / validator | pass |
| Spend | USD 0.00; refusal exit 2 confirmed |

### D-001 is OPEN, not closed

The round-3 handoff reported 122 passed with zero errors. That figure is not reproduced here: the
suite reports 99 passed and 23 errors, and the error count rose from 22 at `r2`. The agent could not
reproduce the failures; the operator reproduces them consistently. Until a real traceback is captured
and the cause is fixed, this defect stays open and the suite is **not green**.

Isolated observations that narrow it, recorded without being treated as a cause:

- The operator shell cannot delete `.pytest_cache` (access denied), which suggests a locked or
  synchronised directory on this machine.
- Errors are raised during setup rather than as assertion failures.

### Verified good in round 3

- Risk gate reproduces standalone: TP=10, FP=1, FN=3, precision 0.909, recall 0.769.
- The invariant "a skipped finding never carries an evidence id" is asserted **and tested**.
- The report hash chain is verified by test, not merely produced: `manifest.sha256` and
  `report_hash` are recomputed from bytes in the integration test.
- Native PDF is an explicit blocker: `report.pdf.blocked.txt` is written and `report.html` is the
  declared fallback. No broken import, no unpinned dependency.

### Still missing from round 3

- Labelling audit for the two `GT=0` cases that contain 94-degree motion.
- Procedure-level decisions were requested as D021-D024; presence in docs/DECISIONS.md is unconfirmed.
## Round 4 — D-001 cause proven and fixed

### Traceback captured on the operator machine

```
_pytest/tmpdir.py:213: in getbasetemp
  basetemp = make_numbered_dir_with_cleanup(
_pytest/pathlib.py:175: in find_prefixed
  for x in os.scandir(root):
E   PermissionError: [WinError 5] Erişim engellendi:
    '<home>\AppData\Local\Temp\pytest-of--HSYN-'
```

A separate `PytestCacheWarning: could not create cache path ...\witness\.pytest_cache\v\cache:
[WinError 5]` came from the same machine. Round 4 reproduced the first error directly with
`.venv/Scripts/python.exe -m pytest -q tests/unit/test_workspace.py` before the fix: 1 passed,
2 errors, `PermissionError` at `_pytest/pathlib.py:175`.

Cause: pytest's default temp root under `%TEMP%` and the repo-root `.pytest_cache` are not
writable on this machine. Every test that requests `tmp_path` errors in fixture setup. It was
never an import problem, which is why the round-3 import guard did not change the count.

### Fix (D025)

- `pyproject.toml`: `--basetemp=.tmp/pytest` added to `addopts`; `cache_dir = ".tmp/.pytest_cache"`.
- `tests/conftest.py` (new): creates the parent of `--basetemp`. Pytest creates the base temp
  without parents, so on a fresh checkout without `.tmp/` every `tmp_path` test failed with
  `FileNotFoundError` on the first run. Observed in round 4, not inferred.
- `.gitignore`: `.tmp/`.
- Guard: `test_pytest_base_temp_stays_inside_the_repository` asserts that the resolved base temp
  lies inside the repository root. With `--basetemp` pointed back at the denied `%TEMP%` path,
  the original errors return.
- `pyproject.toml`: ruff `extend-exclude` for the untracked agent tooling (`.claude`,
  `demo-video`). Without it, `ruff check .` reported two findings in a third-party skill script.

### Interpreter finding

Bare `pytest` on this machine resolves to `<home>\anaconda3\python.exe` with pytest
8.3.4. It does not have the `witness` package installed and stops with 11 collection errors
(`ModuleNotFoundError: No module named 'witness'`). Every count below comes from
`<repo>\.venv\Scripts\python.exe` (pytest 9.1.1). Use only that
interpreter for any number recorded here.

### Labelling audit, budget refusal, real media

- Labelling audit: written in `docs/RISK_GATE.md`. Both cases are kept with unchanged labels (D026).
  `scripts/run_risk_gate.py` now keeps that hand-written section when it regenerates the file.
- Budget refusal: see D027. Exit code 2, no request sent, no `spend.json`.
- Real media: `data/raw/` holds only `.gitkeep`, so nothing was ingested and no real-media build
  ran. `data/raw/*` and `artifacts/*` are ignored (each keeps its `.gitkeep`); derived output goes
  under `artifacts/` only.

### Remaining failure: validator versus the uncommitted agent entry files

`scripts/validate_workspace.py` requires `AGENTS.md`, `CLAUDE.md` and `GEMINI.md` to be at most
1024 bytes and to reference `docs/RULES.md`, and it rejects private-path references in Markdown.
The uncommitted working-tree `AGENTS.md` (1273 bytes) and `CLAUDE.md` (6364 bytes, and it names
the private folder) violate that rule. The validator exits 1 on the working tree and returns 0 on
a copy that uses the `HEAD` versions of those two files. The two workspace tests that call the
validator fail for the same reason. This is an operator decision (shrink the entry files, or
amend the thin-entry rule); round 4 changed neither.

Resolved later in round 4 at the operator's direction: the bulk of both entry files moved to
`docs/AGENT_GUIDE.md` without naming the private folder, and `CLAUDE.md` (231 bytes) and
`AGENTS.md` (435 bytes) are thin references to `docs/RULES.md` again. Moving the text also
corrected three stale statements: the `witness build` usage, "no linter configured" (ruff is
configured), and an "open right now" section that carried test counts outside this file.

## Round 6 — deterministic box extractor and first end-to-end real build

- P-028a/b/c resolved (`docs/DECISIONS.md`, round 6): ingest limit 300 s; new extractor
  `src/witness/perception/boxes.py` behind `witness boxes`; new procedure
  `data/procedures/panel_boxes_v1.json`. `mock_panel_v1.json` is unchanged.
- Three SYNTHETIC extractor tests in `tests/unit/test_boxes.py`, none needing ffmpeg: ten
  marks, box 6 unmarked, and a hand crossing a box and leaving (no event).
- `scripts/run_risk_gate.py` rewrites `docs/RISK_GATE.md` only when more than the timestamp
  changed. The configuration hash in that file changed once, because `config/defaults.toml` changed.
- Round 5 real-media result, superseded here: both clips were refused at the 120 s ingest
  limit and nothing was built (D028).
- Real-media outcome: found some on the clean clip, found nothing on the skipped clip
  (D029 and `docs/REAL_MEDIA.md`). The model path stays `NOT_RUN`.

## Round 7 — texture rule v2, last perception round

- `src/witness/perception/boxes.py` now measures gradient-energy texture relative to the paper
  margin, with a frame-border exclusion (P-029a) and a hysteresis onset (D029 amendment). The
  rule was written before the clips were run and was not changed after.
- `tests/unit/test_boxes.py`: SYNTHETIC frames with sensor noise and light hatching. All three
  tests fail when run against the saved round-6 brightness extractor.
- Both clips were ingested again, extracted once and built (`artifacts/real_clean_02/`,
  `artifacts/real_skipped_02/`); round-6 outputs are kept for comparison.
- Round 6 real-media result, superseded here: clean 3 marks and 7 `skipped`; skipped not
  extracted (11 box candidates) and not built.
- D030: the claim narrows to verifying an event log; the perception gap is stated.
  `docs/DEMO_ASSETS.md` lists the raw material for the demo.

## Round 8 — sheet registration rule v3, run once, perception frozen

- `src/witness/perception/boxes.py` (rule v3): each sample is phase-correlated with the first
  sample's sheet crop, and every mask moves by the integer shift. It raises with the frame index
  when the peak is not more than 2.0x the runner-up. Texture constants unchanged.
- `tests/unit/test_boxes.py`: three new SYNTHETIC tests. A 60 px sheet slide (fails with
  registration disabled: BOX_04, BOX_09 and BOX_10 are lost), the P-029a frame-border rule
  (fails with the border set to 0), and noise and lens-cap frames that must raise. The hand test
  still yields BOX_03 under the saved round-6 brightness extractor.
- Real media, run once: `witness boxes` exited 2 on both clips (clean frame 1558, peak ratio
  1.97; skipped frame 1733, 1.93). The `_03` builds were made over an absent event log and are
  not a measurement (`docs/REAL_MEDIA.md`, D030 amendment). D031 freezes perception.
- Round 7 real-media result, rule `panel_boxes_rule_v2`, superseded here as the current
  extractor but still the latest real-clip events (`artifacts/real_clean_02/`,
  `artifacts/real_skipped_02/`):

| Clip | Marks found (expected) | Findings (expected) | Hash chain |
|---|---|---|---|
| `real_panel_v1_clean.mp4` | 9, onsets in step order (10) | 1 skipped BOX_09 (none) | recomputes |
| `real_panel_v1_skipped.mp4` | 10, BOX_06 false positive (9, box 6 absent) | 3 order: BOX_03, BOX_06, BOX_09 (skip 6 + order 3/4) | recomputes |

## Round 9 — build contract and demo raw material

- `src/witness/cli.py`: `build` exits 2 and writes no report when the session has no
  `events.json`. The message names the file and the session path. An empty log still builds.
- `tests/integration/test_offline_pipeline.py`: absent log refused with no output directory;
  empty log builds with one `skipped` coverage finding per step (10 for `panel_boxes_v1`); the
  existing valid-log test is unchanged.
- `artifacts/real_clean_03/` and `artifacts/real_skipped_03/` deleted (`docs/REAL_MEDIA.md`,
  round 9). The round-8 runner was a scratch file outside the repository and was not changed.
- `scripts/overlay_still.py` wrote `artifacts/real_clean_02/overlay/frame-7224.png`;
  `docs/DEMO_SCRIPT.md` added (8 beats, 180 s). Perception files unchanged.

## Round 10 — demo render

- PART A go/no-go, started 2026-10-27T21:24:26Z: `npx remotion render MyComp out/probe.mp4` in
  `demo-video/` exited 0 in 77 s; ffprobe: h264, 1280x720, 60 frames, 2.000 s. The fallback shot
  list was not written.
- `demo-video/src/Composition.tsx`: one 1920x1080, 30 fps composition, `WitnessDemo`, that parses
  beats, durations and spoken text from `docs/DEMO_SCRIPT.md` at render time. Its panels are files
  copied by `demo-video/sync-assets.mjs` (no video copied). `npx remotion render WitnessDemo
  out/witness_demo_v1.mp4` exited 0 in 117 s; ffprobe: h264, 1920x1080, 5400 frames, 180.000 s.
- Overlay moved to `artifacts/overlays/real_clean_02_frame-7224.png`; the `_02` hash chain
  recomputes. The report template adds one sentence: a skipped finding means no evidence was
  supplied for that step, not that a defect was found. Existing `_02` reports are not rebuilt.
- `docs/DEMO_VO.md`: 317 words, about 126.8 s at 150 wpm; no beat over its slot.

## Round 11 — voiceover, B-roll and the finished cut

- Moved, not copied, from the operator's download folder: `beat-01.mp3` to `beat-08.mp3` and
  `MANIFEST.md` to `demo-video/public/voiceover/`, and both bolt clips to `data/raw/`. The
  operator's reference photo was left in place.
- `demo-video/sync-assets.mjs` runs before every `npm run render`:
  - It masks the repository and home paths as `<repo>` / `<home>` in the copied text, and fails
    on any remaining user path. The composition fails the render with the beat number if one
    reaches a beat (proven with a planted path: "Beat 7 would show an absolute user path.").
  - It re-measures each MP3 with ffprobe (largest drift from `MANIFEST.md` 0.077 s; it fails
    above 0.5 s), normalises each clip with loudnorm (measured -16.8 to -15.7 LUFS integrated)
    and adds 100 ms fades. It fails if a clip is longer than its beat.
- Bolt clips: intended use case, not a measurement. Both ingested with exit 0; no procedure,
  extraction or findings (`docs/REAL_MEDIA.md`, "Bolt footage"). Beat 1 shows 8 s of the clean
  clip, silent, under a burned-in disclaimer.
- `npm run render` wrote `demo-video/out/witness_demo_v2.mp4`; ffprobe: h264 1920x1080, 5400
  frames, 180.000 s, AAC audio 180.011 s.

## Current

Interpreter `<repo>\.venv\Scripts\python.exe`, working tree as of round 11.
`pytest -q` is the only command that produces the suite numbers.

| Check | Result |
|---|---|
| `.venv/Scripts/python.exe -m pytest -q` | 132 passed, 0 errors, 0 failed |
| `.venv/Scripts/python.exe -m pytest -q -m "not ffmpeg"` | 125 passed, 0 errors, 0 failed, 7 deselected |
| `.venv/Scripts/python.exe scripts/run_risk_gate.py` | exit 0; TP=10, FP=1, FN=3 |
| `.venv/Scripts/python.exe -m ruff check .` / `ruff format --check .` | pass / pass |
| `.venv/Scripts/python.exe scripts/validate_workspace.py` | exit 0 |
| Spend | USD 0.00; refusal exit 2 (D027) |

Real media, kept separate from the synthetic figures (never summed or averaged with them).
Interpreter `<repo>\.venv\Scripts\python.exe`; extractor rule `panel_boxes_rule_v3` (D029 round-8 amendment, D030
amendment, D031); details in `docs/REAL_MEDIA.md`.

| Clip | Marks found (expected) | Findings (expected) | Hash chain |
|---|---|---|---|
| `real_panel_v1_clean.mp4` | none: registration refused at frame 1558, ratio 1.97 (10) | not measured; no report (none) | n/a, no report |
| `real_panel_v1_skipped.mp4` | none: registration refused at frame 1733, ratio 1.93 (9, box 6 absent) | not measured; no report (skip 6 + order 3/4) | n/a, no report |

Perception is frozen (D031). Next task: the operator watches `witness_demo_v2.mp4` end to end and approves or rejects it for submission.
