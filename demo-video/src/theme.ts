import { Easing } from "remotion";

/*
 * The film's only source of colour, size, radius, easing and duration (round 18). Nothing under
 * demo-video/src outside this file writes a literal colour or a pixel unit.
 *
 * Palette, Q1 "forensic dark". The ramp is the mark's own gradient, measured from the operator's
 * raster reference: base #01112F (5th percentile of its opaque pixels) to crown #194C9E (95th).
 * The ground is the ramp base, flat, one value. rampLow and rampHigh are the ramp at 35% and 60%
 * and draw quiet structure: empty states, tracks, dividers. The one accent is the mark's rim
 * highlight #3B80DE; it draws rules, ticks, focus outlines and the subtitle edge, and never fills
 * text. Ink is neutral, so no blue sits outside the ramp except the accent. Verified is a sea green
 * (hue 152 degrees) and rejected an amber (hue 36 degrees): neither is pure green or pure red, and
 * after an 8% saturation loss they are still Delta-E76 69.2 apart. No state is carried by colour
 * alone: each also has a check or cross glyph and a word.
 *
 * Contrast, WCAG 2.1, measured against the ground (relative luminance 0.0061):
 *   ink #F4F4F4            17.01:1   body text, needs at least 7
 *   inkMuted #A3A3A3        7.42:1   captions, needs at least 4.5
 *   settled subtitle        4.84:1   ink at 0.5 opacity over the band, a caption, needs at least 4.5
 *   verified #4BC08A        8.20:1
 *   rejected #E7A33E        8.65:1
 *   accent #3B80DE          4.75:1   structure only
 *   rampCrown #194C9E       2.29:1   the mark and structure, never text
 *
 * Type: five sizes. Bahnschrift is the display face, Segoe UI the body, Cascadia Mono the face for
 * identifiers, hashes and filenames. System stacks only; the render fetches no font.
 * Spacing: four steps on the 8 grid. Motion: two easings, one for entrances, one for state changes.
 */

export const color = {
  ground: "#01112F",
  rampBase: "#01112F",
  rampLow: "#092656",
  rampHigh: "#0F3472",
  rampCrown: "#194C9E",
  accent: "#3B80DE",
  ink: "#F4F4F4",
  inkMuted: "#A3A3A3",
  verified: "#4BC08A",
  rejected: "#E7A33E",
  band: "rgba(1, 17, 47, 0.72)",
  clear: "transparent",
};

export const opacity = { settled: 0.5, frameBorder: 0.35, bandRule: 0.6, stateFill: 0.16 };

export const font = {
  display: "Bahnschrift, 'DIN Alternate', 'Segoe UI', sans-serif",
  body: "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
  mono: "'Cascadia Mono', Consolas, 'Courier New', monospace",
};

export const size = { xl: 120, lg: 64, md: 40, sm: 30, xs: 22 };
export const leading = { tight: 1.1, body: 1.4 };
export const weight = { regular: 400, strong: 600 };
export const space = { s1: 8, s2: 24, s3: 48, s4: 96 };
export const radius = { none: 0 };
export const stroke = { hair: 1, rule: 2, outline: 3, threshold: 4, bar: 56, point: 12, cell: 120 };

export const ease = {
  entrance: Easing.bezier(0.16, 1, 0.3, 1),
  state: Easing.bezier(0.65, 0, 0.35, 1),
};

// Durations in frames at 30 fps. Only draw-ons may run longer than 20 frames.
export const frames = {
  typeOn: 15,
  reveal: 18,
  state: 18,
  rule: 30,
  outline: 30,
  threshold: 30,
  bars: 54,
  markSmall: 6,
  markLarge: 60,
};

export const ref = { ramp: "witness-ramp-film", rampPaint: "url(#witness-ramp-film)" };
export const still = { filter: "saturate(0.82)" };
export const glyph = { pass: "✓", fail: "✕", sep: " · " };

const W = 1920;
const H = 1080;
const M = space.s4;

export const layout = {
  w: W,
  h: H,
  left: M,
  right: W - M,
  top: M,
  sourceY: 32,
  band: { h: 112, textW: 1344 },
  caveat: { x: M, w: 480, bottom: 944 },
  artefact: { tick: 24, captionGap: space.s1 },
  b1: { markSize: 96, markY: M, lineY: 216, ruleY: 312, rule: [480, 1440] as [number, number], frame: { x: 530, y: 352, w: 859, h: 504 } },
  b2: { stripLeft: 288, idsY: 272, cellY: 344, evidenceY: 480, still: { x: M, y: 560, w: 528, h: 318 }, checksX: 720, checksY: 568, rowStep: 56, findingsY: 760, findingStep: 120, messageGap: 40 },
  b3: { chainY: 520, points: [336, 960, 1584], labelY: 432, valueY: 552, valueW: 480, formulaY: 680, limitY: 744, anchorY: 792 },
  b4: { baseY: 520, figureY: 376, labelY: 560, caveatY: 648, columns: [312, 744, 1176, 1608], tick: 24, columnW: 432 },
  b5: { scopeY: 120, sceneY: 184, divider: { x: 960, top: 280, bottom: 880 }, colY: 296, clean: M, skipped: 1008, colW: 816, foundY: 344, foundLabelY: 488, missedY: 584, ratioY: 640, swapY: 360, blankY: 424, slidY: 520, outline: [1000, 504, 1824, 648] as [number, number, number, number] },
  b6: { panel: [M, M, W - M, 920] as [number, number, number, number], titleX: 144, titleY: 144, labelX: 144, barX: 360, barL: 1100, rows: [420, 580], lineTop: 320, lineBottom: 680, requiredY: 264, requiredW: 240, valueX: 1508, stopGap: 40, zeroY: 640 },
  b7: { frame: { x: 624, y: 120, w: 1200 }, crop: { x: 40, y: 250, w: 1240, h: 460, srcW: 1280, srcH: 720 }, colX: M, colW: 480, modelY: 128, nameY: 168, anchorsY: 288, anchorsLabelY: 368, costY: 480, agreeY: 592 },
  b8: { claimY: 560, claimW: 1440, ruleY: 752, rule: [480, 1440] as [number, number], markSize: 360, markY: 120 },
};
