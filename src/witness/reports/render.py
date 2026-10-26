"""Render deterministic audit results as a self-contained HTML report."""

import base64
import html
import json
from dataclasses import dataclass
from typing import Mapping

from witness.audit.models import Finding, assert_findings_invariants, finding_dict


@dataclass(frozen=True)
class EvidenceImage:
    """An evidence still already read and approved by the CLI boundary."""

    evidence_id: str
    media_type: str
    content: bytes
    relative_path: str


def _placeholder_image() -> str:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="480" height="140">'
        '<rect width="100%" height="100%" fill="#f3f4f6"/>'
        '<text x="24" y="76" fill="#374151" font-family="sans-serif" '
        'font-size="20">No evidence still available</text></svg>'
    )
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def _image_uri(image: EvidenceImage | None) -> str:
    if image is None:
        return _placeholder_image()
    encoded = base64.b64encode(image.content).decode("ascii")
    return f"data:{image.media_type};base64,{encoded}"


def render_report(
    session: Mapping[str, object],
    findings: tuple[Finding, ...],
    *,
    record_hash: str,
    evidence: Mapping[str, EvidenceImage],
) -> bytes:
    """Return deterministic inline-CSS HTML; no network, framework, or wall clock."""
    assert_findings_invariants(findings)
    video = session.get("video") if isinstance(session.get("video"), Mapping) else {}
    config = session.get("config") if isinstance(session.get("config"), Mapping) else {}
    media = config.get("media") if isinstance(config.get("media"), Mapping) else {}
    provenance = {
        "source_sha256": session.get("source_sha256", "unknown"),
        "created_at_utc": session.get("created_at_utc", "unknown"),
        "frame_count": video.get("decoded_frame_count", "unknown"),
        "sampling_fps": media.get("candidate_sample_fps", "unknown"),
    }
    rows = (
        "".join(
            "<tr>"
            f"<td>{html.escape(finding.finding_id)}</td>"
            f"<td>{html.escape(finding.kind)}</td>"
            f"<td>{html.escape(finding.severity)}</td>"
            f"<td>{html.escape(finding.part_id)}</td>"
            f"<td>{html.escape(finding.message)}</td>"
            "</tr>"
            for finding in findings
        )
        or '<tr><td colspan="5">No deterministic findings.</td></tr>'
    )
    stills = (
        "".join(
            "<figure>"
            f'<img alt="{html.escape(finding.finding_id)} evidence still" '
            f'src="{_image_uri(evidence.get(finding.evidence_id or ""))}">'
            f"<figcaption>{html.escape(finding.finding_id)} — "
            f"{html.escape(finding.evidence_id or 'No evidence id')}</figcaption>"
            "</figure>"
            for finding in findings
        )
        or "<p>No findings require still review.</p>"
    )
    manifest_block = {
        "record_hash": record_hash,
        "findings": [finding_dict(finding) for finding in findings],
        "report_hash_location": "manifest.json",
        "integrity_limitation": "Local hashes are not signatures or legal electronic signatures.",
    }
    provenance_text = html.escape(json.dumps(provenance, sort_keys=True, indent=2))
    manifest_text = html.escape(json.dumps(manifest_block, sort_keys=True, indent=2))
    document = "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            '<head><meta charset="utf-8"><title>WITNESS offline audit report</title><style>',
            "body { font-family: Arial, sans-serif; color: #172033; margin: 32px; }",
            "h1, h2 { color: #13294b; }",
            "table { border-collapse: collapse; width: 100%; }",
            "th, td { border: 1px solid #cbd5e1; padding: 8px; text-align: left; }",
            "th, td { vertical-align: top; }",
            "th { background: #e8eef7; }",
            "figure { display: inline-block; width: 300px; margin: 12px; }",
            "img { max-width: 100%; border: 1px solid #94a3b8; }",
            "pre { white-space: pre-wrap; word-break: break-word; }",
            ".high { color: #991b1b; font-weight: bold; }",
            ".medium { color: #92400e; font-weight: bold; }",
            "</style></head><body>",
            "<h1>WITNESS offline audit report</h1>",
            f"<h2>Provenance</h2><pre>{provenance_text}</pre>",
            "<h2>Measurement statement</h2><p>"
            "This report measures deterministic review findings from supplied visual-event "
            "records. "
            "It does not measure torque values, tightening quality, correct assembly, transferred "
            "force, or flight readiness.</p>",
            "<h2>Findings</h2><table><thead><tr><th>Id</th><th>Kind</th>"
            "<th>Severity</th><th>Part</th><th>Explanation</th></tr></thead>"
            f"<tbody>{rows}</tbody></table>",
            f"<h2>Per-finding evidence stills</h2>{stills}",
            f"<h2>Manifest block</h2><pre>{manifest_text}</pre>",
            "</body></html>",
        ]
    )
    return document.encode("utf-8")
