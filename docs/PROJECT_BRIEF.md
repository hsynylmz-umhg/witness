# Product brief

## User problem and product vision

CubeSat/model-satellite teams often keep assembly checklists separately from phone
photos and video. Reconstructing which visible operation relates to which part and
procedure step is slow. WITNESS aims to turn one permitted fixed-camera civil
assembly recording into a reviewable as-built observation record with timestamps,
source-linked evidence and explicit uncertainty. User interviews, market numbers
and firsthand experience remain unverified unless the user supplies evidence.

The historical end-to-end workflow is retained: set up the camera and part map,
record the session, ingest video, segment/track tools, calculate image-plane motion
candidates, associate them with procedure instances, audit order/evidence coverage,
review supporting clips and export a record. The eventual review flow should make
it easy to return from each finding to the original media. Processing speed and
cost targets require measurement; historical estimates are not current results.

## Intended architecture

Media and provider adapters normalize observations. Pure Python geometry, quality,
matching and ordering functions operate independently of the network. Evidence
artifacts and versioned manifests link the outputs to source video, configuration,
model and procedure revisions. Reports distinguish observed visual motion,
uncertainty, missing evidence and order discrepancies. A language model may extract
procedure language or explain findings with sources; it cannot change audit facts.

## MVP acceptance, beyond this delivery

- The user supplies a fixed-camera video and numbered part/ROI map.
- The initial procedure may be human-reviewed JSON; PDF extraction follows later.
- Visible tool movement, a target part and a time window can be associated with
  supporting masks/stills and replay. Unknown movement/part identity stays unresolved.
- Matching is by procedure action, part and instance; repeated use of a part must
  not collapse multiple steps into one.
- Reports show evidence coverage separately from independent ground truth about
  deliberate omissions. Later observations cannot prove earlier occurrence/order.

PCA estimates a mask's long axis modulo 180 degrees. It does not locate the socket
or measure torque. Motion outside the image plane, perspective, occlusion and camera
motion affect the estimate. Shape validity alone does not establish mask correctness,
identity, visibility, contact or an observed action.

## Current scope

The current round extends the offline perception-risk spike: local ingest and
source-preserving sampling, verified mask decoding/strict output subset, a pure
motion/stop estimator with a measured synthetic gate, and a default-deny spend gate.
The earlier parser-blocker inference was corrected; the diagnostic had duplicated
an encoding marker. The bounded image probe exists but was not run live. No real
hardware video is available, and video-provider timing/perception remain unverified.
This does not start procedure extraction, ordering audit, reports or UI.

Priority remains real short-video masks -> timing/quality -> motion candidates ->
source evidence, followed by procedure matching, ordering, JSON/HTML review and
measured evaluation. UI, PDF, voice, generated cards, alternative providers and a
coverage planner remain later optional work. None is needed to claim this first
slice complete. Flight certification, torque measurement, guaranteed assembly
correctness, legal signatures, moving/multiple cameras, live streaming, accounts,
ERP integration, fine-tuning and autonomous physical control are outside the MVP.
