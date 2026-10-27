# Synthetic perception risk gate

Measured UTC: 2026-10-27T17:28:14.229884Z
Pipeline 0.1.0; algorithm rotation_stop_v1; configuration SHA-256 73ce3d6f5c776dd0403750b7226d84997957faf9047f2c554069d8b44735dd82.

## Meaning and limits

All 25 cases are SYNTHETIC rasterized rectangles, with independent authored motion/stop
labels and supplied camera/visibility/identity flags. Source rate is 25 fps. Repeats
reuse a controlled generator; they are not independent real recordings. This validates
the estimator and its gates, not real perception, SAM mask/ID quality, camera-stability
estimation, 3D rotation, tightening or torque. No real video or API call was used.

Candidate sampling: 5 fps. Ground truth is rotation >=45 degrees followed by a stop.
Only witnessed visual candidates count as detections. Deliberately occluded, switched-ID
and gapped positive cases remain in the recall denominator: withholding them is counted
as a miss rather than hidden as success. The adversarial camera case supplies a wrong
stable-camera flag; a false positive there exposes a limitation of trusting gate inputs.

## Condition results

| SYNTHETIC condition | Ground truth events | Detected (TP) | Missed (FN) | False positives | Outcomes |
|---|---:|---:|---:|---:|---|
| SYNTHETIC_clean_0_no_stop | 0 | 0 | 0 | 0 | none |
| SYNTHETIC_clean_0_stop | 0 | 0 | 0 | 0 | none |
| SYNTHETIC_clean_15_no_stop | 0 | 0 | 0 | 0 | none |
| SYNTHETIC_clean_15_stop | 0 | 0 | 0 | 0 | none |
| SYNTHETIC_clean_44_no_stop | 0 | 0 | 0 | 0 | inferred: 1 |
| SYNTHETIC_clean_44_stop | 0 | 0 | 0 | 0 | none |
| SYNTHETIC_clean_45_no_stop | 0 | 0 | 0 | 0 | unwitnessed-tail: 1 |
| SYNTHETIC_clean_45_stop | 1 | 1 | 0 | 0 | witnessed: 1 |
| SYNTHETIC_clean_60_no_stop | 0 | 0 | 0 | 0 | unwitnessed-tail: 1 |
| SYNTHETIC_clean_60_stop | 1 | 1 | 0 | 0 | witnessed: 1 |
| SYNTHETIC_clean_94_no_stop | 0 | 0 | 0 | 0 | unwitnessed-tail: 1 |
| SYNTHETIC_clean_94_stop | 1 | 1 | 0 | 0 | witnessed: 1 |
| SYNTHETIC_clean_120_no_stop | 0 | 0 | 0 | 0 | unwitnessed-tail: 1 |
| SYNTHETIC_clean_120_stop | 1 | 1 | 0 | 0 | witnessed: 1 |
| SYNTHETIC_clean_repeat_0 | 1 | 1 | 0 | 0 | witnessed: 1 |
| SYNTHETIC_clean_repeat_1 | 1 | 1 | 0 | 0 | witnessed: 1 |
| SYNTHETIC_clean_repeat_2 | 1 | 1 | 0 | 0 | witnessed: 1 |
| SYNTHETIC_clean_repeat_3 | 1 | 1 | 0 | 0 | witnessed: 1 |
| SYNTHETIC_clean_repeat_4 | 1 | 1 | 0 | 0 | witnessed: 1 |
| SYNTHETIC_clean_repeat_5 | 1 | 1 | 0 | 0 | witnessed: 1 |
| SYNTHETIC_occlusion_94_stop | 1 | 0 | 1 | 0 | unwitnessed-tail: 1 |
| SYNTHETIC_identity_switch_94_stop | 1 | 0 | 1 | 0 | inferred: 1 |
| SYNTHETIC_camera_jitter_94_stop | 0 | 0 | 0 | 0 | none |
| SYNTHETIC_timestamp_gap_94_stop | 1 | 0 | 1 | 0 | inferred: 1 |
| SYNTHETIC_unflagged_camera_rotation_94_stop | 0 | 0 | 0 | 1 | witnessed: 1 |

All conditions: TP=10, FP=1, FN=3; precision 10/11 = 0.909091;
recall 10/13 = 0.769231. n=25 cases, 13 ground-truth events.
Clean subset: TP=10, FP=0, FN=0; precision 1.000000; recall 1.000000.
Qualified witnessed outputs in the four explicitly gated bad-quality cases: 0.

## Sampling comparison with unchanged thresholds

| Candidate fps | TP | FP | FN | Precision | Recall |
|---:|---:|---:|---:|---:|---:|
| 1 | 0 | 0 | 13 | undefined (0 denominator) | 0.000000 |
| 5 | 10 | 1 | 3 | 0.909091 | 0.769231 |
| 10 | 8 | 1 | 5 | 0.888889 | 0.615385 |

At 1 fps the unchanged 0.3-second gap limit rejects consecutive samples; the
one-second stop also cannot meet the three-sample rule. At 10 fps some 45-degree
boundary cases lose small increments
under the unchanged movement threshold. Thresholds remain sampling-rate dependent;
these figures do not establish an optimal real-media rate. Unknown times are never
interpolated. No thresholds were tuned after this evaluation to hide the misses.
The three misses are abstentions: request a re-shoot through a future coverage agent,
not threshold loosening.

## Gate thresholds and status

Offline clean gate: 10/10 true candidates (required >=8/10), clean precision 1.000000 (required >=0.90); explicitly invalid witnessed outputs 0 (required 0).
Real perception gate: NOT_RUN. Before advancing, use a held-out permitted mock-panel
clip set with at least 10 clean labeled events, require >=8/10 correct candidates,
precision >=0.90 including predefined negative intervals, and zero witnessed promotion
during annotated occlusion, camera movement, identity breaks or timestamp gaps. Report
all numerators/denominators and review mask, part/ID and source-time correspondence.

## Consumed detector configuration

| Setting | Value |
|---|---:|
| min_rotation_deg | 45.0 |
| movement_delta_deg | 2.0 |
| stop_delta_deg | 1.5 |
| stop_centroid_px | 3.0 |
| min_stop_samples | 3 |
| min_stop_seconds | 0.4 |
| max_gap_seconds | 0.3 |
| max_axis_step_deg | 60.0 |
| max_event_seconds | 10.0 |
| min_pixels | 12 |
| min_elongation | 2.5 |
| min_area_ratio | 0.4 |
| area_history_samples | 5 |
| numeric_tolerance_deg | 1e-09 |

Reproduce without ffmpeg, network or model credentials:

```powershell
.venv/Scripts/python.exe -m scripts.run_risk_gate
```

## Labelling audit

Decision record for the operator, written in round 4. The numbers above are unchanged and
were not re-run with different labels. Both answers were checked against
`src/witness/synthetic/gen_masks.py` and by comparing generated tracks, not from the case names.

1. **SYNTHETIC_camera_jitter_94_stop, GT=0: deliberate negative, correctly outside the recall
   denominator.** The generator ignores the requested 94 degrees for this condition: the mask
   swings by a 12-degree sinusoid, `camera_stable` is false on every sample, and the recorded
   rotation is 0. No genuine rotation-and-stop exists in the data, so there is nothing to recall.
   The case proves one thing: camera shake with an honest unstable-camera flag does not produce a
   witnessed candidate (pinned by `test_bad_quality_never_silently_promotes_to_witnessed`). It does
   **not** prove that a real 94-degree event survives jitter. That scenario is untested, and the
   `94_stop` suffix in the name suggests otherwise.
2. **SYNTHETIC_unflagged_camera_rotation_94_stop, GT=0, FP=1: deliberate adversarial test of gate
   trust, not a mislabel.** Its sampled track is identical to `SYNTHETIC_clean_94_stop` in features,
   visibility, identity, camera flag and timestamps; only the label differs. The story is "the
   camera turned, the tool did not", with a wrong stable-camera flag supplied. No estimator that
   consumes these inputs can separate the two, so the false positive is guaranteed by construction.
   Relabelling it as a true positive would hide the limitation this case exists to show
   (pinned by `test_unflagged_camera_rotation_is_a_measured_estimator_limitation`). The
   all-conditions precision of 10/11 therefore includes one unavoidable input-trust error; the
   clean-subset precision does not.

Outcome: keep both cases and both labels (D026). In a later round, consider renaming the jitter
case so it no longer carries `94_stop`, and adding a separate positive case with real rotation
under flagged jitter, so that the recall denominator measures that scenario explicitly.
