"""Measure the synthetic estimator gate; run as python -m scripts.run_risk_gate."""

import hashlib
from collections import Counter
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from witness import __version__
from witness.config import load_settings
from witness.perception.events import detect_events
from witness.synthetic.gen_masks import generate_sequences, sampled_track


def measure(cases, fps, config):
    rows = []
    for case in cases:
        events = detect_events(sampled_track(case, fps), config)
        witnessed = sum(event.status == "witnessed" for event in events)
        detected = min(witnessed, int(case.ground_truth_event))
        rows.append(
            {
                "name": case.name,
                "condition": case.condition,
                "truth": int(case.ground_truth_event),
                "detected": detected,
                "missed": int(case.ground_truth_event) - detected,
                "false_positive": witnessed - detected,
                "clean": case.eligible_clean_case,
                "outcomes": Counter(event.status for event in events),
            }
        )
    return rows


def summary(rows):
    tp = sum(row["detected"] for row in rows)
    fp = sum(row["false_positive"] for row in rows)
    fn = sum(row["missed"] for row in rows)
    return tp, fp, fn, tp / (tp + fp) if tp + fp else None, tp / (tp + fn) if tp + fn else None


def number(value):
    return "undefined (0 denominator)" if value is None else f"{value:.6f}"


def main() -> int:
    settings = load_settings()
    cases = generate_sequences(settings)
    fps = settings.media.candidate_sample_fps
    rows = measure(cases, fps, settings.detection)
    tp, fp, fn, precision, recall = summary(rows)
    clean = summary([row for row in rows if row["clean"]])
    gated = [
        row
        for row in rows
        if row["condition"]
        in {
            "occlusion",
            "identity_switch",
            "camera_jitter",
            "timestamp_gap",
        }
    ]
    invalid_witnessed = sum(row["detected"] + row["false_positive"] for row in gated)
    root = Path(__file__).resolve().parents[1]
    config_hash = hashlib.sha256((root / "config/defaults.toml").read_bytes()).hexdigest()
    lines = [
        "# Synthetic perception risk gate",
        "",
        f"Measured UTC: {datetime.now(UTC).isoformat().replace('+00:00', 'Z')}",
        f"Pipeline {__version__}; algorithm rotation_stop_v1; configuration SHA-256 {config_hash}.",
        "",
        "## Meaning and limits",
        "",
        "All 25 cases are SYNTHETIC rasterized rectangles, with independent authored motion/stop",
        "labels and supplied camera/visibility/identity flags. Source rate is 25 fps. Repeats",
        "reuse a controlled generator; they are not independent real recordings. This validates",
        "the estimator and its gates, not real perception, SAM mask/ID quality, camera-stability",
        "estimation, 3D rotation, tightening or torque. No real video or API call was used.",
        "",
        f"Candidate sampling: {fps:g} fps. "
        "Ground truth is rotation >=45 degrees followed by a stop.",
        "Only witnessed visual candidates count as detections. Deliberately occluded, switched-ID",
        "and gapped positive cases remain in the recall denominator: withholding them is counted",
        "as a miss rather than hidden as success. The adversarial camera case supplies a wrong",
        "stable-camera flag; a false positive there exposes a limitation of trusting gate inputs.",
        "",
        "## Condition results",
        "",
        "| SYNTHETIC condition | Ground truth events | Detected (TP) | Missed (FN) | "
        "False positives | Outcomes |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        outcomes = ", ".join(f"{name}: {count}" for name, count in sorted(row["outcomes"].items()))
        lines.append(
            f"| {row['name']} | {row['truth']} | {row['detected']} | {row['missed']} | "
            f"{row['false_positive']} | {outcomes or 'none'} |"
        )
    lines.extend(
        [
            "",
            f"All conditions: TP={tp}, FP={fp}, FN={fn}; "
            f"precision {tp}/{tp + fp} = {number(precision)};",
            f"recall {tp}/{tp + fn} = {number(recall)}. "
            f"n={len(cases)} cases, {tp + fn} ground-truth events.",
            f"Clean subset: TP={clean[0]}, FP={clean[1]}, FN={clean[2]}; "
            f"precision {number(clean[3])}; "
            f"recall {number(clean[4])}.",
            "Qualified witnessed outputs in the four explicitly gated bad-quality cases: "
            f"{invalid_witnessed}.",
            "",
            "## Sampling comparison with unchanged thresholds",
            "",
            "| Candidate fps | TP | FP | FN | Precision | Recall |",
            "|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for candidate in (1, 5, 10):
        a, b, c, p, r = summary(measure(cases, candidate, settings.detection))
        lines.append(f"| {candidate} | {a} | {b} | {c} | {number(p)} | {number(r)} |")
    lines.extend(
        [
            "",
            "At 1 fps the unchanged 0.3-second gap limit rejects consecutive samples; the",
            "one-second stop also cannot meet the three-sample rule. At 10 fps some 45-degree",
            "boundary cases lose small increments",
            "under the unchanged movement threshold. Thresholds remain sampling-rate dependent;",
            "these figures do not establish an optimal real-media rate. Unknown times are never",
            "interpolated. No thresholds were tuned after this evaluation to hide the misses.",
            "The three misses are abstentions: request a re-shoot through a future coverage agent,",
            "not threshold loosening.",
            "",
            "## Gate thresholds and status",
            "",
            f"Offline clean gate: {clean[0]}/10 true candidates (required >=8/10), "
            "clean precision "
            f"{number(clean[3])} (required >=0.90); "
            "explicitly invalid witnessed outputs "
            f"{invalid_witnessed} (required 0).",
            "Real perception gate: NOT_RUN. Before advancing, use a held-out permitted mock-panel",
            "clip set with at least 10 clean labeled events, require >=8/10 correct candidates,",
            "precision >=0.90 including predefined negative intervals, "
            "and zero witnessed promotion",
            "during annotated occlusion, camera movement, identity breaks or timestamp gaps. "
            "Report",
            "all numerators/denominators and review mask, part/ID and source-time correspondence.",
            "",
            "## Consumed detector configuration",
            "",
            "| Setting | Value |",
            "|---|---:|",
        ]
    )
    lines.extend(f"| {key} | {value} |" for key, value in asdict(settings.detection).items())
    lines.extend(
        [
            "",
            "Reproduce without ffmpeg, network or model credentials:",
            "",
            "```powershell",
            ".venv/Scripts/python.exe -m scripts.run_risk_gate",
            "```",
            "",
        ]
    )
    target = root / "docs/RISK_GATE.md"
    text = "\n".join(lines)
    # The hand-written labelling audit (D026) is a decision record, so it survives regeneration.
    previous = target.read_text(encoding="utf-8") if target.exists() else ""
    marker = "\n## Labelling audit"
    if marker in previous:
        text += previous[previous.index(marker) :]
    target.write_text(text, encoding="utf-8", newline="\n")
    print("SYNTHETIC risk-gate summary")
    print("| Cases | TP | FP | FN | Precision | Recall | Real perception |")
    print("|---:|---:|---:|---:|---:|---:|---|")
    print(
        f"| {len(cases)} | {tp} | {fp} | {fn} | {number(precision)} | {number(recall)} | NOT_RUN |"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
