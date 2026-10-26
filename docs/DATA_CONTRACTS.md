# Data contracts — offline v0.1 and future boundaries

These are project contracts, not a claim of verified live integration. Ingest remains
offline. A separate budget-gated single-image probe is implemented but PENDING;
video transport and procedure extraction remain unverified. Synthetic motion
candidates are produced only by the offline estimator experiment. Round 3 adds a
zero-model-call procedure/audit/report vertical slice over persisted local artifacts.

## Implemented ingest artifacts

Every run creates a fresh UUID v4 session_id and created_at_utc in UTC ISO 8601 with
Z. Creation time is the ingest time, not a claim about when the video was recorded.
data_origin is an explicit user declaration: real or synthetic. cached_real is
reserved for later imported cached results; the ingest CLI does not claim a cache.

session.json stores schema_version, pipeline_version, source_filename (basename,
local only), source_size_bytes, source_sha256, video metadata, sample_count, empty
model_versions and model_integration_status/observations_status = NOT_RUN.

video metadata preserves stream index, codec, dimensions, rational time_base,
average/nominal rate metadata, declared duration, decoded count, timeline origin,
first-to-last timestamp span and the ffprobe version. Rates are metadata, not used
to manufacture timestamps. timeline_span_s excludes the final frame duration;
declared_duration_s may differ and is retained separately.

timeline.json contains each original_frame_index, raw integer pts or null,
best_effort_timestamp or null, media_time_s or null, timestamp_source and flags.
original_frame_index means zero-based ffprobe decoded presentation order within
the first selected video stream; it is not a packet index or a provider index.
Time is (timestamp_ticks - first usable timestamp_ticks) * time_base. Original PTS
is preferred. A best-effort fallback is flagged missing_original_pts. If both are
missing, time stays null. No FPS-derived fallback is invented. Duplicate/backward
timestamps reject the input. A gap over 1.5 nominal frame intervals is a
timestamp_gap_candidate; it may reflect variable frame rate, not a proven lost frame.

samples.json records sample_index separately from original_frame_index, raw pts,
requested_time_s, actual media_time_s and flags. It selects the first eligible frame
at/after each candidate grid point, never duplicates a source frame, skips missing
timestamps, flags delays and does not interpolate. It does not extract images,
transcode video, configure SAM FPS or claim that provider frame N maps to sample N.

config.json contains effective consumed configuration and experimental sampling
status. The initial manifest contains source/config/artifact SHA-256, versions,
relative artifact paths, creation time, provenance and null procedure/model/parent
and trust-anchor/signature fields. The source is not copied or deleted. Local
filenames can be personal; generated sessions stay outside version control.

Project canonical JSON v1 is UTF-8, sorted keys, compact separators, ensure_ascii
false, finite JSON numbers only, no newline. Hash the exact saved bytes. The
manifest has no self hash; manifest.sha256 is a separate local digest reference.
Changing a complete record and these hashes remains possible without an external
trusted anchor. A write failure may leave a partial session directory; only a
completed manifest plus matching artifacts describes a completed ingest.

## Implemented geometry and continuity

MaskFeatures exposes area_px, centroid_xy, axis_deg_mod180, elongation, shape_valid
and quality_flags in the mask's own raster coordinates, with x rightward and y
downward. Pixel coordinates refer to pixel centers at integer indices. Binary 2D
masks only; nonbinary/NaN/wrong dimensions reject. Missing/empty masks, too few
pixels, ambiguous axes and frame-boundary contact do not pass the shape gate.
Thresholds (12 pixels, elongation 2.5) are experimental, not validated tool models.

PairQuality exposes usable_for_axis_change, delta_axis_deg and flags. Missing
visibility or identity confirmation, unusable masks, occlusion/exit, area loss,
nonincreasing times, timestamp flags or a configured maximum gap prevent use.
Shortest modulo-180 difference handles PCA eigenvector sign reversal. A 90-degree
tie stays ambiguous. Even a passing pair relies on a less-than-90-degree continuity
assumption, not proved by two axes. This API has no observed-action label.

## Provider-independent adapter

SegmentationInput holds UUID, local source, prompt, source frame references and
data origin. MaskObservation separates provider frame/object/response references
from optional source frame, PTS, media seconds and sample index, retaining quality
flags. Its normalized mask would require verified full-source-resolution mapping;
no such mapping is implemented. SamAdapter is a Protocol only, never a fake client.

## Offline procedure, audit, and report contracts

`procedure.json` is the response shape required from a future procedure-extraction
call. It contains `procedure_id` (nonempty string), `rev` (nonempty string), and a
nonempty `steps` array. Each step has exactly `step_id` (nonempty string), `order`
(unique positive integer), `action`, `part_id`, `tool`, and `verbatim` (all nonempty
strings). This first audit slice requires unique part IDs because it cannot yet
disambiguate repeated instances. The checked-in mock-panel fixture has a local
`_fixture_header` that labels it operator-authored and not model output; it is not a
claim of provider output. A future provider response must use the documented
procedure fields and must not inherit the fixture's authorship claim.

`events.json` is an optional session-local input for this offline report. It is either
an array or `{ "events": [...] }`. Every event has `event_id`, `part_id`, unique
positive `observed_order`, and `status`; optional `evidence_id`, `evidence_path`, and
`timestamp_s` remain local references. Only `witnessed` and `corroborated` events are
qualified for coverage, ordering, and undocumented-part findings. An absent
`events.json` is an empty event list; it never triggers a model call.

`findings.json` contains `{ "schema_version": "0.1", "findings": [...] }`. Every
finding has `finding_id`, `kind`, `severity`, `part_id`, `message`, and nullable
`step_id`, `event_id`, and `evidence_id`. `coverage` emits a high-severity `skipped`
review finding for each procedure part with no qualified event. In this tightly scoped
offline audit, `skipped` means a review priority rather than proof of physical
omission; it carries no evidence id and must not be presented as assembly correctness.
`undocumented` is medium severity for a qualified part absent from the procedure.
`ordering` selects one deterministic minimum review set outside a longest increasing
subsequence. When several LIS solutions exist, the selected set is a review aid, not
a claim that any individual event is certainly wrong.

The offline report writes self-contained `report.html`, an `evidence/` directory,
`findings.json`, `manifest.json`, and `manifest.sha256`. Evidence stills, when present,
must be explicit session-local PNG, JPEG, or WebP files; all other findings render a
clearly labelled non-evidence placeholder. The report's measurement statement
explicitly excludes torque values, tightening quality, correct assembly, transferred
force, and flight readiness. It makes no model call.

The report `manifest.json` has `manifest_kind` `offline_audit_report`, a canonical
`record_hash` equal to SHA-256 of canonical JSON `{session, events, findings}`, and a
`report_hash` equal to SHA-256 of the ASCII `record_hash` followed by exact
`report.html` bytes. It lists output artifact hashes and PDF status. Its external
`manifest.sha256` hashes exact manifest bytes. This chain is local integrity evidence,
not signing, a trust anchor, or a legal electronic signature. Existing ingest
manifests stay unchanged.

PDF generation uses optional local WeasyPrint only when already available. A missing
or failed renderer writes `report.pdf.blocked.txt` and retains HTML as the named
fallback. No PDF dependency is imported at module import time or required for tests.

## Future procedure/audit/evidence requirements

A future procedure step needs source page/quote and human-review status in addition
to the current contract. Match by action, part, instance and time; repeated parts
remain distinct. Ambiguous matches stay unresolved. Future finding kinds include
matched_observation, missing_evidence, uncertain_evidence, order_discrepancy,
undocumented_observation and nonobservable_requirement. Carry step indices with
filtered event sequences. Equal order positions or multiple valid LIS solutions must
not identify one arbitrary step as certainly wrong.

Future events require source/time ranges, track/part assignment method, quality,
evidence references and algorithm version. observed means only a narrow visual
motion claim; uncertain evidence cannot be upgraded silently. Crop/resize/raster
coordinate transformations and provider frame-to-source mapping must be explicit.

A follow-up clip receives a new session/hash. Any future relation must be
follow_up_observation with original/supplement session IDs and submission UTC time;
it never overwrites or retroactively upgrades the earlier occurrence/order finding.

## Round 2 additions

sampling.json is an additive artifact with candidate_fps, the same sample rows as
legacy samples.json, and unknown_time_original_frame_indices. Legacy session,
timeline and samples fields remain intact. sampling.py owns the implementation;
timeline.py only re-exports it. map_sample_indices preserves null PTS/time for an
explicitly selected unknown-time frame. Grid planning skips unknown times and
records their source indices without interpolation.

ParsedMask retains provider frame/object ordinals, repeated source dimensions,
inclusive source-pixel box, optional confidences and the decoded mask in its own
raster coordinates. It does not become a source_resolution_mask or acquire a source
PTS automatically. The supported line subset rejects unknown extensions; the full
native parser's tolerant extension/stream-lane behavior is outside this wrapper.

decode_mask accepts a height,width,complete-encoded-payload tuple. Structural
preflight is bounded before raster allocation. It delegates arithmetic decoding to
the pinned public codec, checks the final byte count, and returns uint8 0/1. Typed
errors distinguish unknown marker, malformed/truncated length, invalid alphabet,
dimensions and failed decoding. The test-only reference encoder is never imported
by production code.

TrackSample carries session/local-track identity, source frame, nullable time,
geometry, visibility, explicit camera/identity gates, provenance and flags.
MotionEvent carries stable per-call ID, source/session/track bounds, accumulated
image-plane axis change, flags and data origin. Outcomes witnessed, inferred and
unwitnessed-tail are estimator visual-candidate states. Only a qualified motion plus
stationary tail becomes witnessed; it does not certify a physical operation. Session,
identity, occlusion, bad camera or timestamp breaks close/reset the candidate. No
later frame upgrades a prior uncertain tail. Thresholds are consumed from the
single defaults file and recorded in the risk-gate report.

The spend ledger records request/session references, source hash, UTC reservation,
approved/remaining cap, provenance, status, reserved USD and nullable calculated
actual USD. Unknown outcomes remain reserved. Session spend.json is an append-style
sidecar mirrored from the shared ledger; it is not part of an earlier ingest
manifest or an externally authenticated financial record.
