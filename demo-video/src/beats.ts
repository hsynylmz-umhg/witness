// The eight beats of the demo film (round 19). docs/DEMO_SCRIPT.md is generated from this file by
// `npm run script-doc` and is never read by the render. The spoken text is the recorded narration in
// public/voiceover/beat-NN.mp3, word for word.
//
// The time base is derived here at module load. Each slot is its clip plus a 2.000 s breath, rounded
// up to a frame, except beats 4 and 6, whose holds are the argument and keep their approved slots.
// Narration times inside a beat (cues and landings) are seconds into the clip, measured with ffmpeg
// silencedetect (noise -38 dB, 0.12 s); a figure inside a phrase is placed by its syllable position.
// Each beat's first cue starts on the beat's first frame, so the band is never empty under the voice.
// They become beat-relative frames through framesOf, and global frames through at().

export const FPS = 30;
export const TOTAL_FRAMES = 4914;
export const BOLTS_S = 8;
// ffprobe durations of public/voiceover/beat-01..08.mp3 (round 19).
export const CLIP_S = [12.968345, 18.652744, 17.020227, 12.968345, 29.082993, 19.353832, 21.536508, 6.013968];
export const BREATH_S = 2;
const HOLDS: Record<number, number> = { 4: 642, 6: 750 };
export const SLOTS = CLIP_S.map((clip, i) => HOLDS[i + 1] || Math.ceil((clip + BREATH_S) * FPS));
// Continuity: a beat's first object arrives LEAD frames before its boundary; its last object stays
// LINGER frames after the next boundary.
export const LEAD = 18;
export const LINGER = 60;

export type Cue = { at: number; text: string; onScreen?: boolean };
export type Beat = {
  number: number;
  frames: number;
  spoken: string;
  cues: Cue[];
  at: Record<string, number>;
  text: Record<string, string>;
  onScreen: string;
  sources: string[];
};

export const CAVEAT =
  "The identity rule was calibrated on six frames from these same two clips, so the agreement with the key is a demonstration on known footage, not independent validation.";

export const BEATS: Beat[] = [
  {
    number: 1,
    frames: SLOTS[0],
    spoken:
      "A procedure says: mark ten boxes, in order. Did it happen, and can you prove what you saw? witness answers with findings, and a finding either carries an evidence id or it does not exist.",
    cues: [
      { at: 0, text: "A procedure says: mark ten boxes, in order." },
      { at: 3.99, text: "Did it happen, and can you prove what you saw?", onScreen: true },
      { at: 6.78, text: "witness answers with findings, and a finding either carries an evidence id or it does not exist." },
    ],
    at: { mark: 0.2, line: 0.4, rule: 0.9, bolts: 4.6 },
    text: {
      line: "Did it happen, and can you prove what you saw?",
      caption: "demo_bolts_v1_clean.mp4, 0–8 s",
      note: "intended use case — not a measurement",
    },
    onScreen:
      "Near-black ground; the small mono mark draws on above the question, set alone, with the spine drawn beneath it. From 4.6 s to 12.6 s the bolt B-roll plays its full 8 s in place, captioned as an intended use case, not a measurement. The log's parts and its first still arrive before the boundary.",
    sources: ["`docs/AGENT_GUIDE.md`", "`data/raw/demo_bolts_v1_clean.mp4` (0–8 s)"],
  },
  {
    number: 2,
    frames: SLOTS[1],
    spoken:
      "The input is an event log: which part, in what order, with which still. The audit is deterministic. Coverage, ordering and undocumented parts. Here, one box has no witnessed event, so the report asks for human review instead of calling it done.",
    cues: [
      { at: 0, text: "The input is an event log: which part, in what order, with which still." },
      { at: 6.44, text: "The audit is deterministic. Coverage, ordering and undocumented parts." },
      { at: 12.35, text: "Here, one box has no witnessed event, so the report asks for human review instead of calling it done." },
    ],
    at: { ids: 0.6, events: 2.1, eventsEnd: 5.41, still: 4.18, coverage: 8.66, ordering: 9.48, undocumented: 10.31, gap: 12.99, finding: 15.1 },
    text: {
      rowPart: "part",
      rowOrder: "order seen",
      rowStill: "still",
      coverage: "coverage",
      ordering: "ordering",
      undocumented: "undocumented",
      gap: "no witnessed event",
      source: "artifacts/real_skipped_05",
    },
    onScreen:
      "The question settles two type steps down and heads the skipped clip's event log, drawn on the spine as ten procedure parts that fill in the order they were seen, each with its still id; the first still; the three checks; the empty part outlined; the report's two findings. Nothing on screen implies a model.",
    sources: [
      "`artifacts/real_skipped_05/findings.json`",
      "the event log of session `58bb85e4-77eb-4297-882a-aac467a05bca`",
      "`data/procedures/panel_boxes_v1.json`",
    ],
  },
  {
    number: 3,
    frames: SLOTS[2],
    spoken:
      "Every report is hash-linked: the record hash, then the HTML bytes, then the manifest. Anyone can recompute it from the output. These are local hashes, not a signature. Without an external trust anchor they do not stop someone rewriting files and manifest together.",
    cues: [
      { at: 0, text: "Every report is hash-linked: the record hash, then the HTML bytes, then the manifest." },
      { at: 6.17, text: "Anyone can recompute it from the output." },
      { at: 8.62, text: "These are local hashes, not a signature. Without an external trust anchor they do not stop someone rewriting files and manifest together." },
    ],
    at: { record: 2.11, report: 3.25, manifest: 4.93, recompute: 6.17, limit: 8.62, anchor: 11.64 },
    text: {
      record: "record hash",
      crop: "real_skipped_05 · report.html · cropped",
      report: "report hash",
      manifest: "manifest.sha256",
      recompute: "report_hash = ",
      limit: "local hashes, not a signature",
      anchor: "without an external trust anchor, files and manifest can be rewritten together",
      source: "artifacts/real_skipped_05/manifest.json",
    },
    onScreen:
      "The still's frame now holds the same run's report.html, cropped to its title and findings and captioned as a crop. Three points on the spine carry the record hash, the report hash and manifest.sha256 with their full values; two drawn links; the recompute rule; the limit, local hashes and no trust anchor.",
    sources: ["`artifacts/real_skipped_05/manifest.json`", "`artifacts/real_skipped_05/manifest.sha256`", "`docs/RULES.md`"],
  },
  {
    number: 4,
    frames: SLOTS[3],
    spoken:
      "The audit logic is gated on 25 cases, and all 25 are synthetic: 10 true positives, 1 false positive, 3 false negatives. That tests the rules, not the real world.",
    cues: [
      { at: 0, text: "The audit logic is gated on 25 cases, and all 25 are synthetic: 10 true positives, 1 false positive, 3 false negatives." },
      { at: 10.26, text: "That tests the rules, not the real world." },
    ],
    at: { cases: 1.91, tp: 5.65, fp: 7.09, fn: 8.47 },
    text: {
      cases: "25",
      casesLabel: "cases, all synthetic",
      tp: "10",
      tpLabel: "true positives",
      fp: "1",
      fpLabel: "false positive",
      fn: "3",
      fnLabel: "false negatives",
      caveat: "All 25 cases are synthetic: this tests the rules, not the real world.",
      source: "docs/RISK_GATE.md",
    },
    onScreen:
      "The spine becomes a baseline; 25, 10, 1 and 3 land on it in spoken order with the caveat, then nothing moves until the boundary.",
    sources: ["`docs/RISK_GATE.md`"],
  },
  {
    number: 5,
    frames: SLOTS[4],
    spoken:
      "Then we tried producing the event log from real footage, with deterministic geometry and no model. This is the operator's own scene: one sheet, one angle, one lighting condition. On the clean clip the extractor found 9 of 10 marks in the right order and missed box 9 at 1.91 times its baseline. On the skipped clip it recovered the three-four swap but flagged blank box 6, because the sheet slid about 25 pixels under fixed masks.",
    cues: [
      { at: 0, text: "Then we tried producing the event log from real footage, with deterministic geometry and no model." },
      { at: 6.28, text: "This is the operator's own scene: one sheet, one angle, one lighting condition." },
      { at: 11.57, text: "On the clean clip the extractor found 9 of 10 marks in the right order and missed box 9 at 1.91 times its baseline." },
      { at: 19.4, text: "On the skipped clip it recovered the three-four swap but flagged blank box 6, because the sheet slid about 25 pixels under fixed masks." },
    ],
    at: { divider: 11.57, scope: 3.4, scene: 8.28, clean: 11.57, found: 13.56, missed: 15.6, ratio: 16.95, skipped: 19.4, swap: 20.46, blank: 22.59, slid: 26.41, outline: 27.65 },
    text: {
      scope: "deterministic geometry, no model",
      scene: "one sheet · one angle · one lighting condition",
      clean: "clean clip",
      found: "9 / 10",
      foundLabel: "marks found, in the right order",
      missed: "box 9 missed",
      ratio: "1.91× its baseline",
      skipped: "skipped clip",
      swap: "3–4 swap recovered",
      blank: "blank box 6 flagged",
      slid: "the sheet slid about 25 pixels under fixed masks",
      source: "docs/REAL_MEDIA.md · Round 7 measurement",
    },
    onScreen:
      "The four figures stay two seconds, then the stated figures of the geometry-only run arrive, clean clip and skipped clip side by side under the spine as a section rule. No picture and no model output; the cause line is outlined.",
    sources: ["`docs/REAL_MEDIA.md` (Round 7 measurement)"],
  },
  {
    number: 6,
    frames: SLOTS[5],
    spoken:
      "So we made the masks follow the sheet, and required a clear correlation peak. On both clips the peak fell short, 1.97 and 1.93 against a required 2.0, and the extractor stopped instead of guessing. We did not lower the bar. Perception is frozen, and this disagreement with the key is the measured result.",
    cues: [
      { at: 0, text: "So we made the masks follow the sheet, and required a clear correlation peak." },
      { at: 4.52, text: "On both clips the peak fell short, 1.97 and 1.93 against a required 2.0, and the extractor stopped instead of guessing." },
      { at: 13.07, text: "We did not lower the bar. Perception is frozen, and this disagreement with the key is the measured result." },
    ],
    at: { title: 2.7, threshold: 2.28, bars: 4.52, clean: 6.65, skipped: 7.77, required: 9.44, stopped: 10.34 },
    text: {
      title: "correlation peak ratio",
      clean: "clean",
      skipped: "skipped",
      cleanValue: "1.97",
      skippedValue: "1.93",
      required: "2.0 required",
      zero: "0",
      cleanStop: "stopped at frame 1558",
      skippedStop: "stopped at frame 1733",
      source: "docs/REAL_MEDIA.md · Round 8 measurement",
    },
    onScreen:
      "The outline opens as a mask into the chart frame; the spine is the axis. Tracks mark the unit run from 0 to the threshold, the threshold is drawn at 2.0, two bars stop at 1.97 and 1.93 with the frames where extraction stopped. Then the frame freezes.",
    sources: ["`docs/REAL_MEDIA.md` (Round 8 measurement)", "`docs/DECISIONS.md` (D030, D031)"],
  },
  {
    number: 7,
    frames: SLOTS[6],
    spoken:
      "Then a Meta segmentation model, sam-3.1, proposed the boxes and geometry named them: 78 anchor calls, 0.195 dollars, and both clips now agree with the key. The naming rule was calibrated on six frames from these same clips, so this is a demonstration, not independent validation.",
    cues: [
      { at: 0, text: "Then a Meta segmentation model, sam-3.1, proposed the boxes and geometry named them:" },
      { at: 7.44, text: "78 anchor calls, 0.195 dollars, and both clips now agree with the key." },
      { at: 14.07, text: "The naming rule was calibrated on six frames from these same clips, so this is a demonstration, not independent validation." },
    ],
    at: { meta: 2.6, model: 2.42, skipped: 5.83, anchors: 7.44, cost: 9.28, agree: 11.74 },
    text: {
      meta: "Meta segmentation model",
      model: "sam-3.1",
      anchors: "78 anchors",
      anchorsLabel: "49 clean + 29 skipped, one model call each",
      cost: "USD 0.1950",
      agree: "both clips agree with the key",
      clean: "model_clean_anchor48.png",
      skipped: "model_skipped_anchor28.png",
      source: "docs/REAL_MEDIA.md · Model-produced events",
    },
    onScreen:
      "The chart's frame becomes the overlay crop: the model overlays of both clips at the same crop, clean then skipped, uncovered by a moving edge. Above the spine: sam-3.1, 78 anchors at one call each, USD 0.1950, agreement with the key. The calibration limit types on in the lower-left column and stays to the end.",
    sources: [
      "`artifacts/overlays/model_clean_anchor48.png`",
      "`artifacts/overlays/model_skipped_anchor28.png`",
      "`docs/REAL_MEDIA.md` (Model-produced events)",
      "`docs/STATUS.md` (independence limit)",
    ],
  },
  {
    number: 8,
    frames: SLOTS[7],
    spoken: "witness: an event log in, evidence-linked findings out, and every miss on the record.",
    cues: [{ at: 0, text: "witness: an event log in, evidence-linked findings out, and every miss on the record.", onScreen: true }],
    at: { claim: 0.6, mark: 2.6, rule: 2.6, ruleEnd: 7.5 },
    text: { claim: "witness: an event log in, evidence-linked findings out, and every miss on the record." },
    onScreen:
      "The claim above the spine, which becomes the closing rule; the overlay stays two seconds; then the stroke-only gradient mark is drawn on with all five joints of one construction, and one slow rule draws beneath it. The calibration limit stays lower left.",
    sources: ["`docs/DECISIONS.md` (D030)", "`demo-video/public/brand/witness-logo.svg`"],
  },
];

export const framesOf = (seconds: number): number => Math.round(seconds * FPS);

export const startOf = (number: number): number =>
  BEATS.filter((beat) => beat.number < number).reduce((sum, beat) => sum + beat.frames, 0);

export const endOf = (number: number): number => startOf(number) + BEATS[number - 1].frames;

/** The global frame of a moment `seconds` into beat `number`. */
export const at = (number: number, seconds: number): number => startOf(number) + framesOf(seconds);
