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
| .venv/Scripts/python.exe -m pytest -q | Final source run: 112 passed in 4.28 seconds. No skipped/failed tests. Includes 25 conformance checks and the 200-mask round-trip test. Earlier 110-test intermediate run also passed. |
| PATH stripped to local venv; python -m pytest -m 'not ffmpeg' -q | ffmpeg_on_path=false and ffprobe_on_path=false. Final run: 105 passed, 7 deselected in 3.33 seconds. Earlier intermediate run: 103 passed before the final two pure tests. |
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

- Full suite: 112 passed in 4.28 seconds.
- With ffmpeg and ffprobe both absent from PATH: 105 passed, 7 deselected in 3.33 seconds.
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

## Single next task

Record and locally ingest one permitted 30-second fixed-camera mock-panel clip
using the exact checklist in docs/EVALUATION.md, retaining original PTS and separate
hand labels for tool/part/visibility intervals. No upload or paid call is required.
