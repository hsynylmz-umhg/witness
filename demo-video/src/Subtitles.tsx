import React from "react";
import { BEATS, Cue, at, framesOf, startOf } from "./beats";
import { step, typeOn } from "./motion";
import { color, font, frames, layout, leading, opacity, size, stroke } from "./theme";

// The cue being spoken at frame f, with its start as a global frame; cues end with their beat.
const cueAt = (f: number): (Cue & { from: number }) | null => {
  for (const beat of BEATS) {
    const start = startOf(beat.number);
    if (f < start || f >= start + framesOf(beat.seconds)) continue;
    let current: (Cue & { from: number }) | null = null;
    for (const cue of beat.cues) {
      const from = at(beat.number, cue.at);
      if (f >= from) current = { ...cue, from };
    }
    return current;
  }
  return null;
};

// One band across the foot of the frame with an accent hairline for its top edge. Each cue types on
// within frames.typeOn, then settles to half opacity so the eye returns to the picture. A cue whose
// words are already set on screen as a display line leaves the band empty.
export const Subtitles: React.FC<{ f: number }> = ({ f }) => {
  const cue = cueAt(f);
  const text = cue && !cue.onScreen ? cue.text : "";
  const shown = cue ? typeOn(f, cue.from, text) : 0;
  const settle = cue ? 1 - (1 - opacity.settled) * step(f, cue.from + frames.typeOn) : 1;
  const left = (layout.w - layout.band.textW) / 2;
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        top: layout.h - layout.band.h,
        width: layout.w,
        height: layout.band.h,
        background: color.band,
      }}
    >
      <div
        style={{
          position: "absolute",
          left,
          top: 0,
          width: layout.band.textW,
          height: stroke.hair,
          background: color.accent,
          opacity: opacity.bandRule,
        }}
      />
      <div
        style={{
          position: "absolute",
          left,
          top: 0,
          width: layout.band.textW,
          height: layout.band.h,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
          fontFamily: font.body,
          fontSize: size.sm,
          lineHeight: leading.body,
          color: color.ink,
          opacity: settle,
        }}
      >
        <span>
          {text.slice(0, shown)}
          <span style={{ opacity: 0 }}>{text.slice(shown)}</span>
        </span>
      </div>
    </div>
  );
};
