// The eight beats of the demo film, authored here since round 18 (docs/DEMO_SCRIPT.md is generated
// from this file by `npm run script-doc` and is never read by the render). The slots are frozen and
// the spoken text is the recorded narration in public/voiceover/beat-NN.mp3, word for word.
//
// Times are seconds into the beat. Cue and landing times sit at the end of the pause before the
// word, measured with ffmpeg silencedetect (noise -38 dB, 0.12 s) on each clip; a figure inside a
// phrase is placed by its syllable position within that phrase.

export const FPS = 30;
export const TOTAL_FRAMES = 5400;
export const BOLTS_S = 8;

export type Cue = { at: number; text: string; onScreen?: boolean };
export type Beat = {
  number: number;
  seconds: number;
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
    seconds: 15,
    spoken:
      "A procedure says: mark ten boxes, in order. Did it happen, and can you prove what you saw? witness answers with findings, and a finding either carries an evidence id or it does not exist.",
    cues: [
      { at: 0.18, text: "A procedure says: mark ten boxes, in order." },
      { at: 3.99, text: "Did it happen, and can you prove what you saw?", onScreen: true },
      { at: 6.78, text: "witness answers with findings, and a finding either carries an evidence id or it does not exist." },
    ],
    at: { mark: 0.2, line: 0.4, rule: 0.9, bolts: 3.99 },
    text: {
      line: "Did it happen, and can you prove what you saw?",
      caption: "demo_bolts_v1_clean.mp4, 0–8 s",
      note: "intended use case — not a measurement",
    },
    onScreen:
      "Near-black ground; the small mono mark draws on above the question, set alone, with a rule beneath. At 4 s the bolt B-roll is uncovered in place for its 8 s, captioned as an intended use case, not a measurement.",
    sources: ["`docs/AGENT_GUIDE.md`", "`data/raw/demo_bolts_v1_clean.mp4` (0–8 s)"],
  },
  {
    number: 2,
    seconds: 25,
    spoken:
      "The input is an event log: which part, in what order, with which still. The audit is deterministic. Coverage, ordering and undocumented parts. Here, one box has no witnessed event, so the report asks for human review instead of calling it done.",
    cues: [
      { at: 0.17, text: "The input is an event log: which part, in what order, with which still." },
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
      "The opening rule becomes the header of the skipped clip's event log, drawn as ten procedure parts that fill in the order they were seen, each with its evidence still id; one real still; the three checks; the empty part outlined; the report's two findings.",
    sources: [
      "`artifacts/real_skipped_05/findings.json`",
      "the event log of session `58bb85e4-77eb-4297-882a-aac467a05bca`",
      "`data/procedures/panel_boxes_v1.json`",
    ],
  },
  {
    number: 3,
    seconds: 20,
    spoken:
      "Every report is hash-linked: the record hash, then the HTML bytes, then the manifest. Anyone can recompute it from the output. These are local hashes, not a signature. Without an external trust anchor they do not stop someone rewriting files and manifest together.",
    cues: [
      { at: 0.14, text: "Every report is hash-linked: the record hash, then the HTML bytes, then the manifest." },
      { at: 6.17, text: "Anyone can recompute it from the output." },
      { at: 8.62, text: "These are local hashes, not a signature. Without an external trust anchor they do not stop someone rewriting files and manifest together." },
    ],
    at: { record: 2.11, report: 3.25, manifest: 4.93, recompute: 6.17, limit: 8.62, anchor: 11.64 },
    text: {
      record: "record hash",
      report: "report hash",
      manifest: "manifest.sha256",
      recompute: "report_hash = ",
      limit: "local hashes, not a signature",
      anchor: "without an external trust anchor, files and manifest can be rewritten together",
      source: "artifacts/real_skipped_05/manifest.json",
    },
    onScreen:
      "The chain as three points and two drawn links: record hash, report hash, manifest.sha256, each with its full value; the recompute rule; the limit, local hashes and no trust anchor, in the same frame.",
    sources: ["`artifacts/real_skipped_05/manifest.json`", "`artifacts/real_skipped_05/manifest.sha256`", "`docs/RULES.md`"],
  },
  {
    number: 4,
    seconds: 21.4,
    spoken:
      "The audit logic is gated on 25 cases, and all 25 are synthetic: 10 true positives, 1 false positive, 3 false negatives. That tests the rules, not the real world.",
    cues: [
      { at: 0.2, text: "The audit logic is gated on 25 cases, and all 25 are synthetic: 10 true positives, 1 false positive, 3 false negatives." },
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
      "The chain's line becomes a baseline; 25, 10, 1 and 3 land on it in spoken order with the full-width caveat, then nothing moves for the rest of the beat.",
    sources: ["`docs/RISK_GATE.md`"],
  },
  {
    number: 5,
    seconds: 40,
    spoken:
      "Then we tried producing the event log from real footage, with deterministic geometry and no model. This is the operator's own scene: one sheet, one angle, one lighting condition. On the clean clip the extractor found 9 of 10 marks in the right order and missed box 9 at 1.91 times its baseline. On the skipped clip it recovered the three-four swap but flagged blank box 6, because the sheet slid about 25 pixels under fixed masks.",
    cues: [
      { at: 0.17, text: "Then we tried producing the event log from real footage, with deterministic geometry and no model." },
      { at: 6.28, text: "This is the operator's own scene: one sheet, one angle, one lighting condition." },
      { at: 11.57, text: "On the clean clip the extractor found 9 of 10 marks in the right order and missed box 9 at 1.91 times its baseline." },
      { at: 19.4, text: "On the skipped clip it recovered the three-four swap but flagged blank box 6, because the sheet slid about 25 pixels under fixed masks." },
    ],
    at: { divider: 0.6, scope: 3.4, scene: 8.28, clean: 11.57, found: 13.56, missed: 15.6, ratio: 16.95, skipped: 19.4, swap: 20.46, blank: 22.59, slid: 26.41, outline: 27.65 },
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
      "No picture and no model output: the stated figures of the geometry-only run, clean clip and skipped clip side by side, each landing as it is spoken; the cause line is outlined.",
    sources: ["`docs/REAL_MEDIA.md` (Round 7 measurement)"],
  },
  {
    number: 6,
    seconds: 25,
    spoken:
      "So we made the masks follow the sheet, and required a clear correlation peak. On both clips the peak fell short, 1.97 and 1.93 against a required 2.0, and the extractor stopped instead of guessing. We did not lower the bar. Perception is frozen, and this disagreement with the key is the measured result.",
    cues: [
      { at: 0.18, text: "So we made the masks follow the sheet, and required a clear correlation peak." },
      { at: 4.52, text: "On both clips the peak fell short, 1.97 and 1.93 against a required 2.0, and the extractor stopped instead of guessing." },
      { at: 13.07, text: "We did not lower the bar. Perception is frozen, and this disagreement with the key is the measured result." },
    ],
    at: { title: 0.6, threshold: 2.28, bars: 4.52, clean: 6.65, skipped: 7.77, required: 9.44, stopped: 10.34 },
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
      "The outline from beat 5 opens as a mask into the frame of the comparison: a threshold line drawn at 2.0, two bars drawn toward it that stop at 1.97 and 1.93, and the frames where extraction stopped. Then the frame holds still.",
    sources: ["`docs/REAL_MEDIA.md` (Round 8 measurement)", "`docs/DECISIONS.md` (D030, D031)"],
  },
  {
    number: 7,
    seconds: 23.6,
    spoken:
      "Then a Meta segmentation model, sam-3.1, proposed the boxes and geometry named them: 78 anchor calls, 0.195 dollars, and both clips now agree with the key. The naming rule was calibrated on six frames from these same clips, so this is a demonstration, not independent validation.",
    cues: [
      { at: 0.19, text: "Then a Meta segmentation model, sam-3.1, proposed the boxes and geometry named them:" },
      { at: 7.44, text: "78 anchor calls, 0.195 dollars, and both clips now agree with the key." },
      { at: 14.07, text: "The naming rule was calibrated on six frames from these same clips, so this is a demonstration, not independent validation." },
    ],
    at: { meta: 0.6, model: 2.42, skipped: 5.83, anchors: 7.44, cost: 9.28, agree: 11.74 },
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
      "The model overlays of both clips at the same crop, clean then skipped, uncovered by a moving edge; sam-3.1, 78 anchors at one call each, USD 0.1950, agreement with the key. The calibration limit types on in the lower-left column and stays to the end.",
    sources: [
      "`artifacts/overlays/model_clean_anchor48.png`",
      "`artifacts/overlays/model_skipped_anchor28.png`",
      "`docs/REAL_MEDIA.md` (Model-produced events)",
      "`docs/STATUS.md` (independence limit)",
    ],
  },
  {
    number: 8,
    seconds: 10,
    spoken: "witness: an event log in, evidence-linked findings out, and every miss on the record.",
    cues: [{ at: 0.17, text: "witness: an event log in, evidence-linked findings out, and every miss on the record.", onScreen: true }],
    at: { claim: 0.17, rule: 0.6, ruleEnd: 5.74, mark: 6.01 },
    text: { claim: "witness: an event log in, evidence-linked findings out, and every miss on the record." },
    onScreen:
      "The claim, one slow drawn rule beneath it, and in the quiet after the narration the full gradient mark drawn on above it. The calibration limit stays lower left.",
    sources: ["`docs/DECISIONS.md` (D030)", "`demo-video/public/brand/witness-logo.svg`"],
  },
];

export const framesOf = (seconds: number): number => Math.round(seconds * FPS);

export const startOf = (number: number): number =>
  BEATS.filter((beat) => beat.number < number).reduce((sum, beat) => sum + framesOf(beat.seconds), 0);

/** The global frame of a moment `seconds` into beat `number`. */
export const at = (number: number, seconds: number): number => startOf(number) + framesOf(seconds);
