# Model spike — round 13

Status: **BLOCKED: no credential.** No model call was made; spend USD 0.00; model integration
stays `NOT_RUN` (D032).

## The question

Can a Meta segmentation model (SAM 3.1 through the Meta Model API) find the ten printed boxes on
the real panel footage, where the deterministic extractor was frozen (D031)? The model is a
candidate generator, never an authority: its regions would replace the extractor's box masks,
and the existing texture measure, the audit and the evidence-id rule would still decide.

- Q1, localisation: does the model return ten plausible box regions per frame? Answered from six
  frames.
- Q2, separation: with model regions as masks, does the texture measure stop flagging blank box 6
  and find box 9? It needs every sample of both clips (1205 and 719 images, about USD 4.81 at the
  documented image price), so it is not attempted in this round.

## Go/no-go, fixed before any call

The thresholds are written in the docstring of `scripts/model_spike.py` and were not edited.

| | Pass | Marginal | Fail |
|---|---|---|---|
| Q1: frames with 10 plausible regions | ≥ 5 of 6 | 3–4 of 6 | ≤ 2 of 6 |
| Q1: regions land on the printed boxes (eye check, overlay PNG) | no systematic offset | small offset, correctable by a global shift | wrong regions or scattered |
| Cost per frame | ≤ USD 0.05 | ≤ USD 0.20 | > USD 0.20 |
| Latency per frame | ≤ 10 s | ≤ 30 s | > 30 s |

Prompt text "printed square box"; model `sam-3.1`, the adapter's only model.

## The six frames

| Clip | Original frame index | Position | Frame file | Result |
|---|---:|---|---|---|
| `real_panel_v1_clean.mp4` | 30 | start, before the first mark | `artifacts/spike/real_panel_v1_clean_f30.jpg` | refused before sending |
| `real_panel_v1_clean.mp4` | 3613 | middle | `artifacts/spike/real_panel_v1_clean_f3613.jpg` | refused before sending |
| `real_panel_v1_clean.mp4` | 7224 | end, after the last mark | `artifacts/spike/real_panel_v1_clean_f7224.jpg` | refused before sending |
| `real_panel_v1_skipped.mp4` | 30 | start, before the first mark | `artifacts/spike/real_panel_v1_skipped_f30.jpg` | refused before sending |
| `real_panel_v1_skipped.mp4` | 2155 | middle | `artifacts/spike/real_panel_v1_skipped_f2155.jpg` | refused before sending |
| `real_panel_v1_skipped.mp4` | 4307 | end, after the last mark | `artifacts/spike/real_panel_v1_skipped_f4307.jpg` | refused before sending |

Each run printed the existing gate's refusal: "PENDING: available credits are not confirmed; no
API request sent." No spend ledger and no `spend.json` were written, because the gate refuses
before it reserves anything.

## Numbers

| Measure | Value |
|---|---|
| Calls | 0 |
| Latency | not measured |
| Regions returned | not measured |
| Cost | USD 0.00 (estimate if run: 6 images x USD 2.50 / 1,000 = USD 0.015, `docs/API_VERIFICATION.md` pricing row) |
| Verdict row from B4 | none reached: blocked before the first call |

## Blockers, in the order the gate checks them

1. `WITNESS_MAX_SPEND_USD`: set to 5.00 for these runs only. Persisting it at user level was
   refused by this session's permission policy, so the operator sets it.
2. `--allow-paid`: passed.
3. `budget.max_usd`: 5.0 in `config/spike.toml`.
4. `budget.credits_confirmed`: false in `config/spike.toml`. Only the operator may set it to
   true, after checking the account balance.
5. `MODEL_API_KEY`: absent from this process and from the User and Machine environment. This is
   the credential the adapter reads (`src/witness/cli.py`, `docs/API_VERIFICATION.md`).

## The operator's command

After putting the key in `MODEL_API_KEY` and setting `credits_confirmed = true` in
`config/spike.toml`, from the repository root in PowerShell:

```powershell
$env:WITNESS_MAX_SPEND_USD = '5.00'; foreach ($s in 'clean:30','clean:3613','clean:7224','skipped:30','skipped:2155','skipped:4307') { $c, $f = $s.Split(':'); .venv/Scripts/python.exe -m scripts.model_spike --clip "data/raw/real_panel_v1_$c.mp4" --procedure data/procedures/panel_boxes_v1.json --frame $f --allow-paid --config config/spike.toml }
```

Each frame makes at most one request, without a retry, and saves the response bytes unmodified
as `artifacts/spike/<clip>_f<idx>_masks.json`, with an overlay PNG when a segmentation record
parses. The pinned client path (`meta-sam-parser==0.1.0` for decoding, a standard-library POST
for transport) has never made a live call, so its first run is also the B5 client check.

## What this proves

It proves that the harness, the frame extraction and the spend gate work end to end and refuse
without a credential and confirmed credits. It does not show that the Meta model can or cannot
find the boxes: no model output exists yet.
