import React from "react";
import { drawOn } from "./motion";
import { color, ref } from "./theme";

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

// The mark as stored in public/brand, drawn on along its own strokes in pen order (data-pen): the pen
// starts at joint 0, and each rod ends at the joint with the same pen number. Elements keep the file's
// depth order. A joint fills by sweeping a stroke as wide as its radius.
export const Mark: React.FC<{
  f: number;
  at: number;
  duration: number;
  x: number;
  y: number;
  size: number;
  geometry: MarkGeometry;
  full: boolean;
}> = ({ f, at, duration, x, y, size, geometry, full }) => {
  const total = geometry.rods.reduce((sum, rod) => sum + lengthOf(rod), 0);
  const ordered = geometry.rods.slice().sort((a, b) => a.pen - b.pen);
  const starts: Record<number, number> = {};
  let done = 0;
  for (const rod of ordered) {
    starts[rod.pen] = at + (done / total) * duration;
    done += lengthOf(rod);
  }
  const span = (rod: Rod) => (lengthOf(rod) / total) * duration;
  const arrival = (pen: number) => {
    const rod = ordered.find((r) => r.pen === pen);
    return rod ? starts[pen] + span(rod) : at;
  };
  const sweep = Math.max(1, duration / (ordered.length + 1));
  const paint = full ? ref.rampPaint : color.ink;
  const rimOf = (pen: number) => geometry.rims.find((rim) => rim.pen === pen);
  const [gx1, gy1, gx2, gy2] = geometry.gradient;
  return (
    <svg viewBox="0 0 1024 1024" width={size} height={size} style={{ position: "absolute", left: x, top: y, overflow: "visible" }}>
      {full ? (
        <defs>
          <linearGradient id={ref.ramp} gradientUnits="userSpaceOnUse" x1={gx1} y1={gy1} x2={gx2} y2={gy2}>
            <stop offset="0" stopColor={color.rampBase} />
            <stop offset="1" stopColor={color.rampCrown} />
          </linearGradient>
        </defs>
      ) : null}
      {geometry.rods.map((rod) => {
        const start = starts[rod.pen];
        const rim = full ? rimOf(rod.pen) : undefined;
        return f < start ? null : (
          <g key={`rod-${rod.pen}`}>
            <line
              x1={rod.x1}
              y1={rod.y1}
              x2={rod.x2}
              y2={rod.y2}
              stroke={paint}
              strokeWidth={rod.width}
              strokeLinecap="round"
              {...drawOn(f, start, lengthOf(rod), span(rod))}
            />
            {rim ? (
              <line
                x1={rim.x1}
                y1={rim.y1}
                x2={rim.x2}
                y2={rim.y2}
                stroke={color.accent}
                strokeWidth={rim.width}
                {...drawOn(f, start, lengthOf(rim), span(rod))}
              />
            ) : null}
          </g>
        );
      })}
      {geometry.joints.map((joint) =>
        f < arrival(joint.pen) ? null : (
          <circle
            key={`joint-${joint.pen}`}
            cx={joint.cx}
            cy={joint.cy}
            r={joint.r / 2}
            fill="none"
            stroke={paint}
            strokeWidth={joint.r}
            transform={`rotate(-90 ${joint.cx} ${joint.cy})`}
            {...drawOn(f, arrival(joint.pen), Math.PI * joint.r, sweep)}
          />
        ),
      )}
      {full
        ? geometry.arcs.map((arc) =>
            f < arrival(arc.pen) ? null : (
              <path
                key={`arc-${arc.pen}`}
                d={arc.d}
                fill="none"
                stroke={color.accent}
                strokeWidth={arc.width}
                {...drawOn(f, arrival(arc.pen), Math.PI * arc.r, sweep)}
              />
            ),
          )
        : null}
    </svg>
  );
};
