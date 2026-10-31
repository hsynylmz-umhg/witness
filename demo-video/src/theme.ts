import { Easing } from "remotion";

/*
 * The film's only source of colour, size, radius, easing and duration (round 19). Nothing under
 * demo-video/src outside this file writes a literal colour or a pixel unit.
 *
 * Palette, Q1 "forensic dark". The ramp is the mark's own gradient, measured from the operator's
 * raster reference: base #01112F (5th percentile of its opaque pixels) to crown #194C9E (95th).
 * The ground is #050B1A: one flat value, darker and slightly less saturated than the ramp base, and
 * deliberately off the ramp, so no stop of the mark ever equals the ground. rampLow and rampHigh are
 * the ramp at 35% and 60% and draw quiet structure: empty states, tracks, dividers. The one accent
 * is the mark's rim highlight #3B80DE; it draws rules, ticks, focus outlines, the rim and the
 * subtitle edge, and never fills text. Ink is neutral, so no blue sits outside the ramp except the
 * accent. Verified is a sea green (hue 152 degrees) and rejected an amber (hue 36 degrees): neither
 * is pure green or pure red, and after an 8% saturation loss they are still Delta-E76 69.2 apart.
 * No state is carried by colour alone: each also has a check or cross glyph and a word.
 *
 * Contrast, WCAG 2.1, measured against the ground (relative luminance 0.0035):
 *   ink #F4F4F4            17.86:1   body text, needs at least 7
 *   inkMuted #A3A3A3        7.79:1   captions, needs at least 4.5
 *   settled subtitle        4.95:1   ink at 0.5 opacity over the band, a caption, needs at least 4.5
 *   verified #4BC08A        8.61:1
 *   rejected #E7A33E        9.08:1
 *   accent #3B80DE          4.98:1   structure and the mark's rim: at least 3:1 against the ground
 *                                    and against a joint's interior, which is the ground
 *   rampBase #01112F        1.05:1   the mark's base, never text
 *   rampCrown #194C9E       2.40:1   the mark and structure, never text
 *
 * Type: five sizes. Bahnschrift is the display face, Segoe UI the body, Cascadia Mono the face for
 * identifiers, hashes and filenames. System stacks only; the render fetches no font.
 * Spacing: four steps on the 8 grid. Motion: two easings, one for entrances, one for state changes.
 */

export const color = {
  ground: "#050B1A",
  rampBase: "#01112F",
  rampLow: "#092656",
  rampHigh: "#0F3472",
  rampCrown: "#194C9E",
  accent: "#3B80DE",
  ink: "#F4F4F4",
  inkMuted: "#A3A3A3",
  verified: "#4BC08A",
  rejected: "#E7A33E",
  band: "rgba(5, 11, 26, 0.72)",
  report: "#FFFFFF",
  clear: "transparent",
};

export const opacity = { subtitle: 0.72, settled: 0.5, frameBorder: 0.35, bandRule: 0.6, stateFill: 0.16 };

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
  spine: 45,
  outline: 30,
  threshold: 30,
  bars: 54,
  markSmall: 6,
  markLarge: 60,
};

export const ref = { ramp: "witness-ramp-film", rampPaint: "url(#witness-ramp-film)" };
export const still = { filter: "saturate(0.82)" };
export const glyph = { pass: "✓", fail: "✕", sep: " · " };
// The closing mark is stroke-only: each joint is a ring whose width is this share of its radius.
export const mark = { ring: 0.4 };

const W = 1920;
const H = 1080;
const M = space.s4;

// The spine: one rule at one y for the whole film. Only its weight and colour follow its role.
export const spine = {
  y: 312,
  roles: [
    { beat: 1, weight: stroke.rule, colour: color.accent },
    { beat: 2, weight: stroke.rule, colour: color.accent },
    { beat: 3, weight: stroke.rule, colour: color.accent },
    { beat: 4, weight: stroke.outline, colour: color.inkMuted },
    { beat: 5, weight: stroke.rule, colour: color.rampHigh },
    { beat: 6, weight: stroke.rule, colour: color.inkMuted },
    { beat: 7, weight: stroke.rule, colour: color.accent },
    { beat: 8, weight: stroke.outline, colour: color.accent },
  ],
};

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
  b1: { markSize: 96, markY: M, lineY: 200, frame: { x: 530, y: 352, w: 859, h: 504 } },
  b2: { stripLeft: 288, idsY: 272, cellY: 344, evidenceY: 480, still: { x: M, y: 560, w: 528, h: 318 }, checksX: 720, checksY: 568, rowStep: 56, findingsY: 760, findingStep: 120, messageGap: 40 },
  b3: { points: [336, 960, 1584], labelY: 232, valueY: 344, valueW: 480, formulaY: 432, limitY: 480, anchorY: 520, report: { width: 960, height: 2400, title: ["h1", "h1"], findings: ["h2:nth-of-type(3)", "table"] } },
  b4: { figureY: 168, labelY: 352, caveatY: 432, columns: [312, 744, 1176, 1608], tick: 24, columnW: 432 },
  b5: { scopeY: 192, sceneY: 256, divider: { x: 960, top: 344, bottom: 880 }, colY: 344, clean: M, skipped: 1008, colW: 816, foundY: 384, foundLabelY: 528, missedY: 600, ratioY: 656, swapY: 392, blankY: 456, slidY: 552, outline: [1000, 536, 1824, 680] as [number, number, number, number] },
  b6: { panel: [M, 344, W - M, 776] as [number, number, number, number], titleY: 192, labelX: 144, barX: 360, barL: 1100, rows: [440, 600], lineBottom: 720, requiredY: 256, requiredW: 240, zeroY: 264, valueX: 1508, stopGap: 40 },
  b7: { crop: { x: 40, y: 358, w: 1240, h: 283, srcW: 1280, srcH: 720 }, columns: [M, 560, 1056, 1440], labelY: 144, valueY: 184, noteY: 264, columnW: 384 },
  b8: { claimY: 128, claimW: 1440, markSize: 300, markY: 380, ruleY: 712, rule: [480, 1440] as [number, number] },
};
