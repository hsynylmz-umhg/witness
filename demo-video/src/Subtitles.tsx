import React from "react";
import { BEATS, Cue, at, endOf, startOf } from "./beats";
import { step, typeOn } from "./motion";
import { color, font, frames, layout, leading, opacity, size, stroke } from "./theme";

// The cue being spoken at frame f, with its start as a global frame; a cue stays until the next one
// or the end of its beat, so the band is never empty while the narration plays.
const cueAt = (f: number): (Cue & { from: number }) | null => {
  for (const beat of BEATS) {
    if (f < startOf(beat.number) || f >= endOf(beat.number)) continue;
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
// within frames.typeOn at no more than opacity.subtitle, then settles to opacity.settled so the eye
// returns to the picture. A cue whose words are also set as display type stays at opacity.settled.
export const Subtitles: React.FC<{ f: number }> = ({ f }) => {
  const cue = cueAt(f);
  const text = cue ? cue.text : "";
  const shown = cue ? typeOn(f, cue.from, text) : 0;
  const level = !cue || cue.onScreen
    ? opacity.settled
    : opacity.subtitle - (opacity.subtitle - opacity.settled) * step(f, cue.from + frames.typeOn);
  const left = (layout.w - layout.band.textW) / 2;
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        top: layout.band.top,
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
          opacity: level,
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
