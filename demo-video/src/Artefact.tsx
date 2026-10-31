import React from "react";
import { reveal, rule, step, typeOn } from "./motion";
import { color, font, layout, leading, opacity, size, space, stroke } from "./theme";

// The one frame for every real artefact: a faint accent border, four corner ticks drawn on, the
// content inset and uncovered in place, the file name beneath in mono, and an optional note.
export const Artefact: React.FC<{
  f: number;
  at: number;
  until?: number;
  x: number;
  y: number;
  w: number;
  h: number;
  caption: string;
  note?: string;
  children: React.ReactNode;
}> = ({ f, at, until, x, y, w, h, caption, note, children }) => {
  const tick = rule(f, at, [0, layout.artefact.tick])[1];
  const corners: [number, number, number, number][] = [
    [0, 0, 1, 1],
    [w, 0, -1, 1],
    [0, h, 1, -1],
    [w, h, -1, -1],
  ];
  const typed = note ? typeOn(f, at, note) : 0;
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width: w,
        height: h + space.s4,
        clipPath: reveal(f, at, { until }),
      }}
    >
      <div
        style={{
          position: "absolute",
          left: space.s2,
          top: space.s2,
          width: w - 2 * space.s2,
          height: h - 2 * space.s2,
          overflow: "hidden",
        }}
      >
        {children}
      </div>
      <svg width={w} height={h} style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }}>
        <rect
          x={stroke.hair / 2}
          y={stroke.hair / 2}
          width={w - stroke.hair}
          height={h - stroke.hair}
          fill="none"
          stroke={color.accent}
          strokeOpacity={opacity.frameBorder}
          strokeWidth={stroke.hair}
        />
        {corners.map(([cx, cy, dx, dy]) => (
          <g key={`${cx}-${cy}`} stroke={color.accent} strokeWidth={stroke.rule}>
            <line x1={cx} y1={cy} x2={cx + dx * tick} y2={cy} />
            <line x1={cx} y1={cy} x2={cx} y2={cy + dy * tick} />
          </g>
        ))}
      </svg>
      <div
        style={{
          position: "absolute",
          left: 0,
          top: h + layout.artefact.captionGap,
          fontFamily: font.mono,
          fontSize: size.xs,
          lineHeight: leading.body,
          color: color.inkMuted,
          whiteSpace: "nowrap",
          opacity: step(f, at, 0),
        }}
      >
        {caption}
      </div>
      {note ? (
        <div
          style={{
            position: "absolute",
            left: 0,
            top: h + layout.artefact.captionGap + size.xs * leading.body,
            fontFamily: font.body,
            fontSize: size.sm,
            lineHeight: leading.body,
            color: color.ink,
            whiteSpace: "nowrap",
          }}
        >
          <span>{note.slice(0, typed)}</span>
          <span style={{ opacity: 0 }}>{note.slice(typed)}</span>
        </div>
      ) : null}
    </div>
  );
};
