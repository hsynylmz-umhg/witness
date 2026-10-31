import { interpolate } from "remotion";
import { ease, frames } from "./theme";

// The film's five verbs (MOTION.md). Every beat is composed from these and nothing else moves.

const progress = (f: number, at: number, duration: number, curve: (t: number) => number): number =>
  !Number.isFinite(at)
    ? 0
    : duration <= 0
      ? Number(f >= at)
      : interpolate(f, [at, at + duration], [0, 1], { easing: curve, extrapolateLeft: "clamp", extrapolateRight: "clamp" });

type Inset = [number, number, number, number];

/**
 * A moving edge uncovers content that is already in place, and from `until` covers it again in the
 * same direction; the content never moves. With `from` (an inset in percent of the box: top, right,
 * bottom, left) the mask opens from that window instead, as a state change.
 */
export const reveal = (
  f: number,
  at: number,
  { until = Infinity, edge = "left", from }: { until?: number; edge?: "left" | "top"; from?: Inset } = {},
): string => {
  const open = from ? progress(f, at, frames.reveal, ease.state) : progress(f, at, frames.reveal, ease.entrance);
  const shut = progress(f, until, frames.reveal, ease.entrance);
  const closed: Inset = from ?? (edge === "left" ? [0, 100, 0, 0] : [0, 0, 100, 0]);
  const gone: Inset = edge === "left" ? [0, 0, 0, 100] : [100, 0, 0, 0];
  const inset = closed.map((c, i) => c * (1 - open) + gone[i] * shut);
  return `inset(${inset.map((v) => `${v}%`).join(" ")})`;
};

/** A stroke grows along its own length; spread the result onto the SVG element that has that length. */
export const drawOn = (f: number, at: number, length: number, duration: number) => ({
  strokeDasharray: length,
  strokeDashoffset: length * (1 - progress(f, at, duration, ease.entrance)),
});

/** How many characters of a text are shown: all of them within frames.typeOn, and never again animated. */
export const typeOn = (f: number, at: number, text: string): number =>
  Math.ceil(progress(f, at, frames.typeOn, ease.entrance) * text.length);

/** A state changes once, from 0 to 1. With a duration of 0 a stated number lands whole in one frame. */
export const step = (f: number, at: number, duration: number = frames.state): number =>
  progress(f, at, duration, ease.state);

/**
 * A straight rule along one axis: drawn from its first end from `at`, and, for a matched transition,
 * carried to the extent `to` from `toAt`. Returns the rule's two ends.
 */
export const rule = (
  f: number,
  at: number,
  extent: [number, number],
  { duration = frames.rule, to, toAt = Infinity }: { duration?: number; to?: [number, number]; toAt?: number } = {},
): [number, number] => {
  const drawn = progress(f, at, duration, ease.entrance);
  const carried = to ? progress(f, toAt, frames.state, ease.state) : 0;
  const target = to ?? extent;
  const a = extent[0] + (target[0] - extent[0]) * carried;
  const b = extent[0] + (extent[1] - extent[0]) * drawn;
  return [a, b + (target[1] - extent[1]) * carried];
};
