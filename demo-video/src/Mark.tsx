import React from "react";
import { drawOn } from "./motion";
import { color, mark, ref } from "./theme";

export type Rod = { x1: number; y1: number; x2: number; y2: number; width: number; pen: number };
export type Joint = { cx: number; cy: number; r: number; pen: number };
export type Arc = { d: string; r: number; width: number; pen: number };
export type MarkGeometry = {
  rods: Rod[];
  rims: Rod[];
  joints: Joint[];
  arcs: Arc[];
  gradient: [number, number, number, number];
  stops: string[];
};

const lengthOf = (rod: Rod) => Math.hypot(rod.x2 - rod.x1, rod.y2 - rod.y1);

// A rod shortened at each end to the edge of the joint it meets, so a stroke-only joint stays a ring.
const trimmed = (rod: Rod, joints: Joint[]): Rod => {
  const near = (x: number, y: number) =>
    joints.slice().sort((a, b) => Math.hypot(a.cx - x, a.cy - y) - Math.hypot(b.cx - x, b.cy - y))[0];
  const length = lengthOf(rod);
  const ux = (rod.x2 - rod.x1) / length;
  const uy = (rod.y2 - rod.y1) / length;
  const a = near(rod.x1, rod.y1).r;
  const b = near(rod.x2, rod.y2).r;
  return { ...rod, x1: rod.x1 + ux * a, y1: rod.y1 + uy * a, x2: rod.x2 - ux * b, y2: rod.y2 - uy * b };
};

// The mark as stored in public/brand, drawn on along its own strokes in pen order (data-pen): the pen
// starts at joint 0, and each rod ends at the joint with the same pen number. "mono" is the opening
// mark in ink, its joints filled by a sweeping stroke. "stroke" is the closing mark: the same mono
// construction with no fills, the ramp as a gradient stroke, every joint one ring of the same
// proportion with the same accent rim, and the rods' left-edge rims from the full mark.
export const Mark: React.FC<{
  f: number;
  at: number;
  duration: number;
  x: number;
  y: number;
  size: number;
  geometry: MarkGeometry;
  rims?: Rod[];
  variant: "mono" | "stroke";
}> = ({ f, at, duration, x, y, size, geometry, rims = [], variant }) => {
  const stroked = variant === "stroke";
  const rods = stroked ? geometry.rods.map((rod) => trimmed(rod, geometry.joints)) : geometry.rods;
  const total = rods.reduce((sum, rod) => sum + lengthOf(rod), 0);
  const ordered = rods.slice().sort((a, b) => a.pen - b.pen);
  const starts: Record<number, number> = {};
  let done = 0;
  for (const rod of ordered) {
    starts[rod.pen] = at + (done / total) * duration;
    done += lengthOf(rod);
  }
  const span = (rod: Rod) => (lengthOf(rod) / total) * duration;
  const arrival = (pen: number) => {
    const rod = ordered.filter((r) => r.pen === pen)[0];
    return rod ? starts[pen] + span(rod) : at;
  };
  const sweep = Math.max(1, duration / (ordered.length + 1));
  const paint = stroked ? ref.rampPaint : color.ink;
  const rimWidth = rims.length ? rims[0].width : 0;
  const [gx1, gy1, gx2, gy2] = geometry.gradient;
  return (
    <svg viewBox="0 0 1024 1024" width={size} height={size} style={{ position: "absolute", left: x, top: y, overflow: "visible" }}>
      {stroked ? (
        <defs>
          <linearGradient id={ref.ramp} gradientUnits="userSpaceOnUse" x1={gx1} y1={gy1} x2={gx2} y2={gy2}>
            <stop offset="0" stopColor={color.rampBase} />
            <stop offset="1" stopColor={color.rampCrown} />
          </linearGradient>
        </defs>
      ) : null}
      {rods.map((rod) => {
        const start = starts[rod.pen];
        const found = stroked ? rims.filter((r) => r.pen === rod.pen)[0] : undefined;
        const rim = found ? trimmed(found, geometry.joints) : undefined;
        return f < start ? null : (
          <g key={`rod-${rod.pen}`}>
            <line x1={rod.x1} y1={rod.y1} x2={rod.x2} y2={rod.y2} stroke={paint} strokeWidth={rod.width} strokeLinecap="round" {...drawOn(f, start, lengthOf(rod), span(rod))} />
            {rim ? (
              <line x1={rim.x1} y1={rim.y1} x2={rim.x2} y2={rim.y2} stroke={color.accent} strokeWidth={rim.width} {...drawOn(f, start, lengthOf(rim), span(rod))} />
            ) : null}
          </g>
        );
      })}
      {geometry.joints.map((joint) => {
        const from = arrival(joint.pen);
        if (f < from) return null;
        if (!stroked) {
          return (
            <circle
              key={`joint-${joint.pen}`}
              cx={joint.cx}
              cy={joint.cy}
              r={joint.r / 2}
              fill="none"
              stroke={paint}
              strokeWidth={joint.r}
              transform={`rotate(-90 ${joint.cx} ${joint.cy})`}
              {...drawOn(f, from, Math.PI * joint.r, sweep)}
            />
          );
        }
        const ring = joint.r * mark.ring;
        const middle = joint.r - ring / 2;
        const edge = joint.r - rimWidth / 2;
        return (
          <g key={`joint-${joint.pen}`} transform={`rotate(-90 ${joint.cx} ${joint.cy})`} fill="none">
            <circle cx={joint.cx} cy={joint.cy} r={middle} stroke={paint} strokeWidth={ring} {...drawOn(f, from, 2 * Math.PI * middle, sweep)} />
            <circle cx={joint.cx} cy={joint.cy} r={edge} stroke={color.accent} strokeWidth={rimWidth} {...drawOn(f, from, 2 * Math.PI * edge, sweep)} />
          </g>
        );
      })}
    </svg>
  );
};
