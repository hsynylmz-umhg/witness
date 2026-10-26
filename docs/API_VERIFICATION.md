# API verification record

Round 1 documentation checks: 26 October 2026, 14:15–14:29 UTC. Round 2 recheck
started 2026-10-26T15:29:48Z; verification snapshot recorded 2026-10-26T16:11:58Z. Sources were fetched read-only; installed 0.1.0 codec/parser behavior
was exercised offline. No authenticated SAM request or media upload occurred.

Statuses: DOC_VERIFIED = official documentation, LOCAL_VERIFIED = installed package
or offline contract behavior, LIVE_VERIFIED = a real authorized provider call,
BLOCKED/PENDING = unresolved or deliberately not run, DEFERRED = outside this round.
No result here is LIVE_VERIFIED.

| Requirement | Status | Evidence/type and actual result | Source | Checked UTC, 2026-10-26 |
|---|---|---|---|---|
| Account and credits | BLOCKED | MODEL_API_KEY, META_API_KEY and WITNESS_MAX_SPEND_USD absent from this process. No balance/entitlement query. Config cap 0.0 and credits_confirmed false. | [Quickstart](https://dev.meta.ai/docs/quickstart) | Round 2 snapshot |
| Model/base URL/auth | DOC_VERIFIED | sam-3.1, https://api.meta.ai/v1, Bearer MODEL_API_KEY. Account access unverified. | [SAM overview](https://dev.meta.ai/docs/sam/overview) | Round 1, retained |
| SDK/package | LOCAL_VERIFIED, partial | meta-sam-parser 0.1.0 is pinned and now a runtime codec dependency. No OpenAI SDK is required by the standard-library image probe. No live compatibility claim. | [Client libraries](https://dev.meta.ai/docs/sam/client-libraries), [Python API](https://github.com/meta-models/meta-sam/blob/main/python/README.md) | Round 2 snapshot |
| Image/video request and upload | DOC_VERIFIED | Responses content uses input_text plus input_image/input_video; image data URLs are documented. Upload uses files with purpose=user_data and file_id. Nonstreaming image probe implemented but remains PENDING. No video transport was added. | [Segmentation guide](https://dev.meta.ai/docs/sam/segmenting) | Round 2 snapshot |
| Formats/request limits | DOC_VERIFIED, partial | MP4/MOV; H.264/H.265/MPEG-4; 15,000 frames/request and up to 16 objects/frame. Upload byte caps/account exceptions remain BLOCKED. Project resource caps are local policy. | [Limits](https://dev.meta.ai/docs/sam/segmenting#limits) | Round 1, retained |
| Line/object/frame contract | LOCAL_VERIFIED subset | Explicit sparse/nonascending frame ordinals and sparse object IDs retained. Source-pixel inclusive boxes and each record's source dimensions preserved. Strict parser rejects unknown extensions rather than dropping them silently. | [Output grammar](https://dev.meta.ai/docs/sam/reading-segmentation) | Round 2 snapshot |
| Mask codec and marker | LOCAL_VERIFIED | Keep the encoding marker exactly once. Decode height then width into the mask's own raster. Both documented !/one_bit and ~/lossless markers use the pinned public decoder; no fallback. Packed-envelope and dimension checks precede raster allocation. | [Normative protocol](https://github.com/meta-models/meta-sam/blob/main/protocol/sam3.md) | Round 2 snapshot |
| Source-video frame to PTS | BLOCKED | Offline source mapping is implemented, but provider decode/resampling/rotation/edit behavior and its correspondence to original PTS are not verified. No ordinal-to-time assumption added. | [Frame semantics](https://dev.meta.ai/docs/sam/reading-segmentation) | Round 2 snapshot |
| Pricing / team limits | DOC_VERIFIED | Image $2.50/1,000; video $0.20/1,000 with minimum 50 frames per positive video request. SAM 3,000 RPM/team, no TPM. Config records these rates; actual account quota/invoice remains unverified. | [Official pricing](https://dev.meta.ai/docs/pricing-rate-limits) | Round 2 snapshot |
| Live image probe | PENDING | Budget/credit/key gates not enabled; refusal checked, no request sent. Transport, reservations and calculated-cost recording tested with SYNTHETIC injected transport only. | [Request guide](https://dev.meta.ai/docs/sam/segmenting), [response schema](https://dev.meta.ai/docs/api-reference/responses/schemas) | Round 2 snapshot |
| Procedure/PDF, voice, image cards, alternative backend | DEFERRED | Not implemented or verified this round. | [Portal](https://dev.meta.ai/docs/overview) | Round 2 snapshot |

## Corrected Round 1 diagnostic

Round 1 reported a parser incompatibility. That inference was wrong: its diagnostic
prepended ! to a complete published payload that already included the marker.
The corrected unchanged vector produces 25 decoded pixels, one parsed mask and no
diagnostics in the same 0.1.0 package. No site-packages patch or provider-wire
workaround was necessary. The script is diagnostic only: it prints compatibility
status, never makes a request and returns zero even when it reports a blocker.

```powershell
.venv/Scripts/python.exe scripts/check_sam_contract.py
```

Actual result: OFFLINE_CONTRACT_PASS; direct_decoder_pixels=25,
parsed_mask_count=1, diagnostic_codes=[], live_api_test=NOT_RUN.

The production wrapper calls the verified public decoder, not private package APIs.
Its test-only encoder uses the locked internal reference encoder to test 200 random
mask round trips. Conformance fixtures cover documented rules, typed errors and an
attributed compact lossless vector from the official library. They are SYNTHETIC;
none is a WITNESS real response. No private or unsanitized real response was retained.

The requested fixed symbol-bit-length equation cannot describe the verified
arithmetic-coded format. D017 records the deviation: validate actual packed prefix,
alphabet, envelope length and bounded dimensions first, then require exactly H*W
binary bytes after native decoding/finalization. The wrapper's local allocation cap
is 16,777,216 pixels, not a provider limit. Unknown markers and truncated data raise
MaskDecodeError; malformed line records raise SamParseError.

## Spending and actual results

The offline estimate for two images and one input video frame is $0.005 + $0.010 =
$0.015; the frame floor is applied once because --frames denotes one video request.
Zero frames means no video request and no floor. This estimate is not spend.

A live probe requires operator-confirmed available credits, positive environment and
config caps, --allow-paid, a local key and a printed estimate strictly below the
remaining shared budget. It sends at most one image request, no retries/redirects,
and uses a configured timeout. Reservations are serialized in a local shared ledger
and copied to the session's spend.json. Failed/unknown outcomes keep a reservation
and actual_usd=null. Completed image cost is calculated from the published rate;
it is not a verified invoice. Existing ingest manifests are not rewritten to add
this later sidecar. Refusal messages are listed in docs/TOOLING.md.

Current authenticated SAM calls: 0. Uploads: 0. Actual SAM spend: USD 0.00. Real
image/video integration, provider frame/PTS mapping, credits and account limits
remain unverified. Do not treat offline conformance or synthetic estimator results
as those checks.
